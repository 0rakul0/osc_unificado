from __future__ import annotations

import argparse
import re
import unicodedata
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_DIR, PROCESSADA_DIR, cli_default
from utils.convenios.unificador import build_parquet_table, clean_currency_text, clean_integer_like_text
from utils.common import STANDARD_COLUMNS, clean_cnpj
from utils.gov_convenios import ORIGEM_GOVERNO_FEDERAL, build_gov_convenios_parser


ORIGEM_PADRAO = "convenios"
FIELDS_TO_ENRICH = [
    "cnpj",
    "nome_osc",
    "cod_municipio",
    "municipio",
    "objeto",
    "modalidade",
    "data_inicio",
    "data_fim",
    "ano",
    "mes",
]
FUZZY_MATCH_UFS = {"PB"}
FUZZY_FIELDS = {"cnpj", "municipio", "cod_municipio", "data_fim"}
FUZZY_CUTOFF = 0.8
KEEP_ROWS_WITHOUT_CNPJ_UFS = {"PI", "RO", "RR"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enriquece os parquets de processada com o CSV federal de convenios."
    )
    parser.add_argument("--processed-dir", default=cli_default(PROCESSADA_DIR))
    parser.add_argument("--base-dir", default=cli_default(BASES_CONVENIOS_DIR))
    parser.add_argument("--gov-file", default="governo/20260227_Convenios.csv")
    parser.add_argument("--ufs", nargs="*", help="Lista opcional de UFs para enriquecer.")
    parser.add_argument(
        "--append-new-rows",
        action="store_true",
        help="Anexa ao parquet as linhas que existem so na base federal. Por padrao, o script apenas enriquece linhas ja existentes.",
    )
    return parser.parse_args()


