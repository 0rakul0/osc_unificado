from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import re
import sqlite3
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, HISTORIA_DATA_DIR, SQLITE_PATH, cli_default, ensure_parent_dir
from utils.capitais.shared import CAPITAL_CONFIGS, find_source_files
from utils.orcamento_geral.registry import STATE_CAPITALS


DEFAULT_OUTPUT = HISTORIA_DATA_DIR / "auditoria_valor_total_zerado_capitais.xlsx"
YEAR_MISSING_LABEL = "(sem ano)"
TABLE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DEFAULT_TABLE = "transferencias"
DEFAULT_ORIGEM = "capitais"
LOW_COVERAGE_LIMIT = 3
YEAR_IN_TEXT_RE = re.compile(r"(19|20)\d{2}")

STATE_NAMES = {item.uf: item.estado for item in STATE_CAPITALS}
CAPITAL_NAMES = {item.uf: item.capital for item in STATE_CAPITALS}
DEFAULT_UF_ORDER = [item.uf for item in STATE_CAPITALS]
CAPITAL_CONFIG_BY_UF = {config.uf: config for config in CAPITAL_CONFIGS}


def validate_table_name(table_name: str) -> str:
    if not TABLE_NAME_RE.match(table_name):
        raise ValueError(f"Nome de tabela invalido: {table_name!r}")
    return table_name


def normalize_year(value: object) -> str:
    if pd.isna(value):
        return YEAR_MISSING_LABEL

    text = str(value).strip()
    if not text:
        return YEAR_MISSING_LABEL

    if text.isdigit():
        return text

    try:
        numeric = float(text)
    except ValueError:
        return text

    if numeric.is_integer():
        return str(int(numeric))
    return text


def to_decimal(value: object) -> Decimal | None:
    if pd.isna(value):
        return None

    if isinstance(value, Decimal):
        return value

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace("R$", "").replace(" ", "")
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")

    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def to_centavos(value: object) -> int | None:
    decimal_value = to_decimal(value)
    if decimal_value is None:
        return None

    quantized = decimal_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(quantized * 100)


def year_sort_key(value: object) -> tuple[int, object]:
    text = str(value)
    return (0, int(text)) if text.isdigit() else (1, text)


def ordered_ufs(values: list[str]) -> list[str]:
    unique_values = []
    seen: set[str] = set()
    for value in values:
        uf = str(value).upper()
        if uf in seen:
            continue
        seen.add(uf)
        unique_values.append(uf)

    prioritized = [uf for uf in DEFAULT_UF_ORDER if uf in seen]
    extras = sorted(uf for uf in unique_values if uf not in DEFAULT_UF_ORDER)
    return prioritized + extras


def column_label(uf: str) -> str:
    estado = STATE_NAMES.get(uf, uf)
    capital = CAPITAL_NAMES.get(uf, "")
    if capital:
        return f"{uf} - {estado} ({capital})"
    return f"{uf} - {estado}"


def load_transferencias(sqlite_path: Path, table_name: str, origem: str) -> pd.DataFrame:
    query = (
        f"SELECT uf, ano, municipio, valor_total "
        f"FROM {validate_table_name(table_name)} "
        f"WHERE origem = ?"
    )
    with sqlite3.connect(sqlite_path) as connection:
        return pd.read_sql_query(query, connection, params=[origem])


def build_summary(df: pd.DataFrame, selected_anos: set[str] | None = None) -> pd.DataFrame:
    frame = df.copy()
    frame["uf"] = frame["uf"].astype("string").str.upper().fillna("")
    frame["ano_normalizado"] = frame["ano"].map(normalize_year)
    frame["valor_centavos"] = frame["valor_total"].map(to_centavos)
    frame["valor_centavos_preenchido"] = frame["valor_centavos"].fillna(0).astype("int64")
    frame["valor_total_zerado"] = frame["valor_centavos_preenchido"].eq(0)
    frame["valor_total_ausente"] = frame["valor_centavos"].isna()

    if selected_anos is not None:
        frame = frame.loc[frame["ano_normalizado"].isin(selected_anos)].copy()

    grouped = (
        frame.groupby(["ano_normalizado", "uf"], dropna=False)
        .agg(
            capital=(
                "municipio",
                lambda values: ", ".join(
                    sorted(
                        {
                            str(value).strip()
                            for value in values
                            if pd.notna(value) and str(value).strip()
                        }
                    )
                ),
            ),
            total_registros=("uf", "size"),
            registros_valor_zero=("valor_total_zerado", "sum"),
            registros_valor_ausente=("valor_total_ausente", "sum"),
            soma_valor_centavos=("valor_centavos_preenchido", "sum"),
        )
        .reset_index()
    )
    grouped["pct_registros_valor_zero"] = (
        grouped["registros_valor_zero"] / grouped["total_registros"] * 100
    ).round(2)
    grouped["soma_valor_total"] = grouped["soma_valor_centavos"] / 100
    grouped["soma_anual_zerada"] = grouped["soma_valor_centavos"].eq(0)
    grouped["estado"] = grouped["uf"].map(lambda uf: STATE_NAMES.get(uf, uf))
    grouped["capital_catalogo"] = grouped["uf"].map(lambda uf: CAPITAL_NAMES.get(uf, ""))

    columns = [
        "ano_normalizado",
        "uf",
        "estado",
        "capital_catalogo",
        "capital",
        "total_registros",
        "registros_valor_zero",
        "pct_registros_valor_zero",
        "registros_valor_ausente",
        "soma_valor_total",
        "soma_anual_zerada",
    ]
    return grouped[columns].sort_values(
        by=["ano_normalizado", "uf"],
        key=lambda series: series.map(year_sort_key) if series.name == "ano_normalizado" else series,
    )


