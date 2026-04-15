from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import WorkbookParser, build_parser


class PAWorkbookParser(WorkbookParser):
    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.suffix.lower() == ".csv":
            preview = pd.read_csv(
                workbook_path,
                encoding="utf-8",
                nrows=preview_rows,
                on_bad_lines="skip",
            )
            return self.standardize(preview, workbook_path, workbook_path.stem)

        return super().parse_workbook(workbook_path, preview_rows=preview_rows)


PARSER = PAWorkbookParser(build_parser("PA").config)
