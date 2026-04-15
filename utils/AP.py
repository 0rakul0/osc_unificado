from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .common import STANDARD_COLUMNS, WorkbookParser, build_parser, parse_dates


TARGET_SHEETS = ("CONVÊNIOS ", "TERMO DE FOMENTO")


def strip_appended_cnpj(nome_osc: object, cnpj: object) -> object:
    if pd.isna(nome_osc):
        return pd.NA

    nome = str(nome_osc).strip()
    if not nome:
        return pd.NA

    if pd.isna(cnpj):
        return nome

    digits = re.sub(r"\D+", "", str(cnpj))
    if not digits:
        return nome

    cleaned = re.sub(rf"\s*[-/]*\s*{re.escape(digits)}\s*$", "", nome).strip(" -/")
    trailing_digits_match = re.search(r"[-/\s]*([0-9]{8,14})\s*$", cleaned)
    if trailing_digits_match and digits.startswith(trailing_digits_match.group(1)):
        cleaned = cleaned[: trailing_digits_match.start()].rstrip(" -/")
    return cleaned or nome


def extract_year_from_instrument(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    match = re.search(r"/((?:19|20)\d{2})", str(value))
    return int(match.group(1)) if match else pd.NA


class APWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(build_parser("AP").config)

    @staticmethod
    def empty_df() -> pd.DataFrame:
        return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

    def _prepare_sheet(self, raw: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        prepared = raw.copy()

        renames = {
            "Credor": "cnpj",
            "Nome do Credor": "nome_osc",
            "Objeto": "objeto",
            "Valor Total": "valor_total",
            "Data Início": "data_inicio",
            "Data Termino": "data_fim",
            "SITUAÇÂO": "modalidade",
            "Número Original": "id_unico",
        }
        prepared = prepared.rename(columns=renames)

        # Em várias linhas do termo de fomento, as datas vêm como zero.
        for column in ["data_inicio", "data_fim"]:
            if column in prepared.columns:
                prepared[column] = prepared[column].replace({0: pd.NA, "0": pd.NA, "0.0": pd.NA})

        if "modalidade" not in prepared.columns:
            prepared["modalidade"] = pd.NA

        modalidade_fallback = "TERMO DE FOMENTO" if "FOMENTO" in sheet_name.upper() else "CONVÊNIO"
        prepared["modalidade"] = prepared["modalidade"].fillna(modalidade_fallback)

        instrument_year = (
            prepared["id_unico"].map(extract_year_from_instrument)
            if "id_unico" in prepared.columns
            else pd.Series(pd.NA, index=prepared.index)
        )
        prepared["ano_instrumento"] = instrument_year
        return prepared

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)
        standardized["nome_osc"] = [
            strip_appended_cnpj(nome_osc, cnpj)
            for nome_osc, cnpj in zip(standardized["nome_osc"], standardized["cnpj"], strict=False)
        ]

        data_inicio = parse_dates(df["data_inicio"]) if "data_inicio" in df.columns else pd.Series(pd.NaT, index=df.index)
        ano_instrumento = (
            pd.to_numeric(df["ano_instrumento"], errors="coerce").astype("Int64").astype("string")
            if "ano_instrumento" in df.columns
            else pd.Series(pd.NA, index=df.index, dtype="string")
        )
        standardized["ano"] = (
            data_inicio.dt.year.astype("Int64").astype("string").combine_first(ano_instrumento).combine_first(standardized["ano"])
        )
        standardized["mes"] = data_inicio.dt.month.astype("Int64").astype("string").combine_first(standardized["mes"])
        return standardized

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        excel_file = pd.ExcelFile(workbook_path)
        frames: list[pd.DataFrame] = []

        for sheet_name in TARGET_SHEETS:
            if sheet_name not in excel_file.sheet_names:
                continue

            raw = self.read_sheet(workbook_path, sheet_name, nrows=preview_rows)
            if raw.empty:
                continue

            prepared = self._prepare_sheet(raw, sheet_name)
            frames.append(self.standardize(prepared, workbook_path, sheet_name))

        if not frames:
            return self.empty_df()

        combined = pd.concat(frames, ignore_index=True)
        combined = combined.drop_duplicates(subset=STANDARD_COLUMNS, keep="first")
        return combined.reset_index(drop=True)


PARSER = APWorkbookParser()
