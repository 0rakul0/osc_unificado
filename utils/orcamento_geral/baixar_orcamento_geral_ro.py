from __future__ import annotations

import argparse
from html import unescape
from pathlib import Path
import re
import sys

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


FILTER_URL = "https://transparencia.ro.gov.br/convenios/filtrartransferencias"
YEARS = ("2020", "2021", "2022", "2023")
ROW_PATTERN = re.compile(r'<tr class="text-center"(?P<attrs>.*?)</tr>', re.IGNORECASE | re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa as transferencias realizadas do portal oficial de RO."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "RO"),
        help="Pasta de saida para os arquivos brutos do estado.",
    )
    return parser.parse_args()


def extract_attr(attrs: str, name: str) -> str:
    match = re.search(fr'data-{name}="(.*?)"', attrs, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return " ".join(unescape(match.group(1)).split())


def fetch_year(year: str) -> list[dict[str, str]]:
    response = requests.post(
        FILTER_URL,
        data={"Exercicio": year, "Beneficiario": "", "Instrumento": ""},
        timeout=120,
    )
    response.raise_for_status()

    rows: list[dict[str, str]] = []
    for match in ROW_PATTERN.finditer(response.text):
        attrs = match.group("attrs")
        beneficiario = extract_attr(attrs, "beneficiario")
        if not beneficiario:
            continue
        rows.append(
            {
                "ano_consulta": year,
                "beneficiario": beneficiario,
                "numero_instrumento": extract_attr(attrs, "convenio"),
                "valor_total_previsto": extract_attr(attrs, "total-repasse"),
                "objeto": extract_attr(attrs, "objeto"),
                "valor_repassado_data": extract_attr(attrs, "valor-repassado"),
                "vigencia": extract_attr(attrs, "vigencia"),
                "detalhe_relativo": extract_attr(attrs, "link"),
                "fonte_url": FILTER_URL,
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for year in YEARS:
        rows.extend(fetch_year(year))

    output_path = output_dir / "ro_transferencias_realizadas.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Entrada oficial: {FILTER_URL}")
    print(f"Saida: {output_path}")
    print(f"Linhas consolidadas: {len(rows)}")


if __name__ == "__main__":
    main()