def is_non_empty(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(str(value).strip())


def normalize_text(value: object) -> str | None:
    if not is_non_empty(value):
        return None
    text = unicodedata.normalize("NFKD", str(value).strip().upper())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text or None


def normalize_cnpj(value: object) -> str | None:
    if not is_non_empty(value):
        return None
    digits = re.sub(r"\D+", "", str(value))
    if not digits:
        return None
    return digits.zfill(14) if len(digits) <= 14 else digits


def normalize_nome_alias(value: object) -> str | None:
    text = normalize_text(value)
    if not text:
        return None

    text = re.sub(
        r"^(?:PREFEITURA MUNICIPAL DE|PREFEITURA DE|PREF MUN DE|PREF MUN|MUNICIPIO DE|MUNICIPIO|MUN DE)\s+",
        "",
        text,
    )
    text = re.sub(r"\b([A-Z]{2})$", "", text).strip()
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_key_series(series: pd.Series, kind: str) -> pd.Series:
    if kind == "cnpj":
        return series.map(normalize_cnpj)
    if kind == "nome":
        return series.map(normalize_text)
    if kind == "alias":
        return series.map(normalize_nome_alias)
    raise ValueError(kind)


def unique_lookup(df: pd.DataFrame, key_col: str, value_col: str) -> dict[str, object]:
    subset = df[[key_col, value_col]].copy()
    subset = subset[subset[key_col].map(is_non_empty) & subset[value_col].map(is_non_empty)]
    lookup: dict[str, object] = {}
    for key, group in subset.groupby(key_col, dropna=True):
        values = [value for value in group[value_col].tolist() if is_non_empty(value)]
        unique_values = []
        for value in values:
            if value not in unique_values:
                unique_values.append(value)
        if len(unique_values) == 1:
            lookup[str(key)] = unique_values[0]
    return lookup


def build_fuzzy_lookup(target_keys: pd.Series, source_lookup: dict[str, object], cutoff: float = FUZZY_CUTOFF) -> dict[str, object]:
    source_keys = [key for key in source_lookup.keys() if key]
    if not source_keys:
        return {}

    fuzzy_lookup: dict[str, object] = {}
    unique_targets = [key for key in target_keys.dropna().astype(str).unique().tolist() if len(key) >= 6]
    for target_key in unique_targets:
        matches = get_close_matches(target_key, source_keys, n=2, cutoff=cutoff)
        if not matches:
            continue
        best_match = matches[0]
        best_score = SequenceMatcher(None, target_key, best_match).ratio()
        if best_score < cutoff:
            continue

        if len(matches) > 1:
            second_score = SequenceMatcher(None, target_key, matches[1]).ratio()
            if second_score >= cutoff and (best_score - second_score) < 0.05:
                continue

        fuzzy_lookup[target_key] = source_lookup[best_match]

    return fuzzy_lookup


def enrich_field(
    target_df: pd.DataFrame,
    source_df: pd.DataFrame,
    field: str,
    uf: str,
    eligible_rows_mask: pd.Series,
) -> int:
    source_by_cnpj = unique_lookup(source_df, "cnpj_key", field)
    source_by_nome = unique_lookup(source_df, "nome_key", field)
    source_by_alias = unique_lookup(source_df, "alias_key", field)
    existing = target_df[field].copy()
    missing_mask = existing.map(is_non_empty).fillna(False).astype(bool).map(lambda value: not value)
    missing_mask = missing_mask & eligible_rows_mask
    if not missing_mask.any():
        return 0

    replacement_by_cnpj = target_df["cnpj_key"].map(source_by_cnpj)
    replacement_by_nome = target_df["nome_key"].map(source_by_nome)
    replacement_by_alias = target_df["alias_key"].map(source_by_alias)
    if field == "nome_osc":
        # Para `nome_osc`, priorizamos somente o match por CNPJ.
        replacement = replacement_by_cnpj
    else:
        replacement = replacement_by_cnpj.combine_first(replacement_by_nome).combine_first(replacement_by_alias)

    if uf in FUZZY_MATCH_UFS and field in FUZZY_FIELDS:
        unresolved_mask = missing_mask & replacement.map(is_non_empty).fillna(False).astype(bool).map(lambda value: not value)
        if unresolved_mask.any():
            fuzzy_lookup = build_fuzzy_lookup(target_df.loc[unresolved_mask, "alias_key"], source_by_alias)
            if fuzzy_lookup:
                replacement_by_fuzzy = target_df["alias_key"].map(fuzzy_lookup)
                replacement = replacement.combine_first(replacement_by_fuzzy)

    replacement = replacement.where(missing_mask, pd.NA)

    filled_count = int(replacement.map(is_non_empty).fillna(False).astype(bool).sum())
    target_df[field] = existing.combine_first(replacement)
    return filled_count


def build_row_key(df: pd.DataFrame) -> pd.Series:
    parts = [
        normalize_key_series(df["cnpj"], "cnpj").fillna(""),
        normalize_key_series(df["nome_osc"], "nome").fillna(""),
        df["ano"].map(lambda value: str(value).strip() if is_non_empty(value) else "").fillna(""),
        df["objeto"].map(lambda value: normalize_text(value) or "").fillna(""),
        clean_currency_text(df["valor_total"]).fillna(""),
    ]
    return parts[0] + "|" + parts[1] + "|" + parts[2] + "|" + parts[3] + "|" + parts[4]


def keep_only_cnpj(series: pd.Series) -> pd.Series:
    return series.map(
        lambda value: value
        if pd.notna(value) and len(re.sub(r"\D+", "", str(value))) == 14
        else pd.NA
    )


def normalize_output_drop_missing_cnpj(uf: str) -> bool:
    return uf.upper() not in KEEP_ROWS_WITHOUT_CNPJ_UFS


def normalize_enriched_output(preview_df: pd.DataFrame, uf: str) -> pd.DataFrame:
    normalized = (
        preview_df.reindex(columns=STANDARD_COLUMNS)
        .assign(
            origem=lambda df: df["origem"].astype("string").str.strip().replace("", pd.NA).fillna(ORIGEM_PADRAO),
            ano=lambda df: clean_integer_like_text(df["ano"]),
            mes=lambda df: clean_integer_like_text(df["mes"]),
            cnpj=lambda df: clean_cnpj(df["cnpj"]),
            valor_total=lambda df: clean_currency_text(df["valor_total"]),
        )
    )

    normalized["cnpj"] = keep_only_cnpj(normalized["cnpj"])
    if normalize_output_drop_missing_cnpj(uf):
        normalized = normalized.dropna(subset=["cnpj"])

    if normalized.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

    normalized = normalized.astype("string")
    return normalized.where(pd.notna(normalized), None)


def append_government_rows(
    current_df: pd.DataFrame,
    gov_df: pd.DataFrame,
    uf: str,
) -> tuple[pd.DataFrame, int]:
    if gov_df.empty:
        return current_df, 0

    current_with_key = current_df.copy()
    current_with_key["_row_key"] = build_row_key(current_with_key)
    current_keys = set(current_with_key["_row_key"].dropna().astype(str))

    gov_normalized = normalize_enriched_output(gov_df.reindex(columns=STANDARD_COLUMNS), uf)
    if gov_normalized.empty:
        return current_df, 0

    gov_with_key = gov_normalized.copy()
    gov_with_key["_row_key"] = build_row_key(gov_with_key)
    gov_with_key = gov_with_key.loc[~gov_with_key["_row_key"].duplicated(keep="first")]
    gov_new_rows = gov_with_key.loc[~gov_with_key["_row_key"].isin(current_keys), STANDARD_COLUMNS]
    if gov_new_rows.empty:
        return current_df, 0

    combined = pd.concat([current_df, gov_new_rows], ignore_index=True)
    return combined, len(gov_new_rows)


def enrich_pr_safely(target_df: pd.DataFrame, source_df: pd.DataFrame) -> int:
    filled = 0

    source_cnpj_by_nome = unique_lookup(source_df, "nome_key", "cnpj")
    source_cnpj_by_alias = unique_lookup(source_df, "alias_key", "cnpj")
    source_municipio_by_nome = unique_lookup(source_df, "nome_key", "municipio")
    source_municipio_by_alias = unique_lookup(source_df, "alias_key", "municipio")
    source_municipio_by_cod = unique_lookup(source_df, "cod_municipio", "municipio")

    existing_cnpj = target_df["cnpj"].copy()
    missing_cnpj_mask = ~existing_cnpj.map(is_non_empty).fillna(False).astype(bool)
    cnpj_replacement = (
        target_df["nome_key"].map(source_cnpj_by_nome).combine_first(
            target_df["alias_key"].map(source_cnpj_by_alias)
        )
    ).where(missing_cnpj_mask, pd.NA)
    filled += int(cnpj_replacement.map(is_non_empty).fillna(False).astype(bool).sum())
    target_df["cnpj"] = existing_cnpj.combine_first(cnpj_replacement)

    existing_municipio = target_df["municipio"].copy()
    missing_municipio_mask = ~existing_municipio.map(is_non_empty).fillna(False).astype(bool)
    municipio_replacement = (
        target_df["nome_key"]
        .map(source_municipio_by_nome)
        .combine_first(target_df["alias_key"].map(source_municipio_by_alias))
        .combine_first(target_df["cod_municipio"].map(source_municipio_by_cod))
        .where(missing_municipio_mask, pd.NA)
    )
    filled += int(municipio_replacement.map(is_non_empty).fillna(False).astype(bool).sum())
    target_df["municipio"] = existing_municipio.combine_first(municipio_replacement)

    return filled


def enrich_parquet(parquet_path: Path, gov_path: Path, append_new_rows: bool = False) -> dict[str, object]:
    uf = parquet_path.stem.upper()
    current_df = pd.read_parquet(parquet_path).reindex(columns=STANDARD_COLUMNS)
    gov_df = build_gov_convenios_parser(uf).parse_workbook(gov_path).reindex(columns=STANDARD_COLUMNS)
    if not gov_df.empty:
        gov_df["origem"] = ORIGEM_GOVERNO_FEDERAL

    if gov_df.empty:
        normalized = normalize_enriched_output(current_df, uf)
        pq.write_table(build_parquet_table(normalized), parquet_path, compression="snappy")
        return {
            "uf": uf,
            "filled": 0,
            "added": 0,
            "rows": len(normalized),
            "removed_without_cnpj": len(current_df) - len(normalized),
        }

    working_df = current_df.copy()
    working_df["cnpj_key"] = normalize_key_series(working_df["cnpj"], "cnpj")
    working_df["nome_key"] = normalize_key_series(working_df["nome_osc"], "nome")
    working_df["alias_key"] = normalize_key_series(working_df["nome_osc"], "alias")

    gov_work = gov_df.copy()
    gov_work["cnpj_key"] = normalize_key_series(gov_work["cnpj"], "cnpj")
    gov_work["nome_key"] = normalize_key_series(gov_work["nome_osc"], "nome")
    gov_work["alias_key"] = normalize_key_series(gov_work["nome_osc"], "alias")

    if uf == "PR":
        filled = enrich_pr_safely(working_df, gov_work)
    else:
        filled = 0
        for field in FIELDS_TO_ENRICH:
            if field == "nome_osc":
                # Excecao segura: podemos preencher `nome_osc` quando o CNPJ ja existe na linha.
                field_eligible_rows_mask = current_df["cnpj"].map(is_non_empty).fillna(False).astype(bool)
            else:
                # Regra de negocio: os demais campos so enriquecem linhas que ainda nao tem CNPJ.
                field_eligible_rows_mask = ~current_df["cnpj"].map(is_non_empty).fillna(False).astype(bool)
            filled += enrich_field(working_df, gov_work, field, uf, field_eligible_rows_mask)

    # `valor_total` sai exclusivamente da consolidacao bruta; o enriquecimento nao toca nesse campo.
    working_df["valor_total"] = current_df["valor_total"]
    working_df["origem"] = current_df.get("origem", ORIGEM_PADRAO)

    normalized_current = normalize_enriched_output(working_df[STANDARD_COLUMNS], uf)
    if append_new_rows:
        normalized, added = append_government_rows(normalized_current, gov_df, uf)
    else:
        normalized, added = normalized_current, 0
    pq.write_table(build_parquet_table(normalized), parquet_path, compression="snappy")

    return {
        "uf": uf,
        "filled": filled,
        "added": added,
        "rows": len(normalized),
        "removed_without_cnpj": len(current_df) - len(normalized_current),
    }


def main() -> None:
    args = parse_args()
    processed_dir = Path(args.processed_dir)
    base_dir = Path(args.base_dir)
    gov_path = base_dir / args.gov_file

    target_ufs = {uf.upper() for uf in args.ufs} if args.ufs else None
    results: list[dict[str, object]] = []

    for parquet_path in sorted(processed_dir.glob("*.parquet")):
        if parquet_path.name.endswith(".partial.parquet"):
            continue
        uf = parquet_path.stem.upper()
        if target_ufs and uf not in target_ufs:
            continue
        results.append(enrich_parquet(parquet_path, gov_path, append_new_rows=args.append_new_rows))

    for result in results:
        print(
            f"{result['uf']}: preenchidos={result['filled']} adicionados={result['added']} removidos_sem_cnpj={result['removed_without_cnpj']} total_final={result['rows']}"
        )


if __name__ == "__main__":
    main()
