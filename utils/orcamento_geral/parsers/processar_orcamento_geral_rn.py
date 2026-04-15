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
    r"associ|apae|funda[cç][aã]o|institut|sociedade|grupo reviver|liga|n[uú]cleo|federa[cç][aã]o|casa do menor|centro social",
    re.IGNORECASE,
)
PUBLIC_NAME_PATTERN = re.compile(
    r"prefeitura|municipal|c[âa]mara|governo do estado|secretaria|tribunal|universidade|fundo municipal|consorcio",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa os convênios concedidos do RN com foco em OSC no orçamento geral."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV bruto consolidado do RN. Se omitido, usa o caminho padrao do escopo.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("RN", scope) / "rn_convenios_concedidos.csv"


def read_source(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, dtype=str, encoding="latin1")


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


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    tipo = clean_text(source_df.get("TipoConvenente")).fillna("")
    nome = clean_text(source_df.get("Convenente")).fillna("")

    tipo_osc = tipo.str.contains(r"terceiro setor", case=False, na=False)
    nome_osc = nome.str.contains(OSC_NAME_PATTERN, na=False)
    nome_publico = nome.str.contains(PUBLIC_NAME_PATTERN, na=False)

    return (tipo_osc | nome_osc) & ~nome_publico


def build_rn_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    data_celebracao = clean_text(filtered.get("DataCelebracao"))
    ano_data, mes = extract_year_month(data_celebracao)

    mapped = pd.DataFrame(
        {
            "uf": "RN",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(filtered.get("ano")).combine_first(ano_data),
            "valor_total": filtered.get("ValorTotal"),
            "cnpj": filtered.get("CNPJConvenente"),
            "nome_osc": filtered.get("Convenente"),
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(filtered.get("Processo")),
            "modalidade": first_non_empty(filtered.get("TipoConvenente"), filtered.get("SecretariaConcedente")),
            "data_inicio": data_celebracao,
            "data_fim": first_non_empty(filtered.get("VigenciaUltimoAditivo"), filtered.get("DataVigencia")),
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
    mapped = build_rn_budget_frame(source_df)
    normalized = normalize_preview(mapped, "RN", require_cnpj=True)

    output_path = output_dir / default_output_name("RN", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
