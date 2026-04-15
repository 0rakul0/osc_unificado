from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .common import ParserConfig, STANDARD_COLUMNS, WorkbookParser, parse_dates


PRIMARY_WORKBOOK = "convenios_por_ano - rondônia.xlsx"
FALLBACK_WORKBOOK = "consolidado.xlsx"
RO_MAPPINGS = {
    "Contratado": "nome_osc",
    "Valor Global R$": "valor_total",
    "Data Assinatura": "data_inicio",
    "Vigência": "data_fim",
}


def clean_convenio_label(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).replace("\u200b", "").replace("\xa0", " ").strip()
    if not text:
        return pd.NA

    parts = [part.strip() for part in re.split(r"\s{2,}", text) if part.strip()]
    if len(parts) >= 2 and parts[0] == parts[-1]:
        return parts[-1]

    return text


def extract_first_currency(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).replace("\u200b", "").replace("\xa0", " ").strip()
    if not text or text.lower() == "nan":
        return pd.NA

    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2})", text)
    return match.group(1) if match else text


class ROWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="RO",
                extra_mappings=RO_MAPPINGS,
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        sibling_primary = workbook_path.parent / PRIMARY_WORKBOOK
        if workbook_path.name == FALLBACK_WORKBOOK and sibling_primary.exists():
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")

        if workbook_path.name not in {PRIMARY_WORKBOOK, FALLBACK_WORKBOOK}:
            return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")
        return super().parse_workbook(workbook_path, preview_rows=preview_rows)

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        prepared = df.copy()

        if "Convênio" in prepared.columns:
            prepared["Convênio"] = prepared["Convênio"].map(clean_convenio_label)

        if "Valor Global R$" in prepared.columns:
            prepared["Valor Global R$"] = prepared["Valor Global R$"].map(extract_first_currency)

        standardized = super().standardize(prepared, workbook_path, sheet_name)

        assinatura = parse_dates(df["Data Assinatura"]) if "Data Assinatura" in df.columns else pd.Series(pd.NaT, index=df.index)
        elaboracao = parse_dates(df["Dt. Elaboração"]) if "Dt. Elaboração" in df.columns else pd.Series(pd.NaT, index=df.index)
        inicio = assinatura.fillna(elaboracao)

        standardized["data_inicio"] = (
            standardized["data_inicio"]
            .combine_first(elaboracao.dt.strftime("%d/%m/%Y").astype("string"))
            .combine_first(assinatura.dt.strftime("%d/%m/%Y").astype("string"))
        )
        standardized["ano"] = inicio.dt.year.astype("Int64").astype("string").combine_first(standardized["ano"])
        standardized["mes"] = inicio.dt.month.astype("Int64").astype("string").combine_first(standardized["mes"])
        standardized["modalidade"] = standardized["modalidade"].fillna("CONVENIO")

        return standardized


PARSER = ROWorkbookParser()
