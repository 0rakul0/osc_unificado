from __future__ import annotations

import argparse
import base64
from datetime import datetime
from hashlib import sha256
import hmac
import json
from pathlib import Path
import sys
import time

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


BASE_URL = "https://prodata.palmas.to.gov.br/sig"
PORTAL_URL = f"{BASE_URL}/app.html#/transparencia/transparencia-despesa-simplificado/"
LOGIN_URL = f"{BASE_URL}/rest/loginController/validarLoginParaModuloPublico"
API_URL = f"{BASE_URL}/rest/despesaSimplificadoController/pesquisarPorInteressado"
PUBLIC_MODULE_TOKEN = "d5e5f85abdcfc21cddfc97e1fc6372db0445629f86b1a22a772a58d753bb40f8"
CLIENT_ID = "sig-frontend"
REQUEST_SIGNATURE_SECRET = b"request-prodata-hash-code"
DEFAULT_YEARS = [2023, 2024, 2025]
MONTH_NAMES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa despesas pagas de Palmas pela API oficial do portal Prodata."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Palmas"),
        help="Pasta onde os JSONs de despesas da capital serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=DEFAULT_YEARS,
        help="Anos a consultar. Padrao: 2023 2024 2025.",
    )
    parser.add_argument(
        "--fase",
        choices=["empenhado", "liquidado", "pago"],
        default="pago",
        help="Fase da despesa a consultar. Padrao: pago.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout, em segundos, de cada chamada da API.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def login_public_module(session: requests.Session, timeout: int) -> str:
    response = session.post(
        LOGIN_URL,
        json={"modulo": "transparencia", "token": PUBLIC_MODULE_TOKEN},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    token = payload.get("token") if isinstance(payload, dict) else None
    if not isinstance(token, str) or not token:
        raise ValueError("Login publico de Palmas nao retornou token de autenticacao.")
    return token


def signed_headers(token: str) -> dict[str, str]:
    timestamp = str(int(time.time() * 1000))
    signature_payload = f"{CLIENT_ID}|{timestamp}".encode("utf-8")
    signature = base64.b64encode(
        hmac.new(REQUEST_SIGNATURE_SECRET, signature_payload, digestmod=sha256).digest()
    ).decode("ascii")
    return {
        "x-id": "sig",
        "x-origin": "https://prodata.palmas.to.gov.br",
        "x-url": PORTAL_URL,
        "x-modulo": "TRANSPARENCIA",
        "x-client-id": CLIENT_ID,
        "x-timestamp": timestamp,
        "x-request-signature": signature,
        "x-auth-token": token,
        "x-ip-local": "0.0.0.0",
    }


def payload_for_year(year: int, fase: str) -> dict[str, object]:
    current = datetime.now()
    mes_final = current.month if year == current.year else 12
    return {
        "fase_despesa": fase,
        "agrupamento": "fornecedor",
        "exercicio": year,
        "mesInicial": 1,
        "mesFinal": mes_final,
        "ordenar_gestao": False,
        "ordenar_unidade": False,
        "formatoArquivoRelatorio": "PDF",
        "mesFinalDescricao": MONTH_NAMES[mes_final],
        "grafico": "false",
        "tabela": {},
        "isConsultaText": False,
        "nomeTelaAtualAutocomplete": None,
        "moduloAtual": "TRANSPARENCIA",
        "descricaoModuloAtual": "transparencia",
    }


def month_from_date(value: object) -> object:
    if not value:
        return None
    text = str(value)
    if len(text) >= 7 and text[4] == "-":
        return text[5:7]
    return None


def flatten_record(row: dict[str, object], year: int, fase: str) -> dict[str, object]:
    data = row.get("data")
    return {
        "ano_consulta": year,
        "mes_consulta": month_from_date(data),
        "fase_despesa": fase,
        "ano": row.get("exe") or year,
        "valor_total": row.get("valor_pago_no_mes") or row.get("valor") or row.get("valor_pago"),
        "valor_pago": row.get("valor_pago_no_mes") or row.get("valor_pago"),
        "valor_liquidado": row.get("vl_liquidado"),
        "valor_empenhado": row.get("valor_empenho") or row.get("valor_empenho_bruto"),
        "cnpj": row.get("cgc_fornecedor"),
        "nome_osc": row.get("fornecedor"),
        "objeto": row.get("historico"),
        "modalidade": row.get("ds_cadnat"),
        "data_inicio": data,
        "orgao": row.get("org_nome"),
        "unidade": row.get("unidade") or row.get("caduni_nome"),
        "funcao": row.get("fun_nome"),
        "subfuncao": row.get("sfu_nome"),
        "programa": row.get("pro_nome"),
        "acao": row.get("pra_nome"),
        "fonte": row.get("ds_fonte"),
        "processo": row.get("processo"),
        "fonte_portal": PORTAL_URL,
        "fonte_api": API_URL,
    }


def fetch_year(session: requests.Session, token: str, year: int, fase: str, timeout: int) -> tuple[list[dict[str, object]], dict[str, object]]:
    payload = payload_for_year(year, fase)
    response = session.post(API_URL, json=payload, headers=signed_headers(token), timeout=timeout)
    response.raise_for_status()
    raw_bytes = response.content
    rows = response.json()
    if not isinstance(rows, list):
        raise ValueError(f"Resposta inesperada para Palmas {year}: {type(rows).__name__}.")
    flattened = [flatten_record(row, year, fase) for row in rows if isinstance(row, dict)]
    metadata = {
        "ano": year,
        "fase_despesa": fase,
        "mes_inicial": payload["mesInicial"],
        "mes_final": payload["mesFinal"],
        "registros": len(flattened),
        "status_code": response.status_code,
        "url": API_URL,
        "bytes": len(raw_bytes),
        "sha256": sha256(raw_bytes).hexdigest(),
    }
    return flattened, metadata


def load_existing_manifest(path: Path) -> dict[int, dict[str, object]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    years = payload.get("anos") if isinstance(payload, dict) else None
    if not isinstance(years, list):
        return {}
    result: dict[int, dict[str, object]] = {}
    for item in years:
        if not isinstance(item, dict):
            continue
        try:
            year = int(item.get("ano"))
        except (TypeError, ValueError):
            continue
        result[year] = item
    return result


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "palmas_despesas_manifest.json"

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": f"{BASE_URL}/app.html",
        }
    )

    manifest_by_year = load_existing_manifest(manifest_path)
    try:
        token = login_public_module(session, args.timeout)
        for year in sorted(set(args.years)):
            rows, metadata = fetch_year(session, token, year, args.fase, args.timeout)
            data_path = output_dir / f"palmas_despesas_{year}.json"
            write_json(data_path, rows)
            manifest_by_year[year] = {"arquivo": data_path.name, **metadata}
            print(f"Palmas {year}: {len(rows)} registros -> {data_path}")
    finally:
        session.close()

    write_json(
        manifest_path,
        {
            "fonte_portal": PORTAL_URL,
            "fonte_api": API_URL,
            "fase_despesa": args.fase,
            "anos": [manifest_by_year[year] for year in sorted(manifest_by_year)],
        },
    )


if __name__ == "__main__":
    main()
