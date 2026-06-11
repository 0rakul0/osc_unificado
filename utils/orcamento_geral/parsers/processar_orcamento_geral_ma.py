from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "ESTADO_ORCAMENTO_GERAL"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a trilha de despesas do MA com foco em convenios/subvencoes para parquet."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="CSV consolidado do MA. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("MA", scope) / "DESPESA_2026_01.csv"


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("MA", scope)


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=";",
        dtype=str,
        encoding="utf-8",
        low_memory=False,
        on_bad_lines="skip",
    )


def read_sources(input_dir: Path, explicit_input: Path | None = None) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    csv_paths = [explicit_input] if explicit_input else sorted(input_dir.glob("DESPESA_*.csv"))
    for path in csv_paths:
        if path and path.exists():
            frames.append(read_source(path))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = clean_text(current)
        result = cleaned if result is None else result.combine_first(cleaned)
    if result is None:
        return pd.Series(dtype="string")
    return result


def money_to_number(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = re.sub(r"[^\d,.-]", "", text)
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    return text


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("credor_nome")).fillna("")
    codigo = clean_text(source_df.get("codigo_credor")).fillna("").str.replace(r"\D", "", regex=True)
    natureza = clean_text(source_df.get("nome_natureza")).fillna("")
    descricao = clean_text(source_df.get("descricao")).fillna("")

    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|hospital|casa",
        case=False,
        regex=True,
        na=False,
    )
    natureza_terceiro_setor = natureza.str.contains(
        r"subven..es .* sem fins lucrativos|subven",
        case=False,
        regex=True,
        na=False,
    )
    descricao_convenio = descricao.str.contains(
        r"conv..nio|termo de colabora|termo de parceria|fomento|edital de chamamento|repasse",
        case=False,
        regex=True,
        na=False,
    )
    return nome_osc & (natureza_terceiro_setor | descricao_convenio) & codigo.str.len().eq(14)


def build_legacy_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("credor_nome")).fillna("")
    codigo = clean_text(source_df.get("codigo_credor")).fillna("").str.replace(r"\D", "", regex=True)
    nome_osc = nome.str.contains(
        r"associ|institu|fundac|apae|sociedade|benefic|filantrop|santa casa|comunit|cultural",
        case=False,
        regex=True,
        na=False,
    )
    publico = nome.str.contains(
        r"outros poderes|municipio|prefeitura|secretaria|governo|tribunal|assembleia|"
        r"fundo estadual|fundo municipal|policia|bombeiro|procuradoria|defensoria|"
        r"universidade estadual|departamento estadual|autarquia|servidor|previdencia",
        case=False,
        regex=True,
        na=False,
    )
    return nome_osc & ~publico & codigo.str.len().eq(14)


def build_ma_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()

    mapped = pd.DataFrame(
        {
            "uf": "MA",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get("ano"),
            "valor_total": filtered.get("valor"),
            "cnpj": filtered.get("codigo_credor"),
            "nome_osc": filtered.get("credor_nome"),
            "mes": filtered.get("mes"),
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("descricao"),
            "modalidade": first_non_empty(filtered.get("nome_natureza"), filtered.get("tipo_licitacao")),
            "data_inicio": filtered.get("data_documento"),
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def read_legacy_sources(input_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(input_dir.glob("ma_fornecedores_legacy_20[0-9][0-9].json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            rows.extend(row for row in payload if isinstance(row, dict))
    return pd.DataFrame(rows)


def build_ma_legacy_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    if source_df.empty:
        return pd.DataFrame(columns=STANDARD_COLUMNS)
    filtered = source_df.loc[build_legacy_focus_mask(source_df)].copy()
    mapped = pd.DataFrame(
        {
            "uf": "MA",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get("ano"),
            "valor_total": filtered.get("valor_pago").map(money_to_number),
            "cnpj": filtered.get("codigo_credor"),
            "nome_osc": filtered.get("credor_nome"),
            "mes": pd.NA,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("detalhe_url"),
            "modalidade": "despesa por fornecedor - portal legado",
            "data_inicio": pd.NA,
            "data_fim": pd.NA,
        }
    )
    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_dir = default_input_dir(args.scope)
    input_path = Path(args.input) if args.input else None
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df = read_sources(input_dir, input_path)
    frames = []
    if not source_df.empty:
        frames.append(build_ma_budget_frame(source_df))
    legacy_df = read_legacy_sources(input_dir)
    if not legacy_df.empty:
        frames.append(build_ma_legacy_budget_frame(legacy_df))
    mapped = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=STANDARD_COLUMNS)
    normalized = normalize_preview(mapped, "MA", require_cnpj=True)
    normalized = normalized.drop_duplicates(subset=["ano", "cnpj", "nome_osc", "valor_total", "objeto"])

    output_path = output_dir / default_output_name("MA", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path or input_dir}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas legado: {len(legacy_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
