from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys

import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://api.portovelho.ro.gov.br/api/v1/contratos"
MODELOS_PARCERIA = {
    "Convenios",
    "Termo de Fomento",
    "Termo de Parceria",
    "Termo de Colaboracao",
    "Termo de Colaboracao",
    "Contrato de Gestao",
    "Convenio Estadual",
    "Convenios com a Uniao",
    "Acordo de Cooperacao",
    "Acordo de Cooperacao Tecnica",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os convenios e termos de parceria da capital Porto Velho pela API oficial."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Porto Velho"),
        help="Pasta de saida para os JSONs oficiais consolidados da capital.",
    )
    return parser.parse_args()


def build_session() -> requests.Session:
    session = requests.Session()
    session.verify = False
    return session


def fetch_json(session: requests.Session, page: int) -> dict[str, object]:
    response = session.get(API_URL, params={"page": page}, timeout=120)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError(f"Resposta inesperada da API de Porto Velho: {type(payload).__name__}")
    return payload


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalize_modelo(value: object) -> str:
    text = normalize_text(value)
    replacements = {
        "ç": "c",
        "Ç": "C",
        "ã": "a",
        "Ã": "A",
        "á": "a",
        "Á": "A",
        "é": "e",
        "É": "E",
        "ê": "e",
        "Ê": "E",
        "í": "i",
        "Í": "I",
        "ó": "o",
        "Ó": "O",
        "ô": "o",
        "Ô": "O",
        "õ": "o",
        "Õ": "O",
        "ú": "u",
        "Ú": "U",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def flatten_record(item: dict[str, object]) -> dict[str, object]:
    valor = item.get("valor") if isinstance(item.get("valor"), dict) else {}
    valor_executado = item.get("valor_executado") if isinstance(item.get("valor_executado"), dict) else {}
    fornecedor = item.get("fornecedor") if isinstance(item.get("fornecedor"), dict) else {}
    contratante = item.get("contratante") if isinstance(item.get("contratante"), dict) else {}

    return {
        "id": item.get("id"),
        "contrato_ano": item.get("contrato_ano"),
        "contrato_numero": item.get("contrato_numero"),
        "numero": item.get("numero"),
        "data_assinatura": item.get("data_assinatura"),
        "data_vigencia_inicio": item.get("data_vigencia_inicio"),
        "data_vigencia_fim": item.get("data_vigencia_fim"),
        "publicacao": item.get("publicacao"),
        "objeto": item.get("objeto"),
        "observacao": item.get("observacao"),
        "numero_processo": item.get("numero_processo"),
        "modelo": item.get("modelo"),
        "categoria": item.get("categoria"),
        "situacao": item.get("situacao"),
        "valor_total": valor.get("brl") or valor.get("formatted") or valor.get("value"),
        "valor_executado": valor_executado.get("brl") or valor_executado.get("formatted") or valor_executado.get("value"),
        "contratante_sigla": contratante.get("sigla"),
        "contratante_nome": contratante.get("nome"),
        "fornecedor_nome": fornecedor.get("nome"),
        "fornecedor_razao_social": fornecedor.get("razao_social"),
        "fornecedor_documento": fornecedor.get("documento"),
        "fornecedor_url": fornecedor.get("url"),
        "fonte_api": f"{API_URL}/{item.get('id')}",
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    try:
        first_page = fetch_json(session, 1)
        meta = first_page.get("meta") if isinstance(first_page.get("meta"), dict) else {}
        last_page = int(meta.get("last_page") or 1)

        all_rows: list[dict[str, object]] = []
        all_rows.extend(first_page.get("data") if isinstance(first_page.get("data"), list) else [])

        for page in range(2, last_page + 1):
            payload = fetch_json(session, page)
            page_rows = payload.get("data") if isinstance(payload.get("data"), list) else []
            all_rows.extend(page_rows)
    finally:
        session.close()

    selected_rows = [
        row
        for row in all_rows
        if isinstance(row, dict) and normalize_modelo(row.get("modelo")) in MODELOS_PARCERIA
    ]
    flattened = [flatten_record(row) for row in selected_rows]

    summary = {
        "total_api": len(all_rows),
        "total_parcerias": len(flattened),
        "modelos": dict(sorted(Counter(normalize_text(row.get("modelo")) for row in selected_rows).items())),
        "anos": dict(sorted(Counter(str(row.get("contrato_ano")) for row in selected_rows if row.get("contrato_ano")).items())),
        "com_cnpj": sum(1 for row in flattened if normalize_text(row.get("fornecedor_documento"))),
        "fonte_api": API_URL,
        "fonte_portal": "https://transparencia.portovelho.ro.gov.br/contratos?modelo_nome=7",
    }

    write_json(output_dir / "portovelho_convenios_api_filtrado.json", flattened)
    write_json(output_dir / "portovelho_convenios_api_resumo.json", summary)

    print(
        f"Porto Velho: api={summary['total_api']} parcerias={summary['total_parcerias']} "
        f"com_cnpj={summary['com_cnpj']}"
    )


if __name__ == "__main__":
    main()