def build_matrix(summary: pd.DataFrame, value_column: str, ufs: list[str]) -> pd.DataFrame:
    matrix = (
        summary.pivot(index="ano_normalizado", columns="uf", values=value_column)
        .reindex(index=sorted(summary["ano_normalizado"].unique(), key=year_sort_key))
        .reindex(columns=ufs)
    )
    matrix.columns = [column_label(uf) for uf in matrix.columns]
    matrix.index.name = "ano"
    return matrix.reset_index()


def build_dictionary(ufs: list[str]) -> pd.DataFrame:
    rows = [
        {"uf": uf, "estado": STATE_NAMES.get(uf, uf), "capital": CAPITAL_NAMES.get(uf, "")}
        for uf in ufs
    ]
    return pd.DataFrame(rows)


def format_years(values: list[str]) -> str:
    if not values:
        return "(nenhum)"
    return ", ".join(values)


def extract_years_from_text(value: str) -> list[str]:
    return sorted({match.group(0) for match in YEAR_IN_TEXT_RE.finditer(value)}, key=year_sort_key)


def list_all_matching_files(base_dir: Path, uf: str) -> list[Path]:
    config = CAPITAL_CONFIG_BY_UF.get(uf)
    if config is None:
        return []
    city_dir = base_dir / config.folder
    if not city_dir.exists():
        return []
    return sorted(path for path in city_dir.glob(config.file_glob) if path.is_file())


