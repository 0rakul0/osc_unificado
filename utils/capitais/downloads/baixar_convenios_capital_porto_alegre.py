from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
from playwright.sync_api import Page, sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PORTAL_URL = "https://cnc.procempa.com.br/cnc/servlet/cnc.procempa.com.br.wwconvenios_portal"
STATUS_VALUES = {
    "1": "em_execucao",
    "2": "prestacao_contas",
    "3": "prestacao_aprovada",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os convenios e parcerias de Porto Alegre com detalhamento por instrumento."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Porto Alegre"),
        help="Pasta de saida para os arquivos brutos consolidados da capital.",
    )
    return parser.parse_args()


def safe_text(page: Page, selector: str) -> str:
    locator = page.locator(selector)
    if locator.count() == 0:
        return ""
    return " ".join(locator.first.inner_text().split())


def collect_status_rows(page: Page, status_value: str, status_label: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    page.select_option("#vCNV_STATUS", status_value)
    page.locator("input#IMAGE1").click(force=True)
    page.wait_for_load_state("networkidle")
    page.wait_for_function("() => typeof gx !== 'undefined'")
    page.wait_for_timeout(700)

    while True:
        table_rows = page.locator('table[id="GridContainerTbl"] tbody tr')
        row_count = table_rows.count()
        page_summaries: list[dict[str, str]] = []
        for row_index in range(row_count):
            row = table_rows.nth(row_index)
            parts = [" ".join(part.split()) for part in row.inner_text().split("\t") if part.strip()]
            page_summaries.append(
                {
                    "status_filtro": status_label,
                    "data_inicio_lista": parts[0] if len(parts) >= 1 else "",
                    "numero_lista": parts[1] if len(parts) >= 2 else "",
                    "status_lista": parts[2] if len(parts) >= 3 else "",
                    "orgao_lista": parts[3] if len(parts) >= 4 else "",
                    "valor_lista": parts[4] if len(parts) >= 5 else "",
                    "objeto_lista": parts[5] if len(parts) >= 6 else "",
                }
            )

        rows.extend(page_summaries)

        next_button = page.locator("button.PagingButtonsNext")
        if next_button.count() == 0:
            break
        if "gx-grid-paging-disabled" in (next_button.get_attribute("class") or ""):
            break
        page.evaluate('gx.O.GridContainer.grid.changeGridPage("NEXT")')
        page.wait_for_load_state("networkidle")
        page.wait_for_function("() => typeof gx !== 'undefined'")
        page.wait_for_timeout(700)

    return rows


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, str]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 2400})
        page.goto(PORTAL_URL, wait_until="networkidle", timeout=120000)
        page.wait_for_function("() => typeof gx !== 'undefined'")

        for status_value, status_label in STATUS_VALUES.items():
            status_rows = collect_status_rows(page, status_value, status_label)
            all_rows.extend(status_rows)
            print(f"{status_label}: {len(status_rows)} linhas")
            page.goto(PORTAL_URL, wait_until="networkidle", timeout=120000)
            page.wait_for_function("() => typeof gx !== 'undefined'")

        browser.close()

    frame = pd.DataFrame(all_rows).drop_duplicates(
        subset=["numero_lista", "status_lista", "status_filtro"],
        keep="first",
    )
    frame["ano"] = pd.to_datetime(frame.get("data_inicio_lista"), errors="coerce", dayfirst=True).dt.year.astype("Int64").astype("string")

    output_path = output_dir / "portoalegre_convenios.csv"
    frame.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Saida: {output_path}")
    print(f"Linhas consolidadas: {len(frame)}")


if __name__ == "__main__":
    main()
