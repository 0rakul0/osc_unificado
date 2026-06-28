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

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, CAPITAIS_PROCESSADA_DIR, HISTORIA_DATA_DIR, ensure_parent_dir
from utils.capitais.shared import (
    ORIGEM_CAPITAIS_CONVENIOS,
    ORIGEM_CAPITAIS_ORCAMENTO_GERAL,
    first_non_empty,
    standardize_frame,
)
from utils.convenios.unificador import build_parquet_table, normalize_preview


BASE_DIR = BASES_CONVENIOS_CAPITAIS_DIR / "Recife"
LOOKUP_PATH = HISTORIA_DATA_DIR / "recife_lookup_local" / "recife_lookup_nome_para_cnpj.csv"
OUTPUT_PATH = CAPITAIS_PROCESSADA_DIR / "PE_RECIFE.parquet"
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
    if len(digits) != 14:
        return pd.NA
    return digits


def build_lookup_from_recent_files() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for filename in RECENT_FILES:
        path = BASE_DIR / filename
        if not path.exists():
            continue
        frame = pd.read_csv(
            path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
            usecols=["CPF/CNPJ", "Nome do Credor"],
        ).rename(columns={"CPF/CNPJ": "cpf_cnpj", "Nome do Credor": "nome_credor"})
        frames.append(frame)

    if not frames:
        raise FileNotFoundError("Nenhum arquivo recente de despesa por credor foi encontrado para gerar lookup.")

    recent = pd.concat(frames, ignore_index=True)
    recent["nome_key"] = recent["nome_credor"].map(normalize_text)
    recent["cpf_cnpj"] = recent["cpf_cnpj"].map(normalize_document).astype("string")
    recent = recent.dropna(subset=["nome_key", "cpf_cnpj"]).copy()

    grouped = (
        recent.groupby("nome_key", dropna=False)
        .agg(
            nome_credor=("nome_credor", "first"),
            cnpjs=("cpf_cnpj", lambda values: sorted(set(values))),
            ocorrencias=("nome_key", "size"),
        )
        .reset_index()
    )
    grouped = grouped[grouped["cnpjs"].map(len).eq(1)].copy()
    grouped["cpf_cnpj"] = grouped["cnpjs"].map(lambda values: values[0])
    return grouped[["nome_key", "nome_credor", "cpf_cnpj", "ocorrencias"]]


def load_lookup(path: Path) -> dict[str, str]:
    ensure_parent_dir(path)
    lookup_df = build_lookup_from_recent_files()
    lookup_df.to_csv(path, index=False, encoding="utf-8-sig")
    lookup_df["cpf_cnpj"] = lookup_df["cpf_cnpj"].map(normalize_document).astype("string")
    lookup_df = lookup_df.dropna(subset=["nome_key", "cpf_cnpj"]).copy()
    return dict(zip(lookup_df["nome_key"], lookup_df["cpf_cnpj"]))


def keep_only_cnpj_rows(normalized: pd.DataFrame, modalidade: str) -> pd.DataFrame:
    if normalized.empty:
        return normalized
    filtered = normalized.copy()
    filtered["cnpj"] = filtered["cnpj"].map(normalize_document).astype("string")
    filtered = filtered.dropna(subset=["cnpj"]).copy()
    filtered["origem"] = (
        ORIGEM_CAPITAIS_ORCAMENTO_GERAL if modalidade == "despesa" else ORIGEM_CAPITAIS_CONVENIOS
    )
    filtered["modalidade"] = modalidade
    return filtered


def map_historical_chunk(frame: pd.DataFrame, lookup: dict[str, str]) -> pd.DataFrame:
    nome_key = frame["credor_nome"].map(normalize_text)
    cnpj = nome_key.map(lookup).astype("string")
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": pd.Series("PE", index=frame.index, dtype="string"),
                "origem": pd.Series(ORIGEM_CAPITAIS_ORCAMENTO_GERAL, index=frame.index, dtype="string"),
                "ano": frame.get("ano_movimentacao"),
                "valor_total": first_non_empty(frame.get("valor_liquidado"), frame.get("valor_empenhado"), frame.get("valor_pago")),
                "cnpj": cnpj,
                "nome_osc": frame.get("credor_nome"),
                "mes": frame.get("mes_movimentacao"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": pd.Series("Recife", index=frame.index, dtype="string"),
                "objeto": first_non_empty(frame.get("acao_nome"), frame.get("programa_nome"), frame.get("subelemento_nome")),
                "modalidade": pd.Series("despesa", index=frame.index, dtype="string"),
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
                "origem": pd.Series(ORIGEM_CAPITAIS_ORCAMENTO_GERAL, index=frame.index, dtype="string"),
                "ano": frame.get("Ano"),
                "valor_total": first_non_empty(frame.get("Liquidação"), frame.get("Empenhado"), frame.get("Pagamento")),
                "cnpj": frame["CPF/CNPJ"].map(normalize_document).astype("string"),
                "nome_osc": frame.get("Nome do Credor"),
                "mes": frame.get("Mês"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": pd.Series("Recife", index=frame.index, dtype="string"),
                "objeto": first_non_empty(frame.get("Órgão"), frame.get("Unidade"), frame.get("Grupo de Despesa")),
                "modalidade": pd.Series("despesa", index=frame.index, dtype="string"),
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
    ]

    for path in sorted(BASE_DIR.glob(HISTORICAL_GLOB)):
        for chunk in pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str, usecols=usecols, chunksize=CHUNK_SIZE):
            stats["source_rows"] += len(chunk)
            mapped = map_historical_chunk(chunk, lookup)
            normalized = normalize_preview(mapped, "PE", require_cnpj=True)
            normalized = keep_only_cnpj_rows(normalized, "despesa")
            stats["parquet_rows"] += len(normalized)
            stats["cnpj_rows"] += int(normalized["cnpj"].dropna().astype(str).str.len().eq(14).sum()) if not normalized.empty else 0
            if not normalized.empty:
                writer = write_chunk(writer, normalized)
            del chunk, mapped, normalized
            gc.collect()
    return writer, stats


