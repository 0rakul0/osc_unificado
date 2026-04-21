from __future__ import annotations

import json
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, ensure_parent_dir


BASE_URL = "https://transparencia.pmbv.rr.gov.br/transparencia/VersaoJson/Despesas/"
OUTPUT_DIR = BASES_CONVENIOS_CAPITAIS_DIR / "Boa Vista"
YEARS = list(range(2016, 2027))
ENTITY_CODE = "1"


def build_params(year: int) -> dict[str, str]:
    return {
        "ConectarExercicio": str(year),
        "Listagem": "DespesasGerais",
        "DiaInicioPeriodo": "01",
        "MesInicialPeriodo": "01",
        "DiaFinalPeriodo": "31",
        "MesFinalPeriodo": "12",
        "Ano": str(year),
        "Empresa": ENTITY_CODE,
        "MostrarFornecedor": "True",
        "MostraDadosConsolidado": "False",
        "UFParaFiltroCOVID": "",
        "MostrarCNPJFornecedor": "True",
        "ApenasIDEmpenho": "False",
    }


def main() -> None:
    ensure_parent_dir(OUTPUT_DIR / "placeholder.txt")
    session = requests.Session()

    for year in YEARS:
        response = session.get(BASE_URL, params=build_params(year), timeout=300)
        response.raise_for_status()
        payload = response.json()
        output_path = OUTPUT_DIR / f"boavista_despesas_gerais_{year}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"{year}: {len(payload)} registros -> {output_path}")


if __name__ == "__main__":
    main()
