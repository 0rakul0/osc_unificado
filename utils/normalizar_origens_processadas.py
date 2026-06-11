from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import CAPITAIS_PROCESSADA_DIR, ORCAMENTO_GERAL_PROCESSADA_DIR, PROCESSADA_DIR
from utils.convenios.unificador import build_parquet_table


ORIGEM_MAP = {
    "convenios": "ESTADO_CONVENIOS",
    "convenios_federal": "ESTADO_CONVENIOS",
    "orcamento_geral": "ESTADO_ORCAMENTO_GERAL",
    "capitais_conv": "CAPITAIS_CONVENIOS",
    "capitais_og": "CAPITAIS_ORCAMENTO_GERAL",
}

ALLOWED_ORIGENS = {
    "ESTADO_CONVENIOS",
    "ESTADO_ORCAMENTO_GERAL",
    "CAPITAIS_CONVENIOS",
    "CAPITAIS_ORCAMENTO_GERAL",
}

PROCESSADA_DIRS = (
    PROCESSADA_DIR,
    ORCAMENTO_GERAL_PROCESSADA_DIR,
    CAPITAIS_PROCESSADA_DIR,
)


def normalize_parquet(path: Path) -> tuple[bool, list[str]]:
    frame = pd.read_parquet(path)
    if "origem" not in frame.columns:
        return False, ["sem_coluna_origem"]

    before = sorted(str(value) for value in frame["origem"].dropna().unique())
    frame["origem"] = frame["origem"].replace(ORIGEM_MAP)
    after = sorted(str(value) for value in frame["origem"].dropna().unique())
    unexpected = sorted(set(after) - ALLOWED_ORIGENS)
    if unexpected:
        return False, [f"origem_inesperada={unexpected}"]

    if before != after:
        temp_path = path.with_suffix(".rewrite.tmp.parquet")
        pq.write_table(build_parquet_table(frame), temp_path, compression="snappy")
        temp_path.replace(path)
        return True, after

    return False, after


def main() -> None:
    changed = 0
    errors: list[str] = []
    for directory in PROCESSADA_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.parquet")):
            if path.name.endswith((".tmp.parquet", ".partial.parquet")):
                continue
            try:
                was_changed, details = normalize_parquet(path)
            except Exception as exc:
                errors.append(f"{path}: {type(exc).__name__}: {exc}")
                continue
            if was_changed:
                changed += 1
                print(f"normalizado: {path} -> {details}")

    if errors:
        for error in errors:
            print(f"ERRO: {error}")
        raise SystemExit(1)

    print(f"Normalizacao concluida. Arquivos alterados: {changed}")


if __name__ == "__main__":
    main()
