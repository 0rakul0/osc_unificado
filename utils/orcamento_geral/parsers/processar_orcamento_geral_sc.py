from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
OSC_NAME_PATTERN = re.compile(
    r"associ|instit|fundac|apae|sociedade|centro |casa |lar |movimento|federa|obra social|rede feminina|mmdc",
    re.IGNORECASE,
)
PUBLIC_PATTERN = re.compile(
    r"municipio|prefeitura|estado de|tribunal|camara|fundo municipal|consorcio publico|universidade",
    re.IGNORECASE,
)
INSTRUMENT_PATTERN = re.compile(
    r"conv..nio|termo de fomento|termo de colabora|termo de parceria|acordo de coopera|subven..o social|contrato[s]? de gest",
    re.IGNORECASE,
)
PRIVATE_NATURE_PATTERN = re.compile(
    r"entidade privada sem fins lucrativos|apae|oscip|organiz",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a base do SC Transferencias com foco em convenios/parcerias para OSC."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV bruto do SC. Se omitido, usa o caminho padrao do escopo.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("SC", scope) / "sc_transferencias.csv"


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", dtype=str, low_memory=False)


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = clean_text(current)
        result = cleaned if result is None else result.combine_first(cleaned)
    if result is None:
        return pd.Series(dtype="string")
    return result


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def extract_cnpj(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    return (
        cleaned.str.extract(r"\(([\d\.\-/]+)\)$", expand=False)
        .astype("string")
        .str.replace(r"\D", "", regex=True)
    )


def strip_document_suffix(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    return cleaned.str.replace(r"\s*\([^)]*\)\s*$", "", regex=True).str.strip()


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    beneficiario = clean_text(source_df.get("Beneficiário")).fillna("")
    instrumento = clean_text(source_df.get("Instrumento")).fillna("")
    natureza = clean_text(source_df.get("Natureza Jurídica Proponente")).fillna("")

    nome_osc = strip_document_suffix(source_df.get("Beneficiário")).fillna("")
    cnpj = extract_cnpj(source_df.get("Beneficiário")).fillna("")

    private_nature = natureza.str.contains(PRIVATE_NATURE_PATTERN, na=False)
    instrumento_focus = instrumento.str.contains(INSTRUMENT_PATTERN, na=False)
    name_focus = nome_osc.str.contains(OSC_NAME_PATTERN, na=False)
    public_name = nome_osc.str.contains(PUBLIC_PATTERN, na=False)
    pessoa_fisica = beneficiario.str.contains(r"\*{3}\.", regex=True, na=False)

    return instrumento_focus & (private_nature | name_focus) & ~public_name & ~pessoa_fisica & cnpj.str.len().eq(14)


def build_sc_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    cnpj = extract_cnpj(filtered.get("Beneficiário"))
    nome_osc = strip_document_suffix(filtered.get("Beneficiário"))
    data_envio = clean_text(filtered.get("Data Envio Proposta"))
    ano_data, mes = extract_year_month(data_envio)

    mapped = pd.DataFrame(
        {
            "uf": "SC",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(filtered.get("Ano")).combine_first(ano_data),
            "valor_total": first_non_empty(filtered.get("Valor Repassado"), filtered.get("Valor da Transferência")),
            "cnpj": cnpj,
            "nome_osc": nome_osc,
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": filtered.get("Município"),
            "objeto": first_non_empty(filtered.get("Objeto/Finalidade"), filtered.get("Título")),
            "modalidade": filtered.get("Instrumento"),
            "data_inicio": data_envio,
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input) if args.input else default_input_path(args.scope)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df = read_source(input_path)
    mapped = build_sc_budget_frame(source_df)
    normalized = normalize_preview(mapped, "SC", require_cnpj=True)

    output_path = output_dir / default_output_name("SC", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
