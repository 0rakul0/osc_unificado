from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_DIR, ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
TARGET_SHEETS = ("CONVÊNIOS ", "TERMO DE FOMENTO", "DIÁRIO 2024-2025")
OSC_NAME_PATTERN = re.compile(
    r"associ|instit|fundac|casa |lar |federa|obra social|museu|pestalozzi|hospital de amor|ministerio betel|amazonia",
    re.IGNORECASE,
)
PUBLIC_NAME_PATTERN = re.compile(
    r"prefeitura|municipio|estado do amapa|secretaria|tribunal|camara|universidade|fundo estadual|procuradoria",
    re.IGNORECASE,
)
PRIVATE_COMPANY_PATTERN = re.compile(r"\bltda\b|\bme\b|\bepp\b|comerc|construt|engenharia|servicos", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a base legada de convenios e termos de fomento do Amapa com foco em OSC."
    )
    parser.add_argument(
        "--input",
        default=str(BASES_CONVENIOS_DIR / "AP" / "TERMO DE FOMENTO.xlsx"),
        help="Arquivo xlsx bruto do Amapa.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para o parquet final.",
    )
    return parser.parse_args()


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA, "0": pd.NA, "0.0": pd.NA})
    )


def clean_document(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    digits = cleaned.str.replace(r"\D", "", regex=True)
    return digits.mask(digits.eq(""))


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = clean_text(current)
        result = cleaned if result is None else result.combine_first(cleaned)
    if result is None:
        return pd.Series(dtype="string")
    return result


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def extract_year_from_number(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    return cleaned.str.extract(r"/((?:19|20)\d{2})", expand=False).astype("string")


def read_source(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []
    for sheet_name in TARGET_SHEETS:
        if sheet_name not in xl.sheet_names:
            continue
        frame = pd.read_excel(path, sheet_name=sheet_name)
        frame["__sheet__"] = sheet_name
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def infer_modalidade(frame: pd.DataFrame) -> pd.Series:
    sheet = clean_text(frame.get("__sheet__")).fillna("")
    numero = clean_text(frame.get("Convenio/")).combine_first(clean_text(frame.get("Termo de Fomento"))).fillna("")
    modalidade = pd.Series(pd.NA, index=frame.index, dtype="string")
    modalidade = modalidade.mask(sheet.str.contains("FOMENTO", case=False, na=False), "TERMO DE FOMENTO")
    modalidade = modalidade.mask(sheet.str.contains("CONV", case=False, na=False), "CONVENIO")
    modalidade = modalidade.mask(numero.str.contains("FOMENTO", case=False, na=False), "TERMO DE FOMENTO")
    return modalidade


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("Nome do Credor")).fillna("")
    cnpj = clean_document(source_df.get("Credor")).fillna("")
    osc_name = nome.str.contains(OSC_NAME_PATTERN, na=False)
    public_name = nome.str.contains(PUBLIC_NAME_PATTERN, na=False)
    private_company = nome.str.contains(PRIVATE_COMPANY_PATTERN, na=False)
    has_valid_doc = cnpj.str.len().isin([11, 14]) | nome.str.contains(OSC_NAME_PATTERN, na=False)
    return osc_name & ~public_name & ~private_company & has_valid_doc


def build_ap_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    data_inicio = clean_text(filtered.get("Data Início"))
    data_fim = clean_text(filtered.get("Data Termino"))
    ano_data, mes = extract_year_month(data_inicio)
    ano_numero = extract_year_from_number(filtered.get("Número Original"))

    mapped = pd.DataFrame(
        {
            "uf": "AP",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano_data.combine_first(ano_numero),
            "valor_total": first_non_empty(filtered.get("Valor Total"), filtered.get("Valor do Fomento"), filtered.get("Valor do Convênio")),
            "cnpj": clean_document(filtered.get("Credor")),
            "nome_osc": filtered.get("Nome do Credor"),
            "mes": mes,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("Objeto"),
            "modalidade": infer_modalidade(filtered),
            "data_inicio": data_inicio,
            "data_fim": data_fim,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df = read_source(input_path)
    mapped = build_ap_budget_frame(source_df)
    normalized = normalize_preview(mapped, "AP", require_cnpj=False)

    output_path = output_dir / "AP.parquet"
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
