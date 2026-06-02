from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import CAPITAIS_PROCESSADA_DIR
from utils.convenios.unificador import build_parquet_table


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

        frames: list[pd.DataFrame] = []
        if standard_path.exists():
            frames.append(pd.read_parquet(standard_path))
        frames.append(pd.read_parquet(expenses_path))

        columns = list(frames[-1].columns)
        combined = pd.concat(frames, ignore_index=True, sort=False).reindex(columns=columns)
        combined["modalidade"] = combined["modalidade"].where(
            combined["modalidade"].isin(["despesa", "Despesa por credor", "Despesa paga por favorecido", "Empenho"]),
            "convenio",
        )
        combined.loc[combined["modalidade"] != "convenio", "modalidade"] = "despesa"
        combined = combined.drop_duplicates(ignore_index=True)
        pq.write_table(build_parquet_table(combined), standard_path, compression="snappy")
        expenses_path.unlink()
        print(f"{standard_name}: consolidado em {standard_path.name}, removido {expenses_path.name}, linhas={len(combined)}")


if __name__ == "__main__":
    main()
