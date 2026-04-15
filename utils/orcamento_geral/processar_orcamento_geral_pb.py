from __future__ import annotations

import argparse
import csv
import gc
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq
import requests
from pandas.errors import EmptyDataError

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import (
    ORCAMENTO_GERAL_PROCESSADA_DIR,
    cli_default,
)
from utils.convenios.unificador import (
    build_parquet_table,
    normalize_preview,
    partial_output_path,
)
from utils.common import STANDARD_COLUMNS
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
BASE_URL = "https://www.dados.pb.gov.br"
DEFAULT_TIMEOUT = 120
PROCESSING_MARKER = "Arquivo Sendo Processado!!!"
RELEVANT_COLUMNS = [
    "EXERCICIO",
    "CODIGO_UNIDADE_GESTORA",
    "NUMERO_EMPENHO",
    "DATA_EMPENHO",
    "HISTORICO_EMPENHO",
    "DESCRICAO_TIPO_EMPENHO",
    "NOME_TIPO_CREDITO",
    "VALOR_EMPENHO",
    "NOME_CREDOR",
    "CPFCNPJ_CREDOR",
    "CODIGO_MUNICIPIO",
    "NOME_MUNICIPIO",
]


@dataclass(frozen=True)
class DatasetSpec:
    nome: str
    rotulo: str


PB_DATASETS = [
    DatasetSpec("liquidacaodespesa", "Despesa - Liquidacao"),
    DatasetSpec("empenho_original", "Despesa Orcamentaria - Notas de Empenho"),
    DatasetSpec("empenho_anulacao", "Despesa Orcamentaria - Notas de Empenho de Anulacao"),
    DatasetSpec("empenho_suplementacao", "Despesa Orcamentaria - Notas de Empenho de Suplementacao"),
    DatasetSpec("Diarias", "Despesa Orcamentaria - Notas de Empenho - Diarias"),
    DatasetSpec("pagamento", "Despesas - Autorizacoes de Pagamento"),
    DatasetSpec("pagamento_anulacao", "Despesas - Anulacoes de Autorizacao de Pagamento"),
]


