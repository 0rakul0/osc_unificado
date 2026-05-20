from __future__ import annotations

import argparse
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


SEARCH_URL = "https://sistemas.sefaz.am.gov.br/transpprd/mnt/info/RelPagamentos.do?method=Pesquisar&interno=true"
DOWNLOAD_URL = "https://sistemas.sefaz.am.gov.br/transpprd/mnt/info/RelPagamentosConsultaCredor.do"
DEFAULT_YEARS = tuple(range(2010, 2027))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa pagamentos gerais do Amazonas por credor e ano.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "AM"),
        help="Pasta onde os CSVs brutos do Amazonas serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=list(DEFAULT_YEARS),
        help="Anos a baixar. Padrao: 2010 a 2026.",
    )
    return parser.parse_args()


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def fetch_year(session: requests.Session, year: int) -> bytes:
    session.get(SEARCH_URL, timeout=60).raise_for_status()
    params = {"method": "Consultar", "anoexercicio": year, "filter": "", "mes": "00", "tipoDownload": "CSV"}
    data = {"filter": "", "consignado": "", "anoexercicio": str(year), "periodo": "C", "consulta": "2", "mes": "00"}
    response = session.post(DOWNLOAD_URL, params=params, data=data, timeout=180)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "csv" not in content_type.lower():
        raise ValueError(f"Resposta inesperada para AM {year}: {content_type}")
    return response.content


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    total_rows = 0
    for year in args.years:
        content = fetch_year(session, year)
        output_path = output_dir / f"am_pagamentos_credor_{year}.csv"
        output_path.write_bytes(content)
        rows = max(content.count(b"\n") - 1, 0)
        total_rows += rows
        print(f"{year}: {rows} linhas -> {output_path}")

    print(f"Fonte: {DOWNLOAD_URL}")
    print(f"Linhas brutas estimadas: {total_rows}")


if __name__ == "__main__":
    main()
