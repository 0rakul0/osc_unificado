from __future__ import annotations

from io import StringIO
from pathlib import Path
import re
import sys
import unicodedata

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, GOVERNO_FEDERAL_DIR, HISTORIA_DATA_DIR, ensure_parent_dir


RAW_DIR = BASES_CONVENIOS_CAPITAIS_DIR / "Porto Alegre" / "despesas_por_favorecido_raw"
GOV_PATH = GOVERNO_FEDERAL_DIR / "RS.parquet"
OUTPUT_DIR = HISTORIA_DATA_DIR / "porto_alegre_lookup_governo"
LOOKUP_OUTPUT = OUTPUT_DIR / "porto_alegre_lookup_nome_para_cnpj_governo.csv"
MATCHED_ROWS_OUTPUT = OUTPUT_DIR / "porto_alegre_favorecidos_com_lookup_governo.csv"
MATCHED_UNIQUE_OUTPUT = OUTPUT_DIR / "porto_alegre_nomes_unicos_com_lookup_governo.csv"
MATCHED_UNIQUE_NONPUBLIC_OUTPUT = OUTPUT_DIR / "porto_alegre_nomes_unicos_com_lookup_governo_nao_publico_aparente.csv"
YEAR_SUMMARY_OUTPUT = OUTPUT_DIR / "porto_alegre_lookup_governo_por_ano.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "porto_alegre_lookup_governo_resumo.md"


