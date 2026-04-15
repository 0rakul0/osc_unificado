from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .parser_mappings import UF_HEADER_ROWS, get_uf_mapping


STANDARD_COLUMNS = [
    "uf",
    "origem",
    "ano",
    "valor_total",
    "cnpj",
    "nome_osc",
    "mes",
    "cod_municipio",
    "municipio",
    "objeto",
    "modalidade",
    "data_inicio",
    "data_fim",
]

EXTRA_COLUMNS = [
    "data",
    "data_inicio",
    "data_fim",
    "id_unico",
    "valor_repassado",
    "valor_contrapartida",
    "observacoes",
    "emenda_parlamentar",
    "arquivo_origem",
    "aba_origem",
]

HEURISTIC_ALIASES = {
    "ano": "ano",
    "anocontrato": "ano",
    "anoproposta": "ano",
    "anoassinatura": "ano",
    "exercicioconvenio": "ano",
    "data": "data",
    "datapublicacao": "data",
    "dataassinatura": "data",
    "datacelebracao": "data",
    "cnpj": "cnpj",
    "cnpjconvenente": "cnpj",
    "cnpj_convenente": "cnpj",
    "cnpjcontratante": "cnpj",
    "cpfcnpjconvenente": "cnpj",
    "beneficiado": "cnpj",
    "nomeosc": "nome_osc",
    "convenente": "nome_osc",
    "ososcip": "nome_osc",
    "nomeproponente": "nome_osc",
    "nomeconvenente": "nome_osc",
    "beneficiario": "nome_osc",
    "descricaobeneficiado": "nome_osc",
    "razaosocialcontratado": "nome_osc",
    "nomecontratado": "nome_osc",
    "municipio": "municipio",
    "nomemunicipio": "municipio",
    "municipioconvenente": "municipio",
    "codmunicipio": "cod_municipio",
    "codibgemunicipio": "cod_municipio",
    "ibge": "cod_municipio",
    "objeto": "objeto",
    "objetivo": "objeto",
    "modalidade": "modalidade",
    "tipoaquisicao": "modalidade",
    "tipoconvenio": "modalidade",
    "tipoinstrumento": "modalidade",
    "situacao": "modalidade",
    "vigencia": "vigencia",
    "inicio": "data_inicio",
    "datainiciovigencia": "data_inicio",
    "prazoinicial": "data_inicio",
    "termino": "data_fim",
    "fim": "data_fim",
    "datafimvigencia": "data_fim",
    "prazofinal": "data_fim",
    "valortotal": "valor_total",
    "valorpactuado": "valor_total",
    "valorglobal": "valor_total",
    "valorconcessao": "valor_total",
    "valoraquisicao": "valor_total",
    "valor": "valor_total",
    "valorrepassado": "valor_repassado",
    "valorpartida": "valor_repassado",
    "valordorepasse": "valor_repassado",
    "valorcontrapartida": "valor_contrapartida",
}


@dataclass(slots=True)
class ParserConfig:
    uf: str
    header_row: int = 0
    extra_mappings: dict[str, str] = field(default_factory=dict)

    @property
    def mappings(self) -> dict[str, str]:
        mapping = get_uf_mapping(self.uf)
        mapping.update(self.extra_mappings)
        return mapping


def normalize_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "", text).lower()
    return text


def clean_document(value: object) -> object:
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return pd.NA

    filtered = re.sub(r"[^0-9xX*]+", "", text)
    if not filtered:
        return pd.NA

    filtered = filtered.upper().replace("X", "*")
    digits_only = re.sub(r"\D+", "", filtered)

    if "*" in filtered:
        return filtered if len(filtered) in {11, 14} else pd.NA

    if len(digits_only) == 11:
        return digits_only

    if 11 < len(digits_only) <= 14:
        return digits_only.zfill(14)

    return pd.NA


def clean_cnpj(series: pd.Series) -> pd.Series:
    return series.map(clean_document)


def infer_year(text: str | None) -> int | None:
    if not text:
        return None
    match = re.search(r"(19|20)\d{2}", str(text))
    return int(match.group(0)) if match else None


def choose_first_existing(df: pd.DataFrame, columns: list[str]) -> str | None:
    for column in columns:
        if column in df.columns:
            return column
    return None


