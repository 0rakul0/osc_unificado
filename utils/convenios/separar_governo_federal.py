from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_DIR, GOVERNO_FEDERAL_DIR, cli_default
from utils.convenios.enriquecer_processada_governo import normalize_enriched_output
from utils.convenios.unificador import build_parquet_table
from utils.gov_convenios import build_gov_convenios_parser


ALL_UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
    "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
    "SE", "SP", "TO",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Separa a base federal em um parquet por UF, usando o mesmo schema consolidado."
    )
    parser.add_argument("--base-dir", default=cli_default(BASES_CONVENIOS_DIR))
    parser.add_argument("--gov-file", default="governo/20260227_Convenios.csv")
    parser.add_argument("--output-dir", default=cli_default(GOVERNO_FEDERAL_DIR))
    parser.add_argument("--ufs", nargs="*", help="Lista opcional de UFs para exportar.")
    return parser.parse_args()


def export_uf(uf: str, gov_path: Path, output_dir: Path) -> dict[str, object]:
    frame = build_gov_convenios_parser(uf).parse_workbook(gov_path)
    normalized = normalize_enriched_output(frame, uf)

    output_path = output_dir / f"{uf.upper()}.parquet"
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")
    return {
        "uf": uf.upper(),
        "rows": len(normalized),
        "output": output_path,
    }


def main() -> None:
    args = parse_args()
    base_dir = Path(args.base_dir)
    gov_path = base_dir / args.gov_file
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.ufs:
        target_ufs = sorted({uf.upper() for uf in args.ufs})
    else:
        target_ufs = ALL_UFS

    results = [export_uf(uf, gov_path, output_dir) for uf in target_ufs]
    for result in results:
        print(f"{result['uf']}: linhas={result['rows']} saida={result['output']}")


if __name__ == "__main__":
    main()
