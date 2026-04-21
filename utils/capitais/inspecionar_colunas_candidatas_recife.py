from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
import sys
import unicodedata

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, HISTORIA_DIR, cli_default, ensure_parent_dir


BASE_DIR = Path(cli_default(BASES_CONVENIOS_CAPITAIS_DIR)) / "Recife"
OUTPUT_PATH = Path(cli_default(HISTORIA_DIR)) / "PE_recife_colunas_candidatas.md"
SAMPLE_ROWS = 5

TARGET_PATTERNS = {
    "ano": [r"^ano$", r"ano_movimentacao", r"empenho_ano"],
    "mes": [r"^mes$", r"mes_movimentacao"],
    "valor_total": [r"valor_pago", r"valor_liquidado", r"valor_empenhado", r"^pagamento$", r"^liquidacao$", r"^liquidado$", r"^pago$", r"^empenhado$"],
    "cnpj": [r"cpf_cnpj", r"credor_codigo", r"^cpf$", r"^cnpj$"],
    "nome_osc": [r"credor_nome", r"nome_do_credor", r"^credor$", r"orgao_nome"],
    "objeto": [r"acao_nome", r"descricao_da_acao", r"programa", r"subelemento_nome"],
    "modalidade": [r"modalidade", r"licitacao", r"grupo_despesa", r"elemento_nome", r"categoria"],
    "data_inicio": [r"data_do_empenho", r"dt_", r"data_de_pagamento", r"data_pagamento"],
    "data_fim": [],
}


def normalize_column(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    text = normalized.encode("ascii", "ignore").decode("ascii").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def guess_csv_format(path: Path) -> tuple[str, str]:
    encodings = ("utf-8-sig", "utf-8", "cp1252", "latin1")
    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding, errors="strict") as handle:
                header = handle.readline()
        except UnicodeDecodeError:
            continue
        delimiter_counts = {";": header.count(";"), ",": header.count(","), "\t": header.count("\t")}
        delimiter = max(delimiter_counts, key=delimiter_counts.get)
        return encoding, delimiter
    return "latin1", ";"


def read_csv_sample(path: Path) -> tuple[pd.DataFrame, str, str]:
    encoding, delimiter = guess_csv_format(path)
    frame = pd.read_csv(
        path,
        dtype=str,
        sep=delimiter,
        encoding=encoding,
        nrows=SAMPLE_ROWS,
        engine="python",
    )
    return frame, encoding, delimiter


def classify_columns(columns: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for column in columns:
        normalized = normalize_column(column)
        for target, patterns in TARGET_PATTERNS.items():
            if any(re.search(pattern, normalized) for pattern in patterns):
                grouped[target].append(column)
    return dict(grouped)


def sample_values(frame: pd.DataFrame, columns: list[str]) -> dict[str, list[str]]:
    samples: dict[str, list[str]] = {}
    for column in columns:
        if column not in frame.columns:
            continue
        values: list[str] = []
        for value in frame[column].dropna().astype(str):
            value = re.sub(r"\s+", " ", value).strip()
            if not value or value in values:
                continue
            values.append(value[:160])
            if len(values) >= 3:
                break
        samples[column] = values
    return samples


def format_items(items: list[str], fallback: str = "(nenhuma)") -> str:
    if not items:
        return fallback
    return ", ".join(items)


def render_section(path: Path) -> tuple[str, dict[str, list[str]]]:
    frame, encoding, delimiter = read_csv_sample(path)
    columns = list(frame.columns)
    grouped = classify_columns(columns)

    interesting_columns: list[str] = []
    for target_columns in grouped.values():
        for column in target_columns:
            if column not in interesting_columns:
                interesting_columns.append(column)

    samples = sample_values(frame, interesting_columns)

    lines = [
        f"## {path.name}",
        "",
        "- Tipo: CSV",
        f"- Encoding: `{encoding}`",
        f"- Separador: `{delimiter}`",
        f"- Total de colunas: {len(columns)}",
        "",
        "### Colunas candidatas por campo",
        "",
    ]

    for target in TARGET_PATTERNS:
        lines.append(f"- `{target}`: {format_items(grouped.get(target, []))}")

    lines.extend(["", "### Amostras das colunas candidatas", ""])
    if not samples:
        lines.append("- (nenhuma amostra relevante)")
    else:
        for column, values in samples.items():
            lines.append(f"- `{column}`: {format_items(values, '(sem valores)')}")

    lines.extend(["", "### Todas as colunas", "", f"`{'`, `'.join(columns)}`", ""])
    return "\n".join(lines), grouped


def build_summary(grouped_sections: list[dict[str, list[str]]]) -> str:
    merged: dict[str, list[str]] = defaultdict(list)
    for grouped in grouped_sections:
        for target, columns in grouped.items():
            for column in columns:
                if column not in merged[target]:
                    merged[target].append(column)

    lines = [
        "# Recife - Colunas Candidatas",
        "",
        f"Pasta analisada: `{BASE_DIR}`",
        "",
        "Resumo consolidado das colunas mais prováveis para mapear despesas do Recife.",
        "",
        "## Resumo Geral",
        "",
    ]
    for target in TARGET_PATTERNS:
        lines.append(f"- `{target}`: {format_items(merged.get(target, []))}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {BASE_DIR}")

    ensure_parent_dir(OUTPUT_PATH)

    files = sorted(path for path in BASE_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".csv" and "despesa" in path.name.lower())
    if not files:
        raise FileNotFoundError(f"Nenhum CSV de despesa encontrado em {BASE_DIR}")

    rendered_sections: list[str] = []
    grouped_sections: list[dict[str, list[str]]] = []

    for path in files:
        section, grouped = render_section(path)
        rendered_sections.append(section)
        grouped_sections.append(grouped)

    report = "\n".join([build_summary(grouped_sections)] + rendered_sections)
    OUTPUT_PATH.write_text(report, encoding="utf-8")

    print(f"Relatorio salvo em: {OUTPUT_PATH}")
    print(f"Arquivos analisados: {len(files)}")


if __name__ == "__main__":
    main()
