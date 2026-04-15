from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import zipfile

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
USECOLS = [
    "FaseGasto",
    "Favorecido",
    "CNPJ",
    "Historico",
    "Nome Natureza Despesa",
    "Elemento",
    "Valor",
    "Data",
    "Cod_Convenio",
    "Cod_Municipio",
    "Municipio",
]
OSC_PATTERN = re.compile(
    r"associ|institu|fundac|apae|sociedade|benefic|filantrop|hospital|abrigo|lar|santa casa|irmandade|"
    r"centro social|obras sociais|comunidade",
    re.IGNORECASE,
)
PUBLIC_PATTERN = re.compile(
    r"municipio de |pref mun|prefeitura|fundo municipal|fundo estadual|secretaria|departamento|"
    r"instituto nacional do seguro social|^inss$|banrisul|tribunal|ministerio|camara|universidade",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa as despesas do RS com foco em convenios/subvencoes para OSC no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Diretorio com os ZIPs do RS. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=100000,
        help="Quantidade de linhas por bloco ao ler os CSVs zipados.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("RS", scope)


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


def list_zip_paths(input_dir: Path) -> list[Path]:
    return sorted(input_dir.glob("Despesas do Estado-*.zip"))


def build_focus_mask(frame: pd.DataFrame) -> pd.Series:
    fase = clean_text(frame.get("FaseGasto")).fillna("")
    favorecido = clean_text(frame.get("Favorecido")).fillna("")
    historico = clean_text(frame.get("Historico")).fillna("")
    natureza = clean_text(frame.get("Nome Natureza Despesa")).fillna("")

    pagamento = fase.str.contains(r"pagamento", case=False, regex=True, na=False)
    nome_osc = favorecido.str.contains(OSC_PATTERN, na=False)
    publico = favorecido.str.contains(PUBLIC_PATTERN, na=False)
    natureza_osc = natureza.str.contains(r"subven|aux ent|auxili", case=False, regex=True, na=False)
    texto_convenio = historico.str.contains(r"conven|parcer|fomento|repasse", case=False, regex=True, na=False)
    return pagamento & (natureza_osc | (nome_osc & ~publico) | (texto_convenio & nome_osc & ~publico))


def iter_filtered_frames(input_dir: Path, chunksize: int) -> tuple[list[pd.DataFrame], int]:
    frames: list[pd.DataFrame] = []
    total_source_rows = 0

    for zip_path in list_zip_paths(input_dir):
        with zipfile.ZipFile(zip_path) as archive:
            members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not members:
                continue
            member = members[0]
            with archive.open(member) as handle:
                reader = pd.read_csv(
                    handle,
                    dtype=str,
                    sep=";",
                    encoding="latin1",
                    usecols=USECOLS,
                    chunksize=chunksize,
                )
                for chunk in reader:
                    total_source_rows += len(chunk)
                    filtered = chunk.loc[build_focus_mask(chunk)].copy()
                    if not filtered.empty:
                        frames.append(filtered)
    return frames, total_source_rows


def build_rs_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    parsed_dates = pd.to_datetime(source_df.get("Data"), errors="coerce", dayfirst=True)
    ano = pd.Series(parsed_dates.dt.year, index=source_df.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed_dates.dt.month, index=source_df.index, dtype="Int64").astype("string")

    mapped = pd.DataFrame(
        {
            "uf": "RS",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano,
            "valor_total": source_df.get("Valor"),
            "cnpj": source_df.get("CNPJ"),
            "nome_osc": source_df.get("Favorecido"),
            "mes": mes,
            "cod_municipio": source_df.get("Cod_Municipio"),
            "municipio": source_df.get("Municipio"),
            "objeto": first_non_empty(source_df.get("Historico"), source_df.get("Cod_Convenio")),
            "modalidade": first_non_empty(source_df.get("Nome Natureza Despesa"), source_df.get("Elemento")),
            "data_inicio": source_df.get("Data"),
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir) if args.input_dir else default_input_dir(args.scope)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filtered_frames, total_source_rows = iter_filtered_frames(input_dir, args.chunksize)
    source_df = pd.concat(filtered_frames, ignore_index=True) if filtered_frames else pd.DataFrame(columns=USECOLS)
    mapped = build_rs_budget_frame(source_df)
    normalized = normalize_preview(mapped, "RS", require_cnpj=True)

    output_path = output_dir / default_output_name("RS", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_dir}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {total_source_rows}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
