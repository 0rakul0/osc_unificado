from __future__ import annotations

import argparse
import csv
import gc
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq
import requests
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import (
    ORCAMENTO_GERAL_PROCESSADA_DIR,
    cli_default,
)
from utils.convenios.unificador import build_parquet_table, normalize_preview, partial_output_path
from utils.common import STANDARD_COLUMNS
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
PORTAL_PAGE_URL = "https://consultas.transparencia.mt.gov.br/dados_abertos_consultas/despesa/"
DOWNLOAD_URL_TEMPLATE = "https://consultas.transparencia.mt.gov.br/dados_abertos/despesa/Despesa_{year}.csv"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)
RELEVANT_COLUMNS = [
    "NUANO",
    "NUMES",
    "DTEMISSAODESPESA",
    "SGLDESPESA",
    "TPDESPESA",
    "NREMPENHO",
    "NRDOCUMENTODESPESA",
    "CDUNIDADEORCAMENTARIA",
    "NMUNIDADEORCAMENTARIA",
    "CDUNIDADEGESTORA",
    "NMUNIDADEGESTORA",
    "CDCREDOR",
    "NMCREDOR",
    "CPF_CNPJ",
    "NMTIPOCREDOR",
    "CDFUNCAO",
    "NMFUNCAO",
    "CDSUBFUNCAO",
    "NMSUBFUNCAO",
    "CDPROGRAMA",
    "NMPROGRAMA",
    "CDACAO",
    "NMACAO",
    "CDFONTERECURSO",
    "NMFONTERECURSO",
    "CDCATEGORIA",
    "NMCATEGORIA",
    "CDGRUPONATUREZADESPESA",
    "NMGRUPONATUREZADESPESA",
    "CDMODALIDADEAPLICACAO",
    "NMMODALIDADEAPLICACAO",
    "CDELEMENTODESPESA",
    "NMELEMENTODESPESA",
    "CDSUBELEMENTODESPESA",
    "NMSUBELEMENTODESPESA",
    "VLDESPESA",
    "HISTORICODESPESA",
    "VLEMPENHADO",
    "VLLIQUIDADO",
    "VLPAGO",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa e processa a trilha oficial de despesa do MT para MT.parquet."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Pasta com os CSVs oficiais do MT. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    parser.add_argument(
        "--output-name",
        help="Nome do parquet canonico de saida. Se omitido, usa o nome padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=250000,
        help="Quantidade de linhas por chunk na leitura dos CSVs oficiais.",
    )
    parser.add_argument(
        "--require-date",
        action="store_true",
        help="Mantem apenas linhas com data_inicio preenchida.",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Baixa ou atualiza os CSVs oficiais antes de processar.",
    )
    parser.add_argument(
        "--cookies",
        help="Header Cookie bruto do navegador para consultas.transparencia.mt.gov.br.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=list(range(2010, 2027)),
        help="Anos a baixar quando --download for usado. Default: 2010..2026.",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Rebaixa arquivos ja existentes quando --download for usado.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout de leitura em segundos no download.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("MT", scope) / "oficial"


def parse_cookie_header(cookie_header: str) -> list[dict[str, str]]:
    cookies: list[dict[str, str]] = []
    for item in cookie_header.split(";"):
        part = item.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        cookies.append(
            {
                "name": key.strip(),
                "value": value.strip(),
                "domain": "consultas.transparencia.mt.gov.br",
                "path": "/",
            }
        )
    return cookies


def refresh_portal_cookies(cookie_header: str) -> dict[str, str]:
    initial_cookies = parse_cookie_header(cookie_header)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(initial_cookies)
        page = context.new_page()
        page.goto(PORTAL_PAGE_URL, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(5000)
        refreshed = {
            cookie["name"]: cookie["value"]
            for cookie in context.cookies()
            if "consultas.transparencia.mt.gov.br" in cookie.get("domain", "")
        }
        browser.close()
    return refreshed


def write_manifest_row(manifest_path: Path, row: dict[str, str]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not manifest_path.exists()
    with manifest_path.open("a", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["year", "url", "status", "detail", "output_path"],
        )
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def download_year(
    year: int,
    output_dir: Path,
    cookies: dict[str, str],
    timeout: int,
    force: bool,
    manifest_path: Path,
) -> None:
    output_path = output_dir / f"Despesa_{year}.csv"
    if output_path.exists() and not force:
        write_manifest_row(
            manifest_path,
            {
                "year": str(year),
                "url": DOWNLOAD_URL_TEMPLATE.format(year=year),
                "status": "skipped_existing",
                "detail": "",
                "output_path": str(output_path),
            },
        )
        return

    headers = {
        "User-Agent": USER_AGENT,
        "Referer": PORTAL_PAGE_URL,
        "Accept": "text/csv,application/octet-stream,*/*",
    }
    url = DOWNLOAD_URL_TEMPLATE.format(year=year)

    try:
        with requests.get(url, cookies=cookies, headers=headers, stream=True, timeout=(30, timeout)) as response:
            response.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("wb") as fh:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        fh.write(chunk)
        write_manifest_row(
            manifest_path,
            {
                "year": str(year),
                "url": url,
                "status": "downloaded",
                "detail": "",
                "output_path": str(output_path),
            },
        )
    except Exception as exc:
        write_manifest_row(
            manifest_path,
            {
                "year": str(year),
                "url": url,
                "status": "error",
                "detail": str(exc),
                "output_path": str(output_path),
            },
        )


def maybe_download_mt_sources(args: argparse.Namespace) -> None:
    if not args.download:
        return
    if not args.cookies:
        raise ValueError("--cookies e obrigatorio quando --download for usado.")

    output_dir = Path(args.input_dir) if args.input_dir else default_input_dir(args.scope)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "download_manifest.csv"
    refreshed_cookies = refresh_portal_cookies(args.cookies)
    for year in args.years:
        download_year(year, output_dir, refreshed_cookies, args.timeout, args.force_download, manifest_path)


def list_source_files(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.glob("Despesa_*.csv") if path.is_file())


def iter_official_csv_chunks(path: Path, chunksize: int):
    header_df = pd.read_csv(
        path,
        sep=";",
        dtype=str,
        encoding="latin1",
        nrows=0,
        low_memory=False,
    )
    available = [column for column in RELEVANT_COLUMNS if column in header_df.columns]

    return pd.read_csv(
        path,
        sep=";",
        dtype=str,
        encoding="latin1",
        usecols=available,
        low_memory=False,
        chunksize=chunksize,
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


def build_mt_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    modalidade = first_non_empty(
        source_df.get("NMMODALIDADEAPLICACAO"),
        source_df.get("NMGRUPONATUREZADESPESA"),
        source_df.get("NMCATEGORIA"),
    )
    objeto = first_non_empty(
        source_df.get("HISTORICODESPESA"),
        source_df.get("NMELEMENTODESPESA"),
        source_df.get("NMSUBELEMENTODESPESA"),
        source_df.get("NMACAO"),
    )

    mapped = pd.DataFrame(
        {
            "uf": "MT",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": source_df.get("NUANO"),
            "valor_total": first_non_empty(
                source_df.get("VLDESPESA"),
                source_df.get("VLPAGO"),
                source_df.get("VLLIQUIDADO"),
                source_df.get("VLEMPENHADO"),
            ),
            "cnpj": source_df.get("CPF_CNPJ"),
            "nome_osc": source_df.get("NMCREDOR"),
            "mes": source_df.get("NUMES"),
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": objeto,
            "modalidade": modalidade,
            "data_inicio": source_df.get("DTEMISSAODESPESA"),
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def write_mt_parquet(
    input_dir: Path,
    output_dir: Path,
    output_name: str,
    chunksize: int,
    require_date: bool,
) -> tuple[Path, int, int]:
    source_files = list_source_files(input_dir)
    if not source_files:
        raise FileNotFoundError(f"Nenhum CSV oficial encontrado em {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_name
    temp_path = partial_output_path(output_dir, f"{Path(output_name).stem}_tmp")

    if temp_path.exists():
        temp_path.unlink()
    if output_path.exists():
        output_path.unlink()

    writer: pq.ParquetWriter | None = None
    total_source_rows = 0
    total_parquet_rows = 0

    try:
        for path in source_files:
            for source_df in iter_official_csv_chunks(path, chunksize):
                total_source_rows += len(source_df)
                mapped = build_mt_budget_frame(source_df)
                normalized = normalize_preview(mapped, "MT", require_cnpj=True)
                if require_date and not normalized.empty:
                    normalized = normalized[normalized["data_inicio"].astype("string").str.strip().fillna("") != ""]

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

    temp_path.replace(output_path)
    return output_path, total_source_rows, total_parquet_rows


def main() -> None:
    args = parse_args()
    maybe_download_mt_sources(args)
    input_dir = Path(args.input_dir) if args.input_dir else default_input_dir(args.scope)
    output_name = args.output_name or default_output_name("MT", args.scope)
    output_path, source_rows, parquet_rows = write_mt_parquet(
        input_dir,
        Path(args.output_dir),
        output_name,
        args.chunksize,
        args.require_date,
    )
    print(f"Entrada: {input_dir}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {source_rows}")
    print(f"Linhas parquet: {parquet_rows}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
