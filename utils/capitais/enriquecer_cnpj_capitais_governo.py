from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import polars as pl

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import CAPITAIS_PROCESSADA_DIR, GOVERNO_FEDERAL_DIR


CAPITAIS_DIR = CAPITAIS_PROCESSADA_DIR
GOVERNO_DIR = GOVERNO_FEDERAL_DIR

TARGETS = {
    "MT_CUIABA": "MT",
    "PA_BELEM": "PA",
    "PR_CURITIBA": "PR",
    "RS_PORTO_ALEGRE": "RS",
    "SE_ARACAJU": "SE",
    "GO_GOIANIA": "GO",
    "RS_PORTO_ALEGRE_DESPESAS": "RS",
    "PR_CURITIBA_DESPESAS": "PR",
}

PUBLIC_TERMS = re.compile(
    r"\b(MUNICIPIO|PREFEITURA|SECRETARIA|FUNDO MUNICIPAL|FUNDO ESTADUAL|"
    r"ESTADO DO|ESTADO DE|CAMARA MUNICIPAL|TRIBUNAL DE JUSTICA)\b"
)
LEGAL_TERMS = re.compile(
    r"\b(ASSOCIACAO|ASSOCIACAO|INSTITUTO|FUNDACAO|SOCIEDADE|CENTRO|GRUPO|"
    r"CASA|LAR|OBRA|OBRAS|ORATORIO|FEDERACAO|CONFEDERACAO)\b"
)


