from __future__ import annotations

import argparse
import gc
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


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
CHUNK_SIZE = 200_000
USECOLS = [
    "pagamento_exercicio",
    "data_pagamento",
    "valor_pagamento",
    "historico_pagamento",
    "credor_nome",
    "credor_cnpj",
    "natureza_despesa_nome",
    "elemento_nome",
    "municipio_repasse_cod",
    "municipio_repasse_desc",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa as despesas pagas do PR com foco em subvencoes e convenios de OSC para parquet."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Diretorio com os ZIPs de despesas do PR. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("PR", scope)


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


def iter_source_chunks(input_dir: Path):
    zip_paths = sorted(input_dir.glob("DESPESA_PAGAMENTO-*.zip"))
    for zip_path in zip_paths:
        with zipfile.ZipFile(zip_path) as archive:
            members = [name for name in archive.namelist() if "TB_DESPESA_CREDOR_PAGAMENTO" in name.upper()]
            if not members:
                continue
            with archive.open(members[0]) as handle:
                reader = pd.read_csv(
                    handle,
                    sep=";",
                    dtype=str,
                    encoding="latin1",
                    low_memory=False,
                    usecols=USECOLS,
                    chunksize=CHUNK_SIZE,
                )
                for chunk in reader:
                    yield zip_paths, zip_path, chunk


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("credor_nome")).fillna("")
    historico = clean_text(source_df.get("historico_pagamento")).fillna("")
    natureza = clean_text(source_df.get("natureza_despesa_nome")).fillna("")
    elemento = clean_text(source_df.get("elemento_nome")).fillna("")

    elemento_osc = elemento.str.contains(r"subven", case=False, regex=True, na=False)
    natureza_osc = natureza.str.contains(r"apae|subven|conven|fomento|parcer", case=False, regex=True, na=False)
    historico_osc = historico.str.contains(r"conven|parcer|fomento|termo|repasse", case=False, regex=True, na=False)
    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|organiz|"
        r"miseric|santa casa|lar|abrigo|asilo|creche|pestalozzi|federac|cooperativa|"
        r"acea|apae|apae ",
        case=False,
        regex=True,
        na=False,
    )
    publico = nome.str.contains(
        r"inss|instituto de previd|fundo de previd|agencia de fomento do parana|"
        r"prefeitura|secretaria|tribunal|camara|assembleia|governo|estado do parana|"
        r"conta relacionamento|banco |municipio de |universidade|fundo municipal|fundo estadual",
        case=False,
        regex=True,
        na=False,
    )
    return (elemento_osc | natureza_osc | (nome_osc & historico_osc)) & ~publico


def build_pr_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    ano_data, mes = extract_year_month(filtered.get("data_pagamento"))

    mapped = pd.DataFrame(
        {
            "uf": "PR",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": clean_text(filtered.get("pagamento_exercicio")).combine_first(ano_data),
            "valor_total": filtered.get("valor_pagamento"),
            "cnpj": filtered.get("credor_cnpj"),
            "nome_osc": filtered.get("credor_nome"),
            "mes": mes,
            "cod_municipio": filtered.get("municipio_repasse_cod"),
            "municipio": filtered.get("municipio_repasse_desc"),
            "objeto": filtered.get("historico_pagamento"),
            "modalidade": first_non_empty(filtered.get("natureza_despesa_nome"), filtered.get("elemento_nome")),
            "data_inicio": filtered.get("data_pagamento"),
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

    output_path = output_dir / default_output_name("PR", args.scope)
    temp_path = output_dir / "PR.tmp.parquet"
    if temp_path.exists():
        temp_path.unlink()
    if output_path.exists():
        output_path.unlink()

    writer: pq.ParquetWriter | None = None
    total_source_rows = 0
    total_parquet_rows = 0
    seen_paths: list[Path] = []

    try:
        for seen_paths, current_path, source_df in iter_source_chunks(input_dir):
            total_source_rows += len(source_df)
            mapped = build_pr_budget_frame(source_df)
            normalized = normalize_preview(mapped, "PR", require_cnpj=True)
            if normalized.empty:
                del source_df
                del mapped
                gc.collect()
                continue

            table = build_parquet_table(normalized)
            if writer is None:
                writer = pq.ParquetWriter(temp_path, table.schema, compression="snappy")
            writer.write_table(table)
            total_parquet_rows += len(normalized)

            del source_df
            del mapped
            del normalized
            del table
            gc.collect()
    finally:
        if writer is not None:
            writer.close()

    if not temp_path.exists():
        raise RuntimeError("Nenhuma linha valida foi gerada para PR.")

    temp_path.replace(output_path)
    print(f"Entrada: {input_dir}")
    print(f"Arquivos lidos: {len(seen_paths)}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {total_source_rows}")
    print(f"Linhas parquet: {total_parquet_rows}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
