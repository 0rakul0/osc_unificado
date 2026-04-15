from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .common import WorkbookParser, build_parser


def split_to_vigencia(series: pd.Series) -> pd.DataFrame:
    def parse_value(value: object) -> tuple[object, object]:
        if pd.isna(value):
            return (pd.NA, pd.NA)

        text = str(value).strip()
        if not text:
            return (pd.NA, pd.NA)

        match = re.match(
            r"^\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})(?:\s*\([^)]*\))?\s*$",
            text,
        )
        if match:
            return match.group(1), match.group(2)

        return (text, pd.NA)

    return pd.DataFrame(
        series.map(parse_value).tolist(),
        columns=["data_inicio", "data_fim"],
        index=series.index,
    )


class TOWorkbookParser(WorkbookParser):
    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)

        if "Data de Vigência" in df.columns:
            vigencia_df = split_to_vigencia(df["Data de Vigência"])
            standardized["data_inicio"] = vigencia_df["data_inicio"].combine_first(standardized["data_inicio"])
            standardized["data_fim"] = vigencia_df["data_fim"].combine_first(standardized["data_fim"])

        return standardized


PARSER = TOWorkbookParser(build_parser("TO").config)
