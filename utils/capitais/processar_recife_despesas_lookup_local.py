from __future__ import annotations

import gc
from pathlib import Path
import re
import sys
import unicodedata

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, HISTORIA_DATA_DIR, ensure_parent_dir
from utils.capitais.shared import first_non_empty, standardize_frame
from utils.convenios.unificador import build_parquet_table, normalize_preview


BASE_DIR = BASES_CONVENIOS_CAPITAIS_DIR / "Recife"
LOOKUP_PATH = HISTORIA_DATA_DIR / "recife_lookup_local" / "recife_lookup_nome_para_cnpj.csv"
OUTPUT_DIR = HISTORIA_DATA_DIR / "parquets_teste_capitais"
OUTPUT_PATH = OUTPUT_DIR / "PE_RECIFE.parquet"
CHUNK_SIZE = 200_000

HISTORICAL_GLOB = "recife_despesas-orcamentarias-*.csv"
RECENT_FILES = [
    "recife_despesa-por-credor-empenho-2024.csv",
    "recife_despesa-por-credor-empenho-2025.csv",
]


def normalize_text(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = unicodedata.normalize("NFKD", str(value).strip().upper())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_document(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    digits = re.sub(r"\D+", "", str(value))
    if len(digits) not in {11, 14}:
        return pd.NA
    return digits


def load_lookup(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Lookup não encontrado: {path}")
    lookup_df = pd.read_csv(path, dtype=str)
    lookup_df = lookup_df.dropna(subset=["nome_key", "cpf_cnpj"]).copy()
    return dict(zip(lookup_df["nome_key"], lookup_df["cpf_cnpj"]))


def map_historical_chunk(frame: pd.DataFrame, lookup: dict[str, str]) -> pd.DataFrame:
    nome_key = frame["credor_nome"].map(normalize_text)
    cnpj = nome_key.map(lookup).astype("string")
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": pd.Series("PE", index=frame.index, dtype="string"),
                "origem": pd.Series("capitais", index=frame.index, dtype="string"),
                "ano": frame.get("ano_movimentacao"),
                "valor_total": first_non_empty(frame.get("valor_pago"), frame.get("valor_liquidado"), frame.get("valor_empenhado")),
                "cnpj": cnpj,
                "nome_osc": frame.get("credor_nome"),
                "mes": frame.get("mes_movimentacao"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": pd.Series("Recife", index=frame.index, dtype="string"),
                "objeto": first_non_empty(frame.get("acao_nome"), frame.get("programa_nome"), frame.get("subelemento_nome")),
                "modalidade": first_non_empty(
                    frame.get("modalidade_licitacao_nome"),
                    frame.get("modalidade_aplicacao_nome"),
                    frame.get("grupo_despesa_nome"),
                    frame.get("empenho_modalidade_nome"),
                ),
                "data_inicio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_recent_chunk(frame: pd.DataFrame) -> pd.DataFrame:
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": pd.Series("PE", index=frame.index, dtype="string"),
                "origem": pd.Series("capitais", index=frame.index, dtype="string"),
                "ano": frame.get("Ano"),
                "valor_total": first_non_empty(frame.get("Pagamento"), frame.get("Liquidação"), frame.get("Empenhado")),
                "cnpj": frame["CPF/CNPJ"].map(normalize_document).astype("string"),
                "nome_osc": frame.get("Nome do Credor"),
                "mes": frame.get("Mês"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": pd.Series("Recife", index=frame.index, dtype="string"),
                "objeto": first_non_empty(frame.get("Órgão"), frame.get("Unidade"), frame.get("Grupo de Despesa")),
                "modalidade": first_non_empty(
                    frame.get("Tipo de Licitação"),
                    frame.get("Modalidade"),
                    frame.get("Modadlidade do Empenho"),
                ),
                "data_inicio": first_non_empty(frame.get("Data do Empenho"), frame.get("Data de Pagamento")),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def write_chunk(writer: pq.ParquetWriter | None, normalized: pd.DataFrame) -> pq.ParquetWriter:
    table = build_parquet_table(normalized)
    if writer is None:
        writer = pq.ParquetWriter(OUTPUT_PATH, table.schema, compression="snappy")
    writer.write_table(table)
    del table
    return writer


def process_historical_files(lookup: dict[str, str], writer: pq.ParquetWriter | None) -> tuple[pq.ParquetWriter | None, dict[str, int]]:
    stats = {"source_rows": 0, "parquet_rows": 0, "cnpj_rows": 0}
    usecols = [
        "ano_movimentacao",
        "mes_movimentacao",
        "credor_nome",
        "valor_empenhado",
        "valor_liquidado",
        "valor_pago",
        "acao_nome",
        "programa_nome",
        "subelemento_nome",
        "modalidade_licitacao_nome",
        "modalidade_aplicacao_nome",
        "grupo_despesa_nome",
        "empenho_modalidade_nome",
    ]

    for path in sorted(BASE_DIR.glob(HISTORICAL_GLOB)):
        for chunk in pd.read_csv(
            path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
            usecols=usecols,
            chunksize=CHUNK_SIZE,
        ):
            stats["source_rows"] += len(chunk)
            mapped = map_historical_chunk(chunk, lookup)
            normalized = normalize_preview(mapped, "PE", require_cnpj=True)
            stats["parquet_rows"] += len(normalized)
            stats["cnpj_rows"] += int(normalized["cnpj"].dropna().astype(str).str.len().isin([11, 14]).sum()) if not normalized.empty else 0
            if not normalized.empty:
                writer = write_chunk(writer, normalized)
            del chunk
            del mapped
            del normalized
            gc.collect()

    return writer, stats


def process_recent_files(writer: pq.ParquetWriter | None) -> tuple[pq.ParquetWriter | None, dict[str, int]]:
    stats = {"source_rows": 0, "parquet_rows": 0, "cnpj_rows": 0}
    usecols = [
        "Ano",
        "Mês",
        "CPF/CNPJ",
        "Nome do Credor",
        "Tipo de Licitação",
        "Modalidade",
        "Modadlidade do Empenho",
        "Data do Empenho",
        "Data de Pagamento",
        "Empenhado",
        "Liquidação",
        "Pagamento",
        "Órgão",
        "Unidade",
        "Grupo de Despesa",
    ]

    for filename in RECENT_FILES:
        path = BASE_DIR / filename
        if not path.exists():
            continue
        for chunk in pd.read_csv(
            path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
            usecols=usecols,
            chunksize=CHUNK_SIZE,
        ):
            stats["source_rows"] += len(chunk)
            mapped = map_recent_chunk(chunk)
            normalized = normalize_preview(mapped, "PE", require_cnpj=True)
            stats["parquet_rows"] += len(normalized)
            stats["cnpj_rows"] += int(normalized["cnpj"].dropna().astype(str).str.len().isin([11, 14]).sum()) if not normalized.empty else 0
            if not normalized.empty:
                writer = write_chunk(writer, normalized)
            del chunk
            del mapped
            del normalized
            gc.collect()

    return writer, stats


def main() -> None:
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {BASE_DIR}")

    ensure_parent_dir(OUTPUT_PATH)
    if OUTPUT_PATH.exists():
        OUTPUT_PATH.unlink()

    lookup = load_lookup(LOOKUP_PATH)
    writer: pq.ParquetWriter | None = None

    historical_stats = {"source_rows": 0, "parquet_rows": 0, "cnpj_rows": 0}
    recent_stats = {"source_rows": 0, "parquet_rows": 0, "cnpj_rows": 0}

    try:
        writer, historical_stats = process_historical_files(lookup, writer)
        writer, recent_stats = process_recent_files(writer)
    finally:
        if writer is not None:
            writer.close()

    if not OUTPUT_PATH.exists():
        raise RuntimeError("Nenhuma linha válida foi gerada para Recife.")

    total_rows = historical_stats["parquet_rows"] + recent_stats["parquet_rows"]
    total_cnpj = historical_stats["cnpj_rows"] + recent_stats["cnpj_rows"]

    print(f"Parquet gerado em: {OUTPUT_PATH}")
    print(f"Historico -> origem={historical_stats['source_rows']} parquet={historical_stats['parquet_rows']} com_cnpj={historical_stats['cnpj_rows']}")
    print(f"Recente -> origem={recent_stats['source_rows']} parquet={recent_stats['parquet_rows']} com_cnpj={recent_stats['cnpj_rows']}")
    print(f"Total final -> linhas={total_rows} com_cnpj={total_cnpj}")


if __name__ == "__main__":
    main()
