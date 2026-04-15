from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .common import ParserConfig, WorkbookParser, parse_dates


ORIGEM_GOVERNO_FEDERAL = "convenios_federal"
GOV_CONVENIOS_MAPPINGS = {
    "CÓDIGO CONVENENTE": "cnpj",
    "NOME CONVENENTE": "nome_osc",
    "OBJETO DO CONVÊNIO": "objeto",
    "TIPO INSTRUMENTO": "modalidade",
    "VALOR CONVÊNIO": "valor_total",
    "VALOR CONTRAPARTIDA": "valor_contrapartida",
    "DATA PUBLICAÇÃO": "data",
    "DATA INÍCIO VIGÊNCIA": "data_inicio",
    "DATA FINAL VIGÊNCIA": "data_fim",
    "CÓDIGO SIAFI MUNICÍPIO": "cod_municipio",
    "NOME MUNICÍPIO": "municipio",
    "NÚMERO CONVÊNIO": "id_unico",
}


class GovConveniosWorkbookParser(WorkbookParser):
    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.suffix.lower() == ".csv":
            preview = pd.read_csv(
                workbook_path,
                sep=";",
                encoding="cp1252",
                dtype=str,
            )
            preview.columns = [str(column).strip() for column in preview.columns]
            preview = preview[preview["UF"].astype(str).str.strip().str.upper() == self.config.uf]
            if preview_rows is not None:
                preview = preview.head(preview_rows)
            return self.standardize(preview, workbook_path, workbook_path.stem)

        return super().parse_workbook(workbook_path, preview_rows=preview_rows)

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        numero_convenio_ano = (
            df["NÚMERO CONVÊNIO"].map(
                lambda value: int(match.group(1))
                if (match := re.search(r"/((?:19|20)\d{2})", str(value)))
                else pd.NA
            )
            if "NÚMERO CONVÊNIO" in df.columns
            else pd.Series(pd.NA, index=df.index)
        )
        data_publicacao = (
            parse_dates(df["DATA PUBLICAÇÃO"])
            if "DATA PUBLICAÇÃO" in df.columns
            else pd.Series(pd.NaT, index=df.index)
        )
        data_inicio = (
            parse_dates(df["DATA INÍCIO VIGÊNCIA"])
            if "DATA INÍCIO VIGÊNCIA" in df.columns
            else pd.Series(pd.NaT, index=df.index)
        )
        data_fim = (
            parse_dates(df["DATA FINAL VIGÊNCIA"])
            if "DATA FINAL VIGÊNCIA" in df.columns
            else pd.Series(pd.NaT, index=df.index)
        )

        standardized = super().standardize(df, workbook_path, sheet_name)
        standardized["origem"] = ORIGEM_GOVERNO_FEDERAL

        if "VALOR LIBERADO" in df.columns:
            valor_liberado = df["VALOR LIBERADO"].map(lambda value: str(value).strip() if pd.notna(value) else pd.NA)
            standardized["valor_total"] = standardized["valor_total"].combine_first(valor_liberado)

        parsed_base_date = data_publicacao.combine_first(data_inicio)
        ano_sources = pd.DataFrame(
            {
                "numero_convenio_ano": pd.to_numeric(numero_convenio_ano, errors="coerce"),
                "data_base_ano": parsed_base_date.dt.year,
                "data_fim_ano": data_fim.dt.year,
            },
            index=df.index,
        )
        standardized["ano"] = ano_sources.bfill(axis=1).iloc[:, 0]
        standardized["mes"] = parsed_base_date.dt.month

        return standardized


def build_gov_convenios_parser(uf: str) -> GovConveniosWorkbookParser:
    return GovConveniosWorkbookParser(
        ParserConfig(
            uf=uf.upper(),
            extra_mappings=GOV_CONVENIOS_MAPPINGS,
        )
    )
