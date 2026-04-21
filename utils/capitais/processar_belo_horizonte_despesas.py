from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, HISTORIA_DATA_DIR, ensure_parent_dir
from utils.capitais.parsers.belohorizonte_despesas import CONFIG
from utils.capitais.shared import write_capital_parquet


OUTPUT_DIR = HISTORIA_DATA_DIR / "parquets_teste_capitais"
SOURCE_FILENAMES = [
    "transparencia_despesas_2018.csv",
    "transparencia_despesas_2019.csv",
    "transparencia_despesas_2020.csv",
    "transparencia_despesas_2021.csv",
    "transparencia_despesas_2022.csv",
    "transparencia_despesas_2023.csv",
]


def main() -> None:
    base_dir = BASES_CONVENIOS_CAPITAIS_DIR
    output_dir = OUTPUT_DIR
    ensure_parent_dir(output_dir / "placeholder.txt")

    city_dir = base_dir / CONFIG.folder
    source_paths = [city_dir / filename for filename in SOURCE_FILENAMES if (city_dir / filename).exists()]
    if not source_paths:
        raise FileNotFoundError(
            f"Nenhum CSV de transparencia encontrado em {city_dir}"
        )

    print("Arquivos considerados:")
    for path in source_paths:
        print(f"- {path.name}")

    output_path, source_rows, parquet_rows = write_capital_parquet(CONFIG, source_paths, output_dir, batch_size=20000)
    print(f"Parquet gerado em: {output_path}")
    print(f"Linhas de origem lidas: {source_rows}")
    print(f"Linhas no parquet final: {parquet_rows}")


if __name__ == "__main__":
    main()