def build_raw_coverage_df(base_dir: Path, ufs: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for uf in ufs:
        config = CAPITAL_CONFIG_BY_UF.get(uf)
        all_files = list_all_matching_files(base_dir, uf)
        selected_files = find_source_files(base_dir, config) if config is not None else []

        all_years = sorted(
            {
                year
                for path in all_files
                for year in extract_years_from_text(path.stem)
            },
            key=year_sort_key,
        )
        selected_years = sorted(
            {
                year
                for path in selected_files
                for year in extract_years_from_text(path.stem)
            },
            key=year_sort_key,
        )

        rows.append(
            {
                "uf": uf,
                "estado": STATE_NAMES.get(uf, uf),
                "capital": CAPITAL_NAMES.get(uf, ""),
                "pasta_bruta": str(base_dir / config.folder) if config is not None else "",
                "arquivos_brutos_total": len(all_files),
                "arquivos_brutos_selecionados_pipeline": len(selected_files),
                "anos_brutos_nome_arquivo": format_years(all_years),
                "qtd_anos_brutos_nome_arquivo": len(all_years),
                "anos_brutos_pipeline": format_years(selected_years),
                "qtd_anos_brutos_pipeline": len(selected_years),
                "arquivos_exemplo": ", ".join(path.name for path in all_files[:5]) if all_files else "(nenhum)",
                "usa_latest_only": bool(config.latest_only) if config is not None else False,
            }
        )
    return pd.DataFrame(rows)


def build_year_coverage_df(summary: pd.DataFrame) -> pd.DataFrame:
    valid_years = summary.loc[summary["ano_normalizado"].str.fullmatch(r"(19|20)\d{2}", na=False)].copy()
    coverage = (
        valid_years.groupby("uf", dropna=False)
        .agg(
            anos_cobertos=("ano_normalizado", lambda values: sorted({str(value) for value in values}, key=year_sort_key)),
            qtd_anos_cobertos=("ano_normalizado", lambda values: len({str(value) for value in values})),
            registros_total=("total_registros", "sum"),
            registros_valor_zero=("registros_valor_zero", "sum"),
            soma_valor_total=("soma_valor_total", "sum"),
        )
        .reset_index()
    )
    coverage["estado"] = coverage["uf"].map(lambda uf: STATE_NAMES.get(uf, uf))
    coverage["capital"] = coverage["uf"].map(lambda uf: CAPITAL_NAMES.get(uf, ""))
    coverage["anos_cobertos"] = coverage["anos_cobertos"].map(format_years)
    coverage["cobertura_baixa"] = coverage["qtd_anos_cobertos"].le(LOW_COVERAGE_LIMIT)
    columns = [
        "uf",
        "estado",
        "capital",
        "qtd_anos_cobertos",
        "anos_cobertos",
        "cobertura_baixa",
        "registros_total",
        "registros_valor_zero",
        "soma_valor_total",
    ]
    return coverage[columns].sort_values(["qtd_anos_cobertos", "uf", "estado"])


def main() -> None:
    sqlite_path = Path(cli_default(SQLITE_PATH))
    output_path = Path(cli_default(DEFAULT_OUTPUT))
    base_dir = Path(cli_default(BASES_CONVENIOS_CAPITAIS_DIR))
    ensure_parent_dir(output_path)

    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite nao encontrado em: {sqlite_path}")

    frame = load_transferencias(sqlite_path, DEFAULT_TABLE, DEFAULT_ORIGEM)
    if frame.empty:
        raise ValueError(f"Nenhum registro encontrado para origem={DEFAULT_ORIGEM!r}")

    summary = build_summary(frame)
    if summary.empty:
        raise ValueError("Nenhum registro permaneceu apos aplicar os filtros informados.")

    ufs = ordered_ufs(summary["uf"].tolist())
    raw_coverage_df = build_raw_coverage_df(base_dir, ufs)
    year_coverage_df = build_year_coverage_df(summary)
    low_coverage_df = (
        year_coverage_df.loc[year_coverage_df["cobertura_baixa"]]
        .merge(raw_coverage_df, on=["uf", "estado", "capital"], how="left")
        .sort_values(["qtd_anos_cobertos", "uf"])
        .reset_index(drop=True)
    )
    matriz_registros_zero = build_matrix(summary, "registros_valor_zero", ufs).fillna(0)
    matriz_pct_zero = build_matrix(summary, "pct_registros_valor_zero", ufs).fillna(0.0)
    matriz_soma_anual_zerada = build_matrix(summary, "soma_anual_zerada", ufs)
    matriz_soma_valor_total = build_matrix(summary, "soma_valor_total", ufs).fillna(0.0)
    linhas_consideradas = int(summary["total_registros"].sum())
    for column in matriz_soma_anual_zerada.columns[1:]:
        matriz_soma_anual_zerada[column] = pd.Series(
            [
                int(bool(value)) if pd.notna(value) else 0
                for value in matriz_soma_anual_zerada[column].tolist()
            ],
            index=matriz_soma_anual_zerada.index,
        )

    casos_soma_zerada = (
        summary.loc[summary["soma_anual_zerada"]]
        .sort_values(["ano_normalizado", "uf"], key=lambda series: series.map(year_sort_key) if series.name == "ano_normalizado" else series)
        .reset_index(drop=True)
    )

    resumo_geral = pd.DataFrame(
        [
            {"metrica": "origem", "valor": DEFAULT_ORIGEM},
            {"metrica": "sqlite_path", "valor": str(sqlite_path)},
            {"metrica": "total_linhas_lidas", "valor": len(frame)},
            {"metrica": "total_linhas_consideradas", "valor": linhas_consideradas},
            {"metrica": "total_combinacoes_ano_uf", "valor": len(summary)},
            {"metrica": "anos_cobertos", "valor": summary["ano_normalizado"].nunique()},
            {"metrica": "ufs_cobertas", "valor": summary["uf"].nunique()},
            {"metrica": "anos_filtrados", "valor": "(todos)"},
            {"metrica": "ufs_filtradas", "valor": "(todas)"},
            {
                "metrica": "capitais_com_ate_3_anos_cobertos",
                "valor": int(low_coverage_df["uf"].nunique()),
            },
            {
                "metrica": "combinacoes_com_soma_anual_zerada",
                "valor": int(summary["soma_anual_zerada"].sum()),
            },
            {
                "metrica": "registros_com_valor_total_zero",
                "valor": int(summary["registros_valor_zero"].sum()),
            },
        ]
    )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        resumo_geral.to_excel(writer, sheet_name="Resumo", index=False)
        build_dictionary(ufs).to_excel(writer, sheet_name="Dicionario", index=False)
        summary.to_excel(writer, sheet_name="Resumo_UF_Ano", index=False)
        year_coverage_df.to_excel(writer, sheet_name="Cobertura_Anos", index=False)
        low_coverage_df.to_excel(writer, sheet_name="Cobertura_Baixa_Ate_3", index=False)
        raw_coverage_df.to_excel(writer, sheet_name="Brutos_Cobertura", index=False)
        matriz_registros_zero.to_excel(writer, sheet_name="Matriz_Zeros", index=False)
        matriz_pct_zero.to_excel(writer, sheet_name="Matriz_Pct_Zeros", index=False)
        matriz_soma_anual_zerada.to_excel(writer, sheet_name="Matriz_Soma_Anual_Zero", index=False)
        matriz_soma_valor_total.to_excel(writer, sheet_name="Matriz_Soma_Valor", index=False)
        casos_soma_zerada.to_excel(writer, sheet_name="Casos_Soma_Anual_Zero", index=False)

    print(f"Auditoria salva em: {output_path.resolve()}")
    print(f"Origem auditada: {DEFAULT_ORIGEM}")
    print(f"UFs cobertas: {len(ufs)}")
    print(f"Anos cobertos: {summary['ano_normalizado'].nunique()}")
    print(f"Capitais com ate {LOW_COVERAGE_LIMIT} anos cobertos: {int(low_coverage_df['uf'].nunique())}")
    print(f"Combinacoes ano/UF com soma anual zerada: {int(summary['soma_anual_zerada'].sum())}")


if __name__ == "__main__":
    main()
