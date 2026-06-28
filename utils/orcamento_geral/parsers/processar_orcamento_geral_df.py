from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
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


ORIGEM_ORCAMENTO_GERAL = "ESTADO_ORCAMENTO_GERAL"


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


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("DF", scope)


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


def get_column(frame: pd.DataFrame, *names: str) -> pd.Series:
    for name in names:
        if name in frame.columns:
            return frame[name]
    return pd.Series(pd.NA, index=frame.index, dtype="string")


def normalize_df_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).strip().strip('"') for column in frame.columns]
    for column in frame.select_dtypes(include="object").columns:
        frame[column] = frame[column].astype("string").str.strip().str.strip('"')
    return frame


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, utc=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def read_json_source(path: Path) -> pd.DataFrame:
    return pd.read_json(path)


def iter_zip_frames(path: Path, chunksize: int = 100_000):
    year = path.stem.removeprefix("despesa")
    member_suffix = f"Despesa_Empenho_{year}.csv"
    with zipfile.ZipFile(path) as archive:
        members = [name for name in archive.namelist() if name.endswith(member_suffix)]
        if not members:
            raise FileNotFoundError(f"Arquivo {member_suffix} nao encontrado em {path}.")
        with archive.open(members[0]) as handle:
            yield from pd.read_csv(
                handle,
                sep="\xA8",
                encoding="latin1",
                dtype=str,
                engine="python",
                chunksize=chunksize,
                quoting=csv.QUOTE_NONE,
                on_bad_lines="skip",
            )


def read_source(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".zip":
        frames = [normalize_df_columns(chunk) for chunk in iter_zip_frames(path)]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return read_json_source(path)


def read_default_sources(input_dir: Path) -> pd.DataFrame:
    zip_paths = sorted(input_dir.glob("despesa*.zip"))
    if zip_paths:
        frames: list[pd.DataFrame] = []
        for path in zip_paths:
            for chunk in iter_zip_frames(path):
                chunk = normalize_df_columns(chunk)
                filtered = chunk.loc[build_focus_mask(chunk)].copy()
                if not filtered.empty:
                    frames.append(build_df_budget_frame(filtered, already_filtered=True))
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=STANDARD_COLUMNS)
    return read_json_source(input_dir / "despesa_df_2025.json")


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    modalidade = clean_text(get_column(source_df, "nomeModalidadeAplicacao", "MODALIDADE APLICAÇÃO")).fillna("")
    nome = clean_text(get_column(source_df, "nomeCredor", "CREDOR")).fillna("")
    programa = clean_text(get_column(source_df, "nomeProgramaTrabalho", "PROGRAMA DE TRABALHO", "PROGRAMA")).fillna("")
    subtitulo = clean_text(get_column(source_df, "nomeSubtitulo", "SUBTÍTULO", "AÇÃO")).fillna("")
    fonte = clean_text(get_column(source_df, "nomeFonteRecurso", "FONTE RECURSOS")).fillna("")
    elemento = clean_text(get_column(source_df, "nomeElemento", "ELEMENTO DESPESA")).fillna("")

    modalidade_osc = modalidade.str.contains(r"sem fins lucrativos", case=False, regex=True, na=False)
    texto_convenio = (
        programa.str.contains(r"conv..nio|parceria|fomento|termo|repasse|apoio a projetos", case=False, regex=True, na=False)
        | subtitulo.str.contains(r"conv..nio|parceria|fomento|termo|repasse|apoio a projetos", case=False, regex=True, na=False)
        | fonte.str.contains(r"conv..nio|parceria|fomento", case=False, regex=True, na=False)
        | elemento.str.contains(r"subven..es sociais|contrato de gest", case=False, regex=True, na=False)
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


def build_df_budget_frame(source_df: pd.DataFrame, already_filtered: bool = False) -> pd.DataFrame:
    filtered = source_df.copy() if already_filtered else source_df.loc[build_focus_mask(source_df)].copy()
    data_referencia = first_non_empty(
        get_column(filtered, "dataInicio"),
        get_column(filtered, "dataFim"),
        get_column(filtered, "EMISSÃO"),
        get_column(filtered, "LANCAMENTO"),
    )
    ano_data, mes = extract_year_month(data_referencia)

    mapped = pd.DataFrame(
        {
            "uf": "DF",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(get_column(filtered, "anoExercicio", "EXERCÍCIO")).combine_first(ano_data),
            "valor_total": first_non_empty(
                get_column(filtered, "valorNlBruto"),
                get_column(filtered, "valorObFinal"),
                get_column(filtered, "valorNeFinal"),
                get_column(filtered, "VALOR FINAL"),
                get_column(filtered, "VALOR INICIAL"),
                get_column(filtered, "valorPagoExercicio"),
            ),
            "cnpj": get_column(filtered, "codigoCredor", "CNPJ CPF CREDOR"),
            "nome_osc": get_column(filtered, "nomeCredor", "CREDOR"),
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(
                get_column(filtered, "nomeSubtitulo", "SUBTÍTULO"),
                get_column(filtered, "nomeProgramaTrabalho", "PROGRAMA DE TRABALHO"),
            ),
            "modalidade": first_non_empty(
                get_column(filtered, "nomeModalidadeAplicacao", "MODALIDADE APLICAÇÃO"),
                get_column(filtered, "nomeTipoLicitacao", "LICITAÇÃO"),
                get_column(filtered, "nomeFonteRecurso", "FONTE RECURSOS"),
                get_column(filtered, "ELEMENTO DESPESA"),
            ),
            "data_inicio": first_non_empty(get_column(filtered, "dataInicio"), get_column(filtered, "EMISSÃO")),
            "data_fim": get_column(filtered, "dataFim"),
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
    mapped = source_df if list(source_df.columns) == STANDARD_COLUMNS else build_df_budget_frame(source_df)
    normalized = normalize_preview(mapped, "DF", require_cnpj=True)

    output_path = output_dir / default_output_name("DF", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path or input_dir}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
