from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import STANDARD_COLUMNS, WorkbookParser, build_parser


OLD_SCHEMA_MAP = {
    "Numero": "id_unico",
    "Objeto": "objeto",
    "Situação": "modalidade",
    "Valor Concedente": "valor_total",
    "Convenente": "nome_osc",
    "Início": "data_inicio",
    "Término": "data_fim",
    "Publicação": "data",
    "ano": "ano",
}

NEW_SCHEMA_MAP = {
    "exercicio": "ano",
    "instrumento": "id_unico",
    "numero_ano": "id_unico",
    "nome_proponente": "nome_osc",
    "cnpj_proponente": "cnpj",
    "valor_total": "valor_total",
    "inicio_vigencia": "data_inicio",
    "fim_vigencia": "data_fim",
    "objeto": "objeto",
    "tipo_termo": "modalidade",
    "tipo_demanda": "modalidade",
    "tipo_celebracao": "modalidade",
    "situacao_termo_colaboracao": "modalidade",
    "status_prestacao_contas_final": "modalidade",
    "status_ultimo_repasse": "modalidade",
}


class PIWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(build_parser("PI").config)

    @staticmethod
    def empty_df() -> pd.DataFrame:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    def parse_old_sheet(self, raw: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        working = raw.rename(columns=OLD_SCHEMA_MAP).copy()

        # Para as abas antigas, `Publicação` tende a ser a data mais estável.
        if "data" not in working.columns and "data_inicio" in working.columns:
            working["data"] = working["data_inicio"]

        standardized = self.standardize(working, workbook_path, sheet_name)
        return standardized

    def parse_new_sheet(self, raw: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        working = raw.rename(columns=NEW_SCHEMA_MAP).copy()

        # Priorizamos a natureza do instrumento e, na falta dela, o status.
        modalidade = pd.Series(pd.NA, index=working.index)
        for column in [
            "tipo_termo",
            "tipo_demanda",
            "tipo_celebracao",
            "situacao_termo_colaboracao",
            "status_prestacao_contas_final",
            "status_ultimo_repasse",
        ]:
            if column in raw.columns:
                modalidade = modalidade.combine_first(raw[column])
        working["modalidade"] = modalidade

        if "data" not in working.columns and "data_inicio" in working.columns:
            working["data"] = working["data_inicio"]

        standardized = self.standardize(working, workbook_path, sheet_name)
        return standardized

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.name.lower() != "convenios_pi_v2.xlsx":
            return self.empty_df()

        excel_file = pd.ExcelFile(workbook_path)
        frames: list[pd.DataFrame] = []

        for sheet_name in excel_file.sheet_names:
            try:
                raw = self.read_sheet(workbook_path, sheet_name, nrows=preview_rows)
            except Exception:
                continue

            if raw.empty:
                continue

            if {"numero_ano", "nome_proponente", "cnpj_proponente"}.issubset(set(raw.columns)):
                frames.append(self.parse_new_sheet(raw, workbook_path, sheet_name))
            else:
                frames.append(self.parse_old_sheet(raw, workbook_path, sheet_name))

        if not frames:
            return self.empty_df()

        combined = pd.concat(frames, ignore_index=True)
        combined = combined.drop_duplicates(subset=STANDARD_COLUMNS, keep="first")
        return combined.reset_index(drop=True)


PARSER = PIWorkbookParser()