def parse_args() -> argparse.Namespace:
    current = datetime.now()
    parser = argparse.ArgumentParser(
        description="Baixa e processa os CSVs oficiais de empenho da PB para parquet no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Pasta com os CSVs de empenho_original da PB. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--download-root-dir",
        help="Pasta raiz usada quando o download da PB for executado. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Baixa os datasets do Dados PB antes do processamento.",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2000,
        help="Ano inicial para tentativa de download.",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=current.year,
        help="Ano final para tentativa de download.",
    )
    parser.add_argument(
        "--current-year-last-month",
        type=int,
        default=current.month,
        help="Mes final a considerar no ano corrente.",
    )
    parser.add_argument(
        "--formats",
        nargs="*",
        default=["csv"],
        choices=["csv", "json"],
        help="Formatos a baixar quando --download for usado.",
    )
    parser.add_argument(
        "--datasets",
        nargs="*",
        help="Lista opcional de datasets tecnicos a baixar. Default: mapeamento do pipeline PB.",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Baixa novamente mesmo se o arquivo ja existir.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=4,
        help="Numero de tentativas quando o portal responder que o arquivo esta sendo processado.",
    )
    parser.add_argument(
        "--retry-wait-seconds",
        type=float,
        default=10.0,
        help="Tempo de espera entre tentativas em segundos.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limita quantas combinacoes dataset/ano/mes baixar nesta execucao.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Numero de downloads paralelos.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("PB", scope) / "dados_abertos" / "empenho_original"


def default_download_root_dir(scope: str) -> Path:
    return uf_raw_dir("PB", scope) / "dados_abertos"


def build_dataset_specs(dataset_names: list[str] | None) -> list[DatasetSpec]:
    if not dataset_names:
        return PB_DATASETS

    known = {spec.nome: spec for spec in PB_DATASETS}
    specs: list[DatasetSpec] = []
    for name in dataset_names:
        specs.append(known.get(name, DatasetSpec(name, name)))
    return specs


def month_range_for_year(year: int, end_year: int, current_year_last_month: int) -> range:
    last_month = current_year_last_month if year == end_year else 12
    return range(1, last_month + 1)


def build_download_url(dataset_name: str, file_format: str, year: int, month: int) -> str:
    return f"{BASE_URL}/get{file_format}?nome={dataset_name}&exercicio={year}&mes={month}"


def output_path_for(output_dir: Path, dataset_name: str, year: int, month: int, file_format: str) -> Path:
    return output_dir / dataset_name / f"{year}" / f"{dataset_name}_{year}_{month:02d}.{file_format}"


def fetch_with_retry(
    session: requests.Session,
    dataset_name: str,
    file_format: str,
    year: int,
    month: int,
    retries: int,
    retry_wait_seconds: float,
) -> tuple[str, str]:
    url = build_download_url(dataset_name, file_format, year, month)

    for attempt in range(1, retries + 1):
        response = session.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        body = response.text

        if PROCESSING_MARKER not in body:
            return url, body

        if attempt < retries:
            time.sleep(retry_wait_seconds)

    raise RuntimeError(f"Portal retornou '{PROCESSING_MARKER}' apos {retries} tentativas para {url}")


def write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8-sig")


def append_manifest_row(manifest_path: Path, row: dict[str, object]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = manifest_path.exists()
    with manifest_path.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dataset",
                "label",
                "format",
                "year",
                "month",
                "status",
                "url",
                "output_path",
                "message",
            ],
            delimiter=";",
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def build_tasks(args: argparse.Namespace, specs: list[DatasetSpec], output_dir: Path) -> list[dict[str, object]]:
    tasks: list[dict[str, object]] = []
    completed = 0
    for spec in specs:
        for year in range(args.start_year, args.end_year + 1):
            for month in month_range_for_year(year, args.end_year, args.current_year_last_month):
                for file_format in args.formats:
                    output_path = output_path_for(output_dir, spec.nome, year, month, file_format)
                    if output_path.exists() and not args.force_download:
                        continue

                    tasks.append(
                        {
                            "spec": spec,
                            "year": year,
                            "month": month,
                            "file_format": file_format,
                            "output_path": output_path,
                        }
                    )
                    completed += 1
                    if args.limit is not None and completed >= args.limit:
                        return tasks
    return tasks


def download_single_task(task: dict[str, object], retries: int, retry_wait_seconds: float) -> dict[str, object]:
    spec: DatasetSpec = task["spec"]  # type: ignore[assignment]
    year = int(task["year"])  # type: ignore[arg-type]
    month = int(task["month"])  # type: ignore[arg-type]
    file_format = str(task["file_format"])
    output_path = Path(task["output_path"])  # type: ignore[arg-type]
    url = build_download_url(spec.nome, file_format, year, month)

    session = requests.Session()
    session.headers.update({"User-Agent": "osc_unificado/pb-dados-abertos"})

    try:
        final_url, body = fetch_with_retry(
            session=session,
            dataset_name=spec.nome,
            file_format=file_format,
            year=year,
            month=month,
            retries=retries,
            retry_wait_seconds=retry_wait_seconds,
        )
        write_text_file(output_path, body)
        return {
            "dataset": spec.nome,
            "label": spec.rotulo,
            "format": file_format,
            "year": year,
            "month": month,
            "status": "downloaded",
            "url": final_url,
            "output_path": str(output_path),
            "message": "",
        }
    except Exception as exc:
        error_path = output_path.with_suffix(output_path.suffix + ".error.txt")
        write_text_file(error_path, str(exc))
        return {
            "dataset": spec.nome,
            "label": spec.rotulo,
            "format": file_format,
            "year": year,
            "month": month,
            "status": "error",
            "url": url,
            "output_path": str(output_path),
            "message": str(exc),
        }


def maybe_download_pb_sources(args: argparse.Namespace) -> None:
    if not args.download:
        return

    output_dir = Path(args.download_root_dir) if args.download_root_dir else default_download_root_dir(args.scope)
    manifest_path = output_dir / "download_manifest.csv"
    specs = build_dataset_specs(args.datasets)
    tasks = build_tasks(args, specs, output_dir)
    if not tasks:
        print("Nenhum download pendente.")
        return

    print(f"Tarefas pendentes PB: {len(tasks)}")
    if args.workers <= 1:
        for task in tasks:
            row = download_single_task(task, args.retries, args.retry_wait_seconds)
            append_manifest_row(manifest_path, row)
            print(f"{row['status']}: {row['output_path']}")
        return

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {
            executor.submit(download_single_task, task, args.retries, args.retry_wait_seconds): task for task in tasks
        }
        for index, future in enumerate(as_completed(future_map), start=1):
            row = future.result()
            append_manifest_row(manifest_path, row)
            print(f"[{index}/{len(tasks)}] {row['status']}: {row['output_path']}")


def list_source_files(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.rglob("*.csv") if path.is_file())


def read_empenho_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=";",
        dtype=str,
        encoding="utf-8-sig",
        usecols=RELEVANT_COLUMNS,
        low_memory=False,
    )


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


