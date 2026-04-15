from __future__ import annotations

import argparse
from pathlib import Path
import re
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
OSC_PATTERN = re.compile(
    r"associ|institu|fundac|apae|sociedade|obra social|casa da crian|abrigo|centro educ|pestalozzi|"
    r"santa casa|irmandade|reabilitar|riosolidario",
    re.IGNORECASE,
)
PUBLIC_PATTERN = re.compile(
    r"fundo municipal|fundo estadual|prefeitura|municipio de |secretaria|ministerio|tribunal|procuradoria|"
    r"universidade|fundacao saude|fundacao.*estado|superintend|autarquia|camara municipal|receita federal",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a despesa do RJ com foco em convenios/subvencoes para OSC no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV da despesa do RJ. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("RJ", scope) / "despesa2026.csv"


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, sep=";", encoding="latin1", skiprows=5, engine="python")


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
    nome_credor = clean_text(source_df.get("Nome Credor")).fillna("")
    nome_elemento = clean_text(source_df.get("Nome Elemento")).fillna("")
    historico = clean_text(source_df.get("Histórico")).fillna("")

    nome_osc = nome_credor.str.contains(OSC_PATTERN, na=False)
    publico = nome_credor.str.contains(PUBLIC_PATTERN, na=False)
    subvencao = nome_elemento.str.contains(r"subven", case=False, regex=True, na=False)
    termo_osc = historico.str.contains(
        r"conv..nio|parcer|fomento|termo de colabora|termo de fomento|contrato de gest",
        case=False,
        regex=True,
        na=False,
    )
    return ((subvencao & nome_osc) | (termo_osc & nome_osc)) & ~publico


def infer_year(path: Path) -> str:
    match = re.search(r"(19|20)\d{2}", path.stem)
    return match.group(0) if match else "2026"


def build_rj_budget_frame(source_df: pd.DataFrame, ano: str) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()

    mapped = pd.DataFrame(
        {
            "uf": "RJ",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano,
            "valor_total": filtered.get("Valor Pago"),
            "cnpj": filtered.get("Credor"),
            "nome_osc": filtered.get("Nome Credor"),
            "mes": pd.NA,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("Histórico"),
            "modalidade": first_non_empty(filtered.get("Nome Elemento"), filtered.get("Nome Modalidade de Aplicação")),
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
    mapped = build_rj_budget_frame(source_df, infer_year(input_path))
    normalized = normalize_preview(mapped, "RJ", require_cnpj=True)

    output_path = output_dir / default_output_name("RJ", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
