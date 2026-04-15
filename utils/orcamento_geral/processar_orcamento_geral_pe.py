from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
OSC_NAME_PATTERN = re.compile(
    r"associ|instit|fundac|apae|benefic|filantrop|hospital|matern|"
    r"centro |casa |lar |oratorio|paroquia|igreja|irmandade|santa casa|"
    r"fundacao manoel|tricentenario|medianeiras|imip",
    flags=re.IGNORECASE,
)
PUBLIC_ENTITY_PATTERN = re.compile(
    r"municipio|prefeitura|fundo municipal|secretaria|governo|tribunal|"
    r"camara municipal|estado de pernambuco|universidade de pernambuco|universidade federal|"
    r"transferencias a prefeituras",
    flags=re.IGNORECASE,
)
TEXT_FOCUS_PATTERN = re.compile(
    r"conv..nio|subven..o|contrato de gest..o|organiz.*sociais|termo de fomento|termo de colabora",
    flags=re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a trilha de convenios/OSS do PE para parquet no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Diretorio com os arquivos pe_*.csv. Se omitido, usa o caminho padrao do escopo.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("PE", scope) / "convenios"


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return ""
    return " ".join(text.split())


def first_non_empty(*values: object) -> object:
    for value in values:
        text = clean_text(value)
        if text:
            return text
    return pd.NA


def iter_source_rows(path: Path) -> list[dict[str, object]]:
    year_match = re.search(r"(19|20)\d{2}", path.stem)
    year_text = year_match.group(0) if year_match else ""
    rows: list[dict[str, object]] = []

    with path.open("r", encoding="latin1", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        for row_index, row in enumerate(reader):
            if row_index < 3:
                continue
            if len(row) < 9:
                continue

            row = list(row[:11]) + [""] * max(0, 11 - len(row))
            orgao_convenente = clean_text(row[3])
            cnpj = re.sub(r"\D", "", clean_text(row[4]))
            referencia_legal = clean_text(row[2])
            justificativa = clean_text(row[6])
            tipo = clean_text(row[7])
            texto_contexto = " ".join(
                value for value in [orgao_convenente, referencia_legal, justificativa, tipo] if value
            )

            if len(cnpj) != 14:
                continue
            if PUBLIC_ENTITY_PATTERN.search(orgao_convenente):
                continue
            if not (OSC_NAME_PATTERN.search(orgao_convenente) or TEXT_FOCUS_PATTERN.search(texto_contexto)):
                continue

            rows.append(
                {
                    "uf": "PE",
                    "origem": ORIGEM_ORCAMENTO_GERAL,
                    "ano": year_text or pd.NA,
                    "valor_total": first_non_empty(row[8]),
                    "cnpj": cnpj,
                    "nome_osc": orgao_convenente,
                    "mes": pd.NA,
                    "cod_municipio": pd.NA,
                    "municipio": pd.NA,
                    "objeto": first_non_empty(justificativa, row[1]),
                    "modalidade": first_non_empty(tipo, referencia_legal),
                    "data_inicio": first_non_empty(row[9]),
                    "data_fim": pd.NA,
                }
            )

    return rows


def build_pe_budget_frame(input_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(input_dir.glob("pe_*.csv")):
        rows.extend(iter_source_rows(path))
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS).astype("string")
    for column in STANDARD_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    return frame[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir) if args.input_dir else default_input_dir(args.scope)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mapped = build_pe_budget_frame(input_dir)
    normalized = normalize_preview(mapped, "PE", require_cnpj=True)

    output_path = output_dir / default_output_name("PE", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_dir}")
    print(f"Saida: {output_path}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
