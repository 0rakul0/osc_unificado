from __future__ import annotations

import unicodedata
from pathlib import Path

import pandas as pd

from .common import STANDARD_COLUMNS, WorkbookParser, build_parser


def normalize_column_name(value: object) -> str:
    return (
        unicodedata.normalize("NFKD", str(value))
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


class MTWorkbookParser(WorkbookParser):
    csv_name = "transparencia_csv.csv"

    def __init__(self) -> None:
        super().__init__(build_parser("MT").config)

    def _read_mt_csv(self, csv_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        return pd.read_csv(
            csv_path,
            dtype=str,
            sep=None,
            engine="python",
            encoding="cp1252",
            nrows=preview_rows,
            on_bad_lines="skip",
        )

    @staticmethod
    def _numero_series(raw: pd.DataFrame) -> pd.Series:
        normalized = {normalize_column_name(column): column for column in raw.columns}
        numero_col = normalized.get("numero")
        if numero_col is None:
            return pd.Series(pd.NA, index=raw.index)
        return raw[numero_col]

    def _parse_xlsx_only(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        excel_file = pd.ExcelFile(workbook_path)
        frames: list[pd.DataFrame] = []
        for sheet_name in excel_file.sheet_names:
            raw = self.read_sheet(workbook_path, sheet_name, nrows=preview_rows)
            standardized = self.standardize(raw, workbook_path, sheet_name)
            standardized["_numero"] = self._numero_series(raw)
            standardized["_source_rank"] = 0
            frames.append(standardized)

        if not frames:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        combined = pd.concat(frames, ignore_index=True)
        return combined

    def _parse_csv_only(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        raw = self._read_mt_csv(workbook_path, preview_rows=preview_rows)
        if raw.empty:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        standardized = self.standardize(raw, workbook_path, workbook_path.stem)
        standardized["_numero"] = self._numero_series(raw)
        standardized["_source_rank"] = 1
        return standardized

    def _combine_sources(self, frames: list[pd.DataFrame]) -> pd.DataFrame:
        if not frames:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        combined = pd.concat(frames, ignore_index=True)
        dedup_cols = ["_numero", "cnpj", "data_inicio", "data_fim", "valor_total"]
        combined = combined.sort_values(
            by=["_source_rank", "ano", "mes"],
            na_position="last",
            kind="stable",
        ).drop_duplicates(subset=dedup_cols, keep="first")
        return combined[STANDARD_COLUMNS].reset_index(drop=True)

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        suffix = workbook_path.suffix.lower()

        if suffix == ".csv":
            return self._combine_sources([self._parse_csv_only(workbook_path, preview_rows=preview_rows)])

        if suffix == ".xlsx":
            frames = [self._parse_xlsx_only(workbook_path, preview_rows=preview_rows)]
            sibling_csv = workbook_path.parent / self.csv_name
            if sibling_csv.exists():
                frames.append(self._parse_csv_only(sibling_csv, preview_rows=preview_rows))
            return self._combine_sources(frames)

        return super().parse_workbook(workbook_path, preview_rows=preview_rows)


PARSER = MTWorkbookParser()
