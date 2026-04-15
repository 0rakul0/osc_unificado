from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from .common import ParserConfig, STANDARD_COLUMNS, WorkbookParser, normalize_name


PRIMARY_SHEET = "TransfVolRealizadas_Atualização"
SECONDARY_SHEET = "Página2"

PRIMARY_MAPPINGS = {
    "Tipo de Instrumento (Convênio, acordo, ajuste, outros)": "modalidade",
    "Nr Instrumento (convênio, acordo, ajuste)": "id_unico",
    "Ano Instrumento (convênio, acordo, ajuste)": "ano",
    "Beneficiário": "nome_osc",
    "Objeto do Convênio/Repasse": "objeto",
    "Valor Total Previsto": "valor_total",
    "Valores Repassados/Concedido": "valor_repassado",
    "Observações (se necessário algum esclarecimento adicional)": "observacoes",
}

SECONDARY_MAPPINGS = {
    "Unidade Responsável pela informação": "observacoes",
    "Beneficiário": "nome_osc",
    "Ano do Convênio, Termo, Ajuste (ou instrumento equivalente)": "ano",
    "Número do Instrumento": "id_unico",
    "Objeto do Instrumento": "objeto",
    "Valor Total do Instrumento": "valor_total",
    "Valores repassados": "valor_repassado",
    "Datas dos repasses": "observacoes_datas",
    "Vigência do Instrumento": "vigencia",
}

TEXT_PLACEHOLDERS = {
    "",
    "-",
    "--",
    "?",
    "??",
    "nan",
    "n/a",
    "na",
    "naopossui",
    "adefinir",
    "adefinirdetalhes",
}

VALUE_PLACEHOLDERS = TEXT_PLACEHOLDERS | {"pordemanda"}

MODALIDADE_PATTERNS = (
    ("TERMO DE FOMENTO", "Termo de Fomento"),
    ("TERMO DE COLABORACAO", "Termo de Colaboração"),
    ("ACORDO DE COOPERACAO", "Acordo de Cooperação"),
    ("CONTRATO DE REPASSE", "Contrato de Repasse"),
    ("CONTRATO", "Contrato"),
    ("CONVENIO", "Convênio"),
)


def is_non_empty(value: object) -> bool:
    return pd.notna(value) and bool(str(value).strip())


def clean_text_cell(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).replace("\r", "\n").strip()
    if not text:
        return pd.NA

    normalized = normalize_name(text)
    if normalized in TEXT_PLACEHOLDERS:
        return pd.NA

    compact = re.sub(r"[ \t]+", " ", text)
    compact = re.sub(r"\n+", " ", compact)
    compact = re.sub(r"\s+", " ", compact).strip()
    return compact or pd.NA


def clean_value_cell(value: object) -> object:
    text = clean_text_cell(value)
    if pd.isna(text):
        return pd.NA

    normalized = normalize_name(text)
    if normalized in VALUE_PLACEHOLDERS:
        return pd.NA
    return text


def append_text(base_value: object, extra_value: object) -> object:
    if pd.isna(extra_value):
        return base_value
    if pd.isna(base_value):
        return extra_value

    base_text = str(base_value).strip()
    extra_text = str(extra_value).strip()
    if not extra_text or extra_text in base_text:
        return base_value
    if base_text in extra_text:
        return extra_value
    return f"{base_text} {extra_text}".strip()


def normalize_instrument_number(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    if "00:00:00" in text or re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        parsed = pd.to_datetime(text, errors="coerce")
        if pd.notna(parsed) and int(parsed.day) == 1:
            return f"{int(parsed.month):02d}/{int(parsed.year)}"

    return text


def normalize_modalidade_text(value: object, objeto: object = pd.NA) -> object:
    if is_non_empty(value):
        raw_text = str(value).strip()
        text = unicodedata.normalize("NFKD", raw_text.upper())
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"\s+", " ", text)
        for needle, canonical in MODALIDADE_PATTERNS:
            if needle in text:
                return canonical
        return raw_text

    if is_non_empty(objeto):
        text = unicodedata.normalize("NFKD", str(objeto).strip().upper())
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"\s+", " ", text)
        for needle, canonical in MODALIDADE_PATTERNS:
            if needle in text:
                return canonical

    return pd.NA


