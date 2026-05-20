from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import math
from pathlib import Path
import sys
from time import sleep
from typing import Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


API_URL = "https://api.transparencia.pi.gov.br/api/v2/despesas/{year}/1/12/"
SEARCH_TERMS = ("subven", "contrato", "fomento")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa despesas gerais do PI pela API do portal de transparencia."
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
        help="Termos de busca usados na API quando --all nao for informado.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Baixa todas as paginas de despesas gerais, sem termo de busca.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Numero de requisicoes paralelas na coleta completa. Padrao: 8.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
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


def fetch_page(session: requests.Session | None, year: int, page: int) -> tuple[int, dict[str, object]]:
    url = API_URL.format(year=year)
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            client = session or requests
            response = client.get(url, params={"page": page}, headers=headers, timeout=90)
            response.raise_for_status()
            return page, response.json()
        except Exception as exc:
            last_error = exc
            sleep(min(2**attempt, 30))
    raise RuntimeError(f"Falha ao baixar PI {year}, pagina {page}") from last_error


def fetch_all_rows(session: requests.Session, year: int, workers: int) -> list[dict[str, object]]:
    first_page, first_payload = fetch_page(session, year, 1)
    results = first_payload.get("results") or []
    if not isinstance(results, list):
        raise ValueError(f"Resposta inesperada para PI {year}, pagina {first_page}.")

    total = int(first_payload.get("count") or len(results))
    page_size = max(len(results), 1)
    page_count = math.ceil(total / page_size)
    pages: dict[int, list[dict[str, object]]] = {1: [row for row in results if isinstance(row, dict)]}
    print(f"{year}: pagina 1/{page_count}, acumulado {len(pages[1])} de {total}", flush=True)

    if page_count == 1:
        return pages[1]

    with ThreadPoolExecutor(max_workers=max(workers, 1)) as executor:
        futures = {executor.submit(fetch_page, None, year, page): page for page in range(2, page_count + 1)}
        completed = 1
        for future in as_completed(futures):
            page, payload = future.result()
            page_rows = payload.get("results") or []
            if not isinstance(page_rows, list):
                raise ValueError(f"Resposta inesperada para PI {year}, pagina {page}.")
            pages[page] = [row for row in page_rows if isinstance(row, dict)]
            completed += 1
            if completed % 100 == 0 or completed == page_count:
                accumulated = sum(len(page_rows) for page_rows in pages.values())
                print(f"{year}: paginas {completed}/{page_count}, acumulado {accumulated} de {total}", flush=True)

    rows: list[dict[str, object]] = []
    for page in range(1, page_count + 1):
        rows.extend(pages.get(page, []))
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
        if args.all:
            rows = fetch_all_rows(session, year, args.workers)
            term_counts: dict[str, int] = {}
            output_path = output_dir / f"pi_despesas_gerais_{year}.json"
        else:
            batches = []
            term_counts = {}
            for term in args.terms:
                term_rows = fetch_search_rows(session, year, term)
                batches.append(term_rows)
                term_counts[term] = len(term_rows)
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
                "escopo": "despesas_gerais" if args.all else "busca_por_termos",
            }
        )
        print(f"{year}: {len(rows)} registros unicos -> {output_path}")

    manifest_name = "pi_despesas_gerais_manifest.json" if args.all else "pi_despesas_osc_manifest.json"
    write_json(output_dir / manifest_name, manifest)


if __name__ == "__main__":
    main()
