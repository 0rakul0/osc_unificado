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
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.common import STANDARD_COLUMNS
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a trilha de orcamento geral de AL para parquet no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV consolidado de AL. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("AL", scope) / "coleta_2018_2026" / "despesas_alagoas_todos_anos.csv"


def read_csv_with_fallback(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "latin1"):
        try:
            return pd.read_csv(path, dtype=str, encoding=encoding, low_memory=False)
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Falha ao ler {path}") from last_error


def build_al_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    mapped = pd.DataFrame(
        {
            "uf": "AL",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": source_df.get("ano_consulta"),
            "valor_total": source_df.get("valor_pago"),
            "cnpj": source_df.get("codigo_favorecido"),
            "nome_osc": source_df.get("nome_favorecido"),
            "objeto": source_df.get("projeto_atividade_id__projeto_descricao"),
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

    source_df = read_csv_with_fallback(input_path)
    mapped = build_al_budget_frame(source_df)
    normalized = normalize_preview(mapped, "AL")

    output_path = output_dir / default_output_name("AL", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
