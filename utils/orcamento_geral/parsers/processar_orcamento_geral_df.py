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
        description="Processa as despesas do DF com foco em transferencias a OSC para parquet."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="JSON consolidado do DF. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("DF", scope) / "despesa_df_2025.json"


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


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, utc=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_json(path)


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    modalidade = clean_text(source_df.get("nomeModalidadeAplicacao")).fillna("")
    nome = clean_text(source_df.get("nomeCredor")).fillna("")
    programa = clean_text(source_df.get("nomeProgramaTrabalho")).fillna("")
    subtitulo = clean_text(source_df.get("nomeSubtitulo")).fillna("")
    fonte = clean_text(source_df.get("nomeFonteRecurso")).fillna("")

    modalidade_osc = modalidade.str.contains(r"sem fins lucrativos", case=False, regex=True, na=False)
    texto_convenio = (
        programa.str.contains(r"conv..nio|parceria|fomento|termo|repasse|apoio a projetos", case=False, regex=True, na=False)
        | subtitulo.str.contains(r"conv..nio|parceria|fomento|termo|repasse|apoio a projetos", case=False, regex=True, na=False)
        | fonte.str.contains(r"conv..nio|parceria|fomento", case=False, regex=True, na=False)
    )
    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|organiz|"
        r"miseric|lar|casa|centro|abrigo|hospital|federac|cooperativa|pestalozzi",
        case=False,
        regex=True,
        na=False,
    )
    publico = nome.str.contains(
        r"caixa escolar|coordena..o regional de ensino|diretoria regional de ensino|"
        r"\\bdre\\b|secretaria|governo|tribunal|camara|assembleia|fundo |"
        r"instituto de gest..o estrat..gica|servi..o social aut..nomo|universidade",
        case=False,
        regex=True,
        na=False,
    )
    return (modalidade_osc | (nome_osc & texto_convenio)) & ~publico


def build_df_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    data_referencia = first_non_empty(filtered.get("dataInicio"), filtered.get("dataFim"))
    ano_data, mes = extract_year_month(data_referencia)

    mapped = pd.DataFrame(
        {
            "uf": "DF",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(filtered.get("anoExercicio")).combine_first(ano_data),
            "valor_total": first_non_empty(
                filtered.get("valorObFinal"),
                filtered.get("valorPagoExercicio"),
                filtered.get("valorNlBruto"),
                filtered.get("valorNeFinal"),
            ),
            "cnpj": filtered.get("codigoCredor"),
            "nome_osc": filtered.get("nomeCredor"),
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(filtered.get("nomeSubtitulo"), filtered.get("nomeProgramaTrabalho")),
            "modalidade": first_non_empty(
                filtered.get("nomeModalidadeAplicacao"),
                filtered.get("nomeTipoLicitacao"),
                filtered.get("nomeFonteRecurso"),
            ),
            "data_inicio": filtered.get("dataInicio"),
            "data_fim": filtered.get("dataFim"),
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
    mapped = build_df_budget_frame(source_df)
    normalized = normalize_preview(mapped, "DF", require_cnpj=True)

    output_path = output_dir / default_output_name("DF", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
