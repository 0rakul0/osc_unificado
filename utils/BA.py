from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import WorkbookParser, build_parser


class BAWorkbookParser(WorkbookParser):
    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)
        standardized["data_inicio"] = pd.NA
        standardized["data_fim"] = pd.NA
        return standardized


PARSER = BAWorkbookParser(build_parser("BA").config)
