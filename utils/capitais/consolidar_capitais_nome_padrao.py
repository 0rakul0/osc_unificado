from __future__ import annotations

from pathlib import Path
import sys

import polars as pl

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import CAPITAIS_PROCESSADA_DIR


CAPITAIS_COM_DESPESAS = {
    "MT_CUIABA": "MT_CUIABA_DESPESAS",
    "GO_GOIANIA": "GO_GOIANIA_DESPESAS",
    "SE_ARACAJU": "SE_ARACAJU_DESPESAS",
    "PR_CURITIBA": "PR_CURITIBA_DESPESAS",
    "RS_PORTO_ALEGRE": "RS_PORTO_ALEGRE_DESPESAS",
}


def main() -> None:
    for standard_name, expenses_name in CAPITAIS_COM_DESPESAS.items():
        standard_path = CAPITAIS_PROCESSADA_DIR / f"{standard_name}.parquet"
        expenses_path = CAPITAIS_PROCESSADA_DIR / f"{expenses_name}.parquet"
        if not expenses_path.exists():
            print(f"{standard_name}: sem parquet extra de despesas")
            continue

        frames = []
        if standard_path.exists():
            frames.append(pl.read_parquet(standard_path))
        frames.append(pl.read_parquet(expenses_path))

        columns = pl.read_parquet(expenses_path).columns
        combined = pl.concat(frames, how="diagonal_relaxed").select(columns)
        combined = combined.with_columns(
            pl.when(pl.col("modalidade").is_in(["Despesa por credor", "Despesa paga por favorecido", "Empenho"]))
            .then(pl.lit("despesa"))
            .otherwise(pl.lit("convenio"))
            .alias("modalidade")
        )
        combined = combined.unique(maintain_order=True)
        combined.write_parquet(standard_path)
        expenses_path.unlink()
        print(f"{standard_name}: consolidado em {standard_path.name}, removido {expenses_path.name}, linhas={combined.height}")


if __name__ == "__main__":
    main()