def split_vigencia_value(value: object) -> tuple[object, object]:
    if pd.isna(value):
        return (pd.NA, pd.NA)

    text = str(value).strip()
    if not text:
        return (pd.NA, pd.NA)

    parts = re.split(r"\s+(?:a|ate|até)\s+", text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 2:
        start, end = (part.strip() or pd.NA for part in parts)
        return start, end

    return (text, pd.NA)


def parse_dates(series: pd.Series) -> pd.Series:
    # Normaliza datas com e sem timezone para um tipo comum antes de extrair ano/mes.
    return pd.to_datetime(series, errors="coerce", dayfirst=True, utc=True, format="mixed")


class WorkbookParser:
    def __init__(self, config: ParserConfig):
        self.config = config

    def read_sheet(self, workbook_path: Path, sheet_name: str, nrows: int | None = None) -> pd.DataFrame:
        return pd.read_excel(
            workbook_path,
            sheet_name=sheet_name,
            header=self.config.header_row,
            nrows=nrows,
        )

    def build_rename_map(self, columns: list[object]) -> dict[object, str]:
        direct_mapping = self.config.mappings
        normalized_mapping = {normalize_name(source): target for source, target in direct_mapping.items()}
        rename_map: dict[object, str] = {}
        for column in columns:
            if column in direct_mapping:
                rename_map[column] = direct_mapping[column]
                continue
            normalized = normalize_name(column)
            target = normalized_mapping.get(normalized) or HEURISTIC_ALIASES.get(normalized)
            if target:
                rename_map[column] = target
        return rename_map

    def standardize(self, df: pd.DataFrame, workbook_path: Path, sheet_name: str) -> pd.DataFrame:
        renamed = df.rename(columns=self.build_rename_map(list(df.columns))).copy()
        renamed = self.merge_duplicate_columns(renamed)

        if "uf" not in renamed.columns:
            renamed["uf"] = self.config.uf

        if "ano" not in renamed.columns:
            inferred_year = infer_year(sheet_name) or infer_year(workbook_path.name)
            renamed["ano"] = inferred_year
        else:
            fallback_year = infer_year(sheet_name) or infer_year(workbook_path.name)
            renamed["ano"] = renamed["ano"].combine_first(
                pd.Series([fallback_year] * len(renamed), index=renamed.index)
            )

        if "valor_total" not in renamed.columns and "valor_repassado" in renamed.columns:
            renamed["valor_total"] = renamed["valor_repassado"]

        if "cnpj" in renamed.columns:
            renamed["cnpj"] = clean_cnpj(renamed["cnpj"])

        if "vigencia" in renamed.columns and ("data_inicio" not in renamed.columns or "data_fim" not in renamed.columns):
            vigencia_split = renamed["vigencia"].apply(split_vigencia_value)
            vigencia_df = pd.DataFrame(vigencia_split.tolist(), columns=["data_inicio_extra", "data_fim_extra"], index=renamed.index)
            if "data_inicio" not in renamed.columns:
                renamed["data_inicio"] = vigencia_df["data_inicio_extra"]
            else:
                renamed["data_inicio"] = renamed["data_inicio"].combine_first(vigencia_df["data_inicio_extra"])
            if "data_fim" not in renamed.columns:
                renamed["data_fim"] = vigencia_df["data_fim_extra"]
            else:
                renamed["data_fim"] = renamed["data_fim"].combine_first(vigencia_df["data_fim_extra"])

        date_col = choose_first_existing(renamed, ["data", "data_inicio", "data_fim"])
        if "ano" in renamed.columns and date_col:
            parsed_year = parse_dates(renamed[date_col]).dt.year
            renamed["ano"] = renamed["ano"].combine_first(parsed_year)

        if "mes" not in renamed.columns:
            if date_col:
                parsed = parse_dates(renamed[date_col])
                renamed["mes"] = parsed.dt.month
                if "ano" in renamed.columns:
                    renamed["ano"] = renamed["ano"].combine_first(parsed.dt.year)
            else:
                renamed["mes"] = pd.NA

        renamed["arquivo_origem"] = str(workbook_path)
        renamed["aba_origem"] = str(sheet_name)

        for column in STANDARD_COLUMNS:
            if column not in renamed.columns:
                renamed[column] = pd.NA

        return renamed[STANDARD_COLUMNS]

    @staticmethod
    def merge_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
        if not df.columns.duplicated().any():
            return df

        merged = pd.DataFrame(index=df.index)
        for column_name in dict.fromkeys(df.columns):
            subset = df.loc[:, df.columns == column_name]
            if isinstance(subset, pd.Series):
                merged[column_name] = subset
            else:
                merged[column_name] = subset.bfill(axis=1).iloc[:, 0]
        return merged

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        excel_file = pd.ExcelFile(workbook_path)
        previews: list[pd.DataFrame] = []
        for sheet_name in excel_file.sheet_names:
            try:
                preview = self.read_sheet(workbook_path, sheet_name, nrows=preview_rows)
            except Exception as exc:
                previews.append(
                    pd.DataFrame(
                        [
                            {
                                "uf": self.config.uf,
                                "arquivo_origem": str(workbook_path),
                                "aba_origem": str(sheet_name),
                                "observacoes": f"erro ao ler preview: {exc}",
                            }
                        ]
                    )
                )
                continue
            previews.append(self.standardize(preview, workbook_path, sheet_name))
        return pd.concat(previews, ignore_index=True) if previews else pd.DataFrame(columns=STANDARD_COLUMNS + EXTRA_COLUMNS)


def build_parser(uf: str) -> WorkbookParser:
    return WorkbookParser(
        ParserConfig(
            uf=uf.upper(),
            header_row=UF_HEADER_ROWS.get(uf.upper(), 0),
        )
    )
