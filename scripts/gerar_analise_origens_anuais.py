from __future__ import annotations

import argparse
import sqlite3
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import re
import sys

import pandas as pd
import plotly.express as px

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import PATHS, DB_TABLES


STANDARD_COLUMNS = [
    "uf",
    "origem",
    "ano",
    "valor_total",
    "cnpj",
    "nome_osc",
    "mes",
    "cod_municipio",
    "municipio",
    "objeto",
    "modalidade",
    "data_inicio",
    "data_fim",
]

ORIGEM_ORDER = [
    "CAPITAIS_CONVENIOS",
    "CAPITAIS_ORCAMENTO_GERAL",
    "ESTADO_CONVENIOS",
    "ESTADO_ORCAMENTO_GERAL",
]

UF_ORDER = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
    "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
    "SE", "SP", "TO",
]

NULL_TOKENS = {"", "nan", "none", "null", "nat", "<na>"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera analises anuais por UF e origem a partir dos parquets consolidados."
    )
    parser.add_argument(
        "--sqlite-path",
        default=str(PATHS.sqlite_path),
        help="Caminho do banco SQLite com as tabelas consolidadas.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path("outputs") / "analise_origens_anuais"),
        help="Diretorio de saida para agregados e graficos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        help="Anos especificos para gerar. Se omitido, usa todos os anos validos encontrados.",
    )
    parser.add_argument(
        "--ufs",
        nargs="*",
        help="UFs especificas para processar. Se omitido, usa todas as UFs encontradas no SQLite.",
    )
    parser.add_argument(
        "--aggregate-by",
        choices=["entidade", "registro"],
        default="entidade",
        help="Agrupa por entidade dentro de cada ano/UF/origem ou usa os registros originais.",
    )
    parser.add_argument(
        "--positive-only",
        action="store_true",
        help="Mantem apenas valores positivos nos graficos.",
    )
    parser.add_argument(
        "--min-value",
        type=float,
        default=None,
        help="Filtra observacoes com valor menor que este limite apos a agregacao.",
    )
    parser.add_argument(
        "--write-images",
        action="store_true",
        help="Tambem tenta exportar PNG com Kaleido, se disponivel.",
    )
    return parser.parse_args()


def build_where_clause(years: set[int] | None, uf: str | None, positive_only: bool) -> tuple[str, list[object]]:
    clauses = ["a.ano_valido = 1"]
    params: list[object] = []
    if years:
        placeholders = ", ".join("?" for _ in sorted(years))
        clauses.append(f"a.ano_num IN ({placeholders})")
        params.extend(sorted(years))
    if uf:
        clauses.append("t.uf = ?")
        params.append(uf)
    if positive_only:
        clauses.append("CAST(t.valor_total AS NUMERIC) > 0")
    return " AND ".join(clauses), params


def query_available_ufs(conn: sqlite3.Connection, years: set[int] | None) -> list[str]:
    where_clause, params = build_where_clause(years, None, False)
    query = f"""
        SELECT DISTINCT t.uf
        FROM {DB_TABLES.transferencias} t
        JOIN {DB_TABLES.transferencias_analitica} a
          ON a.transferencia_id = t.rowid
        WHERE {where_clause}
        ORDER BY t.uf
    """
    rows = conn.execute(query, params).fetchall()
    return [row[0] for row in rows if row[0]]


