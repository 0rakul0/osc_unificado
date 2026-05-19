from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import unicodedata
import zipfile

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
        help="CSV ou ZIP da despesa do RJ. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    zip_path = uf_raw_dir("RJ", scope) / "despesa.zip"
    return zip_path if zip_path.exists() else uf_raw_dir("RJ", scope) / "despesa2026.csv"


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


def infer_year(path: Path) -> str:
    match = re.search(r"(19|20)\d{2}", path.stem)
    return match.group(0) if match else "2026"


def iter_source_frames(path: Path) -> list[tuple[pd.DataFrame, str]]:
    if path.suffix.lower() != ".zip":
        return [(read_source(path), infer_year(path))]

    frames: list[tuple[pd.DataFrame, str]] = []
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if not name.lower().endswith(".csv"):
                continue
            year = infer_year(Path(name))
            with archive.open(name) as handle:
                for chunk in pd.read_csv(
                    handle,
                    dtype=str,
                    sep=";",
                    encoding="latin1",
                    skiprows=5,
                    chunksize=100_000,
                    low_memory=False,
                ):
                    frames.append((chunk, year))
    return frames


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


def normalize_column_name(value: str) -> str:
    text = "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def get_column(source_df: pd.DataFrame, *names: str) -> pd.Series | None:
    normalized = {normalize_column_name(column): column for column in source_df.columns}
    for name in names:
        if name in source_df.columns:
            return source_df[name]
        column = normalized.get(normalize_column_name(name))
        if column is not None:
            return source_df[column]
    return None


def first_non_zero(*series: pd.Series | None) -> pd.Series:
    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = clean_text(current)
        numeric = pd.to_numeric(cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
        cleaned = cleaned.where(numeric.ne(0), pd.NA)
        result = cleaned if result is None else result.combine_first(cleaned)
    if result is None:
        return pd.Series(dtype="string")
    return result


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome_credor = clean_text(get_column(source_df, "Nome Credor")).fillna("")
    nome_elemento = clean_text(get_column(source_df, "Nome Elemento")).fillna("")
    historico = clean_text(get_column(source_df, "Historico", "Histórico", "HistÃ³rico")).fillna("")

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


def build_rj_budget_frame(source_df: pd.DataFrame, ano: str) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()

    mapped = pd.DataFrame(
        {
            "uf": "RJ",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano,
            "valor_total": first_non_zero(
                get_column(filtered, "Valor Pago"),
                get_column(filtered, "Valor Liquidado"),
                get_column(filtered, "Valor Empenhado"),
            ),
            "cnpj": get_column(filtered, "Credor"),
            "nome_osc": get_column(filtered, "Nome Credor"),
            "mes": pd.NA,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": get_column(filtered, "Historico", "Histórico", "HistÃ³rico"),
            "modalidade": first_non_empty(
                get_column(filtered, "Nome Elemento"),
                get_column(filtered, "Nome Modalidade de Aplicacao", "Nome Modalidade de Aplicação", "Nome Modalidade de AplicaÃ§Ã£o"),
            ),
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

    mapped_frames = [build_rj_budget_frame(frame, year) for frame, year in iter_source_frames(input_path)]
    mapped = pd.concat(mapped_frames, ignore_index=True) if mapped_frames else pd.DataFrame(columns=STANDARD_COLUMNS)
    normalized = normalize_preview(mapped, "RJ", require_cnpj=True)
    normalized = normalized.drop_duplicates(subset=["ano", "cnpj", "nome_osc", "valor_total", "objeto"])

    output_path = output_dir / default_output_name("RJ", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Partes origem: {len(mapped_frames)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
