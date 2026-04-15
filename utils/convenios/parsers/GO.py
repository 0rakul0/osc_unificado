from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd

from .common import ParserConfig, WorkbookParser, build_parser


ZIP_NAME = "convenios_2008_2018.zip"
GO_MAPPINGS = {
    "CNPJ_PROPONENTE": "cnpj",
    "PROPONENTE": "nome_osc",
    "TITULO_CONVENIO": "objeto",
    "VALOR_TOTAL": "valor_total",
    "DATA_CELEBRACAO": "data",
    "NUMERO_CONVENIO": "id_unico",
    "NUM_PROCESSO": "observacoes",
}


class GOConveniosZipParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(
            ParserConfig(
                uf="GO",
                extra_mappings=GO_MAPPINGS,
            )
        )

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        if workbook_path.name != ZIP_NAME:
            return pd.DataFrame(columns=["uf", "origem", "ano", "valor_total", "cnpj", "nome_osc", "mes", "cod_municipio", "municipio", "objeto", "modalidade", "data_inicio", "data_fim"])

        frames: list[pd.DataFrame] = []
        with zipfile.ZipFile(workbook_path) as archive:
            for member in archive.namelist():
                if not member.lower().endswith(".csv"):
                    continue

                with archive.open(member) as handle:
                    raw = pd.read_csv(
                        io.BytesIO(handle.read()),
                        dtype=str,
                        encoding="utf-8",
                        on_bad_lines="skip",
                    )

                if preview_rows is not None:
                    raw = raw.head(preview_rows)

                standardized = self.standardize(raw, workbook_path, Path(member).stem)
                standardized["_numero_convenio"] = raw.get("NUMERO_CONVENIO", pd.Series(pd.NA, index=raw.index))
                standardized["_num_processo"] = raw.get("NUM_PROCESSO", pd.Series(pd.NA, index=raw.index))
                standardized["_status_convenio"] = raw.get("STATUS_CONVENIO", pd.Series(pd.NA, index=raw.index))
                standardized["_situacao_convenio"] = raw.get("SITUACAO_CONVENIO", pd.Series(pd.NA, index=raw.index))
                frames.append(standardized)

        if not frames:
            return pd.DataFrame(columns=["uf", "origem", "ano", "valor_total", "cnpj", "nome_osc", "mes", "cod_municipio", "municipio", "objeto", "modalidade", "data_inicio", "data_fim"])

        combined = pd.concat(frames, ignore_index=True)
        # Para GO, mantemos o foco no instrumento do proponente; o status textual entra como modalidade.
        combined["modalidade"] = combined["_status_convenio"].combine_first(combined["_situacao_convenio"])

        # Convênios alterados reaparecem em arquivos mensais. Mantemos um registro por processo + número.
        dedup_key = ["_num_processo", "_numero_convenio"]
        combined = combined.sort_values(
            by=["ano", "mes", "_status_convenio", "_situacao_convenio"],
            na_position="last",
            kind="stable",
        ).drop_duplicates(subset=dedup_key, keep="last")

        return combined[["uf", "origem", "ano", "valor_total", "cnpj", "nome_osc", "mes", "cod_municipio", "municipio", "objeto", "modalidade", "data_inicio", "data_fim"]]


PARSER = GOConveniosZipParser()
