from __future__ import annotations

from pathlib import Path
import re
import argparse
import sqlite3
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from config import DB_TABLES, DB_VIEWS, STANDARD_COLUMNS
from project_paths import (
    AUDITORIA_XLSX_PATH,
    CAPITAIS_PROCESSADA_DIR,
    HISTORIA_DIR,
    PROCESSADA_DIR,
    SQLITE_PATH,
    cli_default,
    ensure_parent_dir,
)

TRANSFERENCIAS_TABLE = DB_TABLES.transferencias
TRANSFERENCIAS_ANALITICA_TABLE = DB_TABLES.transferencias_analitica
ARQUIVOS_ORIGEM_TABLE = DB_TABLES.arquivos_origem
HISTORIAS_TABLE = DB_TABLES.historias
AUDITORIA_RESUMO_TABLE = DB_TABLES.auditoria_resumo
VW_RESUMO_UF = DB_VIEWS.resumo_uf
VW_TOP_ENTIDADES = DB_VIEWS.top_entidades
VW_SERIE_ANUAL = DB_VIEWS.serie_anual
VW_ALERTAS_QUALIDADE = DB_VIEWS.alertas_qualidade

ORIGEM_PADRAO = "convenios"
NULL_TOKENS = {"", "nan", "none", "null", "nat", "<na>"}
MONEY_QUANTUM = Decimal("0.01")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carrega os parquets consolidados em um banco SQLite para analise."
    )
    parser.add_argument(
        "--processed-dir",
        default=cli_default(PROCESSADA_DIR),
        help="Pasta com os arquivos parquet por UF.",
    )
    parser.add_argument(
        "--extra-processed-dir",
        action="append",
        default=[],
        help="Pasta adicional com parquets para compor a carga do SQLite, alem de processada e capitais_processada quando existirem. Pode ser repetido.",
    )
    parser.add_argument(
        "--output",
        default=cli_default(SQLITE_PATH),
        help="Arquivo SQLite de saida.",
    )
    parser.add_argument(
        "--history-dir",
        default=cli_default(HISTORIA_DIR),
        help="Pasta com markdowns de historias por UF.",
    )
    parser.add_argument(
        "--audit-xlsx",
        default=cli_default(AUDITORIA_XLSX_PATH),
        help="Planilha de auditoria opcional.",
    )
    return parser.parse_args()


