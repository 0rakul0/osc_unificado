from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .common import ParserConfig, STANDARD_COLUMNS, WorkbookParser


MS_MAPPINGS = {
    "cnpj_Convenente": "cnpj",
    "convenente_Nome": "nome_osc",
    "valorConvenio": "valor_total",
    "tipo_Convenio": "modalidade",
}


def strip_trailing_document(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    text = re.sub(r"\s*\(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\)$", "", text)
    return text.strip() or pd.NA


class MSWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="MS",
                extra_mappings=MS_MAPPINGS,
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.suffix.lower() != ".xlsx":
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")
        return super().parse_workbook(workbook_path, preview_rows=preview_rows)

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        prepared = df.copy()
        if "convenente_Nome" in prepared.columns:
            prepared["convenente_Nome"] = prepared["convenente_Nome"].map(strip_trailing_document)

        standardized = super().standardize(prepared, workbook_path, sheet_name)
        return standardized


PARSER = MSWorkbookParser()