def normalize_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text or text in {"NULL", "NAN", "NONE"}:
        return None
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_alias(value: object) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    text = LEGAL_TERMS.sub(" ", text)
    text = re.sub(r"\b(DE|DA|DO|DAS|DOS|E|A|O|AS|OS)\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def unique_lookup(frame: pl.DataFrame, key_column: str, prefix: str) -> pl.DataFrame:
    rows: list[dict[str, object]] = []
    for key, subset in frame.drop_nulls(key_column).group_by(key_column):
        key_value = key[0] if isinstance(key, tuple) else key
        cnpjs = sorted(set(subset["cnpj"].drop_nulls().to_list()))
        if len(cnpjs) == 1:
            rows.append(
                {
                    key_column: key_value,
                    f"cnpj_{prefix}": cnpjs[0],
                    f"nome_governo_{prefix}": subset["nome_osc"][0],
                    f"ocorrencias_governo_{prefix}": len(subset),
                }
            )
    return pl.DataFrame(rows) if rows else pl.DataFrame(
        {
            key_column: [],
            f"cnpj_{prefix}": [],
            f"nome_governo_{prefix}": [],
            f"ocorrencias_governo_{prefix}": [],
        }
    )


def build_matches(capital_path: Path, governo_path: Path) -> pl.DataFrame:
    capital = pl.read_parquet(capital_path).with_row_index("_row_id")
    candidates = capital.filter(pl.col("cnpj").is_null() & pl.col("nome_osc").is_not_null())
    if candidates.is_empty():
        return pl.DataFrame()

    governo = (
        pl.read_parquet(governo_path, columns=["cnpj", "nome_osc"])
        .filter(pl.col("cnpj").is_not_null() & pl.col("nome_osc").is_not_null())
        .with_columns(
            pl.col("cnpj").str.replace_all(r"\D", "").alias("cnpj"),
            pl.col("nome_osc").map_elements(normalize_text, return_dtype=pl.String).alias("nome_key"),
            pl.col("nome_osc").map_elements(normalize_alias, return_dtype=pl.String).alias("alias_key"),
        )
        .filter(pl.col("cnpj").str.len_chars() == 14)
    )

    lookup_nome = unique_lookup(governo, "nome_key", "nome")
    lookup_alias = unique_lookup(governo, "alias_key", "alias")

    return (
        candidates.with_columns(
            pl.col("nome_osc").map_elements(normalize_text, return_dtype=pl.String).alias("nome_key"),
            pl.col("nome_osc").map_elements(normalize_alias, return_dtype=pl.String).alias("alias_key"),
            pl.col("nome_osc")
            .map_elements(lambda value: bool(PUBLIC_TERMS.search(normalize_text(value) or "")), return_dtype=pl.Boolean)
            .alias("aparenta_publico"),
        )
        .join(lookup_nome, on="nome_key", how="left")
        .join(lookup_alias, on="alias_key", how="left")
        .with_columns(
            pl.coalesce(["cnpj_nome", "cnpj_alias"]).alias("cnpj_encontrado"),
            pl.when(pl.col("cnpj_nome").is_not_null())
            .then(pl.lit("nome_exato"))
            .when(pl.col("cnpj_alias").is_not_null())
            .then(pl.lit("alias"))
            .otherwise(None)
            .alias("metodo_match"),
            pl.coalesce(["nome_governo_nome", "nome_governo_alias"]).alias("nome_governo_match"),
        )
        .filter(pl.col("cnpj_encontrado").is_not_null())
    )


def enrich_capital(capital: str, uf: str, write: bool) -> dict[str, object]:
    capital_path = CAPITAIS_DIR / f"{capital}.parquet"
    governo_path = GOVERNO_DIR / f"{uf}.parquet"
    frame = pl.read_parquet(capital_path)
    null_before = frame.filter(pl.col("cnpj").is_null()).height
    matches = build_matches(capital_path, governo_path)

    if write and not matches.is_empty():
        updates = matches.select("_row_id", pl.col("cnpj_encontrado").alias("cnpj_governo"))
        enriched = (
            frame.with_row_index("_row_id")
            .join(updates, on="_row_id", how="left")
            .with_columns(pl.coalesce(["cnpj", "cnpj_governo"]).alias("cnpj"))
            .drop("_row_id", "cnpj_governo")
        )
        enriched.write_parquet(capital_path)
        frame_after = enriched
    else:
        frame_after = frame

    null_after = frame_after.filter(pl.col("cnpj").is_null()).height
    return {
        "capital": capital,
        "linhas": frame.height,
        "cnpj_nulo_antes": null_before,
        "linhas_enriquecidas": matches.height,
        "nomes_unicos_enriquecidos": matches.select("nome_osc").n_unique() if not matches.is_empty() else 0,
        "matches_aparente_publico": matches.filter(pl.col("aparenta_publico")).height if not matches.is_empty() else 0,
        "cnpj_nulo_depois": null_after,
        "gravado": write and not matches.is_empty(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preenche CNPJs nulos de capitais por match unico de nome na base de governo federal da mesma UF."
    )
    parser.add_argument("--capitais", nargs="*", default=list(TARGETS), help="Capitais no formato UF_CIDADE.")
    parser.add_argument("--write", action="store_true", help="Grava os CNPJs encontrados nos parquets das capitais.")
    args = parser.parse_args()

    summaries = []
    all_matches = []
    for capital in args.capitais:
        uf = TARGETS[capital]
        matches = build_matches(CAPITAIS_DIR / f"{capital}.parquet", GOVERNO_DIR / f"{uf}.parquet")
        if not matches.is_empty():
            all_matches.append(
                matches.with_columns(pl.lit(capital).alias("capital")).select(
                    "capital",
                    "_row_id",
                    "ano",
                    "valor_total",
                    "nome_osc",
                    "cnpj_encontrado",
                    "nome_governo_match",
                    "metodo_match",
                    "aparenta_publico",
                )
            )
        summaries.append(enrich_capital(capital, uf, args.write))

    summary = pl.DataFrame(summaries)
    summary_path = CAPITAIS_DIR / "relatorio_lookup_cnpj_governo_capitais.csv"
    summary.write_csv(summary_path)
    print(summary)
    print(f"Relatorio: {summary_path}")

    if all_matches:
        matches_path = CAPITAIS_DIR / "matches_lookup_cnpj_governo_capitais.csv"
        pl.concat(all_matches, how="diagonal").write_csv(matches_path)
        print(f"Matches: {matches_path}")


if __name__ == "__main__":
    main()
