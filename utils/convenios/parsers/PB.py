from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import ParserConfig, STANDARD_COLUMNS, WorkbookParser, parse_dates


PRIMARY_WORKBOOK = "consolidado.xlsx"
PB_MAPPINGS = {
    "INÍCIO": "data_inicio",
    "Convenente": "nome_osc",
    "Objetivo": "objeto",
    "Tipo": "modalidade",
    "Valor Total": "valor_total",
    "Valor Concedente": "valor_repassado",
    "Valor Contrapartida": "valor_contrapartida",
    "Cadastro CGE": "observacoes",
}


class PBWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="PB",
                extra_mappings=PB_MAPPINGS,
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.name != PRIMARY_WORKBOOK:
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

        excel_file = pd.ExcelFile(workbook_path)
        frames: list[pd.DataFrame] = []
        for sheet_name in excel_file.sheet_names:
            raw = pd.read_excel(workbook_path, sheet_name=sheet_name, header=None, dtype=str)
            if preview_rows is not None:
                raw = raw.head(preview_rows + 2)
            prepared = self.prepare_sheet(raw)
            if prepared.empty:
                continue
            standardized = self.standardize(prepared, workbook_path, sheet_name)
            frames.append(standardized)

        if not frames:
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")
        return pd.concat(frames, ignore_index=True)

    @staticmethod
    def prepare_sheet(raw: pd.DataFrame) -> pd.DataFrame:
        if raw.empty or len(raw) < 3:
            return pd.DataFrame()

        header = raw.iloc[1].fillna("").astype(str).str.strip().tolist()
        body = raw.iloc[2:].copy()
        body.columns = header
        body = body.dropna(how="all").reset_index(drop=True)
        if "" in body.columns:
            body = body.drop(columns=[""])
        return body

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)
        parsed_inicio = parse_dates(df["INÍCIO"]) if "INÍCIO" in df.columns else pd.Series(pd.NaT, index=df.index)
        standardized["ano"] = parsed_inicio.dt.year.astype("Int64").astype("string").combine_first(standardized["ano"])
        standardized["mes"] = parsed_inicio.dt.month.astype("Int64").astype("string").combine_first(standardized["mes"])
        return standardized


PARSER = PBWorkbookParser()
