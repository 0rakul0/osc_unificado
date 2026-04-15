from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import AUDITORIA_XLSX_PATH, BASES_CONVENIOS_DIR, PROCESSADA_DIR, cli_default, ensure_parent_dir
from utils.convenios.unificador import list_workbooks
from utils.common import STANDARD_COLUMNS
from utils.config import get_uf_mapping


STATE_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AM": "Amazonas",
    "AP": "Amapa",
    "BA": "Bahia",
    "CE": "Ceara",
    "DF": "Distrito Federal",
    "ES": "Espirito Santo",
    "GO": "Goias",
    "MA": "Maranhao",
    "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso",
    "PA": "Para",
    "PB": "Paraiba",
    "PE": "Pernambuco",
    "PI": "Piaui",
    "PR": "Parana",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RO": "Rondonia",
    "RR": "Roraima",
    "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina",
    "SE": "Sergipe",
    "SP": "Sao Paulo",
    "TO": "Tocantins",
}

SPECIAL_NOTES = {
    "AP": {
        "nome_osc": "Remove CNPJ colado no final do nome quando ele vier concatenado.",
    },
    "BA": {
        "data_inicio": "Forcado para vazio no parser da UF.",
        "data_fim": "Forcado para vazio no parser da UF.",
    },
    "DF": {
        "cnpj": "codigoCredor e preenchido com zeros a esquerda ate 14 digitos.",
        "objeto": "Usa nomeSubtitulo; se vier vazio, cai para nomeProgramaTrabalho.",
    },
    "PA": {
        "ano": "Derivado de dt_despesa.",
        "nome_osc": "Vem de ds_sigla_orgao, que no arquivo funciona como nome do favorecido.",
    },
    "PI": {
        "cnpj": "Mantem credor_codigo mesmo quando vier mascarado.",
    },
    "RJ": {
        "ano": "No XLSX, extrai de NÚMERO quando presente; nos CSVs de transferencias usa ANO ou o ano inferido do arquivo 2024.",
        "data_inicio": "Extrai data valida de Vigencia Inicial; textos como 'Ate ...' ficam vazios.",
        "data_fim": "Extrai data de Termino.",
        "cnpj": "No CSV 2015-2023 converte notacao cientifica antes da limpeza; no 2024 usa CNPJ/CPF bruto.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera uma auditoria dos arquivos parquet da pasta processada."
    )
    parser.add_argument(
        "--processed-dir",
        default=cli_default(PROCESSADA_DIR),
        help="Pasta com os arquivos parquet por UF.",
    )
    parser.add_argument(
        "--output",
        default=cli_default(AUDITORIA_XLSX_PATH),
        help="Arquivo XLSX de saida.",
    )
    parser.add_argument(
        "--base-dir",
        default=cli_default(BASES_CONVENIOS_DIR),
        help="Pasta raiz com os arquivos brutos por UF.",
    )
    return parser.parse_args()


def is_non_empty(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def to_numeric_value(value: object) -> float | None:
    if not is_non_empty(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace(" ", "")
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")

    try:
        return float(normalized)
    except ValueError:
        return None


def build_year_counts(df: pd.DataFrame) -> pd.DataFrame:
    if "ano" not in df.columns:
        return pd.DataFrame({"ano": ["(coluna ausente)"], "quantidade": [0]})

    def normalize_year(value: object) -> str:
        if not is_non_empty(value):
            return "(sem ano)"

        text = str(value).strip()
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

    ano_series = df["ano"].map(normalize_year)
    counts = ano_series.value_counts(dropna=False).sort_index()
    return counts.rename_axis("ano").reset_index(name="quantidade")


def build_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    empty_columns = [
        column
        for column in df.columns
        if not df[column].map(is_non_empty).fillna(False).astype(bool).any()
    ]
    if not empty_columns:
        empty_columns = ["(nenhuma)"]
    return pd.DataFrame({"coluna_sem_dados": empty_columns})


def build_missing_cnpj_examples(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    if "nome_osc" not in df.columns:
        return pd.DataFrame({"exemplos_nome_osc_sem_cnpj": ["(coluna ausente)"]})

    cnpj_series = df["cnpj"] if "cnpj" in df.columns else pd.Series(pd.NA, index=df.index)
    missing_cnpj_mask = ~cnpj_series.map(is_non_empty).fillna(False).astype(bool)
    names = (
        df.loc[missing_cnpj_mask, "nome_osc"]
        .map(lambda value: str(value).strip() if is_non_empty(value) else None)
        .dropna()
    )
    examples = names.drop_duplicates().head(limit).tolist()
    if not examples:
        examples = ["(nenhum)"]
    return pd.DataFrame({"exemplos_nome_osc_sem_cnpj": examples})


def build_source_files_df(base_dir: Path, uf: str) -> pd.DataFrame:
    paths = list_workbooks(base_dir, uf)
    values = [path.name for path in paths] or ["(nenhum encontrado)"]
    return pd.DataFrame({"arquivos_brutos_usados": values})


def build_mapping_df(uf: str) -> pd.DataFrame:
    uf_mapping = get_uf_mapping(uf)
    target_to_sources: dict[str, list[str]] = {}
    for source, target in uf_mapping.items():
        target_to_sources.setdefault(target, []).append(str(source))

    rows: list[dict[str, str]] = []
    for field in STANDARD_COLUMNS:
        sources = target_to_sources.get(field, [])
        note = SPECIAL_NOTES.get(uf, {}).get(field, "")

        if not sources and field == "mes":
            note = note or "Derivado de data, data_inicio ou data_fim quando disponivel."
        if not sources and field == "ano":
            note = note or "Pode ser derivado de coluna de data ou do nome do arquivo/aba quando o parser nao recebe ano explicito."

        rows.append(
            {
                "campo_schema": field,
                "origem_bruta": ", ".join(sources) if sources else "(nao mapeado diretamente)",
                "regra": note or "(sem regra especial registrada)",
            }
        )

    return pd.DataFrame(rows)


def build_metrics(df: pd.DataFrame, uf: str) -> pd.DataFrame:
    cnpj_series = df["cnpj"] if "cnpj" in df.columns else pd.Series(dtype="object")
    cnpj_non_empty = (
        cnpj_series.map(is_non_empty).fillna(False).astype(bool)
        if not cnpj_series.empty
        else pd.Series(dtype="bool")
    )
    cnpj_values = (
        cnpj_series[cnpj_non_empty].astype(str).str.strip()
        if not cnpj_series.empty
        else pd.Series(dtype="object")
    )
    ano_series = df["ano"] if "ano" in df.columns else pd.Series(dtype="object")
    linhas_sem_ano = (
        int((~ano_series.map(is_non_empty).fillna(False).astype(bool)).sum())
        if not ano_series.empty
        else len(df)
    )
    valor_series = df["valor_total"] if "valor_total" in df.columns else pd.Series(dtype="object")
    valor_numerico = valor_series.map(to_numeric_value) if not valor_series.empty else pd.Series(dtype="float")
    valor_total_zerado = (
        int(sum(value == 0 for value in valor_numerico if value is not None))
        if not valor_series.empty
        else 0
    )
    exemplos_sem_cnpj = build_missing_cnpj_examples(df)

    metrics = [
        ("uf", uf),
        ("estado", STATE_NAMES.get(uf, uf)),
        ("total_linhas", len(df)),
        ("linhas_com_cnpj", int(cnpj_non_empty.sum()) if not cnpj_series.empty else 0),
        ("cnpj_unicos", int(cnpj_values.nunique()) if not cnpj_values.empty else 0),
        ("linhas_sem_ano", linhas_sem_ano),
        ("valor_total_zerado", valor_total_zerado),
        ("nomes_sem_cnpj_exibidos", 0 if exemplos_sem_cnpj.iloc[0, 0] == "(nenhum)" else len(exemplos_sem_cnpj)),
        ("colunas_sem_dados", len(build_empty_columns(df).query("coluna_sem_dados != '(nenhuma)'"))),
    ]
    return pd.DataFrame(metrics, columns=["metrica", "valor"])


def sheet_name_for_uf(uf: str) -> str:
    return f"{STATE_NAMES.get(uf, uf)} - {uf}"[:31]


def write_state_sheet(writer: pd.ExcelWriter, parquet_path: Path, base_dir: Path) -> dict[str, object]:
    uf = parquet_path.stem.upper()
    df = pd.read_parquet(parquet_path)

    metrics_df = build_metrics(df, uf)
    years_df = build_year_counts(df)
    empty_columns_df = build_empty_columns(df)
    missing_cnpj_examples_df = build_missing_cnpj_examples(df)
    source_files_df = build_source_files_df(base_dir, uf)
    mapping_df = build_mapping_df(uf)

    sheet_name = sheet_name_for_uf(uf)
    metrics_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0, index=False)
    years_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=4, index=False)
    empty_columns_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=8, index=False)
    missing_cnpj_examples_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=11, index=False)
    source_files_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=14, index=False)
    mapping_df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=16, index=False)

    return {
        "uf": uf,
        "estado": STATE_NAMES.get(uf, uf),
        "arquivo": parquet_path.name,
        "total_linhas": len(df),
        "linhas_com_cnpj": int(metrics_df.loc[metrics_df["metrica"] == "linhas_com_cnpj", "valor"].iloc[0]),
        "cnpj_unicos": int(metrics_df.loc[metrics_df["metrica"] == "cnpj_unicos", "valor"].iloc[0]),
        "linhas_sem_ano": int(metrics_df.loc[metrics_df["metrica"] == "linhas_sem_ano", "valor"].iloc[0]),
        "valor_total_zerado": int(metrics_df.loc[metrics_df["metrica"] == "valor_total_zerado", "valor"].iloc[0]),
        "exemplos_nome_osc_sem_cnpj": ", ".join(missing_cnpj_examples_df.iloc[:, 0].tolist()),
        "colunas_sem_dados": ", ".join(empty_columns_df["coluna_sem_dados"].tolist()),
    }


def main() -> None:
    args = parse_args()
    processed_dir = Path(args.processed_dir)
    output_path = Path(args.output)
    base_dir = Path(args.base_dir)
    ensure_parent_dir(output_path)

    parquet_files = sorted(processed_dir.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"Nenhum arquivo parquet encontrado em {processed_dir}")

    summary_rows: list[dict[str, object]] = []
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for parquet_path in parquet_files:
            if parquet_path.name.endswith(".partial.parquet"):
                continue
            summary_rows.append(write_state_sheet(writer, parquet_path, base_dir))

        summary_df = pd.DataFrame(summary_rows).sort_values("uf")
        summary_df.to_excel(writer, sheet_name="Resumo", index=False)

    print(f"Relatorio salvo em: {output_path.resolve()}")
    print(f"Estados analisados: {len(summary_rows)}")


if __name__ == "__main__":
    main()
