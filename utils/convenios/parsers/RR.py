from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import ParserConfig, STANDARD_COLUMNS, WorkbookParser


PRIMARY_WORKBOOK = "dados_convenios_receita.xlsx"
CONVENIOS_SHEET_INDEX = 1
RR_MAPPINGS = {
    "Nome Proponente": "nome_osc",
    "Objeto": "objeto",
    "Modalidade": "modalidade",
    "Valor Global": "valor_total",
    "Data Inicio de Vigencia Conv.": "data_inicio",
    "Data Fim de Vigencia Conv.": "data_fim",
}


class RRWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="RR",
                extra_mappings=RR_MAPPINGS,
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.name != PRIMARY_WORKBOOK:
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

        raw = pd.read_excel(workbook_path, sheet_name=CONVENIOS_SHEET_INDEX)
        if preview_rows is not None:
            raw = raw.head(preview_rows)

        return self.standardize(raw, workbook_path, "Convenios")

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        prepared = df.copy()

        # Drop the single row that explicitly belongs to Palmas-TO.
        if "Objeto" in prepared.columns:
            object_text = prepared["Objeto"].fillna("").astype(str).str.upper()
            prepared = prepared.loc[~object_text.str.contains("PALMAS-TO|TOCANTINS", regex=True)].copy()

        standardized = super().standardize(prepared, workbook_path, sheet_name)
        if "Ano Assinatura" in prepared.columns:
            standardized["ano"] = (
                prepared["Ano Assinatura"].astype("Int64").astype("string").combine_first(standardized["ano"])
            )
        return standardized


PARSER = RRWorkbookParser()
