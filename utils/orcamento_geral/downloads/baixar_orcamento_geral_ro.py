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
DESPESAS_PAGE_URL = "https://transparencia.ro.gov.br/despesa/despesa-estadual"
EMPENHOS_FORM_URL = "https://transparencia.ro.gov.br/Despesa/FormConsultaEmpenho"
EMPENHOS_FILTER_URL = "https://transparencia.ro.gov.br/Despesa/FiltrarEmpenhos"
DEFAULT_YEARS = tuple(str(year) for year in range(2017, 2026))
DEFAULT_EXPENSE_YEARS = tuple(str(year) for year in range(2020, 2027))
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
        help="Anos de convenios/transferencias a baixar. Padrao: 2017 a 2025.",
    )
    parser.add_argument(
        "--expense-years",
        nargs="*",
        default=list(DEFAULT_EXPENSE_YEARS),
        help="Anos de despesas gerais/empenhos a baixar. Padrao: 2020 a 2026.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=10000,
        help="Tamanho de pagina para despesas gerais. Padrao: 10000.",
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Nao baixa a API de dados abertos; baixa apenas o HTML legado.",
    )
    parser.add_argument(
        "--skip-convenios",
        action="store_true",
        help="Nao baixa os endpoints legados de convenios/transferencias.",
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


def extract_verification_token(html: str) -> str:
    match = re.search(r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', html)
    if not match:
        raise ValueError("Nao foi possivel localizar __RequestVerificationToken em RO.")
    return match.group(1)


def build_empenhos_payload(token: str, year: str, start: int, length: int, draw: int) -> dict[str, str]:
    payload = {
        "__RequestVerificationToken": token,
        "AnoAvancado": year,
        "MesInicialAvancado": "1",
        "MesFinalAvancado": "12",
        "CdUg": "",
        "CodFuncao": "",
        "CodSubFuncao": "",
        "CodPrograma": "",
        "CodFonteRecurso": "",
        "CodElementoDespesa": "",
        "NumeroEmpenho": "",
        "NomeCredor": "",
        "draw": str(draw),
        "start": str(start),
        "length": str(length),
        "search[value]": "",
        "search[regex]": "false",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
    }
    columns = [
        ("numeroEmpenho", "NotaEmpenho"),
        ("dataDocumentoFormatada", "DataEmpenho"),
        ("unidadeGestora", "Unidade"),
        ("credor", "Credor"),
        ("valorEmpenhado", ""),
        ("valorPago", ""),
    ]
    for index, (data, name) in enumerate(columns):
        payload[f"columns[{index}][data]"] = data
        payload[f"columns[{index}][name]"] = name
        payload[f"columns[{index}][searchable]"] = "true"
        payload[f"columns[{index}][orderable]"] = "true"
        payload[f"columns[{index}][search][value]"] = ""
        payload[f"columns[{index}][search][regex]"] = "false"
    return payload


def fetch_general_expense_year(session: requests.Session, token: str, year: str, page_size: int) -> list[dict[str, object]]:
    headers = {"X-Requested-With": "XMLHttpRequest", "Referer": DESPESAS_PAGE_URL}
    rows: list[dict[str, object]] = []
    start = 0
    total: int | None = None
    draw = 1
    while total is None or start < total:
        response = session.post(
            EMPENHOS_FILTER_URL,
            data=build_empenhos_payload(token, year, start, page_size, draw),
            headers=headers,
            timeout=180,
        )
        response.raise_for_status()
        payload = response.json()
        page_rows = payload.get("data") or []
        if not isinstance(page_rows, list):
            raise ValueError(f"Resposta inesperada em RO {year}, inicio {start}.")
        rows.extend(row for row in page_rows if isinstance(row, dict))
        total = int(payload.get("recordsFiltered") or len(rows))
        print(f"RO {year}: {len(rows)}/{total} empenhos")
        if not page_rows:
            break
        start += page_size
        draw += 1
        sleep(0.05)
    return rows


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    form_response = session.get(EMPENHOS_FORM_URL, timeout=120)
    form_response.raise_for_status()
    token = extract_verification_token(form_response.text)
    manifest: list[dict[str, object]] = []
    for year in args.expense_years:
        rows = fetch_general_expense_year(session, token, str(year), args.page_size)
        output_path = output_dir / f"ro_empenhos_gerais_{year}.json"
        write_json(output_path, rows)
        manifest.append({"ano": int(year), "arquivo": output_path.name, "registros": len(rows), "fonte": EMPENHOS_FILTER_URL})
        print(f"{year}: {len(rows)} empenhos -> {output_path}")
    write_json(output_dir / "ro_empenhos_gerais_manifest.json", manifest)

    if args.skip_convenios:
        print(f"Fonte despesas gerais: {DESPESAS_PAGE_URL}")
        return

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
