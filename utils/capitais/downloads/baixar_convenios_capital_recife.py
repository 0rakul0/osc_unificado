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

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://dados.recife.pe.gov.br"
RESOURCES = {
    "recife_contratos_gestao_2023.csv": (
        "/dataset/a5cb6098-2aa8-4672-b916-fb4c8055b673/resource/"
        "e016ea66-8bd1-4aec-bda1-afafa56017ed/download/contratos-de-gestao-2023.csv"
    ),
    "recife_aditivos_contratos_gestao_2023.csv": (
        "/dataset/a5cb6098-2aa8-4672-b916-fb4c8055b673/resource/"
        "4ff1b9c9-2575-4be6-a615-e7097df14c8d/download/aditivo-dos-contratos-de-gestao-2023.csv"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os datasets oficiais de contratos de gestao do Recife."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Recife"),
        help="Pasta de saida para os arquivos brutos consolidados da capital.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    manifest: list[dict[str, object]] = []
    for filename, resource_path in RESOURCES.items():
        response = session.get(f"{BASE_URL}{resource_path}", timeout=120, verify=False)
        response.raise_for_status()
        target_path = output_dir / filename
        target_path.write_bytes(response.content)
        manifest.append(
            {
                "arquivo": filename,
                "url": f"{BASE_URL}{resource_path}",
                "bytes": len(response.content),
            }
        )
        print(f"Arquivo salvo: {target_path}")

    manifest_path = output_dir / "recife_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest salvo: {manifest_path}")


if __name__ == "__main__":
    main()
