from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import (
    BASES_CONVENIOS_CAPITAIS_DIR,
    BASES_CONVENIOS_DIR,
    BASES_ORCAMENTO_GERAL_CAPITAIS_DIR,
    BASES_ORCAMENTO_GERAL_DIR,
    CAPITAIS_PROCESSADA_DIR,
    HISTORIA_DATA_DIR,
    ORCAMENTO_GERAL_PROCESSADA_DIR,
    PROCESSADA_DIR,
    cli_default,
    ensure_parent_dir,
)
from utils.common import STANDARD_COLUMNS
from utils.orcamento_geral.registry import STATE_CAPITALS, StateCapital, ascii_slug, capital_parquet_name


OSC_KEYWORDS = (
    "ASSOCIAC",
    "INSTITUT",
    "FUNDAC",
    "FEDERAC",
    "CONFEDERAC",
    "SINDICATO",
    "OSCIP",
    "ONG",
    "APAE",
    "PESTALOZZI",
    "PAROQUIA",
    "IGREJA",
    "IRMANDADE",
    "CENTRO SOCIAL",
    "CASA DE",
    "LAR DOS",
    "SOCIEDADE BENEFICENTE",
    "ORGANIZACAO SOCIAL",
    "ORGANIZACAO DA SOCIEDADE CIVIL",
)
OSC_PATTERN = re.compile("|".join(OSC_KEYWORDS), re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um tracker local de estados e capitais com foco em OSC."
    )
    parser.add_argument(
        "--output",
        default=cli_default(HISTORIA_DATA_DIR / "tracker_estado_capital_osc.csv"),
        help="CSV de saida com o status consolidado.",
    )
    return parser.parse_args()


def has_files(path: Path) -> bool:
    return path.exists() and any(item.is_file() for item in path.rglob("*"))


def candidate_dirs(root: Path, item: StateCapital, include_uf: bool = True) -> list[Path]:
    candidates: list[Path] = []
    names = {item.capital, ascii_slug(item.capital), ascii_slug(item.capital).replace("-", " "), item.capital.upper()}
    if include_uf:
        names.add(item.uf)
    for name in names:
        candidates.append(root / name)
    # preserva ordem sem repetir
    seen: set[str] = set()
    ordered: list[Path] = []
    for path in candidates:
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)
    return ordered


def first_existing_dir(root: Path, item: StateCapital, include_uf: bool = True) -> Path | None:
    for path in candidate_dirs(root, item, include_uf=include_uf):
        if path.exists():
            return path
    return None


def parquet_summary(path: Path) -> dict[str, object]:
    parquet = pq.ParquetFile(path)
    total_rows = 0
    cnpj_valid_rows = 0
    osc_name_rows = 0
    osc_name_cnpj_rows = 0

    read_columns = [column for column in ("cnpj", "nome_osc") if column in parquet.schema_arrow.names]
    if not read_columns:
        return {
            "rows": parquet.metadata.num_rows,
            "cnpj_valid_rows": 0,
            "osc_name_rows": 0,
            "osc_name_cnpj_rows": 0,
            "osc_signal": "nao_avaliado",
        }

    for row_group in range(parquet.metadata.num_row_groups):
        frame = parquet.read_row_group(row_group, columns=read_columns).to_pandas()
        total_rows += len(frame)
        cnpj = frame.get("cnpj", pd.Series(dtype="string")).astype("string").str.replace(r"\D", "", regex=True)
        nome = frame.get("nome_osc", pd.Series(dtype="string")).astype("string")
        valid_cnpj = cnpj.str.len().eq(14)
        osc_name = nome.str.upper().str.contains(OSC_PATTERN, na=False)
        cnpj_valid_rows += int(valid_cnpj.sum())
        osc_name_rows += int(osc_name.sum())
        osc_name_cnpj_rows += int((valid_cnpj & osc_name).sum())

    signal = "sem_sinal_osc"
    if osc_name_cnpj_rows > 0:
        signal = "sinal_osc_forte"
    elif osc_name_rows > 0:
        signal = "sinal_osc_por_nome"
    elif cnpj_valid_rows > 0:
        signal = "cnpj_sem_sinal_de_nome"

    return {
        "rows": total_rows,
        "cnpj_valid_rows": cnpj_valid_rows,
        "osc_name_rows": osc_name_rows,
        "osc_name_cnpj_rows": osc_name_cnpj_rows,
        "osc_signal": signal,
    }


