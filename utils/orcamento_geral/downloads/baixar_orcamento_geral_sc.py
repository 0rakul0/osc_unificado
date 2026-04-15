from __future__ import annotations

import argparse
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


CSV_URL = "https://sctransf-api.prod.okd4.ciasc.sc.gov.br/csv/transferencias"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa a base oficial de transferencias do SC Transferencias."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "SC"),
        help="Pasta de saida para os arquivos brutos do estado.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(CSV_URL, timeout=300)
    response.raise_for_status()

    output_path = output_dir / "sc_transferencias.csv"
    output_path.write_bytes(response.content)

    print(f"Entrada oficial: {CSV_URL}")
    print(f"Saida: {output_path}")
    print(f"Bytes: {len(response.content)}")


if __name__ == "__main__":
    main()
