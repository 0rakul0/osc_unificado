from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import csv
import html
import re
import sys
import unicodedata

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, HISTORIA_DIR, cli_default, ensure_parent_dir


BASE_DIR = Path(cli_default(BASES_CONVENIOS_CAPITAIS_DIR)) / "Belo Horizonte"
OUTPUT_PATH = Path(cli_default(HISTORIA_DIR)) / "MG_belo_horizonte_colunas_candidatas.md"
SAMPLE_ROWS = 5

TARGET_PATTERNS = {
    "ano": [r"^ano_ij$", r"^ano_empenho$", r"^ano_liquidacao$", r"^ano_op$"],
    "valor_total": [r"^valor_ij$", r"^valor_bruto_op$", r"^vl_npd$", r"^vl_empenhado$", r"^vl_anul_npd$"],
    "cnpj": [r"^numero_documento$", r"^cnpj$", r"^cpf_cnpj$", r"^cpf$", r"^documento$"],
    "nome_osc": [r"^fornecedor$", r"^nome_credor$", r"^nome_organizacao$", r"^organizacao$"],
    "objeto": [r"^objeto$", r"^justificativa_sucinta$", r"^historico$"],
    "modalidade": [r"^natureza$", r"^tipo_contrato$", r"^situao$", r"^situacao$", r"^instrumento_juridico$", r"^modalidade_licitacao$", r"^natureza_despesa$", r"^nome_natureza_despesa$"],
    "data_inicio": [r"^data_inicio_vigencia$", r"^data_publicacao$", r"^dt_lancamento$", r"^data_liquidacao$", r"^data_op$"],
    "data_fim": [r"^data_fim_vigencia$"],
}


def ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    text = normalized.encode("ascii", "ignore").decode("ascii")
    return text.lower().strip()


def normalize_column(value: str) -> str:
    text = ascii_slug(value)
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
        delimiter_counts = {
            ";": header.count(";"),
            ",": header.count(","),
            "\t": header.count("\t"),
        }
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
    unnamed_count = sum(str(column).startswith("Unnamed:") for column in frame.columns)
    if unnamed_count >= max(3, len(frame.columns) // 2):
        frame = pd.read_csv(
            path,
            dtype=str,
            sep=delimiter,
            encoding=encoding,
            skiprows=1,
            nrows=SAMPLE_ROWS,
            engine="python",
        )
    return frame, encoding, delimiter


def extract_html_headers(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    headers = re.findall(r"<th[^>]*>(.*?)</th>", text, flags=re.IGNORECASE | re.DOTALL)
    cleaned: list[str] = []
    for header_text in headers:
        raw = re.sub(r"<[^>]+>", " ", header_text)
        raw = html.unescape(raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        if raw and raw not in cleaned:
            cleaned.append(raw)
    return cleaned


def classify_columns(columns: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for column in columns:
        normalized = normalize_column(column)
        for target, patterns in TARGET_PATTERNS.items():
            if any(re.search(pattern, normalized) for pattern in patterns):
                grouped[target].append(column)
    return dict(grouped)


def sample_values(frame: pd.DataFrame, columns: list[str]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for column in columns:
        if column not in frame.columns:
            continue
        samples = []
        for value in frame[column].dropna().astype(str):
            value = re.sub(r"\s+", " ", value).strip()
            if not value or value in samples:
                continue
            samples.append(value[:160])
            if len(samples) >= 3:
                break
        values[column] = samples
    return values


def format_bullets(items: list[str], fallback: str = "(nenhuma)") -> str:
    if not items:
        return fallback
    return ", ".join(items)


def build_csv_section(path: Path) -> str:
    frame, encoding, delimiter = read_csv_sample(path)
    columns = list(frame.columns)
    grouped = classify_columns(columns)
    interesting_columns = []
    for target_columns in grouped.values():
        for column in target_columns:
            if column not in interesting_columns:
                interesting_columns.append(column)
    samples = sample_values(frame, interesting_columns)

    lines = [
        f"## {path.name}",
        "",
        f"- Tipo: CSV",
        f"- Encoding: `{encoding}`",
        f"- Separador: `{delimiter}`",
        f"- Total de colunas: {len(columns)}",
        "",
        "### Colunas candidatas por campo",
        "",
    ]
    for target in TARGET_PATTERNS:
        lines.append(f"- `{target}`: {format_bullets(grouped.get(target, []))}")

    lines.extend(
        [
            "",
            "### Amostras das colunas candidatas",
            "",
        ]
    )
    if not samples:
        lines.append("- (nenhuma amostra relevante)")
    else:
        for column, values in samples.items():
            lines.append(f"- `{column}`: {format_bullets(values, '(sem valores)')}")

    lines.extend(
        [
            "",
            "### Todas as colunas",
            "",
            f"`{'`, `'.join(columns)}`",
            "",
        ]
    )
    return "\n".join(lines)


def build_html_section(path: Path) -> str:
    headers = extract_html_headers(path)
    grouped = classify_columns(headers)
    lines = [
        f"## {path.name}",
        "",
        "- Tipo: HTML",
        f"- Total de cabecalhos `<th>` identificados: {len(headers)}",
        "",
        "### Colunas candidatas por campo",
        "",
    ]
    for target in TARGET_PATTERNS:
        lines.append(f"- `{target}`: {format_bullets(grouped.get(target, []))}")

    lines.extend(
        [
            "",
            "### Cabecalhos identificados",
            "",
            f"`{'`, `'.join(headers)}`" if headers else "(nenhum cabecalho reconhecido)",
            "",
        ]
    )
    return "\n".join(lines)


def build_summary(sections: list[tuple[str, dict[str, list[str]]]]) -> str:
    merged: dict[str, list[str]] = defaultdict(list)
    for _, grouped in sections:
        for target, columns in grouped.items():
            for column in columns:
                item = column
                if item not in merged[target]:
                    merged[target].append(item)

    lines = [
        "# Belo Horizonte - Colunas Candidatas",
        "",
        f"Pasta analisada: `{BASE_DIR}`",
        "",
        "Resumo consolidado das colunas que parecem candidatas ao schema do projeto.",
        "",
        "## Resumo Geral",
        "",
    ]
    for target in TARGET_PATTERNS:
        lines.append(f"- `{target}`: {format_bullets(merged.get(target, []))}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Pasta nao encontrada: {BASE_DIR}")

    ensure_parent_dir(OUTPUT_PATH)

    files = sorted(path for path in BASE_DIR.iterdir() if path.is_file() and path.suffix.lower() in {".csv", ".html"})
    if not files:
        raise FileNotFoundError(f"Nenhum CSV/HTML encontrado em {BASE_DIR}")

    rendered_sections: list[str] = []
    grouped_sections: list[tuple[str, dict[str, list[str]]]] = []

    for path in files:
        if path.suffix.lower() == ".csv":
            frame, _, _ = read_csv_sample(path)
            grouped = classify_columns(list(frame.columns))
            grouped_sections.append((path.name, grouped))
            rendered_sections.append(build_csv_section(path))
        else:
            headers = extract_html_headers(path)
            grouped = classify_columns(headers)
            grouped_sections.append((path.name, grouped))
            rendered_sections.append(build_html_section(path))

    report = "\n".join([build_summary(grouped_sections)] + rendered_sections)
    OUTPUT_PATH.write_text(report, encoding="utf-8")

    print(f"Relatorio salvo em: {OUTPUT_PATH}")
    print(f"Arquivos analisados: {len(files)}")


if __name__ == "__main__":
    main()
