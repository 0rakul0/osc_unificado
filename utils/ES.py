from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import STANDARD_COLUMNS, WorkbookParser, build_parser


def empty_standard_df() -> pd.DataFrame:
    return pd.DataFrame(columns=STANDARD_COLUMNS)


class ESWorkbookParser(WorkbookParser):
    def __init__(self) -> None:
        super().__init__(build_parser("ES").config)
        self._reference_cache: dict[Path, pd.DataFrame] = {}

    @staticmethod
    def read_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
        return pd.read_csv(
            path,
            sep=";",
            dtype=str,
            encoding="utf-8",
            nrows=nrows,
            engine="python",
            on_bad_lines="skip",
        )

    def convenios_reference(self, base_dir: Path) -> pd.DataFrame:
        cache_key = base_dir.resolve()
        cached = self._reference_cache.get(cache_key)
        if cached is not None:
            return cached

        frames: list[pd.DataFrame] = []
        for csv_path in sorted(base_dir.glob("convenios-*.csv")):
            raw = self.read_csv(csv_path)
            if raw.empty:
                continue

            standardized = self.standardize(raw, csv_path, csv_path.stem)
            reference = standardized.assign(_cod=raw.get("cod", pd.Series(pd.NA, index=raw.index)))
            reference = reference[["_cod", "cnpj", "nome_osc", "cod_municipio", "municipio", "objeto"]]
            reference = reference.dropna(subset=["_cod"])
            if not reference.empty:
                frames.append(reference)

        if not frames:
            reference_df = pd.DataFrame(
                columns=["_cod", "cnpj", "nome_osc", "cod_municipio", "municipio", "objeto"]
            )
        else:
            reference_df = (
                pd.concat(frames, ignore_index=True)
                .drop_duplicates(subset=["_cod"], keep="first")
                .reset_index(drop=True)
            )

        self._reference_cache[cache_key] = reference_df
        return reference_df

    def parse_convenios_csv(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        raw = self.read_csv(workbook_path, nrows=preview_rows)
        if raw.empty:
            return empty_standard_df()

        standardized = self.standardize(raw, workbook_path, workbook_path.stem)
        modalidade = raw.get("nomeTipoTransferencia", pd.Series(pd.NA, index=raw.index))
        standardized["modalidade"] = standardized["modalidade"].combine_first(modalidade)
        return standardized.drop_duplicates(subset=STANDARD_COLUMNS, keep="first").reset_index(drop=True)

    def parse_aditivos_csv(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        raw = self.read_csv(workbook_path, nrows=preview_rows)
        if raw.empty:
            return empty_standard_df()

        standardized = self.standardize(raw, workbook_path, workbook_path.stem)

        reference = self.convenios_reference(workbook_path.parent)
        if not reference.empty:
            join = reference.rename(columns={"_cod": "codConvenioRef"})
            enriched = pd.concat(
                [
                    standardized.reset_index(drop=True),
                    raw.get("codConvenio", pd.Series(pd.NA, index=raw.index)).reset_index(drop=True).rename("codConvenioRef"),
                ],
                axis=1,
            )
            enriched = enriched.merge(join, how="left", on="codConvenioRef", suffixes=("", "_ref"))
            for field in ["cnpj", "nome_osc", "cod_municipio", "municipio"]:
                enriched[field] = enriched[field].combine_first(enriched[f"{field}_ref"])

            objeto_base = enriched["objeto_ref"].fillna("")
            observacao = raw.get("observacao", pd.Series(pd.NA, index=raw.index)).fillna("")
            combined_obj = observacao.where(observacao.str.strip().ne(""), objeto_base)
            combined_obj = combined_obj.where(
                ~(observacao.str.strip().ne("") & objeto_base.str.strip().ne("")),
                objeto_base.str.strip() + " | Aditivo: " + observacao.str.strip(),
            )
            enriched["objeto"] = enriched["objeto"].combine_first(combined_obj)
            enriched["modalidade"] = "Aditivo de convenio"
            standardized = enriched[STANDARD_COLUMNS]
        else:
            standardized["modalidade"] = "Aditivo de convenio"

        return standardized.drop_duplicates(subset=STANDARD_COLUMNS, keep="first").reset_index(drop=True)

    def parse_execucao_csv(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        raw = self.read_csv(workbook_path, nrows=preview_rows)
        if raw.empty or list(raw.columns) == ["Unnamed: 0"]:
            return empty_standard_df()

        working = raw.copy()
        working["uf"] = "ES"
        working["ano"] = working.get("Ano")
        # `valor_total` deve refletir apenas o valor bruto escolhido da fonte.
        # O enriquecimento nao pode completar nem recalcular esse campo.
        working["valor_total"] = working.get("ValorPago")
        working["cnpj"] = working.get("CpfCnpjNis")
        working["nome_osc"] = working.get("Favorecido")
        working["objeto"] = (
            working.get("HistoricoDocumento")
            .combine_first(working.get("ProcessoAssunto"))
            .combine_first(working.get("Acao"))
        )
        working["modalidade"] = working.get("Modalidade").combine_first(working.get("TipoLicitacao"))
        working["data_inicio"] = pd.NA
        working["data_fim"] = pd.NA
        working["data"] = working.get("DataPagamento")
        working["mes"] = pd.NA
        working["cod_municipio"] = pd.NA
        working["municipio"] = pd.NA

        standardized = self.standardize(working, workbook_path, workbook_path.stem)

        reference = self.convenios_reference(workbook_path.parent)
        if not reference.empty:
            join = reference.rename(columns={"_cod": "CodigoConvenioConcedidoRef"})
            enriched = pd.concat(
                [
                    standardized.reset_index(drop=True),
                    raw.get("CodigoConvenioConcedido", pd.Series(pd.NA, index=raw.index))
                    .reset_index(drop=True)
                    .rename("CodigoConvenioConcedidoRef"),
                ],
                axis=1,
            )
            enriched = enriched.merge(join, how="left", on="CodigoConvenioConcedidoRef", suffixes=("", "_ref"))
            for field in ["cnpj", "nome_osc", "cod_municipio", "municipio"]:
                enriched[field] = enriched[field].combine_first(enriched[f"{field}_ref"])
            standardized = enriched[STANDARD_COLUMNS]

        return standardized.drop_duplicates(subset=STANDARD_COLUMNS, keep="first").reset_index(drop=True)

    def parse_workbook(self, workbook_path: Path, preview_rows: int | None = None) -> pd.DataFrame:
        suffix = workbook_path.suffix.lower()
        if suffix != ".csv":
            return super().parse_workbook(workbook_path, preview_rows=preview_rows)

        name = workbook_path.name.lower()
        if name.startswith("convenios-"):
            return self.parse_convenios_csv(workbook_path, preview_rows=preview_rows)
        if name.startswith("aditivosconvenios-"):
            return self.parse_aditivos_csv(workbook_path, preview_rows=preview_rows)
        if name.startswith("conveniosexecucaoorcamentaria-"):
            return self.parse_execucao_csv(workbook_path, preview_rows=preview_rows)
        return empty_standard_df()


PARSER = ESWorkbookParser()
