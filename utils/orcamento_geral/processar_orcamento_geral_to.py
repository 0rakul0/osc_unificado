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
    r"associ|instit|fundac|sociedade|federa|cooper|servico nacional|museu|casa |lar |obra social|apae|igreja|pastoral|caritas",
    re.IGNORECASE,
)
PUBLIC_NAME_PATTERN = re.compile(
    r"prefeitura|municipio|estado do tocantins|secretaria|tribunal|camara|fundo municipal|universidade|defensoria|governo do estado",
    re.IGNORECASE,
)
VIGENCIA_PATTERN = re.compile(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a base legada de convenios do Tocantins com foco em OSC."
    )
    parser.add_argument(
        "--input",
        default=str(BASES_CONVENIOS_DIR / "TO" / "convenios_completo.xlsx"),
        help="Arquivo xlsx bruto do Tocantins.",
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


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("Convenente")).fillna("")
    cnpj = clean_document(source_df.get("Cnpj")).fillna("")
    return nome.str.contains(OSC_NAME_PATTERN, na=False) & ~nome.str.contains(PUBLIC_NAME_PATTERN, na=False) & cnpj.str.len().eq(14)


def build_to_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    data_inicio, data_fim = split_vigencia(filtered.get("Data de Vigência"))
    ano_abertura, mes_abertura = extract_year_month(filtered.get("Data de Abertura"))
    ano_inicio, _ = extract_year_month(data_inicio)

    mapped = pd.DataFrame(
        {
            "uf": "TO",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano_abertura.combine_first(ano_inicio),
            "valor_total": filtered.get("Valor do Convênio"),
            "cnpj": clean_document(filtered.get("Cnpj")),
            "nome_osc": filtered.get("Convenente"),
            "mes": mes_abertura,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("Objeto"),
            "modalidade": filtered.get("Situação"),
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

    source_df = pd.read_excel(input_path)
    mapped = build_to_budget_frame(source_df)
    normalized = normalize_preview(mapped, "TO", require_cnpj=True)

    output_path = output_dir / "TO.parquet"
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
