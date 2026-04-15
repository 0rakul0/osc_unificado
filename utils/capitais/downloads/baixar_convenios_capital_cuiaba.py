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


BASE_URL = "http://transparencia.cuiaba.mt.gov.br/portaltransparencia/servlet/a"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa convênios da capital Cuiabá em JSON bruto.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Cuiaba"),
        help="Diretório de saída para os JSONs brutos.",
    )
    return parser.parse_args()


def fetch_json(endpoint: str) -> object:
    response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=60)
    response.raise_for_status()
    return response.json()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)

    convenios = fetch_json("apiconveniorecebido")
    filtros = fetch_json("apifilterconveniorecebido")

    write_json(output_dir / "cuiaba_convenio_recebido.json", convenios)
    write_json(output_dir / "cuiaba_filter_convenio_recebido.json", filtros)

    print(f"Convênios baixados: {len(convenios) if isinstance(convenios, list) else 'n/a'}")
    print(f"Diretório: {output_dir}")


if __name__ == "__main__":
    main()
