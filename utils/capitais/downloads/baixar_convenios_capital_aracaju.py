from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

import pandas as pd
import pdfplumber
import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PORTAL_URL = "https://transparencia.aracaju.se.gov.br/prefeitura/convenios-e-outros-ajustes/"
MONTHS = {
    "JAN": "1",
    "FEV": "2",
    "MAR": "3",
    "ABR": "4",
    "MAI": "5",
    "JUN": "6",
    "JUL": "7",
    "AGO": "8",
    "SET": "9",
    "OUT": "10",
    "NOV": "11",
    "DEZ": "12",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa e extrai os relatorios oficiais de repasses a ONGs da capital Aracaju."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Aracaju"),
        help="Pasta de saida para os arquivos brutos consolidados da capital.",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2017,
        help="Ano inicial da coleta.",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2026,
        help="Ano final da coleta.",
    )
    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").strip()
    return " ".join(text.split())


def fetch_pdf_links(session: requests.Session, start_year: int, end_year: int) -> list[tuple[int, str]]:
    response = session.get(PORTAL_URL, timeout=120, verify=False)
    response.raise_for_status()
    links = sorted(set(re.findall(r"https?://[^\s\"']+\.pdf(?:\?[^\s\"']*)?", response.text, flags=re.IGNORECASE)))
    selected_by_year: dict[int, tuple[int, str]] = {}
    for link in links:
        if "municipais" not in link.lower():
            continue
        year_match = re.search(r"(19|20)\d{2}", link)
        if not year_match:
            continue
        year = int(year_match.group(0))
        if start_year <= year <= end_year:
            score = 0
            lower_link = link.lower()
            if "jan_dez" in lower_link or "consolidado" in lower_link:
                score += 10
            if "/prefeitura/" in lower_link:
                score += 1
            if year not in selected_by_year or score > selected_by_year[year][0]:
                selected_by_year[year] = (score, link)
    return sorted((year, item[1]) for year, item in selected_by_year.items())


def parse_pdf_rows(pdf_path: Path, year: int, source_url: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                current_secretaria = ""
                for raw_row in table:
                    if not raw_row or len(raw_row) < 14:
                        continue
                    first_cell = clean_text(raw_row[0])
                    if not first_cell:
                        continue
                    if first_cell.startswith("ESTADO DE SERGIPE") or first_cell == "ESPECIFICAÇÃO":
                        continue
                    if first_cell.startswith("VERIFICAÇÃO DAS"):
                        continue
                    if first_cell.upper().startswith("SECRETARIA"):
                        current_secretaria = first_cell
                        continue
                    if first_cell.upper().startswith("FUNDAÇÃO MUNICIPAL"):
                        current_secretaria = first_cell
                        continue

                    total = clean_text(raw_row[13])
                    if not total or total == "0,00":
                        continue

                    for month_name, month_number in MONTHS.items():
                        value = clean_text(raw_row[list(MONTHS.keys()).index(month_name) + 1])
                        if not value or value == "0,00":
                            continue
                        records.append(
                            {
                                "ano": str(year),
                                "mes": month_number,
                                "nome_osc": first_cell,
                                "secretaria": current_secretaria,
                                "valor_mes": value,
                                "valor_total_ano": total,
                                "objeto": "Repasse para instituicoes sem fins lucrativos - ONGs",
                                "data_inicio": f"{year}-{int(month_number):02d}-01",
                                "fonte_pdf": source_url,
                            }
                        )
    return records


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    pdf_links = fetch_pdf_links(session, args.start_year, args.end_year)

    all_records: list[dict[str, str]] = []
    manifest: list[dict[str, object]] = []
    for year, link in pdf_links:
        target_pdf = output_dir / f"aracaju_repasse_ongs_{year}.pdf"
        target_pdf.write_bytes(session.get(link, timeout=120, verify=False).content)
        year_records = parse_pdf_rows(target_pdf, year, link)
        all_records.extend(year_records)
        manifest.append({"ano": year, "url": link, "rows": len(year_records), "arquivo": target_pdf.name})
        print(f"Aracaju ano={year}: {len(year_records)} linhas")

    frame = pd.DataFrame(all_records)
    if not frame.empty:
        frame = frame.drop_duplicates(
            subset=["ano", "mes", "nome_osc", "secretaria", "valor_mes"],
            keep="first",
        )
    csv_path = output_dir / "aracaju_repasses_ongs.csv"
    manifest_path = output_dir / "aracaju_repasses_ongs_manifest.json"
    frame.to_csv(csv_path, index=False, encoding="utf-8-sig")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saida CSV: {csv_path}")
    print(f"Saida manifest: {manifest_path}")
    print(f"Linhas consolidadas: {len(frame)}")


if __name__ == "__main__":
    main()
