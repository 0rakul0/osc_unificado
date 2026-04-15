from __future__ import annotations

import argparse
import re
from io import StringIO
from pathlib import Path
import sys

import pandas as pd
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PORTAL_URL = "https://www10.goiania.go.gov.br/transweb/Portal_DespesasTransferencias.aspx"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa os convenios/transferencias da capital Goiania.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Goiania"),
        help="Diretorio de saida para os arquivos brutos da capital.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        default=[str(year) for year in range(2016, 2027)],
        help="Lista de anos para coleta.",
    )
    return parser.parse_args()


def clean_cell(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value)
    text = re.sub(r"RichWidgets_Popup_Editor_init\(.*", "", text).strip()
    return text or None


def extract_table(html: str, year: str) -> pd.DataFrame:
    table = pd.read_html(StringIO(html), flavor="lxml")[0]
    table = table.rename(columns=lambda col: str(col).strip())
    for column in table.columns:
        table[column] = table[column].map(clean_cell)
    table["AnoArquivo"] = str(year)
    return table


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, object]] = []
    combined: list[pd.DataFrame] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)
        page.goto(PORTAL_URL, wait_until="networkidle", timeout=120000)

        year_select = page.locator("select").nth(1)
        search_button = page.get_by_role("button", name="Buscar")

        for year in args.years:
            year_select.select_option(str(year))
            search_button.click(timeout=30000)
            page.wait_for_timeout(2500)
            html = page.content()
            frame_df = extract_table(html, str(year))
            output_path = output_dir / f"goiania_convenios_{year}.csv"
            frame_df.to_csv(output_path, index=False, encoding="utf-8-sig")

            combined.append(frame_df)
            summaries.append({"year": str(year), "rows": int(len(frame_df)), "output_path": str(output_path)})
            print(f"Goiania {year}: {len(frame_df)} linhas -> {output_path}")

        browser.close()

    if combined:
        combined_df = pd.concat(combined, ignore_index=True)
        combined_path = output_dir / "goiania_convenios_consolidado.csv"
        combined_df.to_csv(combined_path, index=False, encoding="utf-8-sig")
        print(f"Consolidado: {combined_path} ({len(combined_df)} linhas)")

    pd.DataFrame(summaries).to_json(
        output_dir / "goiania_convenios_resumo.json",
        orient="records",
        force_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    main()