def extract_currency_from_text(text: object) -> Decimal | None:
    if not is_non_empty(text):
        return None

    candidates = re.findall(r"R\$\s*([0-9.\-,]+)", str(text), flags=re.IGNORECASE)
    for candidate in candidates:
        decimal_value = parse_brazilian_decimal(candidate)
        if decimal_value is not None:
            return decimal_value
    return None


def parse_brazilian_decimal(value: object) -> Decimal | None:
    if not is_non_empty(value):
        return None

    text = str(value).strip()
    normalized = normalize_name(text)
    if normalized in VALUE_PLACEHOLDERS:
        return None

    text = text.replace("R$", "").replace("r$", "").strip()
    text = re.sub(r"^[lIi](?=[.,\d])", "1", text)
    if re.fullmatch(r"\d,\d{3}\.\d{3},\d{2}", text):
        head, tail = text.split(",", 1)
        text = f"{head}.{tail}"
    text = re.sub(r"[^0-9,.\-]+", "", text)
    if not text:
        return None

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")

    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def normalize_amount(value: object, repasse_hint: object = pd.NA) -> object:
    decimal_value = parse_brazilian_decimal(value)
    if decimal_value is None and is_non_empty(repasse_hint):
        hint_amount = extract_currency_from_text(repasse_hint)
        if hint_amount is not None and re.search(r"\d{4}\s*/\s*\d{4}", str(repasse_hint)):
            decimal_value = hint_amount * Decimal("2")

    if decimal_value is None:
        return pd.NA

    normalized = format(decimal_value, "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or pd.NA


class MAWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="MA",
                header_row=1,
                extra_mappings={**PRIMARY_MAPPINGS, **SECONDARY_MAPPINGS},
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        excel_file = pd.ExcelFile(workbook_path)
        frames: list[pd.DataFrame] = []

        for sheet_name in excel_file.sheet_names:
            raw = self.read_sheet(workbook_path, sheet_name, nrows=preview_rows)
            if sheet_name == PRIMARY_SHEET:
                frames.append(self.parse_primary_sheet(raw, workbook_path, sheet_name))
            elif sheet_name == SECONDARY_SHEET:
                frames.append(self.parse_secondary_sheet(raw, workbook_path, sheet_name))

        combined = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True) if frames else pd.DataFrame(columns=STANDARD_COLUMNS)
        if combined.empty:
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

        combined = combined.copy()
        combined = combined[
            combined["nome_osc"].notna()
            | combined["valor_total"].notna()
            | combined["data_inicio"].notna()
            | combined["data_fim"].notna()
            | combined["ano"].notna()
        ].copy()
        quality_columns = ["nome_osc", "objeto", "modalidade", "valor_total", "data_inicio", "data_fim", "mes"]
        combined["_quality"] = combined[quality_columns].notna().sum(axis=1)
        combined["_dedup_key"] = combined.apply(self.build_dedup_key, axis=1)
        combined = (
            combined.sort_values(by=["_dedup_key", "_quality"], ascending=[True, False], kind="stable")
            .drop_duplicates(subset=["_dedup_key"], keep="first")
            .drop(columns=["_quality", "_dedup_key"])
            .reset_index(drop=True)
        )
        return combined[STANDARD_COLUMNS]

    def parse_primary_sheet(self, raw: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        cleaned = raw.copy()
        for column in cleaned.columns:
            if column == "Valor Total Previsto":
                cleaned[column] = cleaned[column].map(normalize_amount)
            elif column == "Valores Repassados/Concedido":
                cleaned[column] = cleaned[column].map(normalize_amount)
            else:
                cleaned[column] = cleaned[column].map(clean_text_cell)

        total_col = "Valor Total Previsto"
        repasse_col = "Valores Repassados/Concedido"
        ano_col = "Ano Instrumento (convênio, acordo, ajuste)"
        cleaned[total_col] = cleaned[total_col].combine_first(cleaned[repasse_col])

        missing_year_mask = cleaned[ano_col].isna()
        standardized = self.standardize(cleaned, workbook_path, sheet_name)
        standardized.loc[missing_year_mask, "ano"] = pd.NA
        standardized["modalidade"] = standardized.apply(
            lambda row: normalize_modalidade_text(row["modalidade"], row["objeto"]), axis=1
        )
        standardized = standardized[
            standardized[["nome_osc", "objeto", "valor_total", "modalidade"]].notna().any(axis=1)
        ].copy()
        standardized["_id_key"] = cleaned["Nr Instrumento (convênio, acordo, ajuste)"].reset_index(drop=True)
        return standardized

    def parse_secondary_sheet(self, raw: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        if raw.empty:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        collapsed = self.collapse_secondary_rows(raw)
        if collapsed.empty:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        total_col = "Valor Total do Instrumento"
        repasse_col = "Valores repassados"
        ano_col = "Ano do Convênio, Termo, Ajuste (ou instrumento equivalente)"
        numero_col = "Número do Instrumento"
        objeto_col = "Objeto do Instrumento"
        modalidade_col = "Modalidade Inferida"

        collapsed[total_col] = collapsed.apply(
            lambda row: normalize_amount(row.get(total_col), row.get(repasse_col)),
            axis=1,
        )
        collapsed[repasse_col] = collapsed[repasse_col].map(normalize_amount)
        collapsed[numero_col] = collapsed[numero_col].map(normalize_instrument_number)
        collapsed[modalidade_col] = collapsed.apply(
            lambda row: normalize_modalidade_text(pd.NA, row.get(objeto_col)),
            axis=1,
        )

        missing_year_mask = collapsed[ano_col].isna()
        standardized = self.standardize(collapsed, workbook_path, sheet_name)
        standardized.loc[missing_year_mask, "ano"] = pd.NA
        standardized["modalidade"] = standardized["modalidade"].combine_first(
            collapsed[modalidade_col].reset_index(drop=True)
        )
        standardized["modalidade"] = standardized.apply(
            lambda row: normalize_modalidade_text(row["modalidade"], row["objeto"]), axis=1
        )
        standardized = standardized[
            standardized[["nome_osc", "objeto", "valor_total", "modalidade", "data_inicio", "data_fim"]]
            .notna()
            .any(axis=1)
        ].copy()
        standardized["_id_key"] = collapsed[numero_col].reset_index(drop=True)
        return standardized

    def collapse_secondary_rows(self, raw: pd.DataFrame) -> pd.DataFrame:
        cleaned = raw.copy()
        for column in cleaned.columns:
            if column in {"Valor Total do Instrumento", "Valores repassados"}:
                cleaned[column] = cleaned[column].map(clean_value_cell)
            else:
                cleaned[column] = cleaned[column].map(clean_text_cell)

        columns = list(cleaned.columns)
        unit_col = "Unidade Responsável pela informação"
        text_append_columns = {
            unit_col,
            "Beneficiário",
            "Objeto do Instrumento",
            "Datas dos repasses",
            "Link para o inteiro teor do Instrumento",
        }
        fill_only_columns = set(columns) - text_append_columns

        records: list[dict[str, object]] = []
        current: dict[str, object] | None = None

        for _, row in cleaned.iterrows():
            row_dict = {column: row[column] for column in columns}
            if not any(is_non_empty(value) for value in row_dict.values()):
                continue

            if is_non_empty(row_dict.get(unit_col)):
                if current and self.is_secondary_record_useful(current):
                    records.append(current)
                current = row_dict
                continue

            if current is None:
                current = row_dict
                continue

            for column in columns:
                value = row_dict.get(column)
                if pd.isna(value):
                    continue
                if column in text_append_columns:
                    current[column] = append_text(current.get(column, pd.NA), value)
                elif column in fill_only_columns and pd.isna(current.get(column, pd.NA)):
                    current[column] = value

        if current and self.is_secondary_record_useful(current):
            records.append(current)

        return pd.DataFrame(records, columns=columns)

    @staticmethod
    def is_secondary_record_useful(record: dict[str, object]) -> bool:
        return any(
            is_non_empty(record.get(column))
            for column in [
                "Beneficiário",
                "Número do Instrumento",
                "Objeto do Instrumento",
                "Valor Total do Instrumento",
                "Vigência do Instrumento",
            ]
        )

    @staticmethod
    def build_dedup_key(row: pd.Series) -> str:
        instrument_number = normalize_name(row.get("_id_key"))[:40]
        instrument = normalize_name(row.get("objeto"))[:80]
        beneficiary = normalize_name(row.get("nome_osc"))[:60]
        year_value = row.get("ano")
        amount_value = row.get("valor_total")
        year = "" if pd.isna(year_value) else str(year_value).strip()
        amount = "" if pd.isna(amount_value) else str(amount_value).strip()
        key_core = f"{year}|{instrument_number}|{beneficiary}|{instrument}|{amount}"
        return key_core if key_core.strip("|") else f"row|{row.name}"


PARSER = MAWorkbookParser()
