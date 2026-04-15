from __future__ import annotations

import argparse
import gc
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_DIR, PROCESSADA_DIR, cli_default
from utils import get_parser
from utils.common import STANDARD_COLUMNS, clean_cnpj


ORIGEM_PADRAO = "convenios"
PARQUET_MONEY_PRECISION = 20
PARQUET_MONEY_SCALE = 2
PARQUET_SCHEMA = pa.schema(
    [
        pa.field(
            column,
            pa.decimal128(PARQUET_MONEY_PRECISION, PARQUET_MONEY_SCALE) if column == "valor_total" else pa.string(),
        )
        for column in STANDARD_COLUMNS
    ]
)
EXTRA_INPUT_FILES = {
    "PA": ["*.csv"],
    "GO": ["convenios_2008_2018.zip"],
    "RJ": [
        "transferencias-voluntarias-aos-municipios-2015-a-2023.csv",
        "transferencias-voluntarias-aos-municipios-2024.csv",
    ],
    "RS": ["ConveniosDespesa-RS.csv"],
}
EXCLUSIVE_INPUT_FILES = {
    "AC": ["convenios_ac.csv"],
    "DF": ["dados_credor_convenios_DF.xlsx"],
    "ES": [
        "convenios-*.csv",
        "aditivosconvenios-*.csv",
        "conveniosexecucaoorcamentaria-*.csv",
    ],
    "PI": ["convenios_pi_v2.xlsx"],
    "PR": ["CONVENIOS-*/TB_CONVENIO_EMPREENDIMENTO-*.csv"],
}


def list_workbooks(base_dir: Path, uf: str) -> list[Path]:
    uf_dir = base_dir / uf
    if not uf_dir.exists():
        return []

    exclusive_patterns = EXCLUSIVE_INPUT_FILES.get(uf.upper())
    if exclusive_patterns:
        paths = {path.resolve(): path for pattern in exclusive_patterns for path in uf_dir.rglob(pattern)}
        return sorted(paths.values())

    paths = {path.resolve(): path for path in uf_dir.rglob("*.xlsx")}
    for pattern in EXTRA_INPUT_FILES.get(uf.upper(), []):
        for path in uf_dir.rglob(pattern):
            paths[path.resolve()] = path

    return sorted(paths.values())


def workbook_total_bytes(base_dir: Path, uf: str) -> int:
    return sum(workbook_path.stat().st_size for workbook_path in list_workbooks(base_dir, uf))


def order_ufs_by_workbook_size(base_dir: Path, ufs: list[str]) -> list[str]:
    return sorted(ufs, key=lambda uf: (workbook_total_bytes(base_dir, uf), uf))


def is_uf_directory(path: Path) -> bool:
    name = path.name
    return path.is_dir() and len(name) == 2 and name.isalpha() and name.upper() == name


def clean_required_text(series: pd.Series) -> pd.Series:
    def normalize(value: object) -> object:
        if pd.isna(value):
            return pd.NA

        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null"}:
            return pd.NA

        if text.replace(" ", "") in {"-", "--"}:
            return pd.NA

        return text

    return series.map(normalize)


