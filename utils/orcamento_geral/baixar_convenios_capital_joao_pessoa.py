from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys

import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://transparencia.joaopessoa.pb.gov.br:8080"
LIST_URL = f"{BASE_URL}/convenios/municipais"
DETAIL_URL = f"{BASE_URL}/convenio/municipal/{{id}}"
CONVENENTES_URL = f"{BASE_URL}/convenios/municipais/convenentes"
DEFAULT_WORKERS = 12


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os convênios municipais oficiais da capital João Pessoa via API do portal."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Joao Pessoa"),
        help="Pasta onde os JSONs oficiais serão salvos.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Quantidade de requisições paralelas para buscar detalhes.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.verify = False
    return session


def fetch_json(session: requests.Session, url: str, params: dict[str, object] | None = None) -> object:
    response = session.get(url, params=params, timeout=120)
    response.raise_for_status()
    return response.json()


def fetch_detail(convenio_id: int) -> dict[str, object]:
    session = build_session()
    try:
        payload = fetch_json(session, DETAIL_URL.format(id=convenio_id))
        if not isinstance(payload, dict):
            raise ValueError(f"Detalhe inesperado para id={convenio_id}: {type(payload).__name__}")
        return payload
    finally:
        session.close()


def normalize_convenio(
    item: dict[str, object],
    detail: dict[str, object] | None,
    convenentes_by_id: dict[int, dict[str, object]],
) -> dict[str, object]:
    detail = detail or {}
    convenente = detail.get("convenente") if isinstance(detail.get("convenente"), dict) else {}
    concedente = detail.get("concedente") if isinstance(detail.get("concedente"), dict) else {}
    tipo = detail.get("tipo") if isinstance(detail.get("tipo"), dict) else {}

    convenente_id = convenente.get("id")
    convenente_lookup = convenentes_by_id.get(int(convenente_id)) if isinstance(convenente_id, int) else {}

    convenente_nome = convenente_lookup.get("nome") or item.get("nome") or convenente.get("nome")
    convenente_cnpj = convenente_lookup.get("cpf_cnpj")

    return {
        "id": item.get("id"),
        "numero": detail.get("numero") or item.get("numero"),
        "tipo": tipo.get("tipo") or item.get("tipo"),
        "concedente": concedente.get("nome") or item.get("concedente"),
        "convenente_id": convenente_id,
        "convenente_nome": convenente_nome,
        "convenente_cnpj": convenente_cnpj,
        "objeto": detail.get("objeto") or item.get("objeto"),
        "inicio_vigencia": detail.get("inicio_vigencia") or item.get("inicio_vigencia"),
        "fim_vigencia": detail.get("fim_vigencia") or item.get("fim_vigencia"),
        "data_publicacao": detail.get("data_publicacao") or item.get("data_publicacao"),
        "data_celebracao": detail.get("data_celebracao") or item.get("data_celebracao"),
        "valor_pactuado": detail.get("valor_pactuado") if detail else item.get("valor_pactuado"),
        "valor_contrapartida": detail.get("valor_contrapartida") if detail else item.get("valor_contrapartida"),
        "files_details": detail.get("files_details", []),
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    try:
        convenios = fetch_json(session, LIST_URL)
        convenentes = fetch_json(session, CONVENENTES_URL)
    finally:
        session.close()

    if not isinstance(convenios, list):
        raise ValueError(f"Resposta inesperada em {LIST_URL}: {type(convenios).__name__}")
    if not isinstance(convenentes, list):
        raise ValueError(f"Resposta inesperada em {CONVENENTES_URL}: {type(convenentes).__name__}")

    convenentes_by_id: dict[int, dict[str, object]] = {}
    for item in convenentes:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if isinstance(item_id, int):
            convenentes_by_id[item_id] = item

    details_by_id: dict[int, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {
            executor.submit(fetch_detail, int(item["id"])): int(item["id"])
            for item in convenios
            if isinstance(item, dict) and isinstance(item.get("id"), int)
        }
        for future in as_completed(future_map):
            convenio_id = future_map[future]
            details_by_id[convenio_id] = future.result()

    enriched = [
        normalize_convenio(item, details_by_id.get(int(item["id"])) if isinstance(item.get("id"), int) else None, convenentes_by_id)
        for item in convenios
        if isinstance(item, dict)
    ]

    summary = {
        "total_lista": len(convenios),
        "total_detalhes": len(details_by_id),
        "total_enriquecidos": len(enriched),
        "com_cnpj": sum(1 for item in enriched if str(item.get("convenente_cnpj", "")).strip()),
        "anos": sorted(
            {
                str(item.get("data_publicacao", ""))[:4]
                for item in enriched
                if str(item.get("data_publicacao", "")).strip()
            }
        ),
        "tipos": sorted({str(item.get("tipo", "")).strip() for item in enriched if str(item.get("tipo", "")).strip()}),
        "fonte_lista": LIST_URL,
        "fonte_detalhe": DETAIL_URL.format(id="{id}"),
    }

    write_json(output_dir / "joaopessoa_convenios_api_lista.json", convenios)
    write_json(output_dir / "joaopessoa_convenios_api_convenentes.json", convenentes)
    write_json(output_dir / "joaopessoa_convenios_api_detalhes.json", list(details_by_id.values()))
    write_json(output_dir / "joaopessoa_convenios_api_enriquecido.json", enriched)
    write_json(output_dir / "joaopessoa_convenios_resumo.json", summary)

    print(
        f"João Pessoa: lista={summary['total_lista']} detalhes={summary['total_detalhes']} "
        f"enriquecidos={summary['total_enriquecidos']} com_cnpj={summary['com_cnpj']}"
    )


if __name__ == "__main__":
    main()
