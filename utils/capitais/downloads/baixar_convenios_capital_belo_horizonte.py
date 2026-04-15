from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
from playwright.sync_api import Error, sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR


RAW_URL = "https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/controladoria/convenios-de-repasse-31-10-2024-csv.csv"


def repair_mojibake(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    try:
        repaired = text.encode("latin1").decode("utf-8")
        return repaired.strip() or pd.NA
    except UnicodeError:
        return text


def main() -> None:
    output_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Belo Horizonte"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "belohorizonte_convenios_repasse_raw.csv"
    normalized_path = output_dir / "belohorizonte_convenios_repasse.csv"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        with page.expect_download() as download_info:
            try:
                page.goto(RAW_URL, wait_until="domcontentloaded", timeout=120000)
            except Error:
                pass
        download = download_info.value
        download.save_as(str(raw_path))
        browser.close()

    frame = pd.read_csv(raw_path, dtype=str, sep=";", encoding="latin1", skiprows=1)
    rename_map = dict(
        zip(
            frame.columns,
            [
                "numero_ij",
                "ano_ij",
                "nome_uo",
                "natureza",
                "tipo_contrato",
                "situao",
                "numero_processo",
                "data_inicio_vigencia",
                "data_fim_vigencia",
                "data_registro_pgm",
                "data_publicacao",
                "valor_ij",
                "fornecedor",
                "objeto",
            ],
        )
    )
    frame = frame.rename(columns=rename_map)
    for column in frame.columns:
        frame[column] = frame[column].map(repair_mojibake)

    frame.to_csv(normalized_path, index=False, encoding="utf-8-sig")
    print(raw_path)
    print(normalized_path)


if __name__ == "__main__":
    main()