def extract_year_month(date_series: pd.Series | None, fallback_year_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        ano = clean_text(fallback_year_series)
        return ano, pd.Series(pd.NA, index=ano.index, dtype="string")

    parsed = pd.to_datetime(date_series, errors="coerce", utc=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")

    if fallback_year_series is not None:
        ano = ano.combine_first(clean_text(fallback_year_series))
    return ano, mes


def build_pb_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    ano, mes = extract_year_month(source_df.get("DATA_EMPENHO"), source_df.get("EXERCICIO"))
    modalidade = first_non_empty(source_df.get("DESCRICAO_TIPO_EMPENHO"), source_df.get("NOME_TIPO_CREDITO"))

    mapped = pd.DataFrame(
        {
            "uf": "PB",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano,
            "valor_total": source_df.get("VALOR_EMPENHO"),
            "cnpj": source_df.get("CPFCNPJ_CREDOR"),
            "nome_osc": source_df.get("NOME_CREDOR"),
            "mes": mes,
            "cod_municipio": clean_text(source_df.get("CODIGO_MUNICIPIO")),
            "municipio": source_df.get("NOME_MUNICIPIO"),
            "objeto": source_df.get("HISTORICO_EMPENHO"),
            "modalidade": modalidade,
            "data_inicio": source_df.get("DATA_EMPENHO"),
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def write_pb_parquet(input_dir: Path, output_dir: Path, output_name: str) -> tuple[Path, int, int]:
    source_files = list_source_files(input_dir)
    if not source_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_stem = Path(output_name).stem
    output_suffix = Path(output_name).suffix or ".parquet"
    temp_path = partial_output_path(output_dir, output_stem)
    final_path = output_dir / output_name

    if temp_path.exists():
        temp_path.unlink()
    if final_path.exists():
        final_path.unlink()

    writer: pq.ParquetWriter | None = None
    total_source_rows = 0
    total_parquet_rows = 0

    try:
        for path in source_files:
            try:
                source_df = read_empenho_csv(path)
            except EmptyDataError:
                continue

            total_source_rows += len(source_df)
            mapped = build_pb_budget_frame(source_df)
            normalized = normalize_preview(mapped, "PB", require_cnpj=True)
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
        empty = pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")
        pq.write_table(build_parquet_table(empty), temp_path, compression="snappy")

    temp_path.replace(final_path)
    return final_path, total_source_rows, total_parquet_rows


def main() -> None:
    args = parse_args()
    maybe_download_pb_sources(args)
    input_dir = Path(args.input_dir) if args.input_dir else default_input_dir(args.scope)
    output_dir = Path(args.output_dir)
    output_name = default_output_name("PB", args.scope)

    output_path, source_rows, parquet_rows = write_pb_parquet(input_dir, output_dir, output_name)

    print(f"Entrada: {input_dir}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {source_rows}")
    print(f"Linhas parquet: {parquet_rows}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
