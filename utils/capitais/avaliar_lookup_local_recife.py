from __future__ import annotations

from pathlib import Path
import re
import sys
import unicodedata

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, HISTORIA_DATA_DIR, cli_default, ensure_parent_dir


BASE_DIR = Path(cli_default(BASES_CONVENIOS_CAPITAIS_DIR)) / "Recife"
OUTPUT_DIR = Path(cli_default(HISTORIA_DATA_DIR)) / "recife_lookup_local"
LOOKUP_OUTPUT = OUTPUT_DIR / "recife_lookup_nome_para_cnpj.csv"
MATCHED_OUTPUT = OUTPUT_DIR / "recife_historico_com_lookup.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "recife_lookup_resumo.md"

RECENT_FILES = [
    "recife_despesa-por-credor-empenho-2024.csv",
    "recife_despesa-por-credor-empenho-2025.csv",
]
HISTORICAL_GLOB = "recife_despesas-orcamentarias-*.csv"


def normalize_text(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = unicodedata.normalize("NFKD", str(value).strip().upper())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_document(value: object) -> str | None:
    if pd.isna(value):
        return None
    digits = re.sub(r"\D+", "", str(value))
    if len(digits) not in {11, 14}:
        return None
    return digits


def load_recent_lookup(base_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    for filename in RECENT_FILES:
        path = base_dir / filename
        if not path.exists():
            continue
        frame = pd.read_csv(
            path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
            usecols=["CPF/CNPJ", "Nome do Credor"],
        ).rename(columns={"CPF/CNPJ": "documento", "Nome do Credor": "nome_credor"})
        frame["arquivo_origem"] = filename
        frames.append(frame)

    if not frames:
        raise FileNotFoundError("Nenhum arquivo recente de despesa por credor foi encontrado para Recife.")

    recent = pd.concat(frames, ignore_index=True)
    recent["nome_key"] = recent["nome_credor"].map(normalize_text)
    recent["documento_key"] = recent["documento"].map(normalize_document)
    recent = recent.dropna(subset=["nome_key", "documento_key"]).copy()

    grouped = (
        recent.groupby("nome_key", dropna=False)
        .agg(
            nome_credor=("nome_credor", "first"),
            documentos_unicos=("documento_key", lambda values: sorted(set(values))),
            ocorrencias=("nome_key", "size"),
        )
        .reset_index()
    )
    grouped["qtd_documentos_unicos"] = grouped["documentos_unicos"].map(len)
    grouped["documento_key"] = grouped["documentos_unicos"].map(lambda values: values[0] if len(values) == 1 else None)
    grouped["match_unico"] = grouped["qtd_documentos_unicos"].eq(1)

    unique_lookup = grouped.loc[grouped["match_unico"], ["nome_key", "nome_credor", "documento_key", "ocorrencias"]].copy()
    unique_lookup = unique_lookup.rename(columns={"documento_key": "cpf_cnpj"})
    unique_lookup = unique_lookup.sort_values(["nome_credor"]).reset_index(drop=True)
    return recent, unique_lookup


def load_historical(base_dir: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(base_dir.glob(HISTORICAL_GLOB)):
        frame = pd.read_csv(
            path,
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
            usecols=["ano_movimentacao", "mes_movimentacao", "credor_codigo", "credor_nome", "valor_empenhado", "valor_liquidado", "valor_pago"],
        )
        frame["arquivo_origem"] = path.name
        frames.append(frame)

    if not frames:
        raise FileNotFoundError("Nenhum arquivo historico de despesas orcamentarias foi encontrado para Recife.")

    historical = pd.concat(frames, ignore_index=True)
    historical["nome_key"] = historical["credor_nome"].map(normalize_text)
    historical = historical.dropna(subset=["nome_key"]).copy()
    return historical


def build_summary(recent: pd.DataFrame, unique_lookup: pd.DataFrame, historical: pd.DataFrame, matched: pd.DataFrame) -> str:
    matched_rows = len(matched)
    historical_rows = len(historical)
    matched_unique_names = matched["nome_key"].nunique()
    historical_unique_names = historical["nome_key"].nunique()

    lines = [
        "# Recife - Lookup Local Nome para CNPJ",
        "",
        f"Pasta analisada: `{BASE_DIR}`",
        "",
        "Resumo do lookup local construído a partir dos arquivos `despesa-por-credor-empenho` de 2024 e 2025 para enriquecer a série histórica `despesas-orcamentarias`.",
        "",
        "## Cobertura",
        "",
        f"- Linhas recentes usadas no lookup: {len(recent):,}".replace(",", "."),
        f"- Nomes recentes com documento único: {len(unique_lookup):,}".replace(",", "."),
        f"- Linhas históricas avaliadas: {historical_rows:,}".replace(",", "."),
        f"- Linhas históricas com match via lookup: {matched_rows:,}".replace(",", "."),
        f"- Cobertura por linhas: {matched_rows / historical_rows * 100:.2f}%",
        f"- Nomes históricos únicos: {historical_unique_names:,}".replace(",", "."),
        f"- Nomes históricos únicos com match: {matched_unique_names:,}".replace(",", "."),
        f"- Cobertura por nomes únicos: {matched_unique_names / historical_unique_names * 100:.2f}%",
        "",
        "## Saídas geradas",
        "",
        f"- Lookup consolidado: `{LOOKUP_OUTPUT}`",
        f"- Série histórica com match local: `{MATCHED_OUTPUT}`",
        "",
        "## Leitura prática",
        "",
        "- Este lookup é parcial e local: ele usa apenas os arquivos de 2024 e 2025 com `CPF/CNPJ` explícito.",
        "- Ele é mais forte para credores recorrentes que aparecem também na série histórica.",
        "- Os nomes sem match ainda podem ser tentados depois por base federal, convênios locais ou heurística adicional.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {BASE_DIR}")

    ensure_parent_dir(LOOKUP_OUTPUT)

    recent, unique_lookup = load_recent_lookup(BASE_DIR)
    historical = load_historical(BASE_DIR)
    matched = historical.merge(unique_lookup[["nome_key", "cpf_cnpj", "nome_credor"]], on="nome_key", how="inner")

    unique_lookup.to_csv(LOOKUP_OUTPUT, index=False, encoding="utf-8-sig")
    matched.to_csv(MATCHED_OUTPUT, index=False, encoding="utf-8-sig")
    SUMMARY_OUTPUT.write_text(build_summary(recent, unique_lookup, historical, matched), encoding="utf-8")

    print(f"Lookup salvo em: {LOOKUP_OUTPUT}")
    print(f"Historico com match salvo em: {MATCHED_OUTPUT}")
    print(f"Resumo salvo em: {SUMMARY_OUTPUT}")
    print(f"Linhas historicas com match: {len(matched)}")


if __name__ == "__main__":
    main()
