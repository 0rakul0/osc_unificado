from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import STANDARD_COLUMNS, WorkbookParser, build_parser


PRIMARY_WORKBOOK = "ConveniosDespesa-RS.csv"
FALLBACK_WORKBOOK = "ConveniosDespesa-RS.xlsx"


class RSWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(build_parser("RS").config)

    @staticmethod
    def empty_df() -> pd.DataFrame:
        return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        root_primary = workbook_path.parent / PRIMARY_WORKBOOK

        if workbook_path.name == PRIMARY_WORKBOOK and workbook_path.parent.name == "saida":
            raw = pd.read_csv(
                workbook_path,
                sep=";",
                encoding="latin1",
                dtype=str,
                nrows=preview_rows,
            )
            return self.standardize(raw, workbook_path, workbook_path.stem)

        if workbook_path.name == FALLBACK_WORKBOOK and not root_primary.exists():
            return super().parse_workbook(workbook_path, preview_rows=preview_rows)

        return self.empty_df()


PARSER = RSWorkbookParser()
