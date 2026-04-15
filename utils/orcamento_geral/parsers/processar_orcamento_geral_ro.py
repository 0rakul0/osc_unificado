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
    r"associ|instit|fundac|apae|sociedade|centro |casa |lar |igreja|paroquia|federa|movimento|mmdc|autista",
    re.IGNORECASE,
)
PUBLIC_PATTERN = re.compile(
    r"municipio|prefeitura|estado de|governo do estado|secretaria|camara|tribunal|universidade|instituto federal|campus",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa as transferencias realizadas de RO com foco em beneficiarios OSC."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV bruto de RO. Se omitido, usa o caminho padrao do escopo.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("RO", scope) / "ro_transferencias_realizadas.csv"


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig")


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


def extract_date(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    return cleaned.str.extract(r"(\d{2}/\d{2}/\d{4})", expand=False).astype("string")


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    beneficiario = clean_text(source_df.get("beneficiario")).fillna("")
    return beneficiario.str.contains(OSC_NAME_PATTERN, na=False) & ~beneficiario.str.contains(PUBLIC_PATTERN, na=False)


def build_ro_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    data_repasse = extract_date(filtered.get("valor_repassado_data"))
    ano_repasse, mes = extract_year_month(data_repasse)

    mapped = pd.DataFrame(
        {
            "uf": "RO",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(filtered.get("ano_consulta")).combine_first(ano_repasse),
            "valor_total": filtered.get("valor_total_previsto"),
            "cnpj": pd.NA,
            "nome_osc": filtered.get("beneficiario"),
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("objeto"),
            "modalidade": first_non_empty(filtered.get("numero_instrumento")),
            "data_inicio": data_repasse,
            "data_fim": filtered.get("vigencia"),
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
    mapped = build_ro_budget_frame(source_df)
    normalized = normalize_preview(mapped, "RO", require_cnpj=False)

    output_path = output_dir / default_output_name("RO", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
