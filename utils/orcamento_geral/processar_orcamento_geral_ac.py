from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
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
PUBLIC_NAME_PATTERN = re.compile(
    r"governo do estado|secretaria|tribunal|departamento|defensoria|pol[ií]cia|corpo de bombeiro|servi[cç]o de [áa]gua|estado do acre|funda[cç][aã]o de cultura elias mansour|funda[cç][aã]o de amparo a pesquisa|instituto de administra[cç][aã]o penitenci",
    re.IGNORECASE,
)
OBJECT_OSC_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"ASSOCIA[ÇC][AÃ]O\s+CRIST[ÃA]\s+ALFA(?:\s*\(ACALFA\))?",
            re.IGNORECASE,
        ),
        "ASSOCIACAO CRISTA ALFA - ACALFA",
    ),
    (
        re.compile(
            r"ASSOCIA[ÇC][AÃ]O\s+DE\s+PARENTES\s+E\s+AMIGOS\s+DOS\s+DEPENDENTES\s+QU[ÍI]MICOS\s+EM\s+CRUZEIRO\s+DO\s+SUL(?:\s*\(APADEQ\))?",
            re.IGNORECASE,
        ),
        "ASSOCIACAO DE PARENTES E AMIGOS DOS DEPENDENTES QUIMICOS EM CRUZEIRO DO SUL - APADEQ",
    ),
    (
        re.compile(
            r"ASSOCIA[ÇC][AÃ]O\s+DE\s+CONSELHEIROS\s+E\s+EX-?CONSELHEIROS\s+TUTELARES\s+DO\s+ESTADO\s+DO\s+ACRE(?:\s+ASCONTAC|\s+\(?ASCONTAC\)?)?",
            re.IGNORECASE,
        ),
        "ASSOCIACAO DE CONSELHEIROS E EX-CONSELHEIROS TUTELARES DO ESTADO DO ACRE - ASCONTAC",
    ),
    (
        re.compile(
            r"ASSOCIA[ÇC][AÃ]O\s+DE\s+BANDAS\s+E\s+FANFARRAS\s+DO\s+ESTADO\s+DO\s+ACRE",
            re.IGNORECASE,
        ),
        "ASSOCIACAO DE BANDAS E FANFARRAS DO ESTADO DO ACRE - ABANFACRE",
    ),
    (
        re.compile(r"CONSELHO\s+NACIONAL\s+DOS\s+SERINGUEIROS", re.IGNORECASE),
        "CONSELHO NACIONAL DOS SERINGUEIROS",
    ),
    (
        re.compile(r"SOCIEDADE\s+RECREATIVA\s+TENTAMEN", re.IGNORECASE),
        "SOCIEDADE RECREATIVA TENTAMEN",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa os convenios do Acre com recorte conservador de OSC identificado no objeto da parceria."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="JSON bruto do Acre. Se omitido, usa o caminho padrao do escopo.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("AC", scope) / "ac_convenios_detalhamento.json"


def read_source(path: Path) -> pd.DataFrame:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"JSON inesperado em {path}")
    return pd.DataFrame(rows)


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
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def normalize_ascii_upper(text: str) -> str:
    return (
        text.upper()
        .replace("Á", "A")
        .replace("À", "A")
        .replace("Ã", "A")
        .replace("Â", "A")
        .replace("É", "E")
        .replace("Ê", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Õ", "O")
        .replace("Ô", "O")
        .replace("Ú", "U")
        .replace("Ç", "C")
    )


def extract_object_osc_name(text: object) -> object:
    if pd.isna(text):
        return pd.NA
    normalized = str(text).strip()
    if not normalized:
        return pd.NA

    for pattern, label in OBJECT_OSC_PATTERNS:
        if pattern.search(normalized):
            return label

    return pd.NA


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    convenente = clean_text(source_df.get("orgao_convenente")).fillna("")
    executor = clean_text(source_df.get("orgao_executor")).fillna("")
    objeto = clean_text(source_df.get("objeto")).fillna("")

    explicit_object_osc = objeto.map(extract_object_osc_name).notna()
    convenente_private = ~convenente.str.contains(PUBLIC_NAME_PATTERN, na=False)
    executor_private = ~executor.str.contains(PUBLIC_NAME_PATTERN, na=False)
    convenente_osc_like = convenente.str.contains(r"associ|sociedade|cooper|conselho nacional dos seringueiros", regex=True, case=False, na=False)
    executor_osc_like = executor.str.contains(r"associ|sociedade|cooper|conselho nacional dos seringueiros", regex=True, case=False, na=False)

    return explicit_object_osc | (convenente_private & convenente_osc_like) | (executor_private & executor_osc_like)


def build_nome_osc(source_df: pd.DataFrame) -> pd.Series:
    convenente = clean_text(source_df.get("orgao_convenente"))
    executor = clean_text(source_df.get("orgao_executor"))
    objeto = clean_text(source_df.get("objeto"))

    convenente_valid = convenente.where(~convenente.fillna("").str.contains(PUBLIC_NAME_PATTERN, na=False), pd.NA)
    executor_valid = executor.where(~executor.fillna("").str.contains(PUBLIC_NAME_PATTERN, na=False), pd.NA)
    object_valid = objeto.map(extract_object_osc_name).astype("string")
    return first_non_empty(object_valid, convenente_valid, executor_valid)


def build_ac_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    nome_osc = build_nome_osc(filtered)
    termino = clean_text(filtered.get("termino_da_vigencia"))
    ano_termino, mes = extract_year_month(termino)

    mapped = pd.DataFrame(
        {
            "uf": "AC",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(filtered.get("ano_celebracao")).combine_first(ano_termino),
            "valor_total": first_non_empty(filtered.get("valorprevisto"), filtered.get("valorliberadoconvenio")),
            "cnpj": pd.NA,
            "nome_osc": nome_osc,
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("objeto"),
            "modalidade": filtered.get("numeroconvenio"),
            "data_inicio": pd.NA,
            "data_fim": termino,
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
    mapped = build_ac_budget_frame(source_df)
    normalized = normalize_preview(mapped, "AC", require_cnpj=False)

    output_path = output_dir / default_output_name("AC", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
