from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .common import WorkbookParser, build_parser


def normalize_text_series(series: pd.Series) -> pd.Series:
    return series.map(
        lambda value: str(value).strip() if pd.notna(value) and str(value).strip() else pd.NA
    )


def normalize_df_cnpj(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    digits = re.sub(r"\D+", "", str(value))
    if not digits:
        return pd.NA

    return digits.zfill(14)


class DFWorkbookParser(WorkbookParser):
    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)

        fallback_objeto = (
            normalize_text_series(df["nomeProgramaTrabalho"])
            if "nomeProgramaTrabalho" in df.columns
            else pd.Series(pd.NA, index=df.index)
        )
        standardized["cnpj"] = standardized["cnpj"].map(normalize_df_cnpj)
        standardized["objeto"] = normalize_text_series(standardized["objeto"]).combine_first(fallback_objeto)
        return standardized


PARSER = DFWorkbookParser(build_parser("DF").config)
