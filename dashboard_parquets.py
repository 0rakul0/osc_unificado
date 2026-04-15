from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from project_paths import AUDITORIA_XLSX_PATH, GOVERNO_FEDERAL_DIR, HISTORIA_DIR, PROCESSADA_DIR

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_STATE_DATA_DIR = PROCESSADA_DIR
DEFAULT_FEDERAL_DATA_DIR = GOVERNO_FEDERAL_DIR
HISTORY_DIR = HISTORIA_DIR
AUDIT_REPORT_PATH = AUDITORIA_XLSX_PATH
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
ORIGEM_PADRAO = "convenios"
NULL_TOKENS = {"", "nan", "none", "null", "nat", "<na>"}
QUALITY_COLUMNS = [
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
STOPWORDS = {
    "a", "ao", "aos", "as", "com", "da", "das", "de", "do", "dos", "e", "em",
    "na", "nas", "no", "nos", "o", "os", "ou", "para", "por", "que", "se",
    "sem", "sob", "sobre", "um", "uma", "uns", "umas", "pela", "pelas",
    "pelo", "pelos", "referente", "objeto", "convenio", "execucao", "servicos",
    "servico", "projeto", "apoio", "estado", "municipio", "municipal", "estadual",
}
PAGE_LINKS = [
    ("dashboard_parquets.py", "Inicio", "inicio"),
    ("pages/01_Panorama.py", "Panorama", "panorama"),
    ("pages/02_Territorio.py", "Territorio", "territorio"),
    ("pages/03_Entidades.py", "Entidades", "entidades"),
    ("pages/04_Auditoria.py", "Auditoria", "auditoria"),
    ("pages/05_Historias.py", "Historias", "historias"),
]


@dataclass
class DashboardContext:
    data_label: str
    data_dirs: tuple[str, ...]
    data: pd.DataFrame
    files_df: pd.DataFrame
    filtered: pd.DataFrame
    filtered_without_year: pd.DataFrame


DirectorySignature = tuple[tuple[str, int, int], ...]
FileSignature = tuple[str, int, int] | tuple[()]
SourcesSignature = tuple[tuple[str, DirectorySignature], ...]


def format_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}".replace(",", ".")


def format_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "0,0%"
    return f"{float(value):.1f}%".replace(".", ",")


