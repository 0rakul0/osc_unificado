from __future__ import annotations

import argparse
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PORTAL_URL = "https://saoluis.giap.com.br/ords/saoluis/f?p=839:104"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa os CSVs oficiais de convenios/parcerias da capital Sao Luis.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Sao Luis"),
        help="Diretorio de saida para os arquivos brutos da capital.",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2009,
        help="Ano inicial da coleta.",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2026,
        help="Ano final da coleta.",
    )
    return parser.parse_args()


def parse_registros_text(text: str) -> int:
    for line in text.splitlines():
        line = line.strip().lower()
        if line.startswith("1 - "):
            parts = line.split("-")
            if len(parts) == 2:
                right = parts[1].strip()
                try:
                    return int(right)
                except ValueError:
                    return 0
        if "nenhum registro" in line:
            return 0
    return 0


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, accept_downloads=True)
        page = context.new_page()
        page.goto(PORTAL_URL, wait_until="networkidle", timeout=120000)

        institution_select = page.locator('select[name="INSTITUICAO"]')
        year_select = page.locator('select[name="GLOBAL_EXERCICIO"]')
        institution_options = institution_select.evaluate(
            "e => Array.from(e.options).map(o => ({text: o.textContent.trim(), value: o.value})).filter(o => o.value)"
        )
        years = [str(year) for year in range(args.start_year, args.end_year + 1)]

        for option in institution_options:
            institution_value = str(option["value"])
            safe_institution = institution_value

            institution_select.select_option(institution_value)
            page.wait_for_load_state("networkidle", timeout=120000)

            for year in years:
                year_select.select_option(year)
                page.get_by_role("button", name="Pesquisar").click(timeout=30000)
                page.wait_for_load_state("networkidle", timeout=120000)

                body_text = page.locator("body").inner_text()
                row_count = parse_registros_text(body_text)
                if row_count <= 0:
                    continue

                with page.expect_download(timeout=120000) as dl_info:
                    page.get_by_text("CSV").click()
                download = dl_info.value

                target = output_dir / f"saoluis_{safe_institution}_{year}.csv"
                download.save_as(str(target))
                print(f"Sao Luis inst={institution_value} ano={year}: {row_count} linhas -> {target}")

        browser.close()


if __name__ == "__main__":
    main()
