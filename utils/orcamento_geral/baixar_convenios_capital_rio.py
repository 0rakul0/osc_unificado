from __future__ import annotations

import argparse
import json
import re
from io import StringIO
from pathlib import Path
import sys

import pandas as pd
import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPECIES = [
    "Termo de Colaboracao",
    "Termo de Fomento",
    "Convenio",
    "Acordo de Cooperacao",
    "Contrato de Gestao",
]
BASE_URL = "https://riotransparente.rio.rj.gov.br/web/index.asp"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os contratos e outros termos do Rio com foco em convenios/OSC."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Rio de Janeiro"),
        help="Pasta de saida para os arquivos brutos consolidados da capital.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout em segundos para cada requisicao HTTP.",
    )
    return parser.parse_args()


def extract_total_pages(html_text: str) -> int:
    match = re.search(r"P(?:&aacute;|á)gina <b>\d+</b> de <b>(\d+)</b>", html_text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 1


def fetch_species_frame(session: requests.Session, especie: str, timeout: int) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    first_response = session.get(
        BASE_URL,
        params={
            "cmd": "contratosEspecie",
            "especie": especie,
            "exercicio": "TODOS",
            "favorecidoPesquisado": "",
            "CNPJPesquisado": "",
            "inicioCursor": "0",
            "PagAtual": "1",
            "ordena": "",
            "situacao": "",
        },
        timeout=timeout,
        verify=False,
    )
    total_pages = extract_total_pages(first_response.text)

    for page_number in range(1, total_pages + 1):
        response = (
            first_response
            if page_number == 1
            else session.get(
                BASE_URL,
                params={
                    "cmd": "contratosEspecie",
                    "especie": especie,
                    "exercicio": "TODOS",
                    "favorecidoPesquisado": "",
                    "CNPJPesquisado": "",
                    "inicioCursor": str((page_number - 1) * 20),
                    "PagAtual": str(page_number),
                    "ordena": "",
                    "situacao": "",
                },
                timeout=timeout,
                verify=False,
            )
        )
        tables = pd.read_html(StringIO(response.text))
        if not tables:
            continue
        frame = tables[0].copy()
        frame["EspecieConsulta"] = especie
        frame["PaginaConsulta"] = str(page_number)
        frames.append(frame)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    frames: list[pd.DataFrame] = []
    manifest: list[dict[str, object]] = []

    for especie in SPECIES:
        frame = fetch_species_frame(session, especie, args.timeout)
        if frame.empty:
            manifest.append({"especie": especie, "rows": 0, "pages": 0})
            continue
        frames.append(frame)
        manifest.append(
            {
                "especie": especie,
                "rows": int(len(frame)),
                "pages": int(frame["PaginaConsulta"].astype(int).max()),
            }
        )
        print(f"{especie}: {len(frame)} linhas")

    consolidated = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    csv_path = output_dir / "rio_contratos_especies.csv"
    manifest_path = output_dir / "rio_contratos_especies_manifest.json"

    consolidated.to_csv(csv_path, index=False, encoding="utf-8-sig")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saida CSV: {csv_path}")
    print(f"Saida manifest: {manifest_path}")
    print(f"Linhas consolidadas: {len(consolidated)}")


if __name__ == "__main__":
    main()
