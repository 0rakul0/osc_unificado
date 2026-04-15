from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


PORTAL_URL = "http://convenios.control.rn.gov.br/conveniorelsite.aspx"
DEFAULT_START_YEAR = 2000
DEFAULT_WAIT_MS = 7000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os convênios concedidos do RN por ano de abertura via portal oficial."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "RN"),
        help="Pasta onde os CSVs anuais e o consolidado serao salvos.",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=DEFAULT_START_YEAR,
        help="Ano inicial da consulta por periodo de abertura.",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=pd.Timestamp.today().year,
        help="Ano final da consulta por periodo de abertura.",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=DEFAULT_WAIT_MS,
        help="Tempo de espera apos clicar em Visualizar antes de exportar o CSV.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_csv_rows(path: Path) -> int:
    try:
        frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    except UnicodeDecodeError:
        frame = pd.read_csv(path, dtype=str, encoding="latin1")
    return len(frame)


def download_year(page: Any, year: int, output_dir: Path, wait_ms: int) -> dict[str, object]:
    target_path = output_dir / f"rn_{year}.csv"
    if target_path.exists() and target_path.stat().st_size > 0:
        rows_csv = read_csv_rows(target_path)
        return {
            "ano_abertura": year,
            "arquivo": target_path.name,
            "bytes": target_path.stat().st_size,
            "rows_csv": rows_csv,
            "tabulator_rows": rows_csv,
            "status": "ja_existente",
        }

    page.goto(PORTAL_URL, wait_until="networkidle", timeout=120000)
    page.fill("#txtDataAberturaIni", f"01/01/{year}")
    page.fill("#txtDataAberturaFin", f"31/12/{year}")
    page.click("#btnConsultar", no_wait_after=True)
    try:
        page.wait_for_load_state("domcontentloaded", timeout=30000)
    except PlaywrightTimeoutError:
        pass
    page.wait_for_timeout(wait_ms)

    try:
        body_text = page.locator("body").inner_text(timeout=5000)
    except PlaywrightTimeoutError:
        body_text = ""
    try:
        tabulator_rows = page.locator(".tabulator-row").count()
    except PlaywrightTimeoutError:
        tabulator_rows = 0
    empty_result = "Nenhum registro encontrado" in body_text or tabulator_rows == 0

    if empty_result:
        return {
            "ano_abertura": year,
            "arquivo": None,
            "rows_csv": 0,
            "tabulator_rows": tabulator_rows,
            "status": "sem_dados",
        }

    try:
        with page.expect_download(timeout=45000) as download_info:
            page.click("#btnExportarCSV", no_wait_after=True)
        download = download_info.value
        download.save_as(str(target_path))
    except PlaywrightTimeoutError:
        return {
            "ano_abertura": year,
            "arquivo": None,
            "rows_csv": 0,
            "tabulator_rows": tabulator_rows,
            "status": "sem_download" if empty_result else "falha_download",
        }

    rows_csv = read_csv_rows(target_path) if target_path.exists() and target_path.stat().st_size > 0 else 0
    return {
        "ano_abertura": year,
        "arquivo": target_path.name,
        "bytes": target_path.stat().st_size if target_path.exists() else 0,
        "rows_csv": rows_csv,
        "tabulator_rows": tabulator_rows,
        "status": "ok" if rows_csv else "vazio",
    }


def combine_downloads(output_dir: Path, year_summaries: list[dict[str, object]]) -> tuple[Path, int]:
    frames: list[pd.DataFrame] = []
    for item in year_summaries:
        filename = item.get("arquivo")
        if not filename:
            continue
        csv_path = output_dir / str(filename)
        if not csv_path.exists() or not csv_path.stat().st_size:
            continue
        try:
            frame = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig")
        except UnicodeDecodeError:
            frame = pd.read_csv(csv_path, dtype=str, encoding="latin1")
        frame["ano_abertura_consulta"] = str(item["ano_abertura"])
        frames.append(frame)

    combined_path = output_dir / "rn_convenios_concedidos.csv"
    if not frames:
        pd.DataFrame().to_csv(combined_path, index=False)
        return combined_path, 0

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates().reset_index(drop=True)
    combined.to_csv(combined_path, index=False, encoding="utf-8-sig")
    return combined_path, len(combined)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    year_summaries: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for year in range(args.start_year, args.end_year + 1):
                page = browser.new_page(accept_downloads=True)
                try:
                    summary = download_year(page, year, output_dir, args.wait_ms)
                    year_summaries.append(summary)
                    print(
                        f"RN {year}: status={summary['status']} "
                        f"tabulator={summary['tabulator_rows']} csv_rows={summary['rows_csv']}"
                    )
                finally:
                    page.close()
        finally:
            browser.close()

    combined_path, combined_rows = combine_downloads(output_dir, year_summaries)
    summary = {
        "fonte_portal": PORTAL_URL,
        "anos_consulta": [item["ano_abertura"] for item in year_summaries],
        "downloads": year_summaries,
        "arquivos_ok": sum(1 for item in year_summaries if item["status"] == "ok"),
        "arquivos_ja_existentes": sum(1 for item in year_summaries if item["status"] == "ja_existente"),
        "arquivos_vazios": sum(1 for item in year_summaries if item["status"] == "vazio"),
        "anos_sem_dados": sum(1 for item in year_summaries if item["status"] == "sem_dados"),
        "falhas_download": sum(1 for item in year_summaries if item["status"] == "falha_download"),
        "sem_download": sum(1 for item in year_summaries if item["status"] == "sem_download"),
        "linhas_consolidadas": combined_rows,
        "arquivo_consolidado": combined_path.name,
    }
    write_json(output_dir / "rn_convenios_resumo.json", summary)

    print(f"Fonte oficial: {PORTAL_URL}")
    print(f"Consolidado: {combined_path}")
    print(f"Linhas consolidadas: {combined_rows}")


if __name__ == "__main__":
    main()
