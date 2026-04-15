from __future__ import annotations

import argparse
import gc
from pathlib import Path
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
CHUNK_SIZE = 200_000
USECOLS = [
    "ano_particao",
    "data_formatada",
    "vr_empenhado",
    "vr_liquidado",
    "vr_pago",
    "nome_grupo",
    "nome_elemento_despesa",
    "nome_item_despesa",
    "nome_modalidade_aplic",
    "documento_favorecido",
    "nome_favorecido",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa as despesas do MG com foco em transferencias a OSC para parquet."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Diretorio com os CSVs enriquecidos do MG. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("MG", scope)


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
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, utc=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def iter_source_chunks(input_dir: Path) -> tuple[list[Path], object]:
    paths = sorted(input_dir.glob("ft_despesa_*_enriquecido.csv"))
    for path in paths:
        reader = pd.read_csv(
            path,
            sep=";",
            dtype=str,
            encoding="utf-8",
            encoding_errors="replace",
            low_memory=False,
            usecols=USECOLS,
            chunksize=CHUNK_SIZE,
        )
        for chunk in reader:
            yield paths, path, chunk


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("nome_favorecido")).fillna("")
    modalidade = clean_text(source_df.get("nome_modalidade_aplic")).fillna("")
    elemento = clean_text(source_df.get("nome_elemento_despesa")).fillna("")
    item = clean_text(source_df.get("nome_item_despesa")).fillna("")

    modalidade_osc = modalidade.str.contains(r"sem fins lucrativos", case=False, regex=True, na=False)
    item_osc = item.str.contains(r"subven|contribui|conven|fomento|parcer", case=False, regex=True, na=False)
    elemento_osc = elemento.str.contains(r"subven|contribui|conven|fomento|parcer", case=False, regex=True, na=False)
    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|organiz|"
        r"miseric|santa casa|lar|abrigo|asilo|creche|pestalozzi|federac|cooperativa",
        case=False,
        regex=True,
        na=False,
    )
    publico = nome.str.contains(
        r"fundo municipal|fundo estadual|prefeitura|secretaria|tribunal|camara|assembleia|"
        r"municipio de |estado de |governo|ministerio|cx\\. esc|caixa escolar",
        case=False,
        regex=True,
        na=False,
    )
    return (modalidade_osc | (nome_osc & (item_osc | elemento_osc))) & ~publico


def build_mg_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    ano_data, mes = extract_year_month(filtered.get("data_formatada"))

    mapped = pd.DataFrame(
        {
            "uf": "MG",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(filtered.get("ano_particao")).combine_first(ano_data),
            "valor_total": first_non_empty(
                filtered.get("vr_pago"),
                filtered.get("vr_liquidado"),
                filtered.get("vr_empenhado"),
            ),
            "cnpj": filtered.get("documento_favorecido"),
            "nome_osc": filtered.get("nome_favorecido"),
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(filtered.get("nome_item_despesa"), filtered.get("nome_elemento_despesa")),
            "modalidade": first_non_empty(
                filtered.get("nome_modalidade_aplic"),
                filtered.get("nome_elemento_despesa"),
                filtered.get("nome_grupo"),
            ),
            "data_inicio": filtered.get("data_formatada"),
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir) if args.input_dir else default_input_dir(args.scope)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / default_output_name("MG", args.scope)
    temp_path = output_dir / "MG.tmp.parquet"
    if temp_path.exists():
        temp_path.unlink()
    if output_path.exists():
        output_path.unlink()

    writer: pq.ParquetWriter | None = None
    total_source_rows = 0
    total_parquet_rows = 0
    seen_paths: list[Path] = []

    try:
        for seen_paths, current_path, source_df in iter_source_chunks(input_dir):
            total_source_rows += len(source_df)
            mapped = build_mg_budget_frame(source_df)
            normalized = normalize_preview(mapped, "MG", require_cnpj=True)
            if normalized.empty:
                del source_df
                del mapped
                gc.collect()
                continue

            table = build_parquet_table(normalized)
            if writer is None:
                writer = pq.ParquetWriter(temp_path, table.schema, compression="snappy")
            writer.write_table(table)
            total_parquet_rows += len(normalized)

            del source_df
            del mapped
            del normalized
            del table
            gc.collect()
    finally:
        if writer is not None:
            writer.close()

    if not temp_path.exists():
        raise RuntimeError("Nenhuma linha valida foi gerada para MG.")

    temp_path.replace(output_path)
    print(f"Entrada: {input_dir}")
    print(f"Arquivos lidos: {len(seen_paths)}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {total_source_rows}")
    print(f"Linhas parquet: {total_parquet_rows}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
