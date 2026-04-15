from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.common import STANDARD_COLUMNS
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a compilacao de despesas/convenios do ES para parquet no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV consolidado do ES. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("ES", scope) / "despesas_osc_alta_mais_nao_encontradas.csv"


def read_csv_with_fallback(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "latin1"):
        try:
            return pd.read_csv(path, dtype=str, encoding=encoding, low_memory=False)
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Falha ao ler {path}") from last_error


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    if not series:
        return pd.Series(dtype="string")

    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = current.astype("string").str.strip().replace("", pd.NA)
        result = cleaned if result is None else result.combine_first(cleaned)

    if result is None:
        return pd.Series(dtype="string")
    return result


def extract_year_month(
    date_series: pd.Series | None,
    fallback_year_series: pd.Series | None,
    fallback_month_series: pd.Series | None,
) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        ano = fallback_year_series.astype("string") if fallback_year_series is not None else empty
        mes = fallback_month_series.astype("string") if fallback_month_series is not None else empty
        return ano, mes

    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, utc=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")

    if fallback_year_series is not None:
        ano = ano.combine_first(fallback_year_series.astype("string"))
    if fallback_month_series is not None:
        mes = mes.combine_first(fallback_month_series.astype("string"))
    return ano, mes


def build_es_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    valor_total = first_non_empty(source_df.get("valor_total"))
    objeto = first_non_empty(
        source_df.get("objeto_convenio"),
        source_df.get("HistoricoDocumento"),
        source_df.get("Acao"),
    )
    modalidade = first_non_empty(
        source_df.get("modalidade_convenio"),
        source_df.get("Modalidade"),
        source_df.get("TipoLicitacao"),
    )
    ano, mes = extract_year_month(source_df.get("data_pagamento"), source_df.get("ano"), source_df.get("mes"))

    mapped = pd.DataFrame(
        {
            "uf": "ES",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano,
            "valor_total": valor_total,
            "cnpj": source_df.get("cnpj"),
            "nome_osc": source_df.get("nome_osc"),
            "mes": mes,
            "cod_municipio": source_df.get("cod_municipio_convenio"),
            "municipio": source_df.get("municipio_convenio"),
            "objeto": objeto,
            "modalidade": modalidade,
            "data_inicio": source_df.get("data_inicio_convenio"),
            "data_fim": source_df.get("data_fim_convenio"),
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

    source_df = read_csv_with_fallback(input_path)
    mapped = build_es_budget_frame(source_df)
    normalized = normalize_preview(mapped, "ES", require_cnpj=True)

    output_path = output_dir / default_output_name("ES", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
