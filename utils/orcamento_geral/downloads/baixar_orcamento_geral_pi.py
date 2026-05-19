from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from time import sleep
from typing import Iterable

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


API_URL = "https://api.transparencia.pi.gov.br/api/v2/despesas/{year}/1/12/"
SEARCH_TERMS = ("subven", "contrato", "fomento")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa despesas do PI com termos provaveis de transferencias a OSC."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "PI"),
        help="Pasta onde os arquivos brutos do PI serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=[2022, 2023, 2024, 2025, 2026],
        help="Anos a baixar. Padrao: 2022 2023 2024 2025 2026.",
    )
    parser.add_argument(
        "--terms",
        nargs="*",
        default=list(SEARCH_TERMS),
        help="Termos de busca usados na API.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
    )
    return session


def row_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        row.get("exercicio"),
        row.get("documento_codigo"),
        row.get("credor_codigo"),
        row.get("emissao_data"),
        row.get("temp_pago_saldo"),
    )


def fetch_search_rows(session: requests.Session, year: int, term: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    page = 1
    while True:
        response = session.get(API_URL.format(year=year), params={"search": term, "page": page}, timeout=120)
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results") or []
        if not isinstance(results, list):
            raise ValueError(f"Resposta inesperada para PI {year}, termo {term!r}, pagina {page}.")
        rows.extend(results)
        if not payload.get("next"):
            break
        page += 1
        sleep(0.05)
    return rows


def unique_rows(batches: Iterable[list[dict[str, object]]]) -> list[dict[str, object]]:
    seen: set[tuple[object, ...]] = set()
    rows: list[dict[str, object]] = []
    for batch in batches:
        for row in batch:
            key = row_key(row)
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
    return rows


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    manifest: list[dict[str, object]] = []
    for year in args.years:
        batches = []
        term_counts: dict[str, int] = {}
        for term in args.terms:
            rows = fetch_search_rows(session, year, term)
            batches.append(rows)
            term_counts[term] = len(rows)

        rows = unique_rows(batches)
        output_path = output_dir / f"pi_despesas_osc_{year}.json"
        write_json(output_path, rows)
        manifest.append(
            {
                "ano": year,
                "arquivo": output_path.name,
                "registros_unicos": len(rows),
                "termos": term_counts,
                "fonte": API_URL.format(year=year),
            }
        )
        print(f"{year}: {len(rows)} registros unicos -> {output_path}")

    write_json(output_dir / "pi_despesas_osc_manifest.json", manifest)


if __name__ == "__main__":
    main()
