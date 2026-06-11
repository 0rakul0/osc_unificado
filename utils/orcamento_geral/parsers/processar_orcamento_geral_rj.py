from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import unicodedata
import zipfile

import pandas as pd
import polars as pl
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS, clean_cnpj
from utils.convenios.unificador import (
    build_parquet_table,
    clean_currency_text,
    clean_integer_like_text,
    clean_required_text,
)
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "ESTADO_ORCAMENTO_GERAL"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Processa a despesa geral do RJ no schema padrao.")
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV ou ZIP da despesa do RJ. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    zip_path = uf_raw_dir("RJ", scope) / "despesa.zip"
    return zip_path if zip_path.exists() else uf_raw_dir("RJ", scope) / "despesa2026.csv"


def infer_year(path: Path) -> str:
    match = re.search(r"(19|20)\d{2}", path.stem)
    return match.group(0) if match else "2026"


def normalize_column_name(value: str) -> str:
    text = "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def read_csv_polars(source: object) -> pl.DataFrame:
    return pl.read_csv(source, separator=";", encoding="utf8-lossy", skip_rows=5, infer_schema=False)


def iter_source_frames(path: Path) -> list[tuple[pl.DataFrame, str]]:
    if path.suffix.lower() != ".zip":
        return [(read_csv_polars(path), infer_year(path))]

    frames: list[tuple[pl.DataFrame, str]] = []
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if not name.lower().endswith(".csv"):
                continue
            with archive.open(name) as handle:
                frames.append((read_csv_polars(handle), infer_year(Path(name))))
    return frames


def polars_column(source_df: pl.DataFrame, *names: str) -> str | None:
    normalized = {normalize_column_name(column): column for column in source_df.columns}
    for name in names:
        if name in source_df.columns:
            return name
        column = normalized.get(normalize_column_name(name))
        if column is not None:
            return column
    return None


def pl_col_or_null(source_df: pl.DataFrame, *names: str) -> pl.Expr:
    column = polars_column(source_df, *names)
    return pl.col(column).cast(pl.String) if column else pl.lit(None, dtype=pl.String)


def first_non_empty_expr(*exprs: pl.Expr) -> pl.Expr:
    return pl.coalesce([expr.str.strip_chars().replace("", None) for expr in exprs])


def first_non_zero_expr(*exprs: pl.Expr) -> pl.Expr:
    cleaned: list[pl.Expr] = []
    for expr in exprs:
        text = expr.str.strip_chars().replace("", None)
        numeric = text.str.replace_all(r"\.", "").str.replace(",", ".").cast(pl.Float64, strict=False)
        cleaned.append(pl.when(numeric != 0).then(text).otherwise(None))
    return pl.coalesce(cleaned)


def build_rj_budget_frame(source_df: pl.DataFrame, ano: str) -> pd.DataFrame:
    mapped = source_df.select(
        [
            pl.lit("RJ").alias("uf"),
            pl.lit(ORIGEM_ORCAMENTO_GERAL).alias("origem"),
            pl.lit(ano).alias("ano"),
            first_non_zero_expr(
                pl_col_or_null(source_df, "Valor Pago"),
                pl_col_or_null(source_df, "Valor Liquidado"),
                pl_col_or_null(source_df, "Valor Empenhado"),
            ).alias("valor_total"),
            pl_col_or_null(source_df, "Credor").alias("cnpj"),
            pl_col_or_null(source_df, "Nome Credor").alias("nome_osc"),
            pl.lit(None, dtype=pl.String).alias("mes"),
            pl.lit(None, dtype=pl.String).alias("cod_municipio"),
            pl.lit(None, dtype=pl.String).alias("municipio"),
            pl_col_or_null(source_df, "Historico", "Historico").alias("objeto"),
            first_non_empty_expr(
                pl_col_or_null(source_df, "Nome Elemento"),
                pl_col_or_null(source_df, "Nome Modalidade de Aplicacao"),
            ).alias("modalidade"),
            pl.lit(None, dtype=pl.String).alias("data_inicio"),
            pl.lit(None, dtype=pl.String).alias("data_fim"),
        ]
    )
    return mapped.to_pandas()


def normalize_general_preview(preview_df: pd.DataFrame) -> pd.DataFrame:
    normalized = (
        preview_df.reindex(columns=STANDARD_COLUMNS)
        .assign(
            origem=lambda df: clean_required_text(df["origem"]).fillna(ORIGEM_ORCAMENTO_GERAL),
            ano=lambda df: clean_integer_like_text(df["ano"]),
            mes=lambda df: clean_integer_like_text(df["mes"]),
            cnpj=lambda df: clean_cnpj(df["cnpj"]),
            valor_total=lambda df: clean_currency_text(df["valor_total"]),
        )
        .dropna(subset=["valor_total", "cnpj"])
    )

    if normalized.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

    normalized = normalized.astype("string")
    return normalized.where(pd.notna(normalized), None)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input) if args.input else default_input_path(args.scope)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mapped_frames = [build_rj_budget_frame(frame, year) for frame, year in iter_source_frames(input_path)]
    mapped = pd.concat(mapped_frames, ignore_index=True) if mapped_frames else pd.DataFrame(columns=STANDARD_COLUMNS)
    normalized = normalize_general_preview(mapped)

    output_path = output_dir / default_output_name("RJ", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Partes origem: {len(mapped_frames)}")
    print(f"Linhas origem: {len(mapped)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
