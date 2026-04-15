from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a trilha de despesas do MA com foco em convenios/subvencoes para parquet."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV consolidado do MA. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("MA", scope) / "DESPESA_2026_01.csv"


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=";",
        dtype=str,
        encoding="utf-8",
        low_memory=False,
        on_bad_lines="skip",
    )


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


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("credor_nome")).fillna("")
    natureza = clean_text(source_df.get("nome_natureza")).fillna("")
    descricao = clean_text(source_df.get("descricao")).fillna("")

    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|hospital|casa",
        case=False,
        regex=True,
        na=False,
    )
    natureza_terceiro_setor = natureza.str.contains(
        r"subven..es .* sem fins lucrativos|subven",
        case=False,
        regex=True,
        na=False,
    )
    descricao_convenio = descricao.str.contains(
        r"conv..nio|termo de colabora|termo de parceria|fomento|edital de chamamento|repasse",
        case=False,
        regex=True,
        na=False,
    )
    return descricao_convenio | (nome_osc & natureza_terceiro_setor)


def build_ma_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()

    mapped = pd.DataFrame(
        {
            "uf": "MA",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get("ano"),
            "valor_total": filtered.get("valor"),
            "cnpj": filtered.get("codigo_credor"),
            "nome_osc": filtered.get("credor_nome"),
            "mes": filtered.get("mes"),
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("descricao"),
            "modalidade": first_non_empty(filtered.get("nome_natureza"), filtered.get("tipo_licitacao")),
            "data_inicio": filtered.get("data_documento"),
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
    mapped = build_ma_budget_frame(source_df)
    normalized = normalize_preview(mapped, "MA", require_cnpj=True)

    output_path = output_dir / default_output_name("MA", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