def normalize_text(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = unicodedata.normalize("NFKD", str(value).strip().upper())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_alias(value: object) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    text = re.sub(
        r"^(?:PREFEITURA MUNICIPAL DE|PREFEITURA DE|PREF MUN DE|PREF MUN|MUNICIPIO DE|MUNICIPIO|MUN DE)\s+",
        "",
        text,
    )
    text = re.sub(r"\b(?:RS|POA)$", "", text).strip()
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def is_public_like_name(value: object) -> bool:
    text = normalize_text(value)
    if not text:
        return False
    return bool(
        re.search(
            r"\b("
            r"PREFEITURA|MUNICIPIO|SECRETARIA|GOVERNO|ESTADO DO|CAMARA|ASSEMBLEIA|TRIBUNAL|"
            r"UNIAO|FUNDO MUNICIPAL|BRIGADA|POLICIA|MINISTERIO PUBLICO|DEFENSORIA|SENADO|"
            r"SUPERINTENDENCIA|DEPARTAMENTO ESTADUAL|UNIVERSIDADE FEDERAL|HOSPITAL MUNICIPAL"
            r")\b",
            text,
        )
    )


def parse_raw_csv(path: Path) -> pd.DataFrame:
    text = path.read_bytes().decode("latin-1", errors="replace")
    lines = [line for line in text.splitlines() if line.strip()]
    header_index = next(
        index for index, line in enumerate(lines) if "Exerc" in line and ";" in line
    )
    frame = pd.read_csv(StringIO("\n".join(lines[header_index:])), sep=";", dtype=str)
    year_match = re.search(r"_(\d{4})_", path.name)
    year = int(year_match.group(1)) if year_match else pd.NA
    name_col = frame.columns[2]
    return pd.DataFrame(
        {
            "ano": year,
            "arquivo_origem": path.name,
            "nome_favorecido": frame[name_col],
        }
    )


def load_raw_favorecidos() -> pd.DataFrame:
    paths = sorted(RAW_DIR.glob("portoalegre_despesas_favorecido_*.csv"))
    if not paths:
        raise FileNotFoundError(f"Nenhum bruto encontrado em {RAW_DIR}")

    frame = pd.concat((parse_raw_csv(path) for path in paths), ignore_index=True)
    frame["nome_key"] = frame["nome_favorecido"].map(normalize_text)
    frame["alias_key"] = frame["nome_favorecido"].map(normalize_alias)
    frame = frame.dropna(subset=["nome_key"]).copy()
    return frame


def load_governo_lookup_base() -> pd.DataFrame:
    if not GOV_PATH.exists():
        raise FileNotFoundError(f"Arquivo de governo nao encontrado: {GOV_PATH}")

    frame = pq.read_table(GOV_PATH, columns=["cnpj", "nome_osc"]).to_pandas()
    frame["cnpj"] = frame["cnpj"].astype("string").str.replace(r"\D", "", regex=True)
    frame = frame[frame["cnpj"].str.len().eq(14).fillna(False)].copy()
    frame["nome_key"] = frame["nome_osc"].map(normalize_text)
    frame["alias_key"] = frame["nome_osc"].map(normalize_alias)
    frame = frame.dropna(subset=["nome_key"]).copy()
    return frame


def build_unique_lookup(frame: pd.DataFrame, key_column: str) -> pd.DataFrame:
    grouped = (
        frame.dropna(subset=[key_column])
        .groupby(key_column, dropna=True)
        .agg(
            nome_governo=("nome_osc", "first"),
            cnpjs=("cnpj", lambda values: sorted(set(values))),
            ocorrencias_governo=("cnpj", "size"),
        )
        .reset_index()
    )
    grouped["qtd_cnpjs_unicos"] = grouped["cnpjs"].map(len)
    grouped = grouped[grouped["qtd_cnpjs_unicos"].eq(1)].copy()
    grouped["cnpj"] = grouped["cnpjs"].map(lambda values: values[0])
    return grouped[[key_column, "nome_governo", "cnpj", "ocorrencias_governo"]]


def build_matches(raw: pd.DataFrame, gov: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    lookup_nome = build_unique_lookup(gov, "nome_key").rename(
        columns={
            "nome_governo": "nome_governo_nome",
            "cnpj": "cnpj_nome",
            "ocorrencias_governo": "ocorrencias_governo_nome",
        }
    )
    lookup_alias = build_unique_lookup(gov, "alias_key").rename(
        columns={
            "nome_governo": "nome_governo_alias",
            "cnpj": "cnpj_alias",
            "ocorrencias_governo": "ocorrencias_governo_alias",
        }
    )

    merged = raw.merge(lookup_nome, on="nome_key", how="left")
    merged = merged.merge(lookup_alias, on="alias_key", how="left")

    merged["cnpj"] = merged["cnpj_nome"].combine_first(merged["cnpj_alias"])
    merged["nome_governo"] = merged["nome_governo_nome"].combine_first(merged["nome_governo_alias"])
    merged["metodo_match"] = pd.Series(pd.NA, index=merged.index, dtype="string")
    merged.loc[merged["cnpj_nome"].notna(), "metodo_match"] = "nome_exato"
    merged.loc[merged["cnpj_nome"].isna() & merged["cnpj_alias"].notna(), "metodo_match"] = "alias"

    matched = merged[merged["cnpj"].notna()].copy()
    unique_names = (
        matched.sort_values(["nome_key", "metodo_match", "ano"])
        .drop_duplicates(subset=["nome_key"], keep="first")
        .loc[:, ["nome_favorecido", "nome_key", "alias_key", "cnpj", "nome_governo", "metodo_match"]]
        .rename(columns={"nome_favorecido": "nome_favorecido_exemplo"})
        .sort_values(["metodo_match", "nome_favorecido_exemplo"])
        .reset_index(drop=True)
    )
    return matched, unique_names


def build_year_summary(raw: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    raw_year = raw.groupby("ano", dropna=False).agg(
        favorecidos_linhas=("ano", "size"),
        nomes_unicos=("nome_key", "nunique"),
    )
    matched_year = matched.groupby("ano", dropna=False).agg(
        linhas_recuperadas=("ano", "size"),
        nomes_unicos_recuperados=("nome_key", "nunique"),
    )
    summary = raw_year.join(matched_year, how="left").fillna(0).reset_index()
    for column in [
        "favorecidos_linhas",
        "nomes_unicos",
        "linhas_recuperadas",
        "nomes_unicos_recuperados",
    ]:
        summary[column] = summary[column].astype(int)
    summary["cobertura_linhas_pct"] = (
        summary["linhas_recuperadas"] / summary["favorecidos_linhas"] * 100
    ).round(2)
    summary["cobertura_nomes_pct"] = (
        summary["nomes_unicos_recuperados"] / summary["nomes_unicos"] * 100
    ).round(2)
    return summary.sort_values("ano").reset_index(drop=True)


def build_summary_text(raw: pd.DataFrame, matched: pd.DataFrame, unique_names: pd.DataFrame, year_summary: pd.DataFrame) -> str:
    total_rows = len(raw)
    total_unique = int(raw["nome_key"].nunique())
    matched_rows = len(matched)
    matched_unique = int(unique_names["nome_key"].nunique())
    public_like_unique = int(unique_names["publico_aparente"].sum())
    nonpublic_like_unique = int((~unique_names["publico_aparente"]).sum())

    metodo_counts = matched["metodo_match"].value_counts(dropna=False).to_dict()
    top_years = year_summary.sort_values("linhas_recuperadas", ascending=False).head(5)

    lines = [
        "# Porto Alegre - Lookup com Governo",
        "",
        f"- Pasta de brutos analisada: `{RAW_DIR}`",
        f"- Base de governo usada: `{GOV_PATH}`",
        "",
        "## Cobertura geral",
        "",
        f"- Linhas de favorecidos avaliadas: {total_rows:,}".replace(",", "."),
        f"- Nomes unicos avaliados: {total_unique:,}".replace(",", "."),
        f"- Linhas com CNPJ recuperado: {matched_rows:,}".replace(",", "."),
        f"- Nomes unicos com CNPJ recuperado: {matched_unique:,}".replace(",", "."),
        f"- Cobertura por linhas: {matched_rows / total_rows * 100:.2f}%",
        f"- Cobertura por nomes unicos: {matched_unique / total_unique * 100:.2f}%",
        f"- Nomes unicos com cara de ente publico: {public_like_unique:,}".replace(",", "."),
        f"- Nomes unicos nao publicos aparentes: {nonpublic_like_unique:,}".replace(",", "."),
        "",
        "## Metodo de match",
        "",
        f"- `nome_exato`: {metodo_counts.get('nome_exato', 0):,} linhas".replace(",", "."),
        f"- `alias`: {metodo_counts.get('alias', 0):,} linhas".replace(",", "."),
        "",
        "## Anos com mais recuperacao",
        "",
    ]

    for row in top_years.itertuples(index=False):
        lines.append(
            f"- {row.ano}: {row.linhas_recuperadas:,} linhas e {row.nomes_unicos_recuperados:,} nomes unicos recuperados".replace(",", ".")
        )

    lines.extend(
        [
            "",
            "## Leitura pratica",
            "",
            "- O cruzamento com a base federal do RS ajuda principalmente entidades do terceiro setor e instituicoes recorrentes em convenios.",
            "- A cobertura continua parcial porque a despesa municipal inclui muitos fornecedores privados que nao aparecem como convenentes na trilha federal.",
            "- O lookup salvo pode ser usado como etapa complementar antes de abrir o detalhe do empenho no portal.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    ensure_parent_dir(SUMMARY_OUTPUT)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw = load_raw_favorecidos()
    gov = load_governo_lookup_base()
    matched, unique_names = build_matches(raw, gov)
    unique_names["publico_aparente"] = unique_names["nome_favorecido_exemplo"].map(is_public_like_name)
    year_summary = build_year_summary(raw, matched)

    matched.to_csv(MATCHED_ROWS_OUTPUT, index=False, encoding="utf-8-sig")
    unique_names.to_csv(MATCHED_UNIQUE_OUTPUT, index=False, encoding="utf-8-sig")
    unique_names.to_csv(LOOKUP_OUTPUT, index=False, encoding="utf-8-sig")
    unique_names.loc[~unique_names["publico_aparente"]].to_csv(
        MATCHED_UNIQUE_NONPUBLIC_OUTPUT,
        index=False,
        encoding="utf-8-sig",
    )
    year_summary.to_csv(YEAR_SUMMARY_OUTPUT, index=False, encoding="utf-8-sig")
    SUMMARY_OUTPUT.write_text(
        build_summary_text(raw, matched, unique_names, year_summary),
        encoding="utf-8",
    )

    print(f"Lookup salvo em: {LOOKUP_OUTPUT}")
    print(f"Linhas com match salvas em: {MATCHED_ROWS_OUTPUT}")
    print(f"Nomes unicos com match salvos em: {MATCHED_UNIQUE_OUTPUT}")
    print(f"Nomes unicos nao publicos aparentes salvos em: {MATCHED_UNIQUE_NONPUBLIC_OUTPUT}")
    print(f"Resumo por ano salvo em: {YEAR_SUMMARY_OUTPUT}")
    print(f"Resumo markdown salvo em: {SUMMARY_OUTPUT}")
    print(f"Linhas recuperadas: {len(matched)}")
    print(f"Nomes unicos recuperados: {unique_names['nome_key'].nunique()}")


if __name__ == "__main__":
    main()