def clean_text(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    lower = values.str.lower()
    values = values.mask(lower.isin(NULL_TOKENS))
    values = values.mask(values.isin(["-", "--"]))
    return values


def parse_money_decimal(value: object) -> Decimal | None:
    if pd.isna(value):
        return None
    if isinstance(value, Decimal):
        numeric = value
        if abs(numeric) < Decimal("0.005"):
            numeric = Decimal("0")
        return numeric.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
    text = str(value).strip()
    if not text or text.lower() in NULL_TOKENS:
        return None
    compact = text.replace("\xa0", "").replace(" ", "").removeprefix("R$")
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
        return None
    try:
        numeric = Decimal(compact)
    except InvalidOperation:
        return None
    if abs(numeric) < Decimal("0.005"):
        numeric = Decimal("0")
    return numeric.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def format_money_for_sqlite(value: object) -> object:
    numeric = parse_money_decimal(value)
    if numeric is None:
        return pd.NA
    # Mantem o valor monetario explicitamente arredondado a centavos.
    return format(numeric, ".2f")


def parse_int_like(series: pd.Series) -> pd.Series:
    cleaned = clean_text(series).str.replace(r"\.0+$", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce").astype("Int64")


def parse_dates(series: pd.Series) -> pd.Series:
    cleaned = clean_text(series)
    parsed = pd.to_datetime(cleaned, errors="coerce", format="mixed", dayfirst=True)
    retry = parsed.isna() & cleaned.notna()
    if retry.any():
        parsed.loc[retry] = pd.to_datetime(
            cleaned.loc[retry], errors="coerce", format="mixed", dayfirst=False
        )
    return parsed


def ensure_schema(frame: pd.DataFrame) -> pd.DataFrame:
    for column in STANDARD_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    return frame[STANDARD_COLUMNS].copy()


def list_parquet_paths(processed_dirs: list[Path]) -> list[tuple[Path, Path]]:
    parquet_paths: list[tuple[Path, Path]] = []
    for processed_dir in processed_dirs:
        parquet_paths.extend((processed_dir, path) for path in sorted(processed_dir.glob("*.parquet")))
    if not parquet_paths:
        raise FileNotFoundError(
            f"Nenhum parquet encontrado em {', '.join(str(path) for path in processed_dirs)}"
        )
    return parquet_paths


def resolve_processed_dirs(primary_dir: Path, extra_dirs: list[Path]) -> list[Path]:
    resolved_dirs: list[Path] = []
    seen: set[Path] = set()

    for candidate in [primary_dir, CAPITAIS_PROCESSADA_DIR, *extra_dirs]:
        resolved = candidate.expanduser().resolve()
        if resolved in seen or not resolved.exists() or not resolved.is_dir():
            continue
        seen.add(resolved)
        resolved_dirs.append(resolved)

    return resolved_dirs


def dataframe_sqlite_ready(df: pd.DataFrame) -> pd.DataFrame:
    ready = df.copy()
    bool_cols = ready.select_dtypes(include=["bool", "boolean"]).columns
    for column in bool_cols:
        ready[column] = ready[column].astype("Int64")

    datetime_cols = ready.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns
    for column in datetime_cols:
        ready[column] = ready[column].dt.strftime("%Y-%m-%d %H:%M:%S")

    for column in ready.columns:
        if str(ready[column].dtype) == "Int64":
            ready[column] = ready[column].astype("object")

    ready = ready.replace({pd.NA: None, np.nan: None})
    return ready


def load_histories(history_dir: Path) -> pd.DataFrame:
    if not history_dir.exists():
        return pd.DataFrame(columns=["uf", "arquivo", "titulo", "markdown"])

    rows: list[dict[str, str]] = []
    for path in sorted(history_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        first_header = next((line.strip() for line in text.splitlines() if line.strip().startswith("#")), path.stem.upper())
        title = re.sub(r"^#+\s*", "", first_header).strip()
        rows.append(
            {
                "uf": path.stem.upper(),
                "arquivo": path.name,
                "titulo": title,
                "markdown": text,
            }
        )
    return pd.DataFrame(rows)


def load_audit_summary(audit_path: Path) -> pd.DataFrame:
    if not audit_path.exists():
        return pd.DataFrame()
    try:
        return pd.read_excel(audit_path, sheet_name="Resumo")
    except Exception:
        return pd.DataFrame()


def build_schema_table(data: pd.DataFrame) -> pd.DataFrame:
    schema = data[STANDARD_COLUMNS].copy()
    schema["ano"] = parse_int_like(schema["ano"])
    schema["mes"] = parse_int_like(schema["mes"])
    schema["cod_municipio"] = parse_int_like(schema["cod_municipio"])
    schema["data_inicio"] = parse_dates(schema["data_inicio"])
    schema["data_fim"] = parse_dates(schema["data_fim"])
    return schema


def build_analytic_table(data: pd.DataFrame) -> pd.DataFrame:
    analytic_columns = [
        "uf",
        "arquivo_origem",
        "uf_arquivo",
        "ano_num",
        "mes_num",
        "data_inicio_iso",
        "data_fim_iso",
        "duracao_dias",
        "tem_cnpj_valido",
        "tem_municipio",
        "tem_objeto",
        "tem_modalidade",
        "valor_zero",
        "valor_negativo",
        "ano_valido",
        "mes_valido",
        "entidade_base",
        "municipio_base",
        "modalidade_base",
        "ano_mes",
        "duplicado_aparente",
    ]
    analytic = data[analytic_columns].copy()
    analytic.insert(0, "transferencia_id", pd.RangeIndex(start=1, stop=len(analytic) + 1))
    return analytic


def prepare_enriched_data(data: pd.DataFrame) -> pd.DataFrame:
    prepared = ensure_schema(data)
    for column in STANDARD_COLUMNS:
        prepared[column] = clean_text(prepared[column])
    prepared["origem"] = prepared["origem"].fillna(ORIGEM_PADRAO)

    current_year = pd.Timestamp.today().year
    prepared["valor_total"] = prepared["valor_total"].map(format_money_for_sqlite)
    prepared["ano_num"] = parse_int_like(prepared["ano"])
    prepared["mes_num"] = parse_int_like(prepared["mes"])
    prepared["data_inicio_dt"] = parse_dates(prepared["data_inicio"])
    prepared["data_fim_dt"] = parse_dates(prepared["data_fim"])
    prepared["data_inicio_iso"] = prepared["data_inicio_dt"].dt.strftime("%Y-%m-%d")
    prepared["data_fim_iso"] = prepared["data_fim_dt"].dt.strftime("%Y-%m-%d")
    prepared["duracao_dias"] = (prepared["data_fim_dt"] - prepared["data_inicio_dt"]).dt.days.astype("Int64")
    prepared["tem_cnpj_valido"] = prepared["cnpj"].str.replace(r"\D", "", regex=True).str.len().eq(14)
    prepared["tem_municipio"] = prepared["municipio"].notna()
    prepared["tem_objeto"] = prepared["objeto"].notna()
    prepared["tem_modalidade"] = prepared["modalidade"].notna()
    money_decimal = prepared["valor_total"].map(parse_money_decimal)
    prepared["valor_zero"] = money_decimal.map(lambda value: value is None or value == Decimal("0"))
    prepared["valor_negativo"] = money_decimal.map(lambda value: value is not None and value < 0)
    prepared["ano_valido"] = prepared["ano_num"].between(1990, current_year + 2)
    prepared["mes_valido"] = prepared["mes_num"].between(1, 12)
    prepared["entidade_base"] = prepared["cnpj"].where(
        prepared["tem_cnpj_valido"], prepared["nome_osc"]
    ).fillna("Sem identificacao")
    prepared["municipio_base"] = prepared["municipio"].fillna("Nao informado")
    prepared["modalidade_base"] = prepared["modalidade"].fillna("Nao informada")
    prepared["ano_mes"] = pd.NA
    valid_period = prepared["ano_valido"] & prepared["mes_valido"]
    if valid_period.any():
        prepared.loc[valid_period, "ano_mes"] = pd.to_datetime(
            {
                "year": prepared.loc[valid_period, "ano_num"].astype(int),
                "month": prepared.loc[valid_period, "mes_num"].astype(int),
                "day": 1,
            },
            errors="coerce",
        ).dt.strftime("%Y-%m-%d")

    prepared["duplicado_aparente"] = False
    return prepared


def sqlite_dtype_map_for_schema() -> dict[str, str]:
    return {
        "uf": "TEXT",
        "origem": "TEXT",
        "ano": "INTEGER",
        "valor_total": "MONEY",
        "cnpj": "TEXT",
        "nome_osc": "TEXT",
        "mes": "INTEGER",
        "cod_municipio": "INTEGER",
        "municipio": "TEXT",
        "objeto": "TEXT",
        "modalidade": "TEXT",
        "data_inicio": "TIMESTAMP",
        "data_fim": "TIMESTAMP",
    }


def sqlite_dtype_map_for_analytic() -> dict[str, str]:
    return {
        "transferencia_id": "INTEGER",
        "uf": "TEXT",
        "arquivo_origem": "TEXT",
        "uf_arquivo": "TEXT",
        "ano_num": "INTEGER",
        "mes_num": "INTEGER",
        "data_inicio_iso": "TEXT",
        "data_fim_iso": "TEXT",
        "duracao_dias": "INTEGER",
        "tem_cnpj_valido": "INTEGER",
        "tem_municipio": "INTEGER",
        "tem_objeto": "INTEGER",
        "tem_modalidade": "INTEGER",
        "valor_zero": "INTEGER",
        "valor_negativo": "INTEGER",
        "ano_valido": "INTEGER",
        "mes_valido": "INTEGER",
        "entidade_base": "TEXT",
        "municipio_base": "TEXT",
        "modalidade_base": "TEXT",
        "ano_mes": "TEXT",
        "duplicado_aparente": "INTEGER",
    }


def create_base_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        f"""
        DROP VIEW IF EXISTS {VW_RESUMO_UF};
        DROP VIEW IF EXISTS {VW_TOP_ENTIDADES};
        DROP VIEW IF EXISTS {VW_SERIE_ANUAL};
        DROP VIEW IF EXISTS {VW_ALERTAS_QUALIDADE};

        DROP TABLE IF EXISTS {TRANSFERENCIAS_TABLE};
        CREATE TABLE {TRANSFERENCIAS_TABLE} (
            uf TEXT,
            origem TEXT,
            ano INTEGER,
            valor_total MONEY,
            cnpj TEXT,
            nome_osc TEXT,
            mes INTEGER,
            cod_municipio INTEGER,
            municipio TEXT,
            objeto TEXT,
            modalidade TEXT,
            data_inicio TIMESTAMP,
            data_fim TIMESTAMP
        );

        DROP TABLE IF EXISTS {TRANSFERENCIAS_ANALITICA_TABLE};
        CREATE TABLE {TRANSFERENCIAS_ANALITICA_TABLE} (
            transferencia_id INTEGER,
            uf TEXT,
            arquivo_origem TEXT,
            uf_arquivo TEXT,
            ano_num INTEGER,
            mes_num INTEGER,
            data_inicio_iso TEXT,
            data_fim_iso TEXT,
            duracao_dias INTEGER,
            tem_cnpj_valido INTEGER,
            tem_municipio INTEGER,
            tem_objeto INTEGER,
            tem_modalidade INTEGER,
            valor_zero INTEGER,
            valor_negativo INTEGER,
            ano_valido INTEGER,
            mes_valido INTEGER,
            entidade_base TEXT,
            municipio_base TEXT,
            modalidade_base TEXT,
            ano_mes TEXT,
            duplicado_aparente INTEGER
        );
        """
    )


def update_duplicate_flags(conn: sqlite3.Connection) -> None:
    conn.execute(f"UPDATE {TRANSFERENCIAS_ANALITICA_TABLE} SET duplicado_aparente = 0")
    conn.execute(
        f"""
        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_id
        ON {TRANSFERENCIAS_ANALITICA_TABLE}(transferencia_id);
        """
    )
    conn.executescript(
        f"""
        DROP TABLE IF EXISTS temp_duplicate_ids;

        CREATE TEMP TABLE temp_duplicate_ids AS
        SELECT transferencia_id
        FROM (
            SELECT
                rowid AS transferencia_id,
                COUNT(*) OVER (
                    PARTITION BY
                        COALESCE(uf, '<vazio>'),
                        COALESCE(CAST(ano AS TEXT), '<vazio>'),
                        COALESCE(CAST(mes AS TEXT), '<vazio>'),
                        CASE
                            WHEN valor_total IS NULL THEN '<vazio>'
                            ELSE printf('%.2f', CAST(valor_total AS NUMERIC))
                        END,
                        COALESCE(cnpj, '<vazio>'),
                        COALESCE(nome_osc, '<vazio>'),
                        COALESCE(municipio, '<vazio>'),
                        COALESCE(objeto, '<vazio>'),
                        COALESCE(modalidade, '<vazio>')
                ) AS duplicate_count
            FROM {TRANSFERENCIAS_TABLE}
        ) duplicates
        WHERE duplicate_count > 1;

        CREATE INDEX IF NOT EXISTS idx_temp_duplicate_ids
        ON temp_duplicate_ids(transferencia_id);

        UPDATE {TRANSFERENCIAS_ANALITICA_TABLE}
        SET duplicado_aparente = 1
        WHERE transferencia_id IN (
            SELECT transferencia_id
            FROM temp_duplicate_ids
        );

        DROP TABLE IF EXISTS temp_duplicate_ids;
        """
    )


def load_parquets_incrementally(
    conn: sqlite3.Connection,
    processed_dirs: list[Path],
    batch_size: int = 250000,
) -> pd.DataFrame:
    parquet_paths = list_parquet_paths(processed_dirs)
    file_rows: list[dict[str, object]] = []

    for processed_dir, path in parquet_paths:
        source_name = processed_dir.name
        file_key = f"{source_name}/{path.name}"
        parquet = pq.ParquetFile(path)
        row_count = 0

        for batch in parquet.iter_batches(batch_size=batch_size):
            frame = prepare_enriched_data(batch.to_pandas())
            frame["arquivo_origem"] = file_key
            frame["uf_arquivo"] = path.stem.upper()

            schema_df = build_schema_table(frame)
            analytic_df = build_analytic_table(frame)

            next_rowid = conn.execute(
                f"SELECT IFNULL(MAX(rowid), 0) FROM {TRANSFERENCIAS_TABLE}"
            ).fetchone()[0] + 1
            analytic_df["transferencia_id"] = pd.RangeIndex(
                start=next_rowid, stop=next_rowid + len(analytic_df)
            )

            dataframe_sqlite_ready(schema_df).to_sql(
                TRANSFERENCIAS_TABLE,
                conn,
                if_exists="append",
                index=False,
                chunksize=50000,
                dtype=sqlite_dtype_map_for_schema(),
            )
            dataframe_sqlite_ready(analytic_df).to_sql(
                TRANSFERENCIAS_ANALITICA_TABLE,
                conn,
                if_exists="append",
                index=False,
                chunksize=50000,
                dtype=sqlite_dtype_map_for_analytic(),
            )
            conn.commit()
            row_count += len(frame)

        file_rows.append(
            {
                "arquivo": file_key,
                "pasta_origem": source_name,
                "uf": path.stem.upper(),
                "linhas": row_count,
                "tamanho_mb": round(path.stat().st_size / (1024 * 1024), 4),
                "atualizado_em": pd.Timestamp(path.stat().st_mtime, unit="s").isoformat(),
            }
        )
        print(f"Carregado: {file_key} ({row_count} linhas)")

    return pd.DataFrame(file_rows)


def create_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        f"""
        DROP VIEW IF EXISTS {VW_RESUMO_UF};
        CREATE VIEW {VW_RESUMO_UF} AS
        SELECT
            t.uf,
            COUNT(*) AS registros,
            ROUND(SUM(CAST(t.valor_total AS NUMERIC)), 2) AS valor_total,
            ROUND(AVG(CAST(t.valor_total AS NUMERIC)), 2) AS ticket_medio,
            AVG(CASE WHEN a.tem_cnpj_valido = 1 THEN 1.0 ELSE 0.0 END) * 100 AS cobertura_cnpj_pct,
            AVG(CASE WHEN a.tem_municipio = 1 THEN 1.0 ELSE 0.0 END) * 100 AS cobertura_municipio_pct,
            AVG(CASE WHEN a.tem_objeto = 1 THEN 1.0 ELSE 0.0 END) * 100 AS cobertura_objeto_pct,
            AVG(CASE WHEN a.tem_modalidade = 1 THEN 1.0 ELSE 0.0 END) * 100 AS cobertura_modalidade_pct
        FROM {TRANSFERENCIAS_TABLE} t
        JOIN {TRANSFERENCIAS_ANALITICA_TABLE} a ON a.transferencia_id = t.rowid
        GROUP BY t.uf;

        DROP VIEW IF EXISTS {VW_TOP_ENTIDADES};
        CREATE VIEW {VW_TOP_ENTIDADES} AS
        SELECT
            t.uf,
            a.entidade_base,
            t.nome_osc,
            t.cnpj,
            COUNT(*) AS registros,
            ROUND(SUM(CAST(t.valor_total AS NUMERIC)), 2) AS valor_total,
            ROUND(AVG(CAST(t.valor_total AS NUMERIC)), 2) AS ticket_medio
        FROM {TRANSFERENCIAS_TABLE} t
        JOIN {TRANSFERENCIAS_ANALITICA_TABLE} a ON a.transferencia_id = t.rowid
        GROUP BY t.uf, a.entidade_base, t.nome_osc, t.cnpj;

        DROP VIEW IF EXISTS {VW_SERIE_ANUAL};
        CREATE VIEW {VW_SERIE_ANUAL} AS
        SELECT
            t.uf,
            a.ano_num,
            COUNT(*) AS registros,
            ROUND(SUM(CAST(t.valor_total AS NUMERIC)), 2) AS valor_total,
            ROUND(AVG(CAST(t.valor_total AS NUMERIC)), 2) AS ticket_medio
        FROM {TRANSFERENCIAS_TABLE} t
        JOIN {TRANSFERENCIAS_ANALITICA_TABLE} a ON a.transferencia_id = t.rowid
        WHERE a.ano_valido = 1
        GROUP BY t.uf, a.ano_num;

        DROP VIEW IF EXISTS {VW_ALERTAS_QUALIDADE};
        CREATE VIEW {VW_ALERTAS_QUALIDADE} AS
        SELECT
            t.uf,
            SUM(CASE WHEN a.valor_zero = 1 THEN 1 ELSE 0 END) AS valores_zero,
            SUM(CASE WHEN a.valor_negativo = 1 THEN 1 ELSE 0 END) AS valores_negativos,
            SUM(CASE WHEN a.ano_valido = 0 AND t.ano IS NOT NULL THEN 1 ELSE 0 END) AS anos_invalidos,
            SUM(CASE WHEN a.mes_valido = 0 AND t.mes IS NOT NULL THEN 1 ELSE 0 END) AS meses_invalidos,
            SUM(CASE WHEN a.tem_cnpj_valido = 0 AND t.cnpj IS NOT NULL THEN 1 ELSE 0 END) AS cnpjs_invalidos,
            SUM(CASE WHEN a.tem_municipio = 0 THEN 1 ELSE 0 END) AS sem_municipio,
            SUM(CASE WHEN a.tem_objeto = 0 THEN 1 ELSE 0 END) AS sem_objeto,
            SUM(CASE WHEN a.tem_modalidade = 0 THEN 1 ELSE 0 END) AS sem_modalidade,
            SUM(CASE WHEN a.duplicado_aparente = 1 THEN 1 ELSE 0 END) AS duplicados_aparentes
        FROM {TRANSFERENCIAS_TABLE} t
        JOIN {TRANSFERENCIAS_ANALITICA_TABLE} a ON a.transferencia_id = t.rowid
        GROUP BY t.uf;
        """
    )


def create_indexes(conn: sqlite3.Connection) -> None:
    conn.executescript(
        f"""
        CREATE INDEX IF NOT EXISTS idx_transferencias_uf ON {TRANSFERENCIAS_TABLE}(uf);
        CREATE INDEX IF NOT EXISTS idx_transferencias_origem ON {TRANSFERENCIAS_TABLE}(origem);
        CREATE INDEX IF NOT EXISTS idx_transferencias_cnpj ON {TRANSFERENCIAS_TABLE}(cnpj);
        CREATE INDEX IF NOT EXISTS idx_transferencias_ano ON {TRANSFERENCIAS_TABLE}(ano);
        CREATE INDEX IF NOT EXISTS idx_transferencias_municipio ON {TRANSFERENCIAS_TABLE}(municipio);
        CREATE INDEX IF NOT EXISTS idx_transferencias_modalidade ON {TRANSFERENCIAS_TABLE}(modalidade);

        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_id ON {TRANSFERENCIAS_ANALITICA_TABLE}(transferencia_id);
        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_uf ON {TRANSFERENCIAS_ANALITICA_TABLE}(uf);
        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_ano_num ON {TRANSFERENCIAS_ANALITICA_TABLE}(ano_num);
        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_uf_ano ON {TRANSFERENCIAS_ANALITICA_TABLE}(uf, ano_num);
        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_entidade ON {TRANSFERENCIAS_ANALITICA_TABLE}(entidade_base);
        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_municipio ON {TRANSFERENCIAS_ANALITICA_TABLE}(municipio_base);
        CREATE INDEX IF NOT EXISTS idx_transferencias_analitica_arquivo ON {TRANSFERENCIAS_ANALITICA_TABLE}(arquivo_origem);
        """
    )


def export_to_sqlite(
    processed_dirs: list[Path],
    output_path: Path,
    history_dir: Path,
    audit_path: Path,
) -> None:
    histories_df = load_histories(history_dir)
    audit_summary_df = load_audit_summary(audit_path)

    ensure_parent_dir(output_path)

    if output_path.exists():
        try:
            output_path.unlink()
        except PermissionError as exc:
            raise PermissionError(
                f"O arquivo {output_path} esta aberto por outro processo. Feche o SQLite/DB Browser/Power BI e tente novamente, ou use --output com outro nome."
            ) from exc

    conn = sqlite3.connect(output_path)
    try:
        conn.execute("PRAGMA journal_mode=DELETE;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA temp_store=MEMORY;")

        create_base_tables(conn)
        files_df = load_parquets_incrementally(conn, processed_dirs)
        update_duplicate_flags(conn)

        dataframe_sqlite_ready(files_df).to_sql(
            ARQUIVOS_ORIGEM_TABLE,
            conn,
            if_exists="replace",
            index=False,
            chunksize=1000,
        )
        if not histories_df.empty:
            dataframe_sqlite_ready(histories_df).to_sql(
                HISTORIAS_TABLE,
                conn,
                if_exists="replace",
                index=False,
                chunksize=100,
            )
        if not audit_summary_df.empty:
            dataframe_sqlite_ready(audit_summary_df).to_sql(
                AUDITORIA_RESUMO_TABLE,
                conn,
                if_exists="replace",
                index=False,
                chunksize=100,
            )

        create_indexes(conn)
        create_views(conn)
        conn.commit()
        conn.execute("VACUUM;")
    finally:
        conn.close()


def main() -> None:
    args = parse_args()
    processed_dirs = resolve_processed_dirs(
        primary_dir=Path(args.processed_dir),
        extra_dirs=[Path(item) for item in args.extra_processed_dir],
    )
    output_path = Path(args.output)
    history_dir = Path(args.history_dir)
    audit_path = Path(args.audit_xlsx)

    print("Pastas de parquet na carga:")
    for processed_dir in processed_dirs:
        print(f"- {processed_dir}")

    export_to_sqlite(
        processed_dirs=processed_dirs,
        output_path=output_path,
        history_dir=history_dir,
        audit_path=audit_path,
    )
    print(f"SQLite gerado em: {output_path.resolve()}")


if __name__ == "__main__":
    main()
