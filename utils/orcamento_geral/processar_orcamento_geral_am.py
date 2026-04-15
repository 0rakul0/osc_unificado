from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_DIR, ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
OSC_NAME_PATTERN = re.compile(
    r"associ|instit|fundac|museu|lar |casa |obra social|pestalozzi|agencia amazonense de desenvolvimento cultural|grupo de apoio|fazenda da esperanca|rede amazonica",
    re.IGNORECASE,
)
PUBLIC_NAME_PATTERN = re.compile(
    r"municipio|prefeitura|estado do amazonas|secretaria|tribunal|camara|universidade|fundo estadual|procuradoria",
    re.IGNORECASE,
)
PRIVATE_COMPANY_PATTERN = re.compile(r"\bltda\b|\bme\b|\bepp\b|comerc|construt|engenharia|servicos", re.IGNORECASE)
MODALIDADE_PATTERN = re.compile(
    r"(Contrato de Gest[aã]o|Termo de Fomento|Termo de Parceria|Termo de Coopera[cç][aã]o T[eé]cnica|Termo de Conv[eê]nio|Aditivo)",
    re.IGNORECASE,
)
VIGENCIA_PATTERN = re.compile(r"(\d{2}/\d{2}/\d{4})\s+at[eé]\s+(\d{2}/\d{2}/\d{4})", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a base legada de transferencias voluntarias do Amazonas com foco em OSC."
    )
    parser.add_argument(
        "--input",
        default=str(BASES_CONVENIOS_DIR / "AM" / "AM_convenios_transferencia_voluntaria.xlsx"),
        help="Arquivo xlsx bruto do Amazonas.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para o parquet final.",
    )
    return parser.parse_args()


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def clean_document(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    digits = cleaned.str.replace(r"\D", "", regex=True)
    return digits.mask(digits.eq(""))


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


def split_vigencia(series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if series is None:
        empty = pd.Series(dtype="string")
        return empty, empty

    def parse_value(value: object) -> tuple[object, object]:
        if pd.isna(value):
            return (pd.NA, pd.NA)
        match = VIGENCIA_PATTERN.search(str(value))
        if not match:
            return (pd.NA, pd.NA)
        return match.group(1), match.group(2)

    parsed = series.map(parse_value)
    frame = pd.DataFrame(parsed.tolist(), columns=["data_inicio", "data_fim"], index=series.index)
    return frame["data_inicio"].astype("string"), frame["data_fim"].astype("string")


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def extract_year_from_term(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    return cleaned.str.extract(r"/((?:19|20)\d{2})", expand=False).astype("string")


def infer_modalidade(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    extracted = cleaned.str.extract(MODALIDADE_PATTERN, expand=False)
    return extracted.astype("string").fillna("CONVENIO")


def read_source(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []
    for sheet_name in xl.sheet_names:
        frame = pd.read_excel(path, sheet_name=sheet_name)
        frame["__sheet__"] = sheet_name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("Convenente")).fillna("")
    cnpj = clean_document(source_df.get("CNPJ")).fillna("")
    return (
        nome.str.contains(OSC_NAME_PATTERN, na=False)
        & ~nome.str.contains(PUBLIC_NAME_PATTERN, na=False)
        & ~nome.str.contains(PRIVATE_COMPANY_PATTERN, na=False)
        & cnpj.str.len().eq(14)
    )


def build_am_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    data_inicio, data_fim = split_vigencia(filtered.get("Vigencia"))
    ano_inicio, mes = extract_year_month(data_inicio)
    ano_termo = extract_year_from_term(filtered.get("Nº Termo"))

    mapped = pd.DataFrame(
        {
            "uf": "AM",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano_inicio.combine_first(ano_termo),
            "valor_total": filtered.get("Valor do Repasse (R$)"),
            "cnpj": clean_document(filtered.get("CNPJ")),
            "nome_osc": filtered.get("Convenente"),
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(filtered.get("Objeto"), filtered.get("Título")),
            "modalidade": infer_modalidade(filtered.get("Nº Termo")),
            "data_inicio": data_inicio,
            "data_fim": data_fim,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df = read_source(input_path)
    mapped = build_am_budget_frame(source_df)
    normalized = normalize_preview(mapped, "AM", require_cnpj=True)

    output_path = output_dir / "AM.parquet"
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
