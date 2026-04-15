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
COL_PREFIX = "View Gastos Governamentais - aba Transferencias"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a trilha de transferencias/despesas do GO para parquet no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV consolidado de transferencias do GO. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("GO", scope) / "transparencia_eof_gastos_gov_transf_vol.csv"


def go_col(name: str) -> str:
    return f"{COL_PREFIX}[{name}]"


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig", low_memory=False)


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
    modalidade = clean_text(source_df.get(go_col("Modalidade Aplicacao"))).fillna("")
    tipo = clean_text(source_df.get(go_col("Tipo"))).fillna("")
    nome = clean_text(source_df.get(go_col("Nome Credor"))).fillna("")
    descricao = clean_text(source_df.get(go_col("DESCRICAO"))).fillna("")
    objetivo = clean_text(source_df.get(go_col("Objetivo"))).fillna("")

    modalidade_privada = modalidade.str.contains(
        r"institui..es privadas sem fins lucrativos",
        case=False,
        regex=True,
        na=False,
    )
    tipo_convenio = tipo.str.contains(r"conv..nio|colabora|parceria|fomento", case=False, regex=True, na=False)
    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|abrigo|casa|centro|hospital",
        case=False,
        regex=True,
        na=False,
    )
    texto_convenio = descricao.str.contains(
        r"conv..nio|termo de colabora|termo de parceria|fomento|repasse de recursos|organiz",
        case=False,
        regex=True,
        na=False,
    ) | objetivo.str.contains(
        r"conv..nio|termo de colabora|termo de parceria|fomento|repasse de recursos|organiz",
        case=False,
        regex=True,
        na=False,
    )
    return modalidade_privada | tipo_convenio | (nome_osc & texto_convenio) | (nome_osc & modalidade_privada)


def build_go_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()

    mapped = pd.DataFrame(
        {
            "uf": "GO",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get(go_col("Ano Pagamento")),
            "valor_total": filtered.get(go_col("Valor Pagamento")),
            "cnpj": filtered.get(go_col("CPF_CNPJ")),
            "nome_osc": filtered.get(go_col("Nome Credor")),
            "mes": filtered.get(go_col("Numero Mes")),
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(filtered.get(go_col("DESCRICAO")), filtered.get(go_col("Objetivo"))),
            "modalidade": first_non_empty(filtered.get(go_col("Tipo")), filtered.get(go_col("Modalidade Aplicacao"))),
            "data_inicio": filtered.get(go_col("Data Completa")),
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
    mapped = build_go_budget_frame(source_df)
    normalized = normalize_preview(mapped, "GO", require_cnpj=True)

    output_path = output_dir / default_output_name("GO", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