def clean_currency_value(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return pd.NA

    compact = text.replace("\xa0", "").replace(" ", "")
    compact = compact.removeprefix("R$")
    if compact in {"", "-", "--"}:
        return pd.NA

    if compact.startswith("(") and compact.endswith(")"):
        compact = f"-{compact[1:-1]}"

    if "," in compact and "." in compact:
        if compact.rfind(",") > compact.rfind("."):
            compact = compact.replace(".", "").replace(",", ".")
        else:
            compact = compact.replace(",", "")
    elif "," in compact:
        compact = compact.replace(".", "").replace(",", ".")
    elif compact.count(".") > 1:
        compact = compact.replace(".", "")

    compact = re.sub(r"[^0-9.+\-eE]", "", compact)
    if not compact:
        return pd.NA

    try:
        numeric = Decimal(compact)
    except InvalidOperation:
        return pd.NA

    if abs(numeric) < Decimal("0.005"):
        numeric = Decimal("0")
    else:
        numeric = numeric.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    normalized = format(numeric, "f").rstrip("0").rstrip(".")
    return normalized if normalized and normalized != "-0" else "0"


def clean_currency_text(series: pd.Series) -> pd.Series:
    return series.map(clean_currency_value)


def parse_currency_decimal(value: object) -> Decimal | None:
    normalized = clean_currency_value(value)
    if pd.isna(normalized):
        return None
    return Decimal(str(normalized)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def clean_integer_like_text(series: pd.Series) -> pd.Series:
    def normalize(value: object) -> object:
        if pd.isna(value):
            return pd.NA

        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null"}:
            return pd.NA

        if text.replace(" ", "") in {"-", "--"}:
            return pd.NA

        if text.isdigit():
            return text

        if "." in text:
            try:
                numeric = float(text)
            except ValueError:
                return text
            if numeric.is_integer():
                return str(int(numeric))

        return text

    return series.map(normalize)


def has_cnpj_value(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).strip()
    return len(text) == 14


def normalize_preview(preview_df: pd.DataFrame, uf: str, require_cnpj: bool = False) -> pd.DataFrame:
    normalized = (
        preview_df.reindex(columns=STANDARD_COLUMNS)
        .assign(
            origem=lambda df: clean_required_text(df["origem"]).fillna(ORIGEM_PADRAO),
            ano=lambda df: clean_integer_like_text(df["ano"]),
            mes=lambda df: clean_integer_like_text(df["mes"]),
            cnpj=lambda df: clean_cnpj(df["cnpj"]),
            valor_total=lambda df: clean_currency_text(df["valor_total"]),
        )
        .dropna(subset=["valor_total"])
    )

    if uf.upper() == "RJ":
        normalized = normalized.dropna(subset=["cnpj"])

    if require_cnpj:
        normalized = normalized[normalized["cnpj"].map(has_cnpj_value)]

    if normalized.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

    normalized = normalized.astype("string")
    return normalized.where(pd.notna(normalized), None)


def build_parquet_table(preview_df: pd.DataFrame) -> pa.Table:
    working = preview_df.copy()
    for column in STANDARD_COLUMNS:
        if column not in working.columns:
            working[column] = None
    working = working[STANDARD_COLUMNS]
    if "origem" in working.columns:
        working["origem"] = working["origem"].map(
            lambda value: ORIGEM_PADRAO if pd.isna(value) or not str(value).strip() else str(value).strip()
        )

    arrays = []
    for column in STANDARD_COLUMNS:
        values = working[column].tolist()
        if column == "valor_total":
            arrays.append(
                pa.array(
                    [parse_currency_decimal(value) for value in values],
                    type=pa.decimal128(PARQUET_MONEY_PRECISION, PARQUET_MONEY_SCALE),
                )
            )
        else:
            arrays.append(pa.array([None if pd.isna(value) else str(value) for value in values], type=pa.string()))
    return pa.Table.from_arrays(arrays, schema=PARQUET_SCHEMA)


def processed_output_path(processed_dir: Path, uf: str) -> Path:
    return processed_dir / f"{uf.upper()}.parquet"


def partial_output_path(processed_dir: Path, uf: str) -> Path:
    return processed_dir / f"{uf.upper()}.partial.parquet"


def list_processed_ufs(processed_dir: Path) -> set[str]:
    if not processed_dir.exists():
        return set()

    processed: set[str] = set()
    for parquet_path in processed_dir.glob("*.parquet"):
        if parquet_path.name.endswith(".partial.parquet"):
            continue
        processed.add(parquet_path.stem.upper())
    return processed


def write_empty_parquet(output_path: Path) -> None:
    empty_df = pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")
    pq.write_table(build_parquet_table(empty_df), output_path, compression="snappy")


def write_previews_parquet(
    base_dir: Path,
    ufs: list[str],
    processed_dir: Path,
    preview_rows: int | None = None,
    force: bool = False,
) -> tuple[dict[str, int], list[str]]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed_counts: dict[str, int] = {}
    skipped_ufs: list[str] = []

    for uf in ufs:
        final_path = processed_output_path(processed_dir, uf)
        temp_path = partial_output_path(processed_dir, uf)

        if final_path.exists() and not force:
            skipped_ufs.append(uf)
            continue

        if final_path.exists():
            final_path.unlink()

        if temp_path.exists():
            temp_path.unlink()

        parser = get_parser(uf)
        writer: pq.ParquetWriter | None = None
        total_rows = 0

        try:
            for workbook_path in list_workbooks(base_dir, uf):
                try:
                    preview_df = parser.parse_workbook(workbook_path, preview_rows=preview_rows)
                except Exception as exc:
                    print(f"[aviso] UF {uf}: falha ao ler {workbook_path.name}: {exc}")
                    gc.collect()
                    continue
                preview_df = normalize_preview(preview_df, uf)
                if preview_df.empty:
                    del preview_df
                    gc.collect()
                    continue

                table = build_parquet_table(preview_df)
                if writer is None:
                    writer = pq.ParquetWriter(temp_path, PARQUET_SCHEMA, compression="snappy")
                writer.write_table(table)
                total_rows += len(preview_df)

                del preview_df
                del table
                gc.collect()
        finally:
            if writer is not None:
                writer.close()

        if not temp_path.exists():
            write_empty_parquet(temp_path)

        temp_path.replace(final_path)
        processed_counts[uf] = total_rows
        gc.collect()

    return processed_counts, skipped_ufs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consolida os XLSX por UF em arquivos Parquet separados."
    )
    parser.add_argument("--base-dir", default=cli_default(BASES_CONVENIOS_DIR), help="Diretorio raiz com as subpastas por UF.")
    parser.add_argument("--ufs", nargs="*", help="Lista de UFs a processar. Se vazio, usa todas encontradas em bases_convenios/.")
    parser.add_argument("--skip-ufs", nargs="*", default=[], help="Lista de UFs a pular explicitamente.")
    parser.add_argument("--preview-rows", type=int, default=None, help="Quantidade de linhas lidas por aba. Se omitido, le todas.")
    parser.add_argument("--processed-dir", default=cli_default(PROCESSADA_DIR), help="Pasta onde os arquivos parquet por UF serao salvos.")
    parser.add_argument("--force", action="store_true", help="Reprocessa a UF mesmo que o parquet final ja exista.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(args.base_dir)
    processed_dir = Path(args.processed_dir)
    available_ufs = sorted(path.name.upper() for path in base_dir.iterdir() if is_uf_directory(path))
    skipped_by_arg = {uf.upper() for uf in args.skip_ufs}
    requested_ufs = [uf.upper() for uf in (args.ufs or available_ufs)]
    requested_ufs = [uf for uf in requested_ufs if uf not in skipped_by_arg]
    requested_ufs = order_ufs_by_workbook_size(base_dir, requested_ufs)

    if not args.force:
        done_ufs = list_processed_ufs(processed_dir)
        ufs_to_process = [uf for uf in requested_ufs if uf not in done_ufs]
    else:
        done_ufs = set()
        ufs_to_process = requested_ufs

    processed_counts, skipped_ufs = write_previews_parquet(
        base_dir=base_dir,
        ufs=ufs_to_process,
        processed_dir=processed_dir,
        preview_rows=args.preview_rows,
        force=args.force,
    )

    processed_total = sum(processed_counts.values())
    already_processed = sorted(done_ufs.intersection(requested_ufs))
    skipped_total = sorted(set(already_processed + skipped_ufs + list(skipped_by_arg)))

    print(f"Pasta de saida: {processed_dir}")
    print(f"Ordem de processamento: {', '.join(ufs_to_process) if ufs_to_process else 'nenhuma'}")
    print(f"Linhas consolidadas nesta execucao: {processed_total}")
    print(f"UFs processadas nesta execucao: {', '.join(processed_counts) if processed_counts else 'nenhuma'}")
    print(f"UFs ja processadas/puladas: {', '.join(skipped_total) if skipped_total else 'nenhuma'}")


if __name__ == "__main__":
    main()