def format_money(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "R$ 0,00"
    text = f"{float(value):,.2f}"
    return f"R$ {text.replace(',', 'X').replace('.', ',').replace('X', '.')}"


def render_inline_explainer(text: str) -> None:
    st.markdown(f"> **Como ler:** {text}")


def clean_text(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    lower = values.str.lower()
    values = values.mask(lower.isin(NULL_TOKENS))
    values = values.mask(values.isin(["-", "--"]))
    return values


def derive_instrument_type(data: pd.DataFrame) -> pd.Series:
    modalidade = data["modalidade"].fillna("").astype("string").str.lower()
    objeto = data["objeto"].fillna("").astype("string").str.lower()
    instrument_type = pd.Series("Outros", index=data.index, dtype="string")

    no_info = modalidade.eq("") & objeto.eq("")
    instrument_type.loc[no_info] = "Nao classificado"

    convenio_mask = modalidade.str.contains("convenio|convênio", regex=True) | objeto.str.contains("convenio|convênio", regex=True)
    instrument_type.loc[convenio_mask] = "Convenio"

    parceria_mask = (
        modalidade.str.contains("termo de fomento|termo de colaboracao|termo de colaboração|termo de cooperacao|termo de cooperação|termo de parceria|parceria", regex=True)
        | objeto.str.contains("termo de fomento|termo de colaboracao|termo de colaboração|termo de cooperacao|termo de cooperação|termo de parceria|parceria", regex=True)
    )
    instrument_type.loc[parceria_mask] = "Parceria / termo"

    transferencia_mask = (
        modalidade.str.contains("transferencia|transferência|repasse|auxilio|auxílio|subvenc|contribui", regex=True)
        | objeto.str.contains("transferencia|transferência|repasse|auxilio|auxílio|subvenc|contribui", regex=True)
    )
    instrument_type.loc[transferencia_mask] = "Transferencia / auxilio"

    licitacao_mask = (
        modalidade.str.contains("pregao|pregão|concorr|licit|tomada de preco|tomada de preço|dispensa|dispensad|inexig", regex=True)
        | objeto.str.contains("pregao|pregão|concorr|licit|tomada de preco|tomada de preço|dispensa|inexig", regex=True)
    )
    instrument_type.loc[licitacao_mask] = "Licitacao / contratacao"

    status_mask = modalidade.str.contains(
        "prestacao de contas|prestação de contas|em execucao|em execução|encerrado|vigente|finalizada|formalizada|extinto|rescind|cadastrado|aprovado|lançado|lancado|cancelado",
        regex=True,
    )
    instrument_type.loc[status_mask & instrument_type.isin(["Outros", "Nao classificado"])] = "Status / prestacao de contas"

    return instrument_type.fillna("Outros")


def parse_money_to_centavos(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, Decimal):
        numeric = value
        if abs(numeric) < Decimal("0.005"):
            numeric = Decimal("0")
        numeric = numeric.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return int((numeric * 100).to_integral_value())
    text = str(value).strip()
    if not text or text.lower() in NULL_TOKENS:
        return pd.NA
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
        return pd.NA
    try:
        numeric = Decimal(compact)
    except InvalidOperation:
        return pd.NA
    if abs(numeric) < Decimal("0.005"):
        numeric = Decimal("0")
    numeric = numeric.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((numeric * 100).to_integral_value())


def parse_int_like(series: pd.Series) -> pd.Series:
    cleaned = clean_text(series).str.replace(r"\.0+$", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce").astype("Float64")


def parse_dates(series: pd.Series) -> pd.Series:
    cleaned = clean_text(series)
    parsed = pd.to_datetime(cleaned, errors="coerce", format="mixed", dayfirst=True)
    retry = parsed.isna() & cleaned.notna()
    if retry.any():
        parsed.loc[retry] = pd.to_datetime(cleaned.loc[retry], errors="coerce", format="mixed", dayfirst=False)
    return parsed


def ensure_schema(frame: pd.DataFrame) -> pd.DataFrame:
    for column in STANDARD_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    return frame[STANDARD_COLUMNS].copy()


def build_directory_signature(base_dir: str, pattern: str) -> DirectorySignature:
    path = Path(base_dir)
    if not path.exists():
        return tuple()
    files = sorted(item for item in path.glob(pattern) if item.is_file())
    return tuple(
        (item.name, int(item.stat().st_size), int(item.stat().st_mtime_ns))
        for item in files
    )


def build_file_signature(file_path: str) -> FileSignature:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return tuple()
    stats = path.stat()
    return (path.name, int(stats.st_size), int(stats.st_mtime_ns))


def build_sources_signature(data_dirs: tuple[str, ...]) -> SourcesSignature:
    return tuple((data_dir, build_directory_signature(data_dir, "*.parquet")) for data_dir in data_dirs)


@st.cache_data(show_spinner="Lendo os parquets...", persist="disk")
def load_data(data_dirs: tuple[str, ...], _signatures: SourcesSignature) -> tuple[pd.DataFrame, pd.DataFrame]:
    parquet_paths: list[tuple[str, Path]] = []
    for data_dir in data_dirs:
        base_path = Path(data_dir)
        parquet_paths.extend((data_dir, path) for path in sorted(base_path.glob("*.parquet")))
    if not parquet_paths:
        return pd.DataFrame(columns=STANDARD_COLUMNS), pd.DataFrame()

    frames: list[pd.DataFrame] = []
    file_rows: list[dict[str, object]] = []
    for data_dir, path in parquet_paths:
        source_name = Path(data_dir).name
        frame = ensure_schema(pd.read_parquet(path))
        frame["arquivo_origem"] = f"{source_name}/{path.name}"
        frame["pasta_origem"] = source_name
        frame["uf_arquivo"] = path.stem.upper()
        frames.append(frame)
        file_rows.append(
            {
                "arquivo": f"{source_name}/{path.name}",
                "pasta_origem": source_name,
                "uf": path.stem.upper(),
                "linhas": len(frame),
                "tamanho_mb": round(path.stat().st_size / (1024 * 1024), 2),
                "atualizado_em": pd.Timestamp(path.stat().st_mtime, unit="s"),
            }
        )

    data = pd.concat(frames, ignore_index=True)
    for column in STANDARD_COLUMNS:
        data[column] = clean_text(data[column])
    data["origem"] = data["origem"].fillna(ORIGEM_PADRAO)

    data["valor_num"] = data["valor_total"].map(parse_money_to_centavos).astype("Float64") / 100.0
    data["ano_num"] = parse_int_like(data["ano"])
    data["mes_num"] = parse_int_like(data["mes"])
    data["data_inicio_dt"] = parse_dates(data["data_inicio"])
    data["data_fim_dt"] = parse_dates(data["data_fim"])
    data["duracao_dias"] = (data["data_fim_dt"] - data["data_inicio_dt"]).dt.days.astype("Float64")

    current_year = pd.Timestamp.today().year
    data["tem_cnpj_valido"] = data["cnpj"].str.replace(r"\D", "", regex=True).str.len().eq(14)
    data["tem_municipio"] = data["municipio"].notna()
    data["tem_objeto"] = data["objeto"].notna()
    data["tem_modalidade"] = data["modalidade"].notna()
    data["valor_zero"] = data["valor_num"].fillna(0).eq(0)
    data["valor_negativo"] = data["valor_num"].lt(0).fillna(False)
    data["ano_valido"] = data["ano_num"].between(1990, current_year + 2)
    data["mes_valido"] = data["mes_num"].between(1, 12)
    data["entidade_base"] = data["cnpj"].where(data["tem_cnpj_valido"], data["nome_osc"]).fillna("Sem identificacao")
    data["municipio_base"] = data["municipio"].fillna("Nao informado")
    data["modalidade_base"] = data["modalidade"].fillna("Nao informada")
    data["tipo_instrumento"] = derive_instrument_type(data)

    valid_period = data["ano_valido"] & data["mes_valido"]
    data["ano_mes"] = pd.NaT
    if valid_period.any():
        data.loc[valid_period, "ano_mes"] = pd.to_datetime(
            {
                "year": data.loc[valid_period, "ano_num"].astype(int),
                "month": data.loc[valid_period, "mes_num"].astype(int),
                "day": 1,
            },
            errors="coerce",
        )

    dup_cols = ["uf", "ano", "mes", "valor_total", "cnpj", "nome_osc", "municipio", "objeto", "modalidade"]
    data["duplicado_aparente"] = data[dup_cols].fillna("<vazio>").duplicated(keep=False)

    files_df = pd.DataFrame(file_rows).sort_values(["linhas", "arquivo"], ascending=[False, True]).reset_index(drop=True)
    return data, files_df


@st.cache_data(show_spinner=False, persist="disk")
def load_history_documents(history_dir: str, _signature: DirectorySignature) -> dict[str, str]:
    base = Path(history_dir)
    if not base.exists():
        return {}
    docs: dict[str, str] = {}
    for path in sorted(base.glob("*.md")):
        docs[path.stem.upper()] = path.read_text(encoding="utf-8")
    return docs


@st.cache_data(show_spinner=False, persist="disk")
def load_audit_summary_sheet(audit_path: str, _signature: FileSignature) -> pd.DataFrame:
    path = Path(audit_path)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_excel(path, sheet_name="Resumo")
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False, persist="disk")
def load_audit_sheet_names(audit_path: str, _signature: FileSignature) -> list[str]:
    path = Path(audit_path)
    if not path.exists():
        return []
    try:
        return pd.ExcelFile(path).sheet_names
    except Exception:
        return []


def resolve_audit_sheet_name(uf: str, audit_path: str, signature: FileSignature) -> str | None:
    suffix = f" - {uf}"
    return next((name for name in load_audit_sheet_names(audit_path, signature) if name.endswith(suffix)), None)


@st.cache_data(show_spinner=False, persist="disk")
def load_audit_sheet_detail(audit_path: str, sheet_name: str, _signature: FileSignature) -> dict[str, pd.DataFrame]:
    path = Path(audit_path)
    if not path.exists() or not sheet_name:
        return {}

    try:
        df = pd.read_excel(path, sheet_name=sheet_name)
    except Exception:
        return {}

    def section(start: int, end: int, columns: list[str]) -> pd.DataFrame:
        chunk = df.iloc[:, start:end].copy()
        chunk.columns = columns
        chunk = chunk.dropna(how="all")
        if chunk.empty:
            return chunk
        first_col = columns[0]
        chunk = chunk[chunk[first_col].notna()].copy()
        for column in chunk.columns:
            if chunk[column].dtype == "object":
                chunk[column] = chunk[column].astype("string").str.strip()
        return chunk.reset_index(drop=True)

    return {
        "metrics": section(0, 2, ["metrica", "valor"]),
        "years": section(4, 6, ["ano", "quantidade"]),
        "empty_columns": section(8, 9, ["coluna_sem_dados"]),
        "missing_cnpj_examples": section(11, 12, ["exemplo_nome_osc_sem_cnpj"]),
        "source_files": section(14, 15, ["arquivo_bruto"]),
        "mapping": section(16, 19, ["campo_schema", "origem_bruta", "regra"]),
    }


def history_anchor_id(markdown_text: str, fallback_key: str) -> str:
    first_line = next((line.strip() for line in markdown_text.splitlines() if line.strip().startswith("#")), fallback_key)
    title = re.sub(r"^#+\s*", "", first_line).strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", title).strip("-")
    return slug or fallback_key.lower()


def split_history_markdown(markdown_text: str, fallback_key: str) -> tuple[str, str]:
    lines = markdown_text.splitlines()
    title_line = next((line for line in lines if line.strip().startswith("#")), f"# {fallback_key}")
    title = re.sub(r"^#+\s*", "", title_line).strip()
    title_index = lines.index(title_line) if title_line in lines else 0
    body = "\n".join(lines[title_index + 1:]).strip()
    return title, body


def history_display_label(markdown_text: str, fallback_key: str) -> str:
    title, _ = split_history_markdown(markdown_text, fallback_key)
    match = re.match(r"^(.*?)\s*\(([A-Z]{2})\)\s*$", title)
    if match:
        state_name = match.group(1).strip()
        uf = match.group(2).strip()
        return f"{uf} - {state_name}"
    return fallback_key


def split_history_caveat_section(body: str) -> tuple[str, str | None, str]:
    marker = "## Ressalvas da fonte"
    if marker not in body:
        return body, None, ""
    before, after_marker = body.split(marker, 1)
    after_marker = after_marker.lstrip()
    match = re.search(r"(?m)^##\s+", after_marker)
    if match:
        caveat_content = after_marker[:match.start()].strip()
        remainder = after_marker[match.start():].strip()
    else:
        caveat_content = after_marker.strip()
        remainder = ""
    return before.strip(), caveat_content, remainder


def render_history_body(body: str) -> None:
    before, caveat_content, after = split_history_caveat_section(body)
    if before:
        st.markdown(before)
    if caveat_content:
        st.markdown(
            """
            <style>
            .history-caveat {
                margin: 1rem 0 1.2rem 0;
                padding: 1rem 1.1rem;
                border-left: 6px solid #e36414;
                border-radius: 14px;
                background: linear-gradient(135deg, rgba(255,243,224,0.95), rgba(255,248,240,0.92));
                box-shadow: 0 1px 6px rgba(0,0,0,0.04);
            }
            .history-caveat-title {
                margin-top: 0;
                margin-bottom: 0.35rem;
                font-size: 1.1rem;
                font-weight: 700;
                color: #9a031e;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="history-caveat"><div class="history-caveat-title">Ressalvas da fonte</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(caveat_content)
    if after:
        st.markdown(after)


@st.cache_data(show_spinner=False)
def build_runtime_audit_summary(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    for uf, frame in data.groupby("uf", dropna=False):
        invalid_year_mask = frame["ano"].notna() & ~frame["ano_valido"]
        invalid_month_mask = frame["mes"].notna() & ~frame["mes_valido"]
        invalid_cnpj_mask = frame["cnpj"].notna() & ~frame["tem_cnpj_valido"]
        empty_columns = [
            column
            for column in STANDARD_COLUMNS
            if column != "uf" and frame[column].notna().sum() == 0
        ]
        completeness_components = [
            frame["ano"].notna().mean(),
            frame["tem_cnpj_valido"].mean(),
            frame["tem_municipio"].mean(),
            frame["tem_objeto"].mean(),
            frame["tem_modalidade"].mean(),
            frame["data_inicio"].notna().mean(),
            frame["data_fim"].notna().mean(),
        ]
        rows.append(
            {
                "uf": uf,
                "registros": len(frame),
                "valor_total": float(frame["valor_num"].sum()),
                "valor_zero": int(frame["valor_zero"].sum()),
                "valor_negativo": int(frame["valor_negativo"].sum()),
                "linhas_sem_ano": int(frame["ano"].isna().sum()),
                "anos_invalidos": int(invalid_year_mask.sum()),
                "meses_invalidos": int(invalid_month_mask.sum()),
                "cnpj_invalidos": int(invalid_cnpj_mask.sum()),
                "sem_municipio": int((~frame["tem_municipio"]).sum()),
                "sem_objeto": int((~frame["tem_objeto"]).sum()),
                "sem_modalidade": int((~frame["tem_modalidade"]).sum()),
                "duplicados_aparentes": int(frame["duplicado_aparente"].sum()),
                "colunas_sem_dados_qtd": len(empty_columns),
                "colunas_sem_dados_lista": ", ".join(empty_columns) if empty_columns else "(nenhuma)",
                "completude_pct": float(np.mean(completeness_components) * 100),
            }
        )

    summary = pd.DataFrame(rows)
    summary["indice_alerta"] = (
        (summary["valor_negativo"] > 0).astype(int) * 4
        + (summary["anos_invalidos"] > 0).astype(int) * 3
        + (summary["linhas_sem_ano"] > 0).astype(int) * 2
        + (summary["meses_invalidos"] > 0).astype(int) * 2
        + (summary["cnpj_invalidos"] > 0).astype(int) * 2
        + (summary["colunas_sem_dados_qtd"] > 0).astype(int) * 2
        + (summary["sem_objeto"] > 0).astype(int)
        + (summary["sem_municipio"] > 0).astype(int)
        + (summary["sem_modalidade"] > 0).astype(int)
        + (summary["duplicados_aparentes"] > 0).astype(int)
        + (summary["valor_zero"] > 0).astype(int)
    )
    return summary.sort_values(["indice_alerta", "registros"], ascending=[False, False]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_year_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["ano", "quantidade"])

    years = frame["ano"].astype("string").str.strip()
    years = years.fillna("(sem ano)")
    years = years.replace({"<NA>": "(sem ano)"})
    years = years.str.replace(r"\.0+$", "", regex=True)
    counts = years.value_counts(dropna=False).rename_axis("ano").reset_index(name="quantidade")
    return counts.sort_values("ano").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_missing_cnpj_examples_runtime(frame: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["exemplo_nome_osc_sem_cnpj"])

    examples = (
        frame.loc[frame["cnpj"].isna(), "nome_osc"]
        .dropna()
        .astype("string")
        .str.strip()
        .replace({"": pd.NA})
        .dropna()
        .drop_duplicates()
        .head(limit)
        .tolist()
    )
    if not examples:
        examples = ["(nenhum)"]
    return pd.DataFrame({"exemplo_nome_osc_sem_cnpj": examples})


@st.cache_data(show_spinner=False)
def build_field_completeness(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["campo", "preenchidos", "faltantes", "cobertura_pct"])

    rows: list[dict[str, object]] = []
    total = len(frame)
    for column in STANDARD_COLUMNS:
        filled = int(frame[column].notna().sum())
        rows.append(
            {
                "campo": column,
                "preenchidos": filled,
                "faltantes": total - filled,
                "cobertura_pct": (filled / total * 100) if total else 0,
            }
        )
    return pd.DataFrame(rows).sort_values(["cobertura_pct", "campo"], ascending=[True, True]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_invalid_year_examples(frame: pd.DataFrame, limit: int = 10) -> str:
    values = (
        frame.loc[frame["ano"].notna() & ~frame["ano_valido"], "ano"]
        .astype("string")
        .str.strip()
        .replace({"": pd.NA})
        .dropna()
        .drop_duplicates()
        .head(limit)
        .tolist()
    )
    return ", ".join(values) if values else "(nenhum)"


@st.cache_data(show_spinner=False)
def apply_filters(
    data: pd.DataFrame,
    selected_ufs: list[str],
    year_range: tuple[int, int] | None,
    selected_modalities: list[str],
    selected_instrument_types: list[str],
    minimum_value: float,
    only_valid_cnpj: bool,
    exclude_zero_negative: bool,
    search_text: str,
) -> pd.DataFrame:
    filtered = data.copy()
    if selected_ufs:
        filtered = filtered[filtered["uf"].isin(selected_ufs)]
    if year_range:
        filtered = filtered[filtered["ano_num"].between(year_range[0], year_range[1], inclusive="both")]
    if selected_modalities:
        filtered = filtered[filtered["modalidade_base"].isin(selected_modalities)]
    if selected_instrument_types:
        filtered = filtered[filtered["tipo_instrumento"].isin(selected_instrument_types)]
    if minimum_value > 0:
        filtered = filtered[filtered["valor_num"].ge(minimum_value)]
    if only_valid_cnpj:
        filtered = filtered[filtered["tem_cnpj_valido"]]
    if exclude_zero_negative:
        filtered = filtered[filtered["valor_num"].gt(0)]
    if search_text:
        mask = (
            filtered["nome_osc"].fillna("").str.contains(search_text, case=False, regex=False)
            | filtered["objeto"].fillna("").str.contains(search_text, case=False, regex=False)
            | filtered["municipio"].fillna("").str.contains(search_text, case=False, regex=False)
            | filtered["cnpj"].fillna("").str.contains(search_text, case=False, regex=False)
        )
        filtered = filtered[mask]
    return filtered.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_uf_summary(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return pd.DataFrame()
    grouped = (
        filtered.groupby("uf", dropna=False)
        .agg(
            registros=("uf", "size"),
            valor_total=("valor_num", "sum"),
            ticket_medio=("valor_num", "mean"),
            ticket_mediano=("valor_num", "median"),
            entidades=("nome_osc", lambda values: values.dropna().nunique()),
            cnpjs=("cnpj", lambda values: values.dropna().nunique()),
            municipios=("municipio", lambda values: values.dropna().nunique()),
            cobertura_cnpj=("tem_cnpj_valido", "mean"),
            cobertura_municipio=("tem_municipio", "mean"),
            cobertura_objeto=("tem_objeto", "mean"),
            cobertura_modalidade=("tem_modalidade", "mean"),
        )
        .reset_index()
    )
    for column in ["cobertura_cnpj", "cobertura_municipio", "cobertura_objeto", "cobertura_modalidade"]:
        grouped[column] = grouped[column] * 100
    return grouped.sort_values(["valor_total", "registros"], ascending=[False, False]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_entity_summary(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return pd.DataFrame()
    entities = (
        filtered.groupby("entidade_base", dropna=False)
        .agg(
            nome_osc=("nome_osc", lambda values: values.dropna().mode().iat[0] if not values.dropna().empty else "Sem nome"),
            cnpj=("cnpj", lambda values: values.dropna().iat[0] if not values.dropna().empty else pd.NA),
            registros=("entidade_base", "size"),
            valor_total=("valor_num", "sum"),
            ticket_medio=("valor_num", "mean"),
            ufs=("uf", lambda values: values.dropna().nunique()),
            municipios=("municipio", lambda values: values.dropna().nunique()),
            primeiro_ano=("ano_num", "min"),
            ultimo_ano=("ano_num", "max"),
        )
        .reset_index()
    )
    entities["identificador"] = entities["cnpj"].fillna(entities["nome_osc"])
    return entities.sort_values(["valor_total", "registros"], ascending=[False, False]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_state_benchmark(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    for uf, frame in data.groupby("uf", dropna=False):
        entity_values = frame.groupby("nome_osc", dropna=False)["valor_num"].sum().sort_values(ascending=False)
        total = float(frame["valor_num"].sum())
        rows.append(
            {
                "uf": uf,
                "registros": len(frame),
                "valor_total": total,
                "ticket_medio": float(frame["valor_num"].mean()),
                "ticket_mediano": float(frame["valor_num"].median()),
                "entidades": int(frame["nome_osc"].dropna().nunique()),
                "cnpjs": int(frame.loc[frame["tem_cnpj_valido"], "cnpj"].dropna().nunique()),
                "cob_municipio": float(frame["tem_municipio"].mean() * 100),
                "cob_objeto": float(frame["tem_objeto"].mean() * 100),
                "cob_modalidade": float(frame["tem_modalidade"].mean() * 100),
                "top1_share_pct": float(entity_values.head(1).sum() / total * 100) if total else 0.0,
                "top5_share_pct": float(entity_values.head(5).sum() / total * 100) if total else 0.0,
                "top10_share_pct": float(entity_values.head(10).sum() / total * 100) if total else 0.0,
            }
        )
    benchmark = pd.DataFrame(rows)
    national_total = benchmark["valor_total"].sum()
    benchmark["share_nacional_pct"] = benchmark["valor_total"] / national_total * 100
    benchmark["rank_valor_total"] = benchmark["valor_total"].rank(method="min", ascending=False).astype(int)
    benchmark["rank_registros"] = benchmark["registros"].rank(method="min", ascending=False).astype(int)
    benchmark["rank_ticket_medio"] = benchmark["ticket_medio"].rank(method="min", ascending=False).astype(int)
    benchmark["rank_concentracao"] = benchmark["top5_share_pct"].rank(method="min", ascending=False).astype(int)
    return benchmark.sort_values("valor_total", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_word_frequency(series: pd.Series, top_n: int = 20) -> pd.DataFrame:
    tokens = (
        series.dropna()
        .astype("string")
        .str.upper()
        .str.replace(r"[^A-Z0-9À-Ú]+", " ", regex=True)
        .str.split()
        .explode()
    )
    if tokens.empty:
        return pd.DataFrame(columns=["termo", "frequencia"])
    tokens = tokens[tokens.notna()]
    tokens = tokens[tokens.str.len().ge(4)]
    tokens = tokens[~tokens.str.lower().isin(STOPWORDS)]
    freq = tokens.value_counts().head(top_n)
    return freq.rename_axis("termo").reset_index(name="frequencia")


@st.cache_data(show_spinner=False)
def build_benchmark_export_frames(filtered: pd.DataFrame, full_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    benchmark_full = build_state_benchmark(full_data)
    benchmark_current = build_state_benchmark(filtered)
    uf_summary = build_uf_summary(filtered)
    top_entities = build_entity_summary(filtered).head(200)
    narrativa = build_executive_narrative_rows(filtered, full_data)

    annual = (
        filtered.loc[filtered["ano_valido"]]
        .groupby(["uf", "ano_num"])
        .agg(registros=("uf", "size"), valor_total=("valor_num", "sum"), ticket_medio=("valor_num", "mean"))
        .reset_index()
        .rename(columns={"ano_num": "ano"})
    )

    quality = (
        filtered.groupby("uf")[QUALITY_COLUMNS]
        .apply(lambda frame: frame.isna().mean() * 100)
        .reset_index()
        .melt(id_vars="uf", var_name="campo", value_name="faltante_pct")
    )

    return {
        "resumo_executivo": narrativa,
        "benchmark_atual": benchmark_current,
        "benchmark_nacional": benchmark_full,
        "resumo_uf": uf_summary,
        "top_entidades": top_entities,
        "serie_anual": annual,
        "qualidade": quality,
    }


@st.cache_data(show_spinner=False)
def dataframe_to_excel_bytes(frames: dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, frame in frames.items():
            safe_name = re.sub(r"[^A-Za-z0-9_]", "_", sheet_name)[:31]
            frame.to_excel(writer, sheet_name=safe_name, index=False)
    output.seek(0)
    return output.getvalue()


def classify_state_driver(row: pd.Series, benchmark: pd.DataFrame) -> str:
    high_rows = row["registros"] >= benchmark["registros"].quantile(0.75)
    high_ticket = row["ticket_medio"] >= benchmark["ticket_medio"].quantile(0.75)
    high_concentration = row["top5_share_pct"] >= benchmark["top5_share_pct"].quantile(0.75)
    if high_rows and high_ticket:
        return "volume e ticket"
    if high_rows and not high_ticket:
        return "volume"
    if high_ticket and high_concentration:
        return "ticket e concentracao"
    if high_ticket:
        return "ticket medio"
    if high_concentration:
        return "concentracao"
    return "base mais distribuida"


def build_state_narrative(uf: str, benchmark: pd.DataFrame) -> str:
    row = benchmark.loc[benchmark["uf"] == uf]
    if row.empty:
        return f"`{uf}` nao esta presente no conjunto atual."
    row = row.iloc[0]
    driver = classify_state_driver(row, benchmark)
    return (
        f"`{uf}` tem `rank {int(row['rank_valor_total'])}` em valor total, `rank {int(row['rank_registros'])}` em volume de registros, "
        f"`rank {int(row['rank_ticket_medio'])}` em ticket medio e `rank {int(row['rank_concentracao'])}` em concentracao dos 5 maiores. "
        f"O perfil dominante dessa UF e `{driver}`. "
        f"Ela soma {format_money(row['valor_total'])}, com {format_int(row['registros'])} registros, "
        f"ticket medio de {format_money(row['ticket_medio'])} e concentracao top 5 de {format_pct(row['top5_share_pct'])}."
    )


def render_benchmark_narratives(benchmark: pd.DataFrame) -> None:
    top_value = benchmark.sort_values("valor_total", ascending=False).head(5)["uf"].tolist()
    top_rows = benchmark.sort_values("registros", ascending=False).head(5)["uf"].tolist()
    top_ticket = benchmark.sort_values("ticket_medio", ascending=False).head(5)["uf"].tolist()
    top_concentration = benchmark.sort_values("top5_share_pct", ascending=False).head(5)["uf"].tolist()

    st.markdown("**Leitura guiada**")
    st.write(
        f"No conjunto nacional, as UFs que mais pesam em valor sao `{', '.join(top_value[:5])}`; em quantidade de linhas, `{', '.join(top_rows[:5])}`; "
        f"em ticket medio, `{', '.join(top_ticket[:5])}`; e em concentracao dos 5 maiores beneficiarios, `{', '.join(top_concentration[:5])}`."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(
            "**Por que SP destoa?**\n\n"
            + build_state_narrative("SP", benchmark)
            + "\n\nLeitura: SP e grande porque combina base volumosa com ticket ainda alto, alem de ter estrutura mais diversificada do que estados muito concentrados."
        )
    with col2:
        st.warning(
            "**Por que AM destoa?**\n\n"
            + build_state_narrative("AM", benchmark)
            + "\n\nLeitura: AM sobe no ranking menos por quantidade de linhas e mais por contratos muito grandes concentrados em poucas entidades."
        )
    with col3:
        median_rows = benchmark["registros"].median()
        median_ticket = benchmark["ticket_medio"].median()
        st.success(
            "**Padrao geral das UFs**\n\n"
            f"A mediana do conjunto e de {format_int(median_rows)} registros por UF e ticket medio de {format_money(median_ticket)}. "
            "Estados acima da mediana de registros tendem a crescer por massa de dados; estados acima da mediana de ticket tendem a crescer por contratos maiores. "
            "Quando a concentracao top 5 sobe muito, poucos beneficiarios passam a explicar boa parte do valor total."
        )


def build_executive_narrative_rows(filtered: pd.DataFrame, full_data: pd.DataFrame) -> pd.DataFrame:
    benchmark_full = build_state_benchmark(full_data)
    benchmark_current = build_state_benchmark(filtered)
    reference = benchmark_current if not benchmark_current.empty else benchmark_full

    top_value = benchmark_full.sort_values("valor_total", ascending=False).head(5)["uf"].tolist()
    top_rows = benchmark_full.sort_values("registros", ascending=False).head(5)["uf"].tolist()
    top_ticket = benchmark_full.sort_values("ticket_medio", ascending=False).head(5)["uf"].tolist()
    top_concentration = benchmark_full.sort_values("top5_share_pct", ascending=False).head(5)["uf"].tolist()

    rows = [
        {
            "secao": "Resumo executivo",
            "texto": (
                f"O recorte atual contem {format_int(len(filtered))} registros e {format_money(filtered['valor_num'].sum())} em valor total. "
                f"No conjunto nacional, as maiores UFs por valor sao {', '.join(top_value[:5])}; por quantidade de registros, {', '.join(top_rows[:5])}; "
                f"por ticket medio, {', '.join(top_ticket[:5])}; e por concentracao dos 5 maiores beneficiarios, {', '.join(top_concentration[:5])}."
            ),
        },
        {
            "secao": "Por que SP destoa?",
            "texto": build_state_narrative("SP", benchmark_full)
            + " Leitura executiva: SP se destaca principalmente por volume de base combinado com ticket relevante, formando um total muito alto sem depender tanto de poucos beneficiarios.",
        },
        {
            "secao": "Por que AM destoa?",
            "texto": build_state_narrative("AM", benchmark_full)
            + " Leitura executiva: AM se destaca menos por quantidade e mais por contratos muito grandes concentrados em poucas entidades.",
        },
        {
            "secao": "Padrao geral",
            "texto": (
                f"No recorte atual, a mediana entre as UFs e de {format_int(reference['registros'].median())} registros e ticket medio de {format_money(reference['ticket_medio'].median())}. "
                "Isso ajuda a separar estados puxados por massa de dados daqueles puxados por ticket medio alto ou forte concentracao."
            ),
        },
    ]
    return pd.DataFrame(rows)


def render_dynamic_executive_summary(filtered: pd.DataFrame, full_data: pd.DataFrame) -> None:
    st.markdown("**Resumo Executivo Dinamico**")
    st.caption("Este bloco traduz o recorte atual em leitura executiva antes da exploracao visual.")

    uf_summary = build_uf_summary(filtered)
    entity_summary = build_entity_summary(filtered)
    annual = (
        filtered.loc[filtered["ano_valido"]]
        .groupby("ano_num")
        .agg(valor_total=("valor_num", "sum"), registros=("ano_num", "size"))
        .reset_index()
    )
    instrument_summary = (
        filtered.groupby("tipo_instrumento", dropna=False)
        .agg(valor_total=("valor_num", "sum"), registros=("tipo_instrumento", "size"))
        .reset_index()
        .sort_values(["valor_total", "registros"], ascending=[False, False])
    )

    total_valor = float(filtered["valor_num"].sum())
    top_uf_text = "Sem UF lider no recorte."
    if not uf_summary.empty and total_valor > 0:
        top_uf = uf_summary.iloc[0]
        share = float(top_uf["valor_total"]) / total_valor * 100
        top_uf_text = (
            f"`{top_uf['uf']}` lidera o recorte com {format_money(top_uf['valor_total'])}, "
            f"equivalente a {format_pct(share)} do valor filtrado."
        )

    top_instrument_text = "Sem classificacao de instrumento disponivel."
    if not instrument_summary.empty and total_valor > 0:
        top_instrument = instrument_summary.iloc[0]
        share = float(top_instrument["valor_total"]) / total_valor * 100
        top_instrument_text = (
            f"O tipo dominante e `{top_instrument['tipo_instrumento']}`, com "
            f"{format_money(top_instrument['valor_total'])} e {format_pct(share)} do valor total."
        )

    top_entity_text = "Sem entidade lider identificada."
    if not entity_summary.empty and total_valor > 0:
        top_entity = entity_summary.iloc[0]
        share = float(top_entity["valor_total"]) / total_valor * 100
        top_entity_text = (
            f"A entidade que mais pesa e `{top_entity['nome_osc']}`, com "
            f"{format_money(top_entity['valor_total'])} e {format_pct(share)} do total."
        )

    temporal_text = "Sem leitura temporal valida neste recorte."
    if not annual.empty:
        peak = annual.sort_values("valor_total", ascending=False).iloc[0]
        temporal_text = (
            f"O pico temporal do recorte esta em `{int(peak['ano_num'])}`, com "
            f"{format_money(peak['valor_total'])} e {format_int(peak['registros'])} registros."
        )
        annual_sorted = annual.sort_values("ano_num")
        if len(annual_sorted) >= 2:
            prev = annual_sorted.iloc[-2]
            curr = annual_sorted.iloc[-1]
            if prev["valor_total"] and not pd.isna(prev["valor_total"]):
                variation = ((curr["valor_total"] / prev["valor_total"]) - 1) * 100
                temporal_text += (
                    f" Na borda mais recente, `{int(curr['ano_num'])}` ficou em "
                    f"{format_money(curr['valor_total'])}, variacao de {format_pct(variation)} "
                    f"contra `{int(prev['ano_num'])}`."
                )

    cobertura_objeto = filtered["tem_objeto"].mean() * 100 if len(filtered) else 0
    cobertura_municipio = filtered["tem_municipio"].mean() * 100 if len(filtered) else 0
    cobertura_modalidade = filtered["tem_modalidade"].mean() * 100 if len(filtered) else 0
    anos_invalidos = int(((~filtered["ano_valido"]) & filtered["ano"].notna()).sum())
    valores_negativos = int(filtered["valor_negativo"].sum())
    duplicados = int(filtered["duplicado_aparente"].sum())
    quality_text = (
        f"Cobertura no recorte: objeto {format_pct(cobertura_objeto)}, municipio {format_pct(cobertura_municipio)} "
        f"e modalidade {format_pct(cobertura_modalidade)}."
    )
    alert_parts: list[str] = []
    if anos_invalidos:
        alert_parts.append(f"{format_int(anos_invalidos)} anos invalidos")
    if valores_negativos:
        alert_parts.append(f"{format_int(valores_negativos)} valores negativos")
    if duplicados:
        alert_parts.append(f"{format_int(duplicados)} duplicados aparentes")
    if alert_parts:
        quality_text += " Principais alertas: " + ", ".join(alert_parts) + "."
    else:
        quality_text += " Nao ha alertas fortes de ano invalido, valor negativo ou duplicidade aparente neste recorte."

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Leitura principal**\n\n" + top_uf_text + "\n\n" + top_instrument_text)
    with col2:
        st.success("**Trajetoria**\n\n" + temporal_text)
    with col3:
        st.warning("**Confiabilidade**\n\n" + quality_text)

    st.markdown("**Como comecar a leitura**")
    st.markdown(
        """
        1. Leia o resumo executivo acima para entender o que domina o recorte atual.
        2. Entre em `Panorama` para confirmar volume, tempo e tipo do instrumento.
        3. Use `Territorio` para localizar a concentracao espacial.
        4. Use `Entidades` para identificar os principais beneficiarios.
        5. Feche em `Auditoria` e `Historias` para validar qualidade e interpretar o contexto.
        """
    )


def render_glossary() -> None:
    with st.expander("Glossario rapido"):
        st.markdown(
            """
            - `Recorte atual`: tudo o que sobrou depois dos filtros globais da lateral.
            - `Ticket medio`: valor medio por registro no recorte.
            - `Mediana`: valor central da distribuicao, menos sensivel a outliers.
            - `Valor total`: soma de `valor_num`, derivado do `valor_total` decimal do parquet e exibido em reais.
            - `Ano valido`: ano que passou pela validacao numerica do dashboard.
            - `Duplicado aparente`: registros iguais nos campos centrais do schema; e um sinal de revisao, nao uma prova definitiva de duplicidade.
            - `Tipo do instrumento`: classificacao heuristica baseada em `modalidade` e `objeto`, usada para separar convenios, termos, transferencias e contratacoes.
            - `Cobertura`: percentual de registros com um campo efetivamente preenchido.
            """
        )


def render_header(data: pd.DataFrame, files_df: pd.DataFrame, data_label: str) -> None:
    last_update = files_df["atualizado_em"].max() if not files_df.empty else None
    updated_text = last_update.strftime("%d/%m/%Y %H:%M") if pd.notna(last_update) else "n/d"
    st.markdown(
        """
        <style>
        .hero {padding: 1.1rem 1.3rem; border-radius: 18px; color: white;
        background: linear-gradient(135deg, rgba(15,76,92,0.95), rgba(227,100,20,0.90));
        box-shadow: 0 18px 40px rgba(15,76,92,0.18); margin-bottom: 1rem;}
        .hero h1 {margin: 0; font-size: 2rem;}
        .hero p {margin: .35rem 0 0; opacity: .95;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="hero">
            <h1>Dashboard Analitico dos Parquets</h1>
            <p>Leitura de <strong>{data_label}</strong> com {format_int(len(data))} registros, valor agregado de <strong>{format_money(data['valor_num'].sum())}</strong> e ultima atualizacao em <strong>{updated_text}</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_valid_multiselect_state(key: str, options: list[str], fallback: list[str]) -> list[str]:
    state_value = st.session_state.get(key, fallback)
    if not isinstance(state_value, list):
        return fallback
    sanitized = [value for value in state_value if value in options]
    return sanitized or fallback


def get_valid_year_range_state(key: str, valid_years: list[int]) -> tuple[int, int] | None:
    if not valid_years:
        return None
    fallback = (min(valid_years), max(valid_years))
    state_value = st.session_state.get(key, fallback)
    if not isinstance(state_value, (list, tuple)) or len(state_value) != 2:
        return fallback
    start = max(min(valid_years), min(int(state_value[0]), max(valid_years)))
    end = min(max(valid_years), max(int(state_value[1]), min(valid_years)))
    if start > end:
        return fallback
    return start, end


def render_sidebar(data: pd.DataFrame, files_df: pd.DataFrame) -> tuple[list[str], tuple[int, int] | None, list[str], list[str], float, bool, bool, str]:
    st.sidebar.header("Filtros")
    if st.sidebar.button("Recarregar cache", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    available_ufs = sorted(data["uf"].dropna().unique().tolist())
    selected_ufs = st.sidebar.multiselect(
        "UFs",
        available_ufs,
        default=get_valid_multiselect_state("filter_ufs", available_ufs, available_ufs),
        key="filter_ufs",
    )
    valid_years = sorted(int(v) for v in data.loc[data["ano_valido"], "ano_num"].dropna().unique().tolist())
    year_range = None
    if valid_years:
        year_range = st.sidebar.slider(
            "Filtro global de ano",
            min(valid_years),
            max(valid_years),
            get_valid_year_range_state("filter_year_range", valid_years),
            key="filter_year_range",
        )
    st.sidebar.caption("Esse filtro vale para o dashboard inteiro. O Panorama tem uma comparacao temporal propria.")
    modalities = data["modalidade_base"].value_counts().head(25).index.tolist()
    selected_modalities = st.sidebar.multiselect(
        "Modalidades",
        modalities,
        default=get_valid_multiselect_state("filter_modalities", modalities, []),
        key="filter_modalities",
    )
    instrument_types = data["tipo_instrumento"].value_counts().index.tolist()
    selected_instrument_types = st.sidebar.multiselect(
        "Tipo do instrumento",
        instrument_types,
        default=get_valid_multiselect_state("filter_instrument_types", instrument_types, []),
        key="filter_instrument_types",
    )
    minimum_value = st.sidebar.number_input(
        "Valor minimo",
        min_value=0.0,
        value=float(st.session_state.get("filter_minimum_value", 0.0)),
        step=50000.0,
        key="filter_minimum_value",
    )
    only_valid_cnpj = st.sidebar.checkbox("Somente CNPJ valido", value=bool(st.session_state.get("filter_only_valid_cnpj", False)), key="filter_only_valid_cnpj")
    exclude_zero_negative = st.sidebar.checkbox("Excluir zero e negativos", value=bool(st.session_state.get("filter_exclude_zero_negative", False)), key="filter_exclude_zero_negative")
    search_text = st.sidebar.text_input("Busca textual", value=str(st.session_state.get("filter_search_text", "")), key="filter_search_text")
    st.sidebar.divider()
    st.sidebar.caption(f"Arquivos lidos: {format_int(len(files_df))}")
    return selected_ufs, year_range, selected_modalities, selected_instrument_types, minimum_value, only_valid_cnpj, exclude_zero_negative, search_text


def resolve_selected_data_sources(source_mode: str, state_dir: str, federal_dir: str) -> tuple[str, tuple[str, ...]]:
    if source_mode == "Estadual":
        return Path(state_dir).name, (state_dir,)
    if source_mode == "Governo federal":
        return Path(federal_dir).name, (federal_dir,)
    return f"{Path(state_dir).name} + {Path(federal_dir).name}", (state_dir, federal_dir)


def render_tab_guide() -> None:
    st.markdown("**Guia das abas**")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            "**Panorama**\n\n"
            "Resumo geral do recorte com tendencia temporal, quadro comparativo por UF e leitura por tipo do instrumento."
        )
        st.info(
            "**Territorio**\n\n"
            "Distribuicao territorial dos recursos por UF e municipio."
        )

    with col2:
        st.info(
            "**Entidades**\n\n"
            "Ranking e perfil das OSCs ou beneficiarios com maior peso financeiro ou maior volume de registros."
        )
        st.info(
            "**Auditoria**\n\n"
            "Painel de revisao por UF, com subsecao de qualidade dos dados e subsecao de benchmark entre estados."
        )

    with col3:
        st.info(
            "**Historias**\n\n"
            "Narrativas corridas por UF, em formato de wiki, com interpretacao analitica e fontes."
        )


def render_overview(filtered: pd.DataFrame, full_data: pd.DataFrame, overview_base: pd.DataFrame) -> None:
    st.subheader("Panorama")
    st.markdown("**Como ler esta secao**")
    st.markdown(
        """
        1. **Cards do topo**: mostram o tamanho do recorte atual, com volume, valor, ticket e quantidade de entidades.
        2. **Janela comparativa do panorama**: define se os comparativos abaixo olham o recorte atual, um ano isolado ou um acumulado de anos.
        3. **Valor total por UF**: responde quais estados mais pesam financeiramente dentro da janela escolhida.
        4. **Distribuicao dos valores**: mostra se a base e puxada por muitos registros pequenos ou por poucos registros muito grandes.
        5. **Tendencia temporal**: mostra como o volume evolui ao longo do tempo e onde ha mudancas de ritmo.
        6. **Leitura por tipo do instrumento**: mostra se o resultado vem mais de convenios, termos, transferencias ou contratacoes.
        7. **Tabela final**: serve para conferir os numeros consolidados por UF sem depender so da leitura visual.
        """
    )
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Registros", format_int(len(filtered)))
    col2.metric("Valor total", format_money(filtered["valor_num"].sum()))
    col3.metric("Ticket medio", format_money(filtered["valor_num"].mean()))
    col4.metric("Mediana", format_money(filtered["valor_num"].median()))
    col5.metric("Entidades", format_int(filtered["nome_osc"].dropna().nunique()))
    col6.metric("CNPJs validos", format_int(filtered.loc[filtered["tem_cnpj_valido"], "cnpj"].dropna().nunique()))

    valid_years = sorted(int(year) for year in overview_base.loc[overview_base["ano_valido"], "ano_num"].dropna().unique().tolist())
    st.markdown("**Janela temporal do panorama**")
    render_inline_explainer("Use esta etapa para decidir se os comparativos vao olhar um ano especifico, um acumulado de anos ou simplesmente manter o recorte global atual.")

    overview_mode = st.radio(
        "Modo de comparacao do panorama",
        ["Faixa acumulada", "Ano isolado", "Recorte atual"],
        horizontal=True,
        index=0,
        key="overview_time_mode",
    )

    comparison_source = filtered
    comparison_label = "recorte atual"

    if overview_mode == "Ano isolado" and valid_years:
        selected_year = st.slider(
            "Barra temporal do panorama",
            min_value=min(valid_years),
            max_value=max(valid_years),
            value=max(valid_years),
            key="overview_single_year",
        )
        comparison_source = overview_base.loc[overview_base["ano_num"].eq(selected_year)].copy()
        comparison_label = f"ano {selected_year}"
    elif overview_mode == "Faixa acumulada" and valid_years:
        selected_range = st.slider(
            "Barra temporal do panorama",
            min_value=min(valid_years),
            max_value=max(valid_years),
            value=(min(valid_years), max(valid_years)),
            key="overview_year_range",
        )
        comparison_source = overview_base.loc[
            overview_base["ano_num"].between(selected_range[0], selected_range[1], inclusive="both")
        ].copy()
        comparison_label = f"acumulado de {selected_range[0]} a {selected_range[1]}"
    else:
        st.info("A barra temporal do panorama aparece nos modos `Faixa acumulada` e `Ano isolado`.")

    summary = build_uf_summary(comparison_source)
    st.markdown("**Comparacao entre UFs**")
    render_inline_explainer("Aqui a pergunta principal e: quais estados concentram mais valor dentro da janela escolhida?")
    left, right = st.columns([1.2, 0.8])
    with left:
        fig = px.bar(
            summary.sort_values("valor_total").tail(15),
            x="valor_total",
            y="uf",
            orientation="h",
            title=f"Valor total por UF ({comparison_label})",
            color="valor_total",
            color_continuous_scale=["#d8f3dc", "#0f4c5c"],
        )
        fig.update_layout(height=440, margin=dict(l=10, r=10, t=60, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")
    with right:
        positive = filtered.loc[filtered["valor_num"].gt(0), "valor_num"].dropna()
        if positive.empty:
            st.info("Sem valores positivos para distribuicao.")
        else:
            hist = pd.DataFrame({"log10_valor": np.log10(positive.clip(lower=1))})
            fig = px.histogram(hist, x="log10_valor", nbins=40, title="Distribuicao dos valores (log10)", color_discrete_sequence=["#e36414"])
            fig.update_layout(height=440, margin=dict(l=10, r=10, t=60, b=10))
            st.plotly_chart(fig, width="stretch")

    st.markdown("**Distribuicao dos valores**")
    render_inline_explainer("Este histograma mostra se a base e dominada por poucos contratos muito altos ou por uma massa mais distribuida de registros.")

    render_temporal_analysis(filtered)

    st.markdown("**Leitura por tipo do instrumento**")
    render_inline_explainer("Nesta etapa, a pergunta muda de `quanto` para `como`: que tipo de instrumento esta puxando o resultado financeiro?")
    instrument_summary = (
        comparison_source.groupby("tipo_instrumento", dropna=False)
        .agg(registros=("tipo_instrumento", "size"), valor_total=("valor_num", "sum"))
        .reset_index()
        .sort_values(["valor_total", "registros"], ascending=[False, False])
    )
    instrument_summary["share_valor_pct"] = instrument_summary["valor_total"] / max(instrument_summary["valor_total"].sum(), 1) * 100

    left, right = st.columns([1.0, 1.0])
    with left:
        fig = px.bar(
            instrument_summary.sort_values("valor_total", ascending=True),
            x="valor_total",
            y="tipo_instrumento",
            orientation="h",
            title="Valor total por tipo do instrumento",
            color="tipo_instrumento",
        )
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10), showlegend=False)
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.pie(
            instrument_summary,
            names="tipo_instrumento",
            values="valor_total",
            title="Participacao no valor total",
            hole=0.45,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")

    instrument_display = instrument_summary.copy()
    instrument_display["valor_total"] = instrument_display["valor_total"].map(format_money)
    instrument_display["share_valor_pct"] = instrument_display["share_valor_pct"].map(format_pct)
    st.dataframe(instrument_display, width="stretch", hide_index=True)

    display = summary.copy()
    st.markdown("**Tabela de conferência por UF**")
    render_inline_explainer("Use esta tabela para validar os totais e coberturas por UF sem depender apenas dos graficos.")
    for column in ["valor_total", "ticket_medio", "ticket_mediano"]:
        display[column] = display[column].map(format_money)
    for column in ["cobertura_cnpj", "cobertura_municipio", "cobertura_objeto", "cobertura_modalidade"]:
        display[column] = display[column].map(format_pct)
    st.dataframe(display, width="stretch", hide_index=True)
    st.caption(
        f"O recorte atual representa {format_pct(len(filtered) / max(len(full_data), 1) * 100)} da base carregada. "
        f"Os graficos comparativos acima estao mostrando `{comparison_label}`."
    )


def render_temporal_analysis(filtered: pd.DataFrame) -> None:
    st.markdown("**Tendencia temporal**")
    render_inline_explainer("Aqui voce observa ritmo, inflexoes e picos ao longo do tempo no recorte atual.")
    annual = (
        filtered.loc[filtered["ano_valido"]]
        .groupby("ano_num")
        .agg(valor_total=("valor_num", "sum"), registros=("ano_num", "size"), ticket_medio=("valor_num", "mean"))
        .reset_index()
    )
    if annual.empty:
        st.info("Nao ha anos validos no recorte atual para a leitura temporal.")
        return
    render_inline_explainer("Esta secao mostra a tendencia temporal do recorte global atual.")
    metric = st.radio("Metrica temporal", ["Valor total", "Registros", "Ticket medio"], horizontal=True, key="temporal_metric")
    y_map = {"Valor total": "valor_total", "Registros": "registros", "Ticket medio": "ticket_medio"}
    left, right = st.columns([1.1, 0.9])
    with left:
        fig = px.line(annual, x="ano_num", y=y_map[metric], markers=True, title=f"Evolucao anual - {metric.lower()}", color_discrete_sequence=["#0f4c5c"])
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        by_uf_year = filtered.loc[filtered["ano_valido"]].groupby(["uf", "ano_num"])["valor_num"].sum().reset_index()
        if by_uf_year.empty:
            st.info("Sem combinacoes de UF e ano.")
        else:
            heat = by_uf_year.pivot(index="uf", columns="ano_num", values="valor_num")
            fig = px.imshow(heat, aspect="auto", color_continuous_scale=["#fff4e6", "#fb8b24", "#9a031e"], title="Heatmap de valor por UF e ano")
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=60, b=10))
            st.plotly_chart(fig, width="stretch")

    instrument_year = (
        filtered.loc[filtered["ano_valido"]]
        .groupby(["ano_num", "tipo_instrumento"], dropna=False)
        .agg(valor_total=("valor_num", "sum"), registros=("tipo_instrumento", "size"))
        .reset_index()
    )
    if not instrument_year.empty:
        st.markdown("**Evolucao por tipo do instrumento**")
        render_inline_explainer("Este bloco mostra se a mudanca no tempo veio de convenios, termos, transferencias ou contratacoes.")
        instrument_metric = st.radio(
            "Leitura por tipo",
            ["Valor total por tipo", "Registros por tipo"],
            horizontal=True,
            key="temporal_instrument_metric",
        )
        instrument_y = "valor_total" if instrument_metric == "Valor total por tipo" else "registros"
        fig = px.area(
            instrument_year,
            x="ano_num",
            y=instrument_y,
            color="tipo_instrumento",
            title=f"Evolucao anual por tipo do instrumento - {instrument_metric.lower()}",
        )
        fig.update_layout(height=430, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")

    st.markdown("**Corte anual por UF**")
    render_inline_explainer("Este e o corte mais auditavel para comparar estados em um ano especifico: filtra o ano, soma `valor_num` por UF e ordena pelo total.")

    available_years = sorted(int(year) for year in annual["ano_num"].dropna().unique().tolist())
    default_year = available_years[-1]
    control_col1, control_col2 = st.columns([0.35, 0.65])
    with control_col1:
        selected_year = st.selectbox("Ano para comparar UFs", available_years, index=len(available_years) - 1)
    with control_col2:
        top_n = st.slider("Quantidade de UFs no ranking", min_value=5, max_value=min(len(by_uf_year["uf"].unique()), 27), value=min(15, len(by_uf_year["uf"].unique())))

    annual_cut = (
        filtered.loc[filtered["ano_num"].eq(selected_year)]
        .groupby("uf", dropna=False)
        .agg(valor_total=("valor_num", "sum"), registros=("uf", "size"), ticket_medio=("valor_num", "mean"))
        .reset_index()
        .sort_values(["valor_total", "registros"], ascending=[False, False])
    )

    if annual_cut.empty:
        st.info(f"Nao ha registros para {selected_year} no recorte atual.")
        return

    annual_type_cut = (
        filtered.loc[filtered["ano_num"].eq(selected_year)]
        .groupby(["uf", "tipo_instrumento"], dropna=False)
        .agg(valor_total=("valor_num", "sum"))
        .reset_index()
    )

    cut_left, cut_right = st.columns([1.0, 1.0])
    with cut_left:
        top_cut = annual_cut.head(top_n).sort_values("valor_total", ascending=True)
        fig = px.bar(
            top_cut,
            x="valor_total",
            y="uf",
            orientation="h",
            title=f"Valor repassado por UF ({selected_year})",
            text="valor_total",
            color="valor_total",
            color_continuous_scale=["#d8f3dc", "#0f4c5c"],
        )
        fig.update_traces(
            texttemplate="%{text:,.2f}",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Valor total: %{x:,.2f}<extra></extra>",
            cliponaxis=False,
        )
        fig.update_layout(
            height=520,
            margin=dict(l=10, r=80, t=60, b=10),
            coloraxis_showscale=False,
            xaxis_title="Valor total",
            yaxis_title="UF",
        )
        st.plotly_chart(fig, width="stretch")
    with cut_right:
        annual_type_top = (
            annual_type_cut.groupby("uf", dropna=False)["valor_total"].sum().reset_index()
            .sort_values("valor_total", ascending=False)
            .head(top_n)["uf"]
            .tolist()
        )
        type_plot = annual_type_cut.loc[annual_type_cut["uf"].isin(annual_type_top)].copy()
        fig = px.bar(
            type_plot,
            x="uf",
            y="valor_total",
            color="tipo_instrumento",
            title=f"Composicao por tipo do instrumento ({selected_year})",
        )
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10), xaxis_title="UF", yaxis_title="Valor total")
        st.plotly_chart(fig, width="stretch")

    display = annual_cut.copy()
    display["valor_total"] = display["valor_total"].map(format_money)
    display["ticket_medio"] = display["ticket_medio"].map(format_money)
    st.dataframe(display, width="stretch", hide_index=True)


def render_territory(filtered: pd.DataFrame) -> None:
    st.subheader("Territorio")
    st.markdown("**Como ler esta secao**")
    st.markdown(
        """
        1. **Top municipios por valor**: mostra onde o recurso se concentra territorialmente.
        2. **Treemap territorial**: ajuda a perceber peso relativo entre UFs e municipios ao mesmo tempo.
        3. **Leitura correta**: primeiro identifique os municipios lideres; depois veja se a concentracao fica espalhada por varias cidades ou muito presa a poucos polos.
        """
    )
    geo = (
        filtered.groupby(["uf", "municipio_base"], dropna=False)
        .agg(registros=("municipio_base", "size"), valor_total=("valor_num", "sum"))
        .reset_index()
        .sort_values(["valor_total", "registros"], ascending=[False, False])
    )
    st.caption("A pergunta central aqui e territorial: em que lugares o recurso realmente esta pousando?")
    left, right = st.columns([1.1, 0.9])
    with left:
        fig = px.bar(geo.head(25).sort_values("valor_total"), x="valor_total", y="municipio_base", orientation="h", color="uf", title="Top municipios por valor")
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.treemap(geo.head(120), path=["uf", "municipio_base"], values="valor_total", color="registros", title="Treemap territorial")
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")


def render_entities(filtered: pd.DataFrame) -> None:
    st.subheader("Entidades")
    st.markdown("**Como ler esta secao**")
    st.markdown(
        """
        1. **Top entidades por valor**: mostra quem concentra mais recursos.
        2. **Top entidades por quantidade de registros**: mostra quem aparece mais vezes, mesmo sem liderar em valor.
        3. **Tabela detalhada**: serve para validar ticket medio, cobertura territorial e horizonte temporal de cada entidade.
        """
    )
    entities = build_entity_summary(filtered)
    if entities.empty:
        st.info("Sem entidades para o recorte.")
        return
    st.caption("A pergunta principal aqui e institucional: quem recebe mais e quem aparece com mais recorrencia?")
    left, right = st.columns(2)
    with left:
        fig = px.bar(entities.head(20).sort_values("valor_total"), x="valor_total", y="identificador", orientation="h", title="Top entidades por valor", color="valor_total", color_continuous_scale=["#ffd6a5", "#9a031e"])
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")
    with right:
        top_rows = entities.sort_values(["registros", "valor_total"], ascending=[False, False]).head(20).sort_values("registros")
        fig = px.bar(top_rows, x="registros", y="identificador", orientation="h", title="Top entidades por quantidade de registros", color="valor_total", color_continuous_scale=["#d8f3dc", "#0f4c5c"])
        fig.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    display = entities.head(200).copy()
    display["valor_total"] = display["valor_total"].map(format_money)
    display["ticket_medio"] = display["ticket_medio"].map(format_money)
    st.dataframe(display[["identificador", "nome_osc", "registros", "valor_total", "ticket_medio", "ufs", "municipios", "primeiro_ano", "ultimo_ano"]], width="stretch", hide_index=True)


def render_quality(filtered: pd.DataFrame) -> None:
    st.subheader("Qualidade")
    st.markdown("**Como ler esta secao**")
    st.markdown(
        """
        1. **Heatmap de vazio por campo e UF**: mostra onde faltam dados estruturais.
        2. **Alertas de qualidade**: resume problemas concretos como ano invalido, valor negativo, ausencia de municipio e duplicidade aparente.
        3. **Leitura correta**: primeiro veja quais campos faltam; depois olhe quais alertas podem afetar mais a confiabilidade da analise.
        """
    )
    st.caption("Aqui a pergunta nao e financeira, e sim de confiabilidade: o quanto da base esta bem preenchido e o que pode distorcer a leitura?")
    left, right = st.columns([1.05, 0.95])
    with left:
        missing = (
            filtered.groupby("uf")[QUALITY_COLUMNS]
            .apply(lambda frame: frame.isna().mean() * 100)
            .reset_index()
            .melt(id_vars="uf", var_name="campo", value_name="faltante_pct")
        )
        heat = missing.pivot(index="uf", columns="campo", values="faltante_pct")
        fig = px.imshow(heat, aspect="auto", color_continuous_scale=["#eff7f6", "#ffbf69", "#d90429"], title="% de vazio por campo e UF")
        fig.update_layout(height=460, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        alerts = pd.DataFrame(
            {
                "indicador": ["Valor zero", "Valor negativo", "Ano invalido", "Mes invalido", "Sem municipio", "Sem objeto", "Sem modalidade", "Duplicado aparente"],
                "quantidade": [
                    int(filtered["valor_zero"].sum()),
                    int(filtered["valor_negativo"].sum()),
                    int((~filtered["ano_valido"]).sum()),
                    int((filtered["mes"].notna() & ~filtered["mes_valido"]).sum()),
                    int((~filtered["tem_municipio"]).sum()),
                    int((~filtered["tem_objeto"]).sum()),
                    int((~filtered["tem_modalidade"]).sum()),
                    int(filtered["duplicado_aparente"].sum()),
                ],
            }
        )
        fig = px.bar(alerts.sort_values("quantidade"), x="quantidade", y="indicador", orientation="h", title="Alertas de qualidade", color="quantidade", color_continuous_scale=["#ffe5d9", "#9a031e"])
        fig.update_layout(height=460, margin=dict(l=10, r=10, t=60, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")


def render_audit(filtered: pd.DataFrame, full_data: pd.DataFrame, files_df: pd.DataFrame) -> None:
    st.subheader("Auditoria")
    st.markdown("**Como ler esta secao**")
    st.markdown(
        """
        1. **Painel**: prioriza UFs com maior risco operacional ou estrutural.
        2. **Qualidade**: aprofunda cobertura de campos e alertas de consistencia.
        3. **Benchmark UFs**: compara os estados para entender se o peso vem de volume, ticket medio ou concentracao.
        4. **Detalhe por UF**: aprofunda uma unidade especifica com sinais, anos suspeitos e trilha de origem.
        """
    )
    subsection = st.radio(
        "Subsecao de auditoria",
        ["Painel", "Qualidade", "Benchmark UFs"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if subsection == "Qualidade":
        st.caption("Cobertura dos campos e alertas de dados faltantes, anos invalidos, valores negativos e duplicidades aparentes.")
        render_quality(filtered)
        return

    if subsection == "Benchmark UFs":
        st.caption("Comparacao entre estados para identificar quem cresce por volume, ticket medio ou concentracao.")
        render_benchmark(filtered, full_data)
        return

    st.caption("A melhor estrategia e ler a auditoria em duas camadas: primeiro o painel nacional de riscos, depois o detalhe da UF com colunas vazias, anos suspeitos e trilha de origem.")

    scope = st.radio("Escopo da auditoria", ["Base completa", "Recorte atual"], horizontal=True)
    audit_data = full_data if scope == "Base completa" else filtered
    summary = build_runtime_audit_summary(audit_data)
    if summary.empty:
        st.info("Sem dados para auditoria.")
        return

    audit_available = AUDIT_REPORT_PATH.exists()
    audit_signature = build_file_signature(str(AUDIT_REPORT_PATH))
    audit_summary_sheet = load_audit_summary_sheet(str(AUDIT_REPORT_PATH), audit_signature) if audit_available else pd.DataFrame()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("UFs auditadas", format_int(summary["uf"].nunique()))
    col2.metric("Registros auditados", format_int(summary["registros"].sum()))
    col3.metric("UFs com anos suspeitos", format_int((summary["anos_invalidos"] > 0).sum()))
    col4.metric("UFs com colunas vazias", format_int((summary["colunas_sem_dados_qtd"] > 0).sum()))
    col5.metric("UFs com valor zero/negativo", format_int(((summary["valor_zero"] + summary["valor_negativo"]) > 0).sum()))

    left, right = st.columns([1.1, 0.9])
    with left:
        heat_source = summary[
            [
                "uf",
                "linhas_sem_ano",
                "anos_invalidos",
                "meses_invalidos",
                "cnpj_invalidos",
                "sem_municipio",
                "sem_objeto",
                "sem_modalidade",
                "valor_zero",
                "valor_negativo",
                "duplicados_aparentes",
                "colunas_sem_dados_qtd",
            ]
        ].copy()
        heat_source = heat_source.rename(
            columns={
                "linhas_sem_ano": "sem_ano",
                "anos_invalidos": "ano_invalido",
                "meses_invalidos": "mes_invalido",
                "cnpj_invalidos": "cnpj_invalido",
                "sem_municipio": "sem_municipio",
                "sem_objeto": "sem_objeto",
                "sem_modalidade": "sem_modalidade",
                "valor_zero": "valor_zero",
                "valor_negativo": "valor_negativo",
                "duplicados_aparentes": "duplicado",
                "colunas_sem_dados_qtd": "colunas_vazias",
            }
        )
        heat = heat_source.set_index("uf")
        fig = px.imshow(heat, aspect="auto", color_continuous_scale=["#eff7f6", "#ffbf69", "#9a031e"], title="Mapa de alertas por UF")
        fig.update_layout(height=470, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.scatter(
            summary,
            x="linhas_sem_ano",
            y="colunas_sem_dados_qtd",
            size="registros",
            color="indice_alerta",
            hover_name="uf",
            custom_data=["anos_invalidos", "valor_zero", "valor_negativo", "sem_objeto"],
            title="Prioridade de revisao por UF",
            color_continuous_scale=["#d8f3dc", "#e36414", "#9a031e"],
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                + "Linhas sem ano: %{x}<br>"
                + "Colunas vazias: %{y}<br>"
                + "Anos invalidos: %{customdata[0]}<br>"
                + "Valores zero: %{customdata[1]}<br>"
                + "Valores negativos: %{customdata[2]}<br>"
                + "Sem objeto: %{customdata[3]}<extra></extra>"
            )
        )
        fig.update_layout(height=470, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")

    display = summary.copy()
    display["valor_total"] = display["valor_total"].map(format_money)
    display["completude_pct"] = display["completude_pct"].map(format_pct)
    st.dataframe(
        display[
            [
                "uf",
                "indice_alerta",
                "registros",
                "valor_total",
                "completude_pct",
                "linhas_sem_ano",
                "anos_invalidos",
                "meses_invalidos",
                "cnpj_invalidos",
                "valor_zero",
                "valor_negativo",
                "sem_municipio",
                "sem_objeto",
                "sem_modalidade",
                "duplicados_aparentes",
                "colunas_sem_dados_qtd",
                "colunas_sem_dados_lista",
            ]
        ],
        width="stretch",
        hide_index=True,
    )

    st.markdown("**Detalhe por UF**")
    ordered_ufs = summary.sort_values(["indice_alerta", "registros"], ascending=[False, False])["uf"].tolist()
    selected_uf = st.selectbox("Escolha a UF para investigar", ordered_ufs, index=0)
    state_frame = audit_data.loc[audit_data["uf"] == selected_uf].copy()
    state_row = summary.loc[summary["uf"] == selected_uf].iloc[0]
    source_paths = files_df.loc[files_df["uf"] == selected_uf, "arquivo"].dropna().tolist()

    audit_detail: dict[str, pd.DataFrame] = {}
    sheet_name = resolve_audit_sheet_name(selected_uf, str(AUDIT_REPORT_PATH), audit_signature) if audit_available else None
    if sheet_name:
        audit_detail = load_audit_sheet_detail(str(AUDIT_REPORT_PATH), sheet_name, audit_signature)

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("Registros", format_int(state_row["registros"]))
    top2.metric("Completude", format_pct(state_row["completude_pct"]))
    top3.metric("Indice de alerta", format_int(state_row["indice_alerta"]))
    top4.metric("Valor zero/negativo", format_int(state_row["valor_zero"] + state_row["valor_negativo"]))

    source_description = ", ".join(f"`{path}`" for path in source_paths) if source_paths else "`(nao identificado)`"
    summary_text = [
        f"Parquet(s) carregado(s) para esta UF: {source_description}.",
        f"O estado tem {format_int(state_row['registros'])} registros, valor agregado de {format_money(state_row['valor_total'])} e completude media de {format_pct(state_row['completude_pct'])}.",
        f"Os principais alertas sao: {format_int(state_row['linhas_sem_ano'])} linhas sem ano, {format_int(state_row['anos_invalidos'])} anos invalidos, {format_int(state_row['cnpj_invalidos'])} CNPJs invalidos e {format_int(state_row['colunas_sem_dados_qtd'])} colunas totalmente vazias.",
        f"Exemplos de anos suspeitos: {build_invalid_year_examples(state_frame)}.",
    ]
    if audit_available and not audit_summary_sheet.empty:
        summary_text.append(f"Fonte complementar da auditoria: `{AUDIT_REPORT_PATH}`.")
    st.info("\n\n".join(summary_text))

    detail_tabs = st.tabs(["Alertas", "Anos", "Campos", "Origem"])
    with detail_tabs[0]:
        alert_table = pd.DataFrame(
            {
                "indicador": [
                    "linhas_sem_ano",
                    "anos_invalidos",
                    "meses_invalidos",
                    "cnpj_invalidos",
                    "valor_zero",
                    "valor_negativo",
                    "sem_municipio",
                    "sem_objeto",
                    "sem_modalidade",
                    "duplicados_aparentes",
                ],
                "quantidade": [
                    int(state_row["linhas_sem_ano"]),
                    int(state_row["anos_invalidos"]),
                    int(state_row["meses_invalidos"]),
                    int(state_row["cnpj_invalidos"]),
                    int(state_row["valor_zero"]),
                    int(state_row["valor_negativo"]),
                    int(state_row["sem_municipio"]),
                    int(state_row["sem_objeto"]),
                    int(state_row["sem_modalidade"]),
                    int(state_row["duplicados_aparentes"]),
                ],
            }
        )
        fig = px.bar(alert_table.sort_values("quantidade"), x="quantidade", y="indicador", orientation="h", title=f"Alertas da UF {selected_uf}", color="quantidade", color_continuous_scale=["#ffe5d9", "#9a031e"])
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")

        examples = audit_detail.get("missing_cnpj_examples", pd.DataFrame())
        if examples.empty:
            examples = build_missing_cnpj_examples_runtime(state_frame)
        st.dataframe(examples, width="stretch", hide_index=True)

    with detail_tabs[1]:
        years = audit_detail.get("years", pd.DataFrame())
        if years.empty:
            years = build_year_distribution(state_frame)
        st.dataframe(years, width="stretch", hide_index=True)

    with detail_tabs[2]:
        completeness = build_field_completeness(state_frame)
        completeness["cobertura_pct"] = completeness["cobertura_pct"].map(format_pct)
        st.dataframe(completeness, width="stretch", hide_index=True)

        empty_columns = audit_detail.get("empty_columns", pd.DataFrame())
        if empty_columns.empty:
            empty_columns = pd.DataFrame({"coluna_sem_dados": state_row["colunas_sem_dados_lista"].split(", ")})
        st.caption("Colunas totalmente vazias")
        st.dataframe(empty_columns, width="stretch", hide_index=True)

    with detail_tabs[3]:
        if audit_available:
            st.download_button(
                "Baixar auditoria_processada.xlsx",
                data=AUDIT_REPORT_PATH.read_bytes(),
                file_name="auditoria_processada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
            )
        else:
            st.caption("A planilha `auditoria_processada.xlsx` nao esta presente neste ambiente.")

        source_files = audit_detail.get("source_files", pd.DataFrame())
        mapping = audit_detail.get("mapping", pd.DataFrame())
        if not source_files.empty:
            st.markdown("**Arquivos brutos usados**")
            st.dataframe(source_files, width="stretch", hide_index=True)
        else:
            st.info("Os arquivos brutos usados nao estao disponiveis aqui. Se a planilha de auditoria estiver no deploy, esse bloco aparece automaticamente.")

        if not mapping.empty:
            st.markdown("**Mapeamento do schema**")
            st.dataframe(mapping, width="stretch", hide_index=True)
        else:
            st.info("O mapeamento campo a campo da origem bruta nao esta disponivel neste ambiente.")


def render_benchmark(filtered: pd.DataFrame, full_data: pd.DataFrame) -> None:
    st.subheader("Benchmark entre estados")
    st.markdown("**Como ler esta secao**")
    st.markdown(
        """
        1. **Leitura guiada**: resume rapidamente o que diferencia SP, AM e o padrao geral das UFs.
        2. **Dispersao volume x ticket x concentracao**: separa estados grandes por massa de registros daqueles grandes por contratos altos.
        3. **Peso relativo das UFs**: mostra quem ocupa mais espaco no conjunto nacional.
        4. **Tabela final**: consolida ranks e indicadores para conferencia.
        """
    )
    st.caption("A pergunta central aqui e comparativa: por que um estado aparece grande? Por volume, por ticket medio ou por concentracao?")
    benchmark = build_state_benchmark(full_data)
    current = build_state_benchmark(filtered)
    if benchmark.empty:
        st.info("Sem dados para benchmark.")
        return
    compare = current if len(filtered) != len(full_data) else benchmark
    render_benchmark_narratives(benchmark)

    export_frames = build_benchmark_export_frames(filtered, full_data)
    csv_bytes = export_frames["benchmark_atual"].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    excel_bytes = dataframe_to_excel_bytes(export_frames)

    download_col1, download_col2 = st.columns(2)
    with download_col1:
        st.download_button(
            "Baixar benchmark em CSV",
            data=csv_bytes,
            file_name="benchmark_ufs_recorte_atual.csv",
            mime="text/csv",
            width="stretch",
        )
    with download_col2:
        st.download_button(
            "Baixar Excel com resumo executivo",
            data=excel_bytes,
            file_name="relatorio_comparativo_ufs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    left, right = st.columns([1.1, 0.9])
    with left:
        fig = px.scatter(
            compare,
            x="registros",
            y="ticket_medio",
            size="valor_total",
            color="top5_share_pct",
            hover_name="uf",
            title="Volume x ticket medio x concentracao",
            color_continuous_scale=["#d8f3dc", "#e36414", "#9a031e"],
            log_x=True,
        )
        fig.update_layout(height=430, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.bar(
            compare.sort_values("valor_total", ascending=False).head(15),
            x="uf",
            y="share_nacional_pct" if "share_nacional_pct" in compare.columns else "valor_total",
            color="rank_ticket_medio",
            title="Peso relativo das UFs",
            color_continuous_scale=["#eff7f6", "#0f4c5c"],
        )
        fig.update_layout(height=430, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, width="stretch")

    display = benchmark.copy()
    for column in ["valor_total", "ticket_medio", "ticket_mediano"]:
        display[column] = display[column].map(format_money)
    for column in ["share_nacional_pct", "top1_share_pct", "top5_share_pct", "top10_share_pct", "cob_municipio", "cob_objeto", "cob_modalidade"]:
        display[column] = display[column].map(format_pct)
    st.dataframe(
        display[["uf", "rank_valor_total", "rank_registros", "rank_ticket_medio", "rank_concentracao", "valor_total", "registros", "ticket_medio", "ticket_mediano", "share_nacional_pct", "top1_share_pct", "top5_share_pct", "top10_share_pct", "entidades", "cob_municipio", "cob_objeto", "cob_modalidade"]],
        width="stretch",
        hide_index=True,
    )


def render_histories() -> None:
    st.subheader("Historias")
    st.markdown("**Como ler esta secao**")
    st.markdown(
        """
        1. **Modo corrido**: funciona como uma wiki sequencial para ler varias UFs em ordem.
        2. **Selecionar UF**: serve para mergulhar em um estado especifico.
        3. **Leitura correta**: use esta aba depois da analise quantitativa, para transformar numeros em interpretacao narrativa com contexto e fontes.
        """
    )
    history_signature = build_directory_signature(str(HISTORY_DIR), "*.md")
    docs = load_history_documents(str(HISTORY_DIR), history_signature)
    if not docs:
        st.warning("Nenhum markdown foi encontrado em `historia/`. Rode `python gerar_historias.py` para gerar as narrativas.")
        return

    ordered_keys = [key for key in sorted(docs.keys()) if key != "INDEX"]
    anchors = {key: history_anchor_id(docs[key], key) for key in ordered_keys}
    labels = {key: history_display_label(docs[key], key) for key in ordered_keys}
    st.markdown(
        """
        <style>
        .history-nav {
            position: sticky;
            top: 1rem;
            max-height: calc(100vh - 3rem);
            overflow-y: auto;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(15,76,92,0.10);
            border-radius: 16px;
            background: rgba(255,255,255,0.92);
        }
        .history-nav h4 {
            margin: 0 0 0.75rem 0;
            font-size: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    nav_col, content_col = st.columns([0.28, 0.72], gap="large")

    with nav_col:
        st.markdown('<div class="history-nav">', unsafe_allow_html=True)
        st.markdown("#### Navegacao")
        mode = st.radio("Visao", ["Corrido", "Selecionar UF"], label_visibility="collapsed")
        if mode == "Selecionar UF":
            label_options = [labels[key] for key in ordered_keys]
            selected_label = st.selectbox("Escolha a UF", label_options, index=0, label_visibility="collapsed")
            selected = next(key for key in ordered_keys if labels[key] == selected_label)
            markdown = docs.get(selected, "")
            st.download_button(
                "Baixar markdown",
                data=markdown.encode("utf-8"),
                file_name=f"{selected}.md",
                mime="text/markdown",
                width="stretch",
            )
        else:
            st.caption("Clique para navegar na mesma pagina.")
            summary_links = "\n".join(f"- [{labels[key]}](#{anchors[key]})" for key in ordered_keys)
            st.markdown(summary_links)
        st.markdown('</div>', unsafe_allow_html=True)

    with content_col:
        if mode == "Selecionar UF":
            markdown = docs.get(selected, "")
            title, body = split_history_markdown(markdown, selected)
            st.caption(f"Lendo `{selected}.md` da pasta `historia/`.")
            st.header(title, anchor=anchors[selected])
            if body:
                render_history_body(body)
        else:
            st.caption("Leitura encadeada em formato corrido, como uma wiki sequencial por UF.")
            st.header("Sumario", anchor="sumario")
            for key in ordered_keys:
                title, body = split_history_markdown(docs[key], key)
                st.header(title, anchor=anchors[key])
                if body:
                    render_history_body(body)
                st.markdown("[Voltar ao sumario](#sumario)")


def configure_page(page_title: str) -> None:
    st.set_page_config(page_title=page_title, page_icon=":bar_chart:", layout="wide")


def get_dashboard_context() -> DashboardContext | None:
    st.sidebar.header("Fonte de dados")
    source_mode = st.sidebar.radio(
        "Conjunto carregado",
        ["Estadual", "Governo federal", "Ambos"],
        key="source_mode",
    )
    state_dir = st.sidebar.text_input("Pasta estadual", value=str(DEFAULT_STATE_DATA_DIR), key="state_data_dir")
    federal_dir = st.sidebar.text_input("Pasta federal", value=str(DEFAULT_FEDERAL_DATA_DIR), key="federal_data_dir")
    data_label, data_dirs = resolve_selected_data_sources(source_mode, state_dir, federal_dir)
    parquet_signatures = build_sources_signature(data_dirs)
    data, files_df = load_data(data_dirs, parquet_signatures)
    if data.empty:
        st.error(f"Nenhum arquivo .parquet foi encontrado em {', '.join(data_dirs)}.")
        return None

    selected_ufs, year_range, selected_modalities, selected_instrument_types, minimum_value, only_valid_cnpj, exclude_zero_negative, search_text = render_sidebar(data, files_df)
    filtered = apply_filters(
        data,
        selected_ufs,
        year_range,
        selected_modalities,
        selected_instrument_types,
        minimum_value,
        only_valid_cnpj,
        exclude_zero_negative,
        search_text,
    )
    filtered_without_year = apply_filters(
        data,
        selected_ufs,
        None,
        selected_modalities,
        selected_instrument_types,
        minimum_value,
        only_valid_cnpj,
        exclude_zero_negative,
        search_text,
    )
    return DashboardContext(
        data_label=data_label,
        data_dirs=data_dirs,
        data=data,
        files_df=files_df,
        filtered=filtered,
        filtered_without_year=filtered_without_year,
    )


def render_page_navigation(current_page: str) -> None:
    st.markdown("**Paginas**")
    columns = st.columns(len(PAGE_LINKS))
    for column, (target, label, slug) in zip(columns, PAGE_LINKS):
        with column:
            label_text = f"{label} *" if slug == current_page else label
            st.page_link(target, label=label_text, use_container_width=True)


def render_shared_frame(context: DashboardContext, current_page: str, show_tab_guide: bool = False, show_summary: bool = False, show_glossary_block: bool = False) -> bool:
    render_header(context.data, context.files_df, context.data_label)
    st.caption("O dashboard cruza volume, temporalidade, concentracao, cobertura e benchmarking entre UFs a partir dos parquets consolidados.")
    render_page_navigation(current_page)
    with st.expander("Premissas de leitura"):
        st.markdown(
            """
            - `valor_num` e derivado do `valor_total` decimal preservado no parquet.
            - `ano_num` e `mes_num` sao lidos como inteiros quando possivel.
            - `tem_cnpj_valido` usa 14 digitos apos limpeza.
            - `duplicado_aparente` considera igualdade nos campos centrais do schema.
            - O benchmark entre UFs ajuda a distinguir estados puxados por volume, ticket medio ou concentracao.
            - A aba de auditoria combina sinais calculados direto dos parquets com a planilha `auditoria_processada.xlsx` quando ela estiver presente.
            """
        )
    if context.filtered.empty:
        st.warning("Os filtros atuais nao retornaram registros.")
        return False
    if show_tab_guide:
        render_tab_guide()
    if show_summary:
        render_dynamic_executive_summary(context.filtered, context.data)
    if show_glossary_block:
        render_glossary()
    return True


def main() -> None:
    configure_page("Dashboard Parquets OSC")
    context = get_dashboard_context()
    if context is None:
        return
    if not render_shared_frame(context, current_page="inicio", show_tab_guide=True, show_summary=True, show_glossary_block=True):
        return
    st.info("Use o menu lateral do Streamlit ou os atalhos acima para navegar entre as paginas do dashboard.")


if __name__ == "__main__":
    main()
