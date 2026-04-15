from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

from config import (
    CAPITAIS_PROCESSADA_DIR,
    EXTERNAL_DATA_ROOT,
    GOVERNO_FEDERAL_DIR,
    ORCAMENTO_GERAL_PROCESSADA_DIR,
    PROCESSADA_DIR,
    SQLITE_PATH,
)


DEFAULT_DIRECTORIES = {
    "E:/dados (raiz)": EXTERNAL_DATA_ROOT,
    "Processada (estados)": PROCESSADA_DIR,
    "Capitais processada": CAPITAIS_PROCESSADA_DIR,
    "Orcamento geral processada": ORCAMENTO_GERAL_PROCESSADA_DIR,
    "Governo federal": GOVERNO_FEDERAL_DIR,
}


def format_size_mb(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def normalize_directory(path_text: str) -> Path:
    return Path(path_text.strip()).expanduser().resolve()


def list_available_files(directory: Path, recursive: bool) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    iterator = directory.rglob("*.parquet") if recursive else directory.glob("*.parquet")
    for path in sorted(iterator):
        parquet = pq.ParquetFile(path)
        rows.append(
            {
                "arquivo": path.name,
                "pasta": str(path.parent),
                "linhas": parquet.metadata.num_rows,
                "colunas": len(parquet.schema.names),
                "tamanho": format_size_mb(path.stat().st_size),
                "atualizado_em": pd.Timestamp(path.stat().st_mtime, unit="s"),
                "caminho": str(path),
            }
        )
    return pd.DataFrame(rows)


def load_sample_dataframe(path: Path, limit: int) -> pd.DataFrame:
    parquet = pq.ParquetFile(path)
    batches: list[pd.DataFrame] = []
    loaded_rows = 0

    for batch in parquet.iter_batches(batch_size=limit):
        frame = batch.to_pandas()
        batches.append(frame)
        loaded_rows += len(frame)
        if loaded_rows >= limit:
            break

    if not batches:
        return pd.DataFrame(columns=parquet.schema.names)

    return pd.concat(batches, ignore_index=True).head(limit)


def build_columns_summary(path: Path, sample_df: pd.DataFrame) -> pd.DataFrame:
    parquet = pq.ParquetFile(path)
    rows: list[dict[str, object]] = []

    for column_name in parquet.schema.names:
        arrow_field = parquet.schema_arrow.field(column_name)
        sample_series = sample_df[column_name] if column_name in sample_df.columns else pd.Series(dtype="object")
        sample_non_null = sample_series.dropna()
        sample_value = sample_non_null.iloc[0] if not sample_non_null.empty else None
        rows.append(
            {
                "coluna": column_name,
                "tipo_parquet": str(arrow_field.type),
                "tipo_amostra": str(sample_series.dtype),
                "nulos_na_amostra": int(sample_series.isna().sum()) if column_name in sample_df.columns else 0,
                "valor_exemplo": str(sample_value)[:120] if sample_value is not None else "",
            }
        )

    return pd.DataFrame(rows)


@st.cache_data(show_spinner="Lendo arquivos da pasta...")
def cached_files_index(directory_str: str, recursive: bool) -> pd.DataFrame:
    return list_available_files(Path(directory_str), recursive)


@st.cache_data(show_spinner="Abrindo parquet...")
def cached_sample(file_path_str: str, limit: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    path = Path(file_path_str)
    sample_df = load_sample_dataframe(path, limit)
    columns_df = build_columns_summary(path, sample_df)
    return sample_df, columns_df


def main() -> None:
    st.set_page_config(page_title="Visualizador de Processados", layout="wide")
    st.title("Visualizador de Arquivos Processados")
    st.caption("Escolha uma pasta, clique em um parquet e veja uma amostra com colunas e tipos.")

    preset_name = st.sidebar.selectbox(
        "Pasta configurada",
        options=list(DEFAULT_DIRECTORIES.keys()) + ["Outro caminho"],
        index=0,
    )
    default_path = DEFAULT_DIRECTORIES.get(preset_name, EXTERNAL_DATA_ROOT)
    custom_path = st.sidebar.text_input(
        "Diretorio para leitura",
        value=str(default_path),
        help="Voce pode manter uma pasta configurada ou apontar para qualquer diretorio com arquivos .parquet.",
    )
    recursive = st.sidebar.checkbox(
        "Buscar nas subpastas",
        value=True,
        help="Ative para listar arquivos .parquet encontrados dentro da pasta e de todas as subpastas.",
    )
    sample_limit = st.sidebar.slider("Linhas da amostra", min_value=10, max_value=50, value=50, step=10)
    st.sidebar.write(f"**SQLite configurado:** `{SQLITE_PATH}`")

    directory = normalize_directory(custom_path)
    st.write(f"**Diretorio atual:** `{directory}`")
    st.write(f"**SQLite configurado:** `{SQLITE_PATH}`")

    if not directory.exists():
        st.error("O diretorio informado nao existe.")
        return
    if not directory.is_dir():
        st.error("O caminho informado nao e uma pasta.")
        return

    files_df = cached_files_index(str(directory), recursive)
    if files_df.empty:
        st.warning("Nenhum arquivo `.parquet` foi encontrado nessa pasta.")
        return

    st.subheader("Arquivos encontrados")
    st.caption("Clique em uma linha para abrir a amostra do parquet.")

    files_view = files_df.drop(columns=["caminho"]).copy()
    files_view["atualizado_em"] = files_view["atualizado_em"].dt.strftime("%Y-%m-%d %H:%M:%S")
    selection = st.dataframe(
        files_view,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = selection.selection.rows
    selected_idx = selected_rows[0] if selected_rows else 0
    selected_file = files_df.iloc[selected_idx]

    selected_path = Path(selected_file["caminho"])
    st.subheader(f"Arquivo selecionado: {selected_file['arquivo']}")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Linhas no parquet", f"{int(selected_file['linhas']):,}".replace(",", "."))
    metric_cols[1].metric("Colunas", str(int(selected_file["colunas"])))
    metric_cols[2].metric("Tamanho", str(selected_file["tamanho"]))
    metric_cols[3].metric("Atualizado em", selected_file["atualizado_em"].strftime("%Y-%m-%d %H:%M:%S"))

    st.code(str(selected_path), language="text")

    sample_df, columns_df = cached_sample(str(selected_file["caminho"]), sample_limit)

    left_col, right_col = st.columns([1.5, 1])
    with left_col:
        st.markdown(f"**Amostra do dataframe ({len(sample_df)} linhas)**")
        st.dataframe(sample_df, hide_index=True, use_container_width=True)
    with right_col:
        st.markdown("**Resumo das colunas**")
        st.dataframe(columns_df, hide_index=True, use_container_width=True)

    with st.expander("Lista simples de colunas"):
        st.write(list(sample_df.columns))


if __name__ == "__main__":
    main()
