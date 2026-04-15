from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
import unicodedata
from pathlib import Path

import pandas as pd

from .common import WorkbookParser, build_parser, parse_dates


def extract_year_from_numero(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    match = re.search(r"/((?:19|20)\d{2})", str(value))
    if not match:
        return pd.NA

    return int(match.group(1))


def parse_single_date(text: str) -> object:
    iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if iso_match:
        parsed = pd.to_datetime(iso_match.group(1), errors="coerce", format="%Y-%m-%d")
        return parsed.normalize() if pd.notna(parsed) else pd.NA

    matches = re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text)
    if matches:
        parsed = pd.to_datetime(matches[-1], errors="coerce", dayfirst=True)
        return parsed.normalize() if pd.notna(parsed) else pd.NA

    parsed = pd.to_datetime(text, errors="coerce", format="mixed")
    return parsed.normalize() if pd.notna(parsed) else pd.NA


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()


def extract_start_date(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    if isinstance(value, pd.Timestamp):
        return value.normalize()

    text = str(value).strip()
    if not text:
        return pd.NA

    if normalize_text(text).startswith("ate "):
        return pd.NA

    return parse_single_date(text)


def extract_end_date(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    if isinstance(value, pd.Timestamp):
        return value.normalize()

    text = str(value).strip()
    if not text:
        return pd.NA

    return parse_single_date(text)


def normalize_csv_document(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    if "E+" not in text.upper():
        return text

    normalized = text.replace(".", "").replace(",", ".")
    try:
        number = Decimal(normalized)
    except InvalidOperation:
        return text

    return format(number, "f").split(".")[0]


def read_rj_2024_csv(workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    with workbook_path.open("r", encoding="cp1252") as file_obj:
        for raw_line in file_obj:
            line = raw_line.strip()
            if not line:
                continue

            fields = [field.strip() for field in line.split(";")]
            if not fields:
                continue

            first_value = normalize_text(fields[0])
            if first_value in {
                "modalidade de aplicacao",
                "total",
                "coluna1",
                "fonte: siafe-rio.",
            }:
                continue

            if len(fields) < 18:
                continue

            if not any(fields[index].strip() for index in (1, 2, 4, 17) if index < len(fields)):
                continue

            rows.append(
                {
                    "CNPJ/CPF": fields[1],
                    "FAVORECIDO": fields[2],
                    "NOME DO PROGRAMA": fields[4],
                    "TOTAL": fields[17],
                }
            )

            if preview_rows is not None and len(rows) >= preview_rows:
                break

    return pd.DataFrame(rows)


class RJWorkbookParser(WorkbookParser):
    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.suffix.lower() == ".csv":
            if "2024" in workbook_path.stem:
                preview = read_rj_2024_csv(workbook_path, preview_rows=preview_rows)
            else:
                preview = pd.read_csv(
                    workbook_path,
                    sep=";",
                    encoding="cp1252",
                    dtype=str,
                    nrows=preview_rows,
                )
                preview.columns = [str(column).strip() for column in preview.columns]

            if "CNPJ/CPF" in preview.columns:
                preview["CNPJ/CPF"] = preview["CNPJ/CPF"].map(normalize_csv_document)
            return self.standardize(preview, workbook_path, workbook_path.stem)

        return super().parse_workbook(workbook_path, preview_rows=preview_rows)

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        rename_map = self.build_rename_map(list(df.columns))
        id_source = next((column for column, target in rename_map.items() if target == "id_unico"), None)
        ano_from_numero = (
            df[id_source].map(extract_year_from_numero)
            if id_source is not None
            else pd.Series(pd.NA, index=df.index, dtype="object")
        )

        standardized = super().standardize(df, workbook_path, sheet_name)

        standardized["ano"] = ano_from_numero.combine_first(standardized["ano"])
        standardized["data_inicio"] = standardized["data_inicio"].map(extract_start_date)
        standardized["data_fim"] = standardized["data_fim"].map(extract_end_date)

        parsed = parse_dates(standardized["data_inicio"]).combine_first(parse_dates(standardized["data_fim"]))
        standardized["mes"] = parsed.dt.month
        standardized["ano"] = standardized["ano"].combine_first(parsed.dt.year)

        return standardized


PARSER = RJWorkbookParser(build_parser("RJ").config)
