from __future__ import annotations

import argparse
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PORTAL_URL = "https://sig-transparencia.campogrande.ms.gov.br/repasses-estaduais/consulta"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os repasses estaduais voluntarios publicados para Campo Grande."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Campo Grande"),
        help="Diretorio de saida para os arquivos brutos da capital.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        default=["2022", "2023", "2024", "2025"],
        help="Lista de anos para coleta.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, accept_downloads=True)
        page = context.new_page()
        page.goto(PORTAL_URL, wait_until="networkidle", timeout=120000)

        year_select = page.locator("select").nth(0)

        for year in args.years:
            year_select.select_option(str(year))
            page.get_by_role("button", name="Consultar").click(timeout=30000)
            page.wait_for_load_state("networkidle", timeout=120000)

            body_text = page.locator("body").inner_text().lower()
            if "registros 0" in body_text:
                continue

            with page.expect_download(timeout=120000) as dl_info:
                page.get_by_text("CSV").click()
            download = dl_info.value

            target = output_dir / f"campogrande_repasses_estaduais_{year}.csv"
            download.save_as(str(target))
            print(f"Campo Grande {year}: {target}")

        browser.close()


if __name__ == "__main__":
    main()
