from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import ParserConfig, STANDARD_COLUMNS, WorkbookParser, parse_dates


PRIMARY_WORKBOOK = "convenios_sem_fins_lucrativos.xlsx"
CE_MAPPINGS = {
    "Exercício": "ano",
    "Credor": "nome_osc",
    "Ação de governo": "objeto",
    "Natureza da despesa": "modalidade",
    "Valor empenhado final": "valor_total",
    "Valor pago final": "valor_repassado",
    "Data de emissão": "data_inicio",
}


class CEWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="CE",
                extra_mappings=CE_MAPPINGS,
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.name != PRIMARY_WORKBOOK:
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")
        return super().parse_workbook(workbook_path, preview_rows=preview_rows)

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)
        emissao = parse_dates(df["Data de emissão"]) if "Data de emissão" in df.columns else pd.Series(pd.NaT, index=df.index)
        standardized["ano"] = emissao.dt.year.astype("Int64").astype("string").combine_first(standardized["ano"])
        standardized["mes"] = emissao.dt.month.astype("Int64").astype("string").combine_first(standardized["mes"])
        return standardized


PARSER = CEWorkbookParser()
