from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE


BASE_DIR = Path(r"D:\github\osc_unificado\bases_convenios\PR")
OUTPUT_CSV = BASE_DIR / "convenios_relacional_consolidado.csv"
OUTPUT_XLSX = BASE_DIR / "convenios_relacional_consolidado.xlsx"


def read_csv_with_fallback(path: Path) -> pd.DataFrame:
    encodings = ("utf-8", "utf-8-sig", "latin1")
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(path, sep=";", dtype=str, encoding=encoding)
        except Exception as exc:  # pragma: no cover - defensive fallback
            last_error = exc
    raise RuntimeError(f"Falha ao ler {path}") from last_error


def normalize_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.upper()


def sanitize_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        if pd.api.types.is_object_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].map(
                lambda value: ILLEGAL_CHARACTERS_RE.sub("", value)
                if isinstance(value, str)
                else value
            )
    return cleaned


def build_consolidated_dataframe() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    year_dirs = sorted(
        p for p in BASE_DIR.iterdir() if p.is_dir() and p.name.startswith("CONVENIOS-")
    )

    for year_dir in year_dirs:
        year = year_dir.name.split("-")[-1]
        empreendimento_path = year_dir / f"TB_CONVENIO_EMPREENDIMENTO-{year}.csv"
        entidade_path = year_dir / f"TB_CONVENIO_ENTIDADE-{year}.csv"

        empreendimento = read_csv_with_fallback(empreendimento_path)
        entidade = read_csv_with_fallback(entidade_path).rename(
            columns={"nome": "entidade_nome", "cnpj": "entidade_cnpj"}
        )

        merged = empreendimento.merge(
            entidade,
            on="convenio_entidade_cod",
            how="left",
        )
        merged["ano_fonte"] = int(year)

        concedente_norm = normalize_text(merged["concedente"])
        tomador_norm = normalize_text(merged["tomador"])
        entidade_norm = normalize_text(merged["entidade_nome"])

        merged["entidade_eh_concedente"] = entidade_norm.eq(concedente_norm)
        merged["entidade_eh_tomador"] = entidade_norm.eq(tomador_norm)

        frames.append(merged)

    consolidated = pd.concat(frames, ignore_index=True)

    preferred_order = [
        "ano_fonte",
        "convenio_empreendimento_cod",
        "convenio_entidade_cod",
        "numero",
        "atividade",
        "situacao",
        "concedente",
        "entidade_nome",
        "entidade_cnpj",
        "tomador",
        "objeto",
        "dt_celebracao",
        "dt_publicacao",
        "dt_vigencia_inicio",
        "dt_vigencia_fim",
        "ibge",
        "qtd_unidade",
        "unidade",
        "total_repasses",
        "total_repassado",
        "total_repassado_1",
        "total_contra_partida",
        "total_contra_partida_depositada",
        "info_adicional",
        "representante_legal_concedente",
        "representante_legal_tomador",
        "entidade_eh_concedente",
        "entidade_eh_tomador",
    ]
    remaining_cols = [col for col in consolidated.columns if col not in preferred_order]
    return consolidated[preferred_order + remaining_cols]


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("ano_fonte", dropna=False)
        .agg(
            registros=("convenio_empreendimento_cod", "size"),
            entidades_distintas=("convenio_entidade_cod", "nunique"),
            concedentes_distintos=("concedente", "nunique"),
            tomadores_distintos=("tomador", "nunique"),
            entidade_nome_eq_concedente=("entidade_eh_concedente", "sum"),
            entidade_nome_eq_tomador=("entidade_eh_tomador", "sum"),
        )
        .reset_index()
        .sort_values("ano_fonte")
    )

    summary["pct_entidade_eq_concedente"] = (
        summary["entidade_nome_eq_concedente"] / summary["registros"] * 100
    ).round(2)
    summary["pct_entidade_eq_tomador"] = (
        summary["entidade_nome_eq_tomador"] / summary["registros"] * 100
    ).round(2)
    return summary


def build_dictionary() -> pd.DataFrame:
    rows = [
        (
            "ano_fonte",
            "Ano da pasta CONVENIOS-YYYY de onde a linha foi lida.",
        ),
        (
            "convenio_empreendimento_cod",
            "Chave principal do empreendimento/convênio no arquivo de empreendimento.",
        ),
        (
            "convenio_entidade_cod",
            "Chave usada para juntar empreendimento com a tabela de entidade.",
        ),
        (
            "concedente",
            "Órgão concedente informado no empreendimento.",
        ),
        (
            "entidade_nome",
            "Nome vindo da tabela TB_CONVENIO_ENTIDADE.",
        ),
        (
            "entidade_cnpj",
            "CNPJ vindo da tabela TB_CONVENIO_ENTIDADE.",
        ),
        (
            "tomador",
            "Beneficiário/tomador informado no empreendimento.",
        ),
        (
            "entidade_eh_concedente",
            "True quando entidade_nome é igual ao concedente.",
        ),
        (
            "entidade_eh_tomador",
            "True quando entidade_nome é igual ao tomador.",
        ),
        (
            "total_repasses",
            "Valor de repasses no empreendimento.",
        ),
    ]
    return pd.DataFrame(rows, columns=["coluna", "descricao"])


def build_notes(summary: pd.DataFrame) -> pd.DataFrame:
    total_rows = int(summary["registros"].sum())
    total_eq_concedente = int(summary["entidade_nome_eq_concedente"].sum())
    total_eq_tomador = int(summary["entidade_nome_eq_tomador"].sum())

    notes = [
        (
            "Leitura principal",
            "A tabela ENTIDADE representa o concedente no material bruto do PR, não o tomador.",
        ),
        (
            "Evidência",
            f"{total_eq_concedente:,} de {total_rows:,} linhas ({(total_eq_concedente / total_rows) * 100:.2f}%) têm entidade_nome igual ao concedente.",
        ),
        (
            "Contraprova",
            f"{total_eq_tomador:,} de {total_rows:,} linhas ({(total_eq_tomador / total_rows) * 100:.2f}%) têm entidade_nome igual ao tomador.",
        ),
        (
            "Implicação analítica",
            "Se nome_osc/cnpj forem preenchidos a partir da tabela ENTIDADE, o parquet do PR identifica o concedente como se fosse o beneficiário.",
        ),
    ]
    return pd.DataFrame(notes, columns=["topico", "nota"])


def main() -> None:
    consolidated = build_consolidated_dataframe()
    summary = build_summary(consolidated)
    dictionary = build_dictionary()
    notes = build_notes(summary)

    consolidated.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        sanitize_for_excel(consolidated).to_excel(
            writer, sheet_name="consolidado", index=False
        )
        sanitize_for_excel(summary).to_excel(writer, sheet_name="resumo_anual", index=False)
        sanitize_for_excel(notes).to_excel(writer, sheet_name="notas", index=False)
        sanitize_for_excel(dictionary).to_excel(
            writer, sheet_name="dicionario", index=False
        )

    print(f"CSV gerado em: {OUTPUT_CSV}")
    print(f"XLSX gerado em: {OUTPUT_XLSX}")
    print(f"Linhas consolidadas: {len(consolidated):,}")
    print(
        "Percentual entidade==concedente:",
        f"{(consolidated['entidade_eh_concedente'].mean() * 100):.2f}%",
    )
    print(
        "Percentual entidade==tomador:",
        f"{(consolidated['entidade_eh_tomador'].mean() * 100):.2f}%",
    )


if __name__ == "__main__":
    main()