def next_action(row: dict[str, object]) -> str:
    if not row["orcamento_estado_parquet"]:
        return "fechar_orcamento_geral_estado"
    if not row["capital_convenios_bruto"]:
        return "buscar_convenios_capital"
    if not row["capital_parquet"]:
        return "processar_capital"
    if row["capital_osc_signal"] in {"sem_sinal_osc", "nao_avaliado"}:
        return "revisar_heuristica_osc_capital"
    return "seguir_para_proxima_uf"


def build_tracker_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in STATE_CAPITALS:
        state_budget_raw_dir = BASES_ORCAMENTO_GERAL_DIR / item.uf
        state_convenio_raw_dir = BASES_CONVENIOS_DIR / item.uf
        capital_budget_raw_dir = first_existing_dir(BASES_ORCAMENTO_GERAL_CAPITAIS_DIR, item)
        capital_convenio_raw_dir = first_existing_dir(BASES_CONVENIOS_CAPITAIS_DIR, item)

        state_budget_parquet = ORCAMENTO_GERAL_PROCESSADA_DIR / f"{item.uf}.parquet"
        state_convenio_parquet = PROCESSADA_DIR / f"{item.uf}.parquet"
        capital_parquet = CAPITAIS_PROCESSADA_DIR / capital_parquet_name(item.uf, item.capital)

        state_budget_summary = parquet_summary(state_budget_parquet) if state_budget_parquet.exists() else {}
        state_convenio_summary = parquet_summary(state_convenio_parquet) if state_convenio_parquet.exists() else {}
        capital_summary = parquet_summary(capital_parquet) if capital_parquet.exists() else {}

        row = {
            "uf": item.uf,
            "estado": item.estado,
            "capital": item.capital,
            "orcamento_estado_bruto": has_files(state_budget_raw_dir),
            "convenios_estado_bruto": has_files(state_convenio_raw_dir),
            "orcamento_capital_bruto": has_files(capital_budget_raw_dir) if capital_budget_raw_dir else False,
            "capital_convenios_bruto": has_files(capital_convenio_raw_dir) if capital_convenio_raw_dir else False,
            "orcamento_estado_parquet": state_budget_parquet.exists(),
            "convenios_estado_parquet": state_convenio_parquet.exists(),
            "capital_parquet": capital_parquet.exists(),
            "orcamento_estado_rows": state_budget_summary.get("rows"),
            "convenios_estado_rows": state_convenio_summary.get("rows"),
            "capital_rows": capital_summary.get("rows"),
            "orcamento_estado_osc_signal": state_budget_summary.get("osc_signal"),
            "convenios_estado_osc_signal": state_convenio_summary.get("osc_signal"),
            "capital_osc_signal": capital_summary.get("osc_signal"),
            "orcamento_estado_osc_name_cnpj_rows": state_budget_summary.get("osc_name_cnpj_rows"),
            "convenios_estado_osc_name_cnpj_rows": state_convenio_summary.get("osc_name_cnpj_rows"),
            "capital_osc_name_cnpj_rows": capital_summary.get("osc_name_cnpj_rows"),
            "capital_convenios_dir": str(capital_convenio_raw_dir) if capital_convenio_raw_dir else "",
            "capital_orcamento_dir": str(capital_budget_raw_dir) if capital_budget_raw_dir else "",
        }
        row["proxima_acao"] = next_action(row)
        rows.append(row)
    return rows


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    ensure_parent_dir(output_path)
    tracker = pd.DataFrame(build_tracker_rows())
    tracker.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Tracker salvo em: {output_path}")
    print(f"Linhas: {len(tracker)}")


if __name__ == "__main__":
    main()
