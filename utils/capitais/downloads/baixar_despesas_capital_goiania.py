from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PORTAL_URL = "https://www10.goiania.go.gov.br/transweb/Portal_Despesas.aspx"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exporta despesas mensais da capital Goiania pelo TransWeb oficial.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Goiania" / "despesas"),
    )
    parser.add_argument("--years", nargs="*", default=[str(year) for year in range(2015, datetime.now().year + 1)])
    parser.add_argument("--months", nargs="*", default=[f"{month:02d}" for month in range(1, 13)])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


def applicable_months(year: str, months: list[str]) -> list[str]:
    now = datetime.now()
    selected = [str(month).zfill(2) for month in months]
    if int(year) == now.year:
        selected = [month for month in selected if int(month) <= now.month]
    return selected


def select_option(page, select_index: int, value: str) -> None:
    page.locator("select").nth(select_index).select_option(value)
    page.wait_for_timeout(500)


def export_month(page, year: str, month: str, output_dir: Path, force: bool) -> dict[str, object]:
    output_path = output_dir / f"goiania_despesas_{year}_{month}.csv"
    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        return {"ano": year, "mes": month, "arquivo": output_path.name, "status": "skipped", "bytes": output_path.stat().st_size}

    select_option(page, 0, f"__ossli_{month}")
    select_option(page, 1, year)
    select_option(page, 12, "__ossli_2")

    try:
        with page.expect_download(timeout=90000) as download_info:
            page.eval_on_selector('input[value="OK"]', "el => el.click()")
        download = download_info.value
        download.save_as(output_path)
        status = "downloaded"
        bytes_count = output_path.stat().st_size
    except PlaywrightTimeoutError:
        status = "timeout"
        bytes_count = 0

    return {"ano": year, "mes": month, "arquivo": output_path.name, "status": status, "bytes": bytes_count}


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headed is False)
        page = browser.new_page(ignore_https_errors=True, accept_downloads=True)
        page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(5000)

        for year in [str(year) for year in args.years]:
            for month in applicable_months(year, args.months):
                row = export_month(page, year, month, output_dir, args.force)
                manifest.append(row)
                print(f"Goiania {year}-{month}: {row['status']} {row['bytes']} bytes")

        browser.close()

    (output_dir / "goiania_despesas_manifest.json").write_text(
        json.dumps({"fonte": PORTAL_URL, "arquivos": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
