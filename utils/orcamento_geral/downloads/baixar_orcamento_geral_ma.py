from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


BASE_URL = "https://transparencia2015.ma.gov.br"
SEARCH_URL = f"{BASE_URL}/app/despesas/por-fornecedor/search/{{year}}"
DEFAULT_TERMS = [
    "associacao",
    "fundacao",
    "instituto",
    "apae",
    "sociedade",
    "santa casa",
    "beneficente",
    "comunitaria",
    "cultural",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa fornecedores de despesas do MA no portal legado, em partes por ano e termo."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "MA"),
        help="Pasta onde os arquivos brutos de MA serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=list(range(2015, 2026)),
        help="Anos a baixar no portal legado. Padrao: 2015 a 2025.",
    )
    parser.add_argument(
        "--terms",
        nargs="*",
        default=DEFAULT_TERMS,
        help="Termos de busca para localizar potenciais OSC.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=500,
        help="Tamanho do lote na chamada DataTables. Padrao: 500.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rebaixa arquivos ja existentes.",
    )
    return parser.parse_args()


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
        }
    )
    return session


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "termo"


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = BeautifulSoup(str(value), "html.parser").get_text(" ", strip=True)
    return " ".join(text.split())


def extract_href(value: object) -> str:
    soup = BeautifulSoup(str(value or ""), "html.parser")
    anchor = soup.find("a", href=True)
    if not anchor:
        return ""
    return urljoin(BASE_URL, anchor["href"])


def fetch_term(session: requests.Session, year: int, term: str, page_size: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start = 0
    while True:
        params = {
            "sEcho": 1,
            "iDisplayStart": start,
            "iDisplayLength": page_size,
            "sSearch": term,
        }
        response = session.get(SEARCH_URL.format(year=year), params=params, timeout=180)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data") or []
        if not isinstance(data, list):
            raise ValueError(f"Resposta inesperada para MA {year} termo {term!r}.")
        for item in data:
            if not isinstance(item, list) or len(item) < 5:
                continue
            rows.append(
                {
                    "ano": year,
                    "termo_busca": term,
                    "codigo_credor": clean_text(item[0]),
                    "credor_nome": clean_text(item[1]),
                    "detalhe_url": extract_href(item[1]),
                    "valor_empenhado": clean_text(item[2]),
                    "valor_liquidado": clean_text(item[3]),
                    "valor_pago": clean_text(item[4]),
                    "fonte": SEARCH_URL.format(year=year),
                }
            )
        if len(data) < page_size:
            break
        start += page_size
        sleep(0.5)
    return rows


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    session = build_session()

    manifest: list[dict[str, object]] = []
    for year in args.years:
        year_rows: list[dict[str, object]] = []
        for term in args.terms:
            part_path = output_dir / f"ma_fornecedores_legacy_{year}_{slugify(term)}.json"
            if part_path.exists() and not args.overwrite:
                part_rows = json.loads(part_path.read_text(encoding="utf-8"))
            else:
                part_rows = fetch_term(session, year, term, args.page_size)
                write_json(part_path, part_rows)
            if isinstance(part_rows, list):
                year_rows.extend(row for row in part_rows if isinstance(row, dict))
                count = len(part_rows)
            else:
                count = 0
            manifest.append({"ano": year, "termo": term, "arquivo": part_path.name, "registros": count})
            print(f"{year} {term}: {count} registros")
            sleep(0.4)

        by_key: dict[tuple[str, str], dict[str, object]] = {}
        for row in year_rows:
            key = (str(row.get("ano") or ""), str(row.get("codigo_credor") or ""))
            if key[1] and key not in by_key:
                by_key[key] = row
        consolidated_path = output_dir / f"ma_fornecedores_legacy_{year}.json"
        write_json(consolidated_path, list(by_key.values()))
        print(f"{year}: {len(by_key)} registros unicos -> {consolidated_path}")

    write_json(output_dir / "ma_fornecedores_legacy_manifest.json", manifest)


if __name__ == "__main__":
    main()
