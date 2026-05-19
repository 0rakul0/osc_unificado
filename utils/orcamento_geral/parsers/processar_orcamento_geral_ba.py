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
        description="Processa os arquivos de despesas gerais da BA para parquet no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="Arquivo bruto da BA. Se omitido, usa despesas_*.xlsx do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("BA", scope) / "pagamentos_osc_candidatas_cruzadas.csv"


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("BA", scope)


def read_csv_with_fallback(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "latin1"):
        try:
            return pd.read_csv(path, dtype=str, encoding=encoding, low_memory=False)
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Falha ao ler {path}") from last_error


def read_source(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path, dtype=str)
    return read_csv_with_fallback(path)


def read_default_sources(input_dir: Path) -> pd.DataFrame:
    paths = sorted(input_dir.glob("despesas_*.xlsx"))
    if not paths:
        return read_source(input_dir / "pagamentos_osc_candidatas_cruzadas.csv")

    frames: list[pd.DataFrame] = []
    for path in paths:
        frame = pd.read_excel(path, dtype=str)
        frame["_arquivo_origem"] = path.name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    if not series:
        return pd.Series(dtype="string")

    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = current.astype("string").str.strip().replace("", pd.NA)
        result = cleaned if result is None else result.combine_first(cleaned)

    if result is None:
        return pd.Series(dtype="string")
    return result


def build_ba_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    if "ANO_EXERCICIO" in source_df.columns:
        return build_ba_general_expense_frame(source_df)

    modalidade = first_non_empty(
        source_df.get("tipo_parceria_convenio"),
        source_df.get("tipo_instrumento_convenio"),
        source_df.get("tipo_despesa_convenio"),
    )
    objeto = first_non_empty(source_df.get("objeto_convenio"))
    municipio = first_non_empty(source_df.get("municipio_convenio"))

    mapped = pd.DataFrame(
        {
            "uf": "BA",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": source_df.get("ano"),
            "valor_total": source_df.get("valor_total"),
            "cnpj": source_df.get("cnpj"),
            "nome_osc": source_df.get("recebedor"),
            "mes": source_df.get("mes"),
            "municipio": municipio,
            "objeto": objeto,
            "modalidade": modalidade,
            "data_inicio": source_df.get("data_inicio_convenio"),
            "data_fim": source_df.get("data_fim_convenio"),
        }
    )

    # A compilacao da BA nao traz um codigo de municipio confiavel.
    mapped["cod_municipio"] = pd.NA

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def build_ba_general_expense_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    mapped = pd.DataFrame(
        {
            "uf": "BA",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": source_df.get("ANO_EXERCICIO"),
            "valor_total": first_non_empty(
                source_df.get("VAL_PAGO"),
                source_df.get("VAL_LIQUIDADO_TOTAL"),
                source_df.get("VAL_EMPENHADO_TOTAL"),
            ),
            "cnpj": pd.NA,
            "nome_osc": first_non_empty(source_df.get("NOM_UNIDADE_GESTORA"), source_df.get("NOM_ORGAO_ORCAMENTO")),
            "mes": source_df.get("MES_EXERCICIO"),
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(source_df.get("NOM_ACAO_PROGRAMA_GOVERNO"), source_df.get("NOM_PROGRAMA_GOVERNO")),
            "modalidade": first_non_empty(
                source_df.get("NOM_MODALIDADE_APLICACAO_ORCAMENTO"),
                source_df.get("NOM_ELEMENTO_DESPESA_ORCAMENTO"),
                source_df.get("NOM_GRUPO_DESPESA_ORCAMENTO"),
            ),
            "data_inicio": source_df.get("DATA_COMPLETA"),
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input) if args.input else None
    input_dir = default_input_dir(args.scope)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df = read_source(input_path) if input_path else read_default_sources(input_dir)
    mapped = build_ba_budget_frame(source_df)
    normalized = normalize_preview(mapped, "BA", require_cnpj=False)

    output_path = output_dir / default_output_name("BA", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path or input_dir / 'despesas_*.xlsx'}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
