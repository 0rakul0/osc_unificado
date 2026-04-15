from __future__ import annotations

import argparse
from pathlib import Path
import sys

import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings()
BASE_URL = "https://wstransparencia.vitoria.es.gov.br"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os CSVs de convenios da capital Vitoria via API oficial."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Vitoria"),
        help="Diretorio onde os CSVs serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        help="Lista opcional de anos a baixar.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebaixa arquivos existentes.",
    )
    return parser.parse_args()


def get_json(url: str) -> object:
    response = requests.get(url, timeout=60, verify=False, headers={"User-Agent": "osc_unificado/vitoria-capital"})
    response.raise_for_status()
    return response.json()


def iter_valid_pairs(years_filter: set[int] | None) -> list[tuple[int, int, str]]:
    ugs = get_json(f"{BASE_URL}/api/secretariasEmUso")
    years = [int(item["Valor"]) for item in get_json(f"{BASE_URL}/api/convenios/anos")]
    if years_filter:
        years = [year for year in years if year in years_filter]

    pairs: list[tuple[int, int, str]] = []
    for ug in ugs:
        ug_id = int(ug["Id"])
        ug_name = str(ug["Nome"])
        for year in years:
            url = f"{BASE_URL}/api/convenios/secretaria?unidadeGestoraId={ug_id}&exercicio={year}"
            response = requests.get(url, timeout=60, verify=False, headers={"User-Agent": "osc_unificado/vitoria-capital"})
            if response.status_code != 200:
                continue
            text = response.text.strip()
            if text in {"[]", "[ ]"}:
                continue
            pairs.append((ug_id, year, ug_name))
    return pairs


def download_csv(ug_id: int, year: int, output_dir: Path, force: bool) -> tuple[Path, int]:
    output_path = output_dir / f"vitoria_convenios_ug{ug_id}_{year}.csv"
    if output_path.exists() and not force:
        return output_path, output_path.stat().st_size

    url = f"{BASE_URL}/api/convenios/csv?unidadeGestoraId={ug_id}&exercicio={year}"
    response = requests.get(url, timeout=120, verify=False, headers={"User-Agent": "osc_unificado/vitoria-capital"})
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path, len(response.content)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    years_filter = set(args.years or [])

    pairs = iter_valid_pairs(years_filter or None)
    print(f"Pares validos encontrados: {len(pairs)}")
    for ug_id, year, ug_name in pairs:
        path, size = download_csv(ug_id, year, output_dir, args.force)
        print(f"{year} | UG {ug_id} | {ug_name} -> {path.name} ({size} bytes)")


if __name__ == "__main__":
    main()
