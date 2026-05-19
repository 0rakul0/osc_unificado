from __future__ import annotations

import argparse
from html import unescape
import json
from pathlib import Path
import re
import sys
from time import sleep

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


FILTER_URL = "https://transparencia.ro.gov.br/convenios/filtrartransferencias"
API_URL = "https://transparencia.api.ro.gov.br/api/v1/convenios"
DEFAULT_YEARS = tuple(str(year) for year in range(2017, 2026))
ROW_PATTERN = re.compile(r'<tr class="text-center"(?P<attrs>.*?)</tr>', re.IGNORECASE | re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa as transferencias realizadas do portal oficial de RO."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "RO"),
        help="Pasta de saida para os arquivos brutos do estado.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        default=list(DEFAULT_YEARS),
        help="Anos a baixar. Padrao: 2017 a 2025.",
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Nao baixa a API de dados abertos; baixa apenas o HTML legado.",
    )
    return parser.parse_args()


def extract_attr(attrs: str, name: str) -> str:
    match = re.search(fr'data-{name}="(.*?)"', attrs, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return " ".join(unescape(match.group(1)).split())


def fetch_year(year: str) -> list[dict[str, str]]:
    response = requests.post(
        FILTER_URL,
        data={"Exercicio": year, "Beneficiario": "", "Instrumento": ""},
        timeout=120,
    )
    response.raise_for_status()

    rows: list[dict[str, str]] = []
    for match in ROW_PATTERN.finditer(response.text):
        attrs = match.group("attrs")
        beneficiario = extract_attr(attrs, "beneficiario")
        if not beneficiario:
            continue
        rows.append(
            {
                "ano_consulta": year,
                "beneficiario": beneficiario,
                "numero_instrumento": extract_attr(attrs, "convenio"),
                "valor_total_previsto": extract_attr(attrs, "total-repasse"),
                "objeto": extract_attr(attrs, "objeto"),
                "valor_repassado_data": extract_attr(attrs, "valor-repassado"),
                "vigencia": extract_attr(attrs, "vigencia"),
                "detalhe_relativo": extract_attr(attrs, "link"),
                "fonte_url": FILTER_URL,
            }
        )
    return rows


def fetch_api_pages() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    page = 1
    total_pages = 1
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    while page <= total_pages:
        response = session.get(API_URL, params={"Page": page, "PageSize": 100}, timeout=120)
        if response.status_code == 404 and rows:
            print(f"API pagina {page}: 404; encerrando com {len(rows)} registros ja coletados")
            break
        response.raise_for_status()
        payload = response.json()
        data = payload.get("resultados") or []
        if not isinstance(data, list):
            raise ValueError(f"Resposta inesperada da API de RO na pagina {page}.")
        rows.extend(row for row in data if isinstance(row, dict))
        total_pages = int(payload.get("totalDePaginas") or page)
        print(f"API pagina {page}/{total_pages}: {len(data)} registros")
        page += 1
        sleep(0.1)
    return rows


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_api:
        api_rows = fetch_api_pages()
        api_path = output_dir / "ro_convenios_api.json"
        write_json(api_path, api_rows)
        print(f"API oficial: {API_URL}")
        print(f"Saida API: {api_path}")
        print(f"Linhas API: {len(api_rows)}")

    rows: list[dict[str, str]] = []
    for year in args.years:
        year_rows = fetch_year(str(year))
        rows.extend(year_rows)
        print(f"{year}: {len(year_rows)} registros")

    output_path = output_dir / "ro_transferencias_realizadas.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Entrada oficial: {FILTER_URL}")
    print(f"Saida: {output_path}")
    print(f"Linhas consolidadas: {len(rows)}")


if __name__ == "__main__":
    main()