def query_aggregated_state(
    conn: sqlite3.Connection,
    uf: str,
    years: set[int] | None,
    aggregate_by: str,
    positive_only: bool,
    min_value: float | None,
) -> pd.DataFrame:
    where_clause, params = build_where_clause(years, uf, positive_only)
    if aggregate_by == "registro":
        query = f"""
            SELECT
                a.ano_num,
                t.uf,
                t.origem,
                a.entidade_base AS entidade_id,
                COALESCE(t.nome_osc, a.entidade_base, 'Sem identificacao') AS entidade_nome,
                1 AS registros,
                CAST(t.valor_total AS NUMERIC) AS valor_num,
                substr(a.arquivo_origem, 1, instr(a.arquivo_origem || '/', '/') - 1) AS pasta_origem
            FROM {DB_TABLES.transferencias} t
            JOIN {DB_TABLES.transferencias_analitica} a
              ON a.transferencia_id = t.rowid
            WHERE {where_clause}
        """
    else:
        query = f"""
            SELECT
                a.ano_num,
                t.uf,
                t.origem,
                a.entidade_base AS entidade_id,
                MIN(COALESCE(t.nome_osc, a.entidade_base, 'Sem identificacao')) AS entidade_nome,
                COUNT(*) AS registros,
                ROUND(SUM(CAST(t.valor_total AS NUMERIC)), 2) AS valor_num,
                MIN(substr(a.arquivo_origem, 1, instr(a.arquivo_origem || '/', '/') - 1)) AS pasta_origem
            FROM {DB_TABLES.transferencias} t
            JOIN {DB_TABLES.transferencias_analitica} a
              ON a.transferencia_id = t.rowid
            WHERE {where_clause}
            GROUP BY a.ano_num, t.uf, t.origem, a.entidade_base
        """
    frame = pd.read_sql_query(query, conn, params=params)
    if frame.empty:
        return frame
    frame["ano_num"] = frame["ano_num"].astype("Int64")
    frame["registros"] = frame["registros"].astype("Int64")
    frame["valor_num"] = pd.to_numeric(frame["valor_num"], errors="coerce").astype("Float64")
    if min_value is not None:
        frame = frame.loc[frame["valor_num"].ge(min_value)]
    return frame.reset_index(drop=True)


def save_state_aggregates(
    conn: sqlite3.Connection,
    ufs: list[str],
    years: set[int] | None,
    aggregate_by: str,
    positive_only: bool,
    min_value: float | None,
    intermediate_dir: Path,
) -> list[Path]:
    written_paths: list[Path] = []
    for uf in ufs:
        frame = query_aggregated_state(conn, uf, years, aggregate_by, positive_only, min_value)
        if frame.empty:
            continue
        parquet_path = intermediate_dir / f"{uf}.parquet"
        csv_path = intermediate_dir / f"{uf}.csv"
        frame.to_parquet(parquet_path, index=False)
        frame.to_csv(csv_path, index=False, encoding="utf-8-sig")
        written_paths.append(parquet_path)
    return written_paths


