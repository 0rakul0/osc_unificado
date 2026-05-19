from __future__ import annotations

import argparse
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


DOWNLOAD_URL = "https://tfe.fazenda.rj.gov.br/tfe-download/despesa.zip"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa a base completa de despesas do RJ no TFE/Fazenda.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "RJ"),
        help="Pasta onde o ZIP bruto do RJ sera salvo.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "despesa.zip"

    with requests.get(DOWNLOAD_URL, timeout=300, stream=True, headers={"User-Agent": "Mozilla/5.0"}) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    handle.write(chunk)

    print(f"Fonte oficial: {DOWNLOAD_URL}")
    print(f"Saida: {output_path}")
    print(f"Bytes: {output_path.stat().st_size}")


if __name__ == "__main__":
    main()