def process_recent_files(writer: pq.ParquetWriter | None) -> tuple[pq.ParquetWriter | None, dict[str, int]]:
    stats = {"source_rows": 0, "parquet_rows": 0, "cnpj_rows": 0}
    usecols = [
        "Ano",
        "Mês",
        "CPF/CNPJ",
        "Nome do Credor",
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
        for chunk in pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str, usecols=usecols, chunksize=CHUNK_SIZE):
            stats["source_rows"] += len(chunk)
            mapped = map_recent_chunk(chunk)
            normalized = normalize_preview(mapped, "PE", require_cnpj=True)
            normalized = keep_only_cnpj_rows(normalized, "despesa")
            stats["parquet_rows"] += len(normalized)
            stats["cnpj_rows"] += int(normalized["cnpj"].dropna().astype(str).str.len().eq(14).sum()) if not normalized.empty else 0
            if not normalized.empty:
                writer = write_chunk(writer, normalized)
            del chunk, mapped, normalized
            gc.collect()
    return writer, stats


def process_convenio_file(writer: pq.ParquetWriter | None) -> tuple[pq.ParquetWriter | None, dict[str, int]]:
    path = BASE_DIR / "recife_contratos_gestao_2023.csv"
    stats = {"source_rows": 0, "parquet_rows": 0, "cnpj_rows": 0}
    if not path.exists():
        return writer, stats

    frame = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
    stats["source_rows"] = len(frame)
    valor_mes = first_non_empty(frame.get("VALOR MÊS"), frame.get("VALOR MÃŠS"))
    observacoes = first_non_empty(frame.get("Observações"), frame.get("Observaçoes"), frame.get("ObservaÃ§oes"), frame.get("Observacoes"))
    mapped = standardize_frame(
        pd.DataFrame(
            {
                "uf": pd.Series("PE", index=frame.index, dtype="string"),
                "origem": pd.Series(ORIGEM_CAPITAIS_CONVENIOS, index=frame.index, dtype="string"),
                "ano": pd.Series("2023", index=frame.index, dtype="string"),
                "valor_total": valor_mes,
                "cnpj": frame.get("CNPJ"),
                "nome_osc": frame.get("Contratada"),
                "mes": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": pd.Series("Recife", index=frame.index, dtype="string"),
                "objeto": first_non_empty(frame.get("Objeto"), observacoes, frame.get("Contrato")),
                "modalidade": pd.Series("convenio", index=frame.index, dtype="string"),
                "data_inicio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )
    normalized = normalize_preview(mapped, "PE", require_cnpj=True)
    normalized = keep_only_cnpj_rows(normalized, "convenio")
    stats["parquet_rows"] = len(normalized)
    stats["cnpj_rows"] = int(normalized["cnpj"].dropna().astype(str).str.len().eq(14).sum()) if not normalized.empty else 0
    if not normalized.empty:
        writer = write_chunk(writer, normalized)
    return writer, stats


def main() -> None:
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {BASE_DIR}")

    ensure_parent_dir(OUTPUT_PATH)
    if OUTPUT_PATH.exists():
        OUTPUT_PATH.unlink()

    lookup = load_lookup(LOOKUP_PATH)
    writer: pq.ParquetWriter | None = None
    convenio_stats = {"source_rows": 0, "parquet_rows": 0, "cnpj_rows": 0}

    try:
        writer, historical_stats = process_historical_files(lookup, writer)
        writer, recent_stats = process_recent_files(writer)
        writer, convenio_stats = process_convenio_file(writer)
    finally:
        if writer is not None:
            writer.close()

    if not OUTPUT_PATH.exists():
        raise RuntimeError("Nenhuma linha válida foi gerada para Recife.")

    total_rows = historical_stats["parquet_rows"] + recent_stats["parquet_rows"] + convenio_stats["parquet_rows"]
    total_cnpj = historical_stats["cnpj_rows"] + recent_stats["cnpj_rows"] + convenio_stats["cnpj_rows"]
    print(f"Parquet gerado em: {OUTPUT_PATH}")
    print(f"Historico -> origem={historical_stats['source_rows']} parquet={historical_stats['parquet_rows']} com_cnpj={historical_stats['cnpj_rows']}")
    print(f"Recente -> origem={recent_stats['source_rows']} parquet={recent_stats['parquet_rows']} com_cnpj={recent_stats['cnpj_rows']}")
    print(f"Convenios -> origem={convenio_stats['source_rows']} parquet={convenio_stats['parquet_rows']} com_cnpj={convenio_stats['cnpj_rows']}")
    print(f"Total final -> linhas={total_rows} com_cnpj={total_cnpj}")


if __name__ == "__main__":
    main()