def load_intermediate_aggregates(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        return pd.DataFrame()
    frames = [pd.read_parquet(path) for path in paths]
    combined = pd.concat(frames, ignore_index=True)
    return (
        combined.groupby(["ano_num", "uf", "origem", "entidade_id"], dropna=False, as_index=False)
        .agg(
            valor_num=("valor_num", "sum"),
            registros=("registros", "sum"),
            entidade_nome=("entidade_nome", "first"),
            pasta_origem=("pasta_origem", "first"),
        )
    )


def apply_filters(data: pd.DataFrame, positive_only: bool, min_value: float | None) -> pd.DataFrame:
    filtered = data.copy()
    if positive_only:
        filtered = filtered.loc[filtered["valor_num"].gt(0)]
    if min_value is not None:
        filtered = filtered.loc[filtered["valor_num"].ge(min_value)]
    return filtered


def build_boxplot(year_df: pd.DataFrame, year: int):
    fig = px.box(
        year_df,
        x="uf",
        y="valor_num",
        color="origem",
        points="outliers",
        category_orders={"uf": UF_ORDER, "origem": ORIGEM_ORDER},
        title=str(year),
        hover_data={
            "entidade_id": True,
            "entidade_nome": True,
            "registros": True,
            "valor_num": ":,.2f",
        },
    )
    fig.update_layout(
        xaxis_title="UF",
        yaxis_title="Valor agregado no ano (R$)",
        boxmode="group",
        legend_title_text="Origem",
        template="plotly_white",
        width=1600,
        height=720,
    )
    fig.update_traces(quartilemethod="inclusive")
    return fig


def build_stripplot(year_df: pd.DataFrame, year: int):
    fig = px.strip(
        year_df,
        x="uf",
        y="valor_num",
        color="origem",
        category_orders={"uf": UF_ORDER, "origem": ORIGEM_ORDER},
        title=str(year),
        hover_data={
            "entidade_id": True,
            "entidade_nome": True,
            "registros": True,
            "valor_num": ":,.2f",
        },
    )
    fig.update_traces(jitter=0.35, marker={"size": 6, "opacity": 0.7})
    fig.update_layout(
        xaxis_title="UF",
        yaxis_title="Valor agregado no ano (R$)",
        legend_title_text="Origem",
        template="plotly_white",
        width=1600,
        height=720,
    )
    return fig


def maybe_write_image(fig, path: Path) -> str | None:
    try:
        fig.write_image(path)
    except Exception as exc:
        return str(exc)
    return None


def main() -> None:
    args = parse_args()

    output_dir = Path(args.output_dir)
    charts_dir = output_dir / "graficos"
    yearly_dir = output_dir / "agregados_anuais"
    intermediate_dir = output_dir / "agregados_por_uf"
    charts_dir.mkdir(parents=True, exist_ok=True)
    yearly_dir.mkdir(parents=True, exist_ok=True)
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    requested_years = set(args.years) if args.years else None
    sqlite_path = Path(args.sqlite_path)
    if not sqlite_path.exists():
        raise SystemExit(f"SQLite nao encontrado em {sqlite_path}")

    with sqlite3.connect(sqlite_path) as conn:
        selected_ufs = sorted(set(args.ufs)) if args.ufs else query_available_ufs(conn, requested_years)
        if not selected_ufs:
            raise SystemExit("Nenhuma UF encontrada no SQLite para os filtros informados.")
        written_paths = save_state_aggregates(
            conn=conn,
            ufs=selected_ufs,
            years=requested_years,
            aggregate_by=args.aggregate_by,
            positive_only=args.positive_only,
            min_value=args.min_value,
            intermediate_dir=intermediate_dir,
        )

    aggregated = load_intermediate_aggregates(written_paths)
    if aggregated.empty:
        raise SystemExit("Nenhum agregado por UF foi gerado a partir do SQLite.")

    aggregated["ano_num"] = aggregated["ano_num"].astype("Int64")
    available_years = sorted(int(year) for year in aggregated["ano_num"].dropna().unique())
    years = sorted(set(args.years)) if args.years else available_years
    years = [year for year in years if year in available_years]
    if not years:
        raise SystemExit("Nenhum dos anos solicitados esta disponivel na base agregada.")

    aggregated_all_path = output_dir / "base_agregada_todos_os_anos.parquet"
    aggregated.to_parquet(aggregated_all_path, index=False)
    aggregated.to_csv(output_dir / "base_agregada_todos_os_anos.csv", index=False, encoding="utf-8-sig")

    image_errors: list[str] = []
    summary_rows: list[dict[str, object]] = []

    for year in years:
        year_df = aggregated.loc[aggregated["ano_num"].eq(year)].copy()
        if year_df.empty:
            continue

        year_df = year_df.sort_values(["uf", "origem", "valor_num"], ascending=[True, True, False])
        year_df.to_parquet(yearly_dir / f"ano_{year}.parquet", index=False)
        year_df.to_csv(yearly_dir / f"ano_{year}.csv", index=False, encoding="utf-8-sig")

        boxplot = build_boxplot(year_df, year)
        stripplot = build_stripplot(year_df, year)

        boxplot_html = charts_dir / f"boxplot_{year}.html"
        stripplot_html = charts_dir / f"stripplot_{year}.html"
        boxplot.write_html(boxplot_html, include_plotlyjs="cdn")
        stripplot.write_html(stripplot_html, include_plotlyjs="cdn")

        if args.write_images:
            error = maybe_write_image(boxplot, charts_dir / f"boxplot_{year}.png")
            if error:
                image_errors.append(f"{year} boxplot: {error}")
            error = maybe_write_image(stripplot, charts_dir / f"stripplot_{year}.png")
            if error:
                image_errors.append(f"{year} stripplot: {error}")

        summary_rows.append(
            {
                "ano": year,
                "observacoes": len(year_df),
                "ufs": year_df["uf"].nunique(dropna=True),
                "origens": year_df["origem"].nunique(dropna=True),
                "valor_total_ano": float(year_df["valor_num"].sum()),
                "mediana_ano": float(year_df["valor_num"].median()),
                "max_ano": float(year_df["valor_num"].max()),
            }
        )

    summary_df = pd.DataFrame(summary_rows).sort_values("ano")
    summary_df.to_csv(output_dir / "resumo_anos.csv", index=False, encoding="utf-8-sig")

    print(f"Base agregada: {aggregated_all_path}")
    print(f"Agregados por UF: {intermediate_dir}")
    print(f"Anos gerados: {', '.join(str(year) for year in years)}")
    print(f"Graficos HTML: {charts_dir}")
    print(f"Agregados anuais: {yearly_dir}")
    if image_errors:
        print("Falhas ao exportar imagens:")
        for error in image_errors:
            print(f"- {error}")


if __name__ == "__main__":
    main()
