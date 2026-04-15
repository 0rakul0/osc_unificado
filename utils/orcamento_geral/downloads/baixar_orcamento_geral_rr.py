from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://api.transparencia.rr.gov.br/api/v1/portal/transparencia/visualizar-despesa-detalhada"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa a despesa detalhada da API oficial de RR."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "RR"),
        help="Pasta de saida para os arquivos brutos do estado.",
    )
    return parser.parse_args()


def normalize_groups(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [item for item in payload.values() if isinstance(item, dict)]
    return []


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    first_response = requests.get(API_URL, params={"page": 1}, timeout=180, verify=False)
    first_response.raise_for_status()
    first_payload = first_response.json()["data"]
    last_page = int(first_payload.get("last_page") or 1)

    rows: list[dict[str, object]] = []
    for page in range(1, last_page + 1):
        response = requests.get(API_URL, params={"page": page}, timeout=180, verify=False)
        response.raise_for_status()
        payload = response.json()["data"]
        for group in normalize_groups(payload.get("data")):
            unidade = group.get("indice")
            for item in group.get("dados") or []:
                if not isinstance(item, dict):
                    continue
                item["indice_grupo"] = unidade
                item["pagina_origem"] = page
                rows.append(item)

    output_path = output_dir / "rr_despesa_detalhada.json"
    output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Entrada oficial: {API_URL}")
    print(f"Saida: {output_path}")
    print(f"Linhas consolidadas: {len(rows)}")


if __name__ == "__main__":
    main()
