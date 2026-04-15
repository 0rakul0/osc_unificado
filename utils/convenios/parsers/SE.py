from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import WorkbookParser, build_parser, parse_dates


def normalize_text_series(series: pd.Series) -> pd.Series:
    return series.map(
        lambda value: str(value).strip() if pd.notna(value) and str(value).strip() else pd.NA
    )


def first_non_empty(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    available = [normalize_text_series(df[column]) for column in columns if column in df.columns]
    if not available:
        return pd.Series(pd.NA, index=df.index)

    combined = available[0]
    for candidate in available[1:]:
        combined = combined.combine_first(candidate)
    return combined


def keep_only_cnpj(series: pd.Series) -> pd.Series:
    return series.map(
        lambda value: value
        if pd.notna(value) and len("".join(ch for ch in str(value) if ch.isdigit())) == 14
        else pd.NA
    )


class SEWorkbookParser(WorkbookParser):
    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        standardized = super().standardize(df, workbook_path, sheet_name)

        # Prefer the original committed amount, then fall back to requested and execution totals.
        standardized["valor_total"] = first_non_empty(
            df,
            [
                "vlOriginalEmpenho",
                "vlSolicEmpenho",
                "vlTotalLiquidadoEmpenho",
                "vlTotalPagoEmpenho",
            ],
        )

        standardized["objeto"] = first_non_empty(df, ["dsObjetoLicitacao"])
        standardized["ano"] = first_non_empty(df, ["dtAnoExercicioCtb", "_ano"]).combine_first(
            standardized["ano"]
        )
        standardized["mes"] = first_non_empty(df, ["_mes"]).combine_first(standardized["mes"])
        standardized["cnpj"] = keep_only_cnpj(standardized["cnpj"])

        base_dates = parse_dates(
            first_non_empty(df, ["dtEmissaoEmpenho", "dtLancamentoEmpenho", "dtGeracaoEmpenho"])
        )
        standardized["ano"] = standardized["ano"].combine_first(base_dates.dt.year)
        standardized["mes"] = standardized["mes"].combine_first(base_dates.dt.month)
        standardized["data_inicio"] = pd.NA
        standardized["data_fim"] = pd.NA
        return standardized


PARSER = SEWorkbookParser(build_parser("SE").config)
