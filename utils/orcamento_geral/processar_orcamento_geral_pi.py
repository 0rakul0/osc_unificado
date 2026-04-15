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
        description="Processa as despesas do PI com foco em transferencias para OSC no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="Workbook consolidado do PI. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("PI", scope) / "dados_consolidados_pi.xlsx"


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, dtype=str)


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    modalidade = clean_text(source_df.get("modalidade_titulo")).fillna("")
    elemento = clean_text(source_df.get("elemento_titulo")).fillna("")

    return modalidade.str.contains(
        r"institui..es privadas sem fins lucrativos",
        case=False,
        regex=True,
        na=False,
    ) | elemento.str.contains(r"contrato de gest..o|subven", case=False, regex=True, na=False)


def build_pi_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()

    mapped = pd.DataFrame(
        {
            "uf": "PI",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get("exercicio"),
            "valor_total": filtered.get("temp_pago_saldo"),
            "cnpj": filtered.get("credor_codigo"),
            "nome_osc": filtered.get("credor_titulo"),
            "mes": pd.to_datetime(filtered.get("emissao_data"), errors="coerce").dt.month.astype("Int64").astype("string"),
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("elemento_titulo"),
            "modalidade": filtered.get("modalidade_titulo"),
            "data_inicio": filtered.get("emissao_data"),
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
    mapped = build_pi_budget_frame(source_df)
    normalized = normalize_preview(mapped, "PI", require_cnpj=True)

    output_path = output_dir / default_output_name("PI", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
