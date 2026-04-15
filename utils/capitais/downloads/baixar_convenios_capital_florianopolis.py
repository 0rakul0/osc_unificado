from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


LIST_URL = "https://transparencia.e-publica.net/epublica-portal/rest/florianopolis/despesa/convenioRepassado/listAll"
DETAIL_URL = "https://transparencia.e-publica.net/epublica-portal/rest/florianopolis/despesa/convenioRepassado/form"
PORTAL_URL = "https://transparencia.e-publica.net/epublica-portal/#/florianopolis/portal/despesa/convenioRepassadoTable?entidade=2002"
DEFAULT_PARAMS = {"ano": "2026", "entidade": "2002"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os convenios repassados da capital Florianopolis pela API oficial do e-publica."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Florianopolis"),
        help="Pasta onde os JSONs consolidados da capital serao salvos.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def flatten_participants(participants: object) -> dict[str, object]:
    result: dict[str, object] = {}
    if not isinstance(participants, list):
        return result
    for item in participants:
        if not isinstance(item, dict):
            continue
        tipo = normalize_text(item.get("tipo")).lower()
        prefix = "recebedor" if "recebedor" in tipo else "repassador" if "repassador" in tipo else None
        if prefix is None:
            continue
        result[f"{prefix}_nome"] = item.get("nome")
        result[f"{prefix}_cnpj"] = item.get("cpfCnpj")
    return result


def fetch_rows(session: requests.Session) -> list[dict[str, object]]:
    response = session.get(LIST_URL, params=DEFAULT_PARAMS, timeout=120)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("rows") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise ValueError("Resposta inesperada na listagem de Florianopolis.")
    return rows


def fetch_detail(session: requests.Session, identifier: object) -> dict[str, object]:
    response = session.post(DETAIL_URL, params=DEFAULT_PARAMS, json={"id": identifier, "mode": "INFO"}, timeout=120)
    response.raise_for_status()
    payload = response.json()
    pojo = payload.get("pojo") if isinstance(payload, dict) else None
    if not isinstance(pojo, dict):
        raise ValueError(f"Detalhe inesperado para convenio id={identifier}")
    return pojo


def flatten_detail(item: dict[str, object]) -> dict[str, object]:
    row = {
        "id": item.get("id"),
        "numero": item.get("numero"),
        "tipo": item.get("tipo"),
        "objetoResumido": item.get("objetoResumido"),
        "assinatura": item.get("assinatura"),
        "inicioVigencia": item.get("inicioVigencia"),
        "vencimento": item.get("vencimento"),
        "publicacao": item.get("publicacao"),
        "valorTotal": item.get("valorTotal"),
        "valorConvenente": item.get("valorConvenente"),
        "valorPagoTotal": item.get("valorPagoTotal"),
        "valorEmpenhadoTotal": item.get("valorEmpenhadoTotal"),
        "fonte_portal": PORTAL_URL,
        "fonte_api": DETAIL_URL,
    }
    row.update(flatten_participants(item.get("participantes")))
    return row


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    try:
        rows = fetch_rows(session)
        detailed = [flatten_detail(fetch_detail(session, row.get("id"))) for row in rows if isinstance(row, dict)]
    finally:
        session.close()

    summary = {
        "total_lista": len(rows),
        "total_enriquecido": len(detailed),
        "com_cnpj": sum(1 for item in detailed if normalize_text(item.get("recebedor_cnpj"))),
        "fonte_portal": PORTAL_URL,
        "fonte_api_lista": LIST_URL,
        "fonte_api_detalhe": DETAIL_URL,
    }

    write_json(output_dir / "florianopolis_convenios_lista.json", rows)
    write_json(output_dir / "florianopolis_convenios_enriquecido.json", detailed)
    write_json(output_dir / "florianopolis_convenios_resumo.json", summary)

    print(
        f"Florianopolis: lista={summary['total_lista']} enriquecido={summary['total_enriquecido']} "
        f"com_cnpj={summary['com_cnpj']}"
    )


if __name__ == "__main__":
    main()
