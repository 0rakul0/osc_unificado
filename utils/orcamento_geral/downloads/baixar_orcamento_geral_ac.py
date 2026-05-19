from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


PAGE_URL = "https://transparencia.ac.gov.br/convenios"
DETAIL_URL = "https://transparencia.ac.gov.br/convenios/detalhamento-pdf"
DESPESAS_PAGE_URL = "https://transparencia.ac.gov.br/despesas"
DESPESAS_LIST_URL = "https://transparencia.ac.gov.br/despesas/listar"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa as despesas gerais oficiais do portal de transparencia do Acre."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "AC"),
        help="Pasta onde os arquivos brutos do Acre serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        help="Anos de despesas gerais a baixar. Se omitido, usa os anos disponiveis na pagina.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=5000,
        help="Tamanho de pagina para a coleta de despesas gerais. Padrao: 5000.",
    )
    parser.add_argument(
        "--skip-convenios",
        action="store_true",
        help="Nao rebaixa o endpoint de convenios legado.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def extract_csrf_token(html: str) -> str:
    csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', html)
    if not csrf_match:
        raise ValueError("Nao foi possivel localizar o csrf-token da pagina.")
    return csrf_match.group(1)


def extract_expense_years(html: str) -> list[int]:
    match = re.search(r'<select[^>]+id="ano"[^>]*>(.*?)</select>', html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    years = sorted({int(year) for year in re.findall(r'value="((?:19|20)\d{2})"', match.group(1))}, reverse=True)
    return years


def fetch_expense_year(session: requests.Session, csrf_token: str, year: int, page_size: int) -> list[dict[str, object]]:
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": DESPESAS_PAGE_URL,
        "X-CSRF-TOKEN": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
    }
    rows: list[dict[str, object]] = []
    start = 0
    total: int | None = None
    draw = 1
    while total is None or start < total:
        payload = {
            "draw": draw,
            "start": start,
            "length": page_size,
            "ano": year,
            "orgao": "",
            "busca": "",
            "filtro": "",
            "fonte": "",
            "despesa": "",
            "periodo": 0,
            "inicio": "",
            "fim": "",
            "mes": "",
            "bimestre": "",
            "quadrimestre": "",
            "semestre": "",
            "trimestre": "",
            "nr_empenho": "",
            "motivo": "",
            "programa": "",
            "order[0][column]": 7,
            "order[0][dir]": "desc",
        }
        response = session.post(DESPESAS_LIST_URL, data=payload, headers=headers, timeout=240)
        response.raise_for_status()
        data = response.json()
        page_rows = data.get("data") or []
        if not isinstance(page_rows, list):
            raise ValueError(f"Resposta inesperada de despesas gerais AC {year}, inicio {start}.")
        rows.extend(row for row in page_rows if isinstance(row, dict))
        total = int(data.get("recordsFiltered") or len(rows))
        print(f"{year}: {len(rows)}/{total} registros")
        if not page_rows:
            break
        start += page_size
        draw += 1
    return rows


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    despesas_response = session.get(DESPESAS_PAGE_URL, timeout=120)
    despesas_response.raise_for_status()
    despesas_csrf = extract_csrf_token(despesas_response.text)
    years = args.years or extract_expense_years(despesas_response.text)
    if not years:
        raise ValueError("Nao foi possivel identificar anos disponiveis em despesas gerais do Acre.")

    manifest: list[dict[str, object]] = []
    for year in years:
        rows = fetch_expense_year(session, despesas_csrf, year, args.page_size)
        output_path = output_dir / f"ac_despesas_gerais_{year}.json"
        write_json(output_path, rows)
        manifest.append({"ano": year, "arquivo": output_path.name, "registros": len(rows), "fonte": DESPESAS_LIST_URL})
        print(f"{year}: {len(rows)} registros -> {output_path}")
    write_json(output_dir / "ac_despesas_gerais_manifest.json", manifest)

    if not args.skip_convenios:
        page_response = session.get(PAGE_URL, timeout=120)
        page_response.raise_for_status()
        csrf_token = extract_csrf_token(page_response.text)
        post_headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": PAGE_URL,
            "X-CSRF-TOKEN": csrf_token,
            "X-Requested-With": "XMLHttpRequest",
        }
        payload = {
            "situacao": "",
            "ano": "",
            "orgao": "",
            "busca": "",
            "filtro": "0",
            "fonte": "",
            "periodo": "",
            "inicio": "",
            "fim": "",
            "mes": "",
            "bimestre": "",
            "trimestre": "",
            "quadrimestre": "",
            "semestre": "",
        }

        details_response = session.post(DETAIL_URL, data=payload, headers=post_headers, timeout=300)
        details_response.raise_for_status()
        convenio_rows = details_response.json()
        if not isinstance(convenio_rows, list):
            raise ValueError(f"Resposta inesperada em {DETAIL_URL}: {type(convenio_rows).__name__}")

        summary = {
            "fonte_pagina": PAGE_URL,
            "fonte_detalhamento": DETAIL_URL,
            "total_registros": len(convenio_rows),
            "atualizado_em": re.search(r"Dados atualizados em:</b>\s*([^<]+)", page_response.text).group(1).strip()
            if re.search(r"Dados atualizados em:</b>\s*([^<]+)", page_response.text)
            else "",
        }

        write_json(output_dir / "ac_convenios_detalhamento.json", convenio_rows)
        write_json(output_dir / "ac_convenios_resumo.json", summary)

    print(f"Fonte despesas gerais: {DESPESAS_PAGE_URL}")
    print(f"Manifest despesas: {output_dir / 'ac_despesas_gerais_manifest.json'}")


if __name__ == "__main__":
    main()
