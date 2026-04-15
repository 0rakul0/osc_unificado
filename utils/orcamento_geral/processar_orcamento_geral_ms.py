from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa o resumo anual de despesas por credor do MS com foco em OSC para parquet."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="Workbook consolidado do MS. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    base_dir = uf_raw_dir("MS", scope)
    preferred = base_dir / "MS_orcamento_geral.xlsx"
    if preferred.exists():
        return preferred

    matches = sorted(base_dir.glob("MS*.xlsx"))
    if matches:
        return matches[0]
    return preferred


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = clean_text(current)
        result = cleaned if result is None else result.combine_first(cleaned)
    if result is None:
        return pd.Series(dtype="string")
    return result


def read_source(path: Path) -> pd.DataFrame:
    workbook = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []

    for sheet_name in workbook.sheet_names:
        sheet_df = pd.read_excel(workbook, sheet_name=sheet_name, header=4, dtype=str)
        expected = {"Cpf/Cnpj", "Credor", "Empenhado", "Liquidado", "Pago"}
        if not expected.issubset(set(sheet_df.columns)):
            continue

        frame = sheet_df.loc[:, ["Cpf/Cnpj", "Credor", "Empenhado", "Liquidado", "Pago"]].copy()
        frame = frame[frame["Cpf/Cnpj"].astype("string").str.strip().ne("Cpf/Cnpj")]
        frame["ano"] = str(sheet_name)
        frames.append(frame)

    if not frames:
        return pd.DataFrame(columns=["Cpf/Cnpj", "Credor", "Empenhado", "Liquidado", "Pago", "ano"])
    return pd.concat(frames, ignore_index=True)


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("Credor")).fillna("")

    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|hospital|abrigo|lar|cooperativa",
        case=False,
        regex=True,
        na=False,
    )
    publico = nome.str.contains(
        r"prefeitura|secretaria|governo|tribunal|ministerio|fundo municipal|fundo estadual|"
        r"instituto municipal de previd|instituto de prev|fundacao estadual|fundacao municipal|"
        r"universidade|agencia municipal|detran|procuradoria|camara|assembleia|banco do brasil",
        case=False,
        regex=True,
        na=False,
    )
    return nome_osc & ~publico


def build_ms_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()

    mapped = pd.DataFrame(
        {
            "uf": "MS",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get("ano"),
            "valor_total": first_non_empty(filtered.get("Pago"), filtered.get("Liquidado"), filtered.get("Empenhado")),
            "cnpj": filtered.get("Cpf/Cnpj"),
            "nome_osc": filtered.get("Credor"),
            "mes": pd.NA,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": pd.NA,
            "modalidade": "resumo_credor_anual",
            "data_inicio": pd.NA,
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input) if args.input else default_input_path(args.scope)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df = read_source(input_path)
    mapped = build_ms_budget_frame(source_df)
    normalized = normalize_preview(mapped, "MS", require_cnpj=True)

    output_path = output_dir / default_output_name("MS", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
