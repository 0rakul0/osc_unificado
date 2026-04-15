from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import STANDARD_COLUMNS, WorkbookParser, build_parser, parse_dates


class PRWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(build_parser("PR").config)

    @staticmethod
    def empty_df() -> pd.DataFrame:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    @staticmethod
    def read_csv_with_fallback(workbook_path: Path) -> pd.DataFrame:
        last_error: Exception | None = None
        for encoding in ("utf-8", "utf-8-sig", "latin1"):
            try:
                return pd.read_csv(workbook_path, sep=";", dtype=str, encoding=encoding)
            except Exception as exc:  # pragma: no cover - defensive fallback
                last_error = exc
        raise RuntimeError(f"Falha ao ler {workbook_path}") from last_error

    @staticmethod
    def choose_primary_date(raw: pd.DataFrame) -> pd.Series:
        primary = pd.Series(pd.NA, index=raw.index, dtype="object")
        for column in ["dt_vigencia_inicio", "dt_celebracao", "dt_publicacao", "dt_vigencia_fim"]:
            if column in raw.columns:
                primary = primary.combine_first(raw[column])
        return primary

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if "TB_CONVENIO_EMPREENDIMENTO" not in workbook_path.name.upper():
            return self.empty_df()

        raw = self.read_csv_with_fallback(workbook_path)
        if preview_rows is not None:
            raw = raw.head(preview_rows)
        if raw.empty:
            return self.empty_df()

        working = raw.copy()
        working["uf"] = "PR"
        working["id_unico"] = raw.get("numero")
        working["nome_osc"] = raw.get("tomador")
        working["objeto"] = raw.get("objeto")
        working["modalidade"] = raw.get("situacao")
        working["valor_total"] = raw.get("total_repasses")
        working["cod_municipio"] = raw.get("ibge")
        working["data_inicio"] = raw.get("dt_vigencia_inicio")
        working["data_fim"] = raw.get("dt_vigencia_fim")
        working["data"] = self.choose_primary_date(raw)

        primary_dates = parse_dates(working["data_inicio"]).fillna(parse_dates(working["data"]))
        working["ano"] = primary_dates.dt.year.astype("Int64")
        working["mes"] = primary_dates.dt.month.astype("Int64")

        standardized = self.standardize(working, workbook_path, workbook_path.stem)
        standardized = standardized.drop_duplicates(subset=STANDARD_COLUMNS, keep="first")
        return standardized.reset_index(drop=True)


PARSER = PRWorkbookParser()
