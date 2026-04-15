from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import ParserConfig, STANDARD_COLUMNS, WorkbookParser, parse_dates


PRIMARY_WORKBOOK = "convenios.xlsx"
MG_MAPPINGS = {
    "cnpj": "cnpj",
    "nome_convenente": "nome_osc",
    "nome_municipio": "municipio",
    "objetivo": "objeto",
    "tp_instrumento": "modalidade",
    "vr_total_atual": "valor_total",
    "dt_publicacao": "data",
    "dt_vigencia_inicial": "data_inicio",
    "dt_vigencia_final": "data_fim",
}


class MGWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="MG",
                extra_mappings=MG_MAPPINGS,
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.name != PRIMARY_WORKBOOK:
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

        standardized = super().parse_workbook(workbook_path, preview_rows=preview_rows)
        return standardized.drop_duplicates().reset_index(drop=True)

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)

        if "tp_instrumento" in df.columns:
            modalidade = df["tp_instrumento"].replace("-", pd.NA).astype("string")
            standardized["modalidade"] = modalidade.combine_first(standardized["modalidade"])
        standardized["modalidade"] = standardized["modalidade"].replace("-", pd.NA)

        publicacao = parse_dates(df["dt_publicacao"]) if "dt_publicacao" in df.columns else pd.Series(pd.NaT, index=df.index)
        standardized["ano"] = publicacao.dt.year.astype("Int64").astype("string").combine_first(standardized["ano"])
        standardized["mes"] = publicacao.dt.month.astype("Int64").astype("string").combine_first(standardized["mes"])

        return standardized


PARSER = MGWorkbookParser()
