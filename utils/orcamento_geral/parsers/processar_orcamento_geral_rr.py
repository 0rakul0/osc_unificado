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

from project_paths import BASES_CONVENIOS_DIR, ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
OSC_NAME_PATTERN = re.compile(
    r"associ|instit|fundac|apae|sociedade|centro |casa |lar |federa|movimento|igreja|paroquia|autista|caritas|comunit",
    re.IGNORECASE,
)
PRIVATE_COMPANY_PATTERN = re.compile(
    r"ltda|eireli|s\.a| s/a|me\b|epp\b|comerc|construt|banco|farmacia|laborat|distrib|engenharia|clinica|servic",
    re.IGNORECASE,
)
TEXT_FOCUS_PATTERN = re.compile(
    r"conv..nio|fomento|colabora|repasse|projeto|termo",
    re.IGNORECASE,
)
LEGACY_OSC_PATTERN = re.compile(
    r"associ|instit|fundac|sociedade|servico de apoio|obra social|museu|federa|caritas|apae",
    re.IGNORECASE,
)
LEGACY_PUBLIC_PATTERN = re.compile(
    r"estado de roraima|secretaria|prefeitura|municipio|tribunal|camara|universidade|procuradoria|minist|funda[cç][aã]o estadual",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a despesa detalhada de RR com foco em sinais de OSC."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input",
        help="JSON bruto de RR. Se omitido, usa o caminho padrao do escopo.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_path(scope: str) -> Path:
    return uf_raw_dir("RR", scope) / "rr_despesa_detalhada.json"


def default_legacy_input_path() -> Path:
    return BASES_CONVENIOS_DIR / "RR" / "dados_convenios_receita.xlsx"


def read_json_source(path: Path) -> pd.DataFrame:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"JSON inesperado em {path}")
    return pd.DataFrame(rows)


def read_legacy_source(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name="Convênios")


def read_source(path: Path) -> tuple[pd.DataFrame, str]:
    if path.suffix.lower() == ".json":
        return read_json_source(path), "json"
    return read_legacy_source(path), "legacy_xlsx"


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


def collapse_exec_history(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")

    def normalize(value: object) -> object:
        if not isinstance(value, list):
            return pd.NA
        historicos = []
        for item in value:
            if not isinstance(item, dict):
                continue
            historico = str(item.get("historico") or "").strip()
            if historico:
                historicos.append(" ".join(historico.split()))
        if not historicos:
            return pd.NA
        return " | ".join(historicos)

    return series.map(normalize).astype("string")


def build_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("razaoSocial")).fillna("")
    texto = first_non_empty(clean_text(source_df.get("historicoPed")), collapse_exec_history(source_df.get("despesaPorCredorExecucao"))).fillna("")

    nome_osc = nome.str.contains(OSC_NAME_PATTERN, na=False)
    empresa_privada = nome.str.contains(PRIVATE_COMPANY_PATTERN, na=False)
    texto_foco = texto.str.contains(TEXT_FOCUS_PATTERN, na=False)

    return nome_osc & ~empresa_privada & texto_foco


def build_rr_budget_frame(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_focus_mask(source_df)].copy()
    historico = first_non_empty(clean_text(filtered.get("historicoPed")), collapse_exec_history(filtered.get("despesaPorCredorExecucao")))

    mapped = pd.DataFrame(
        {
            "uf": "RR",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get("exercicio"),
            "valor_total": first_non_empty(filtered.get("totalPago"), filtered.get("totalLiquidado"), filtered.get("valorEmpenho")),
            "cnpj": filtered.get("cpfCnpj"),
            "nome_osc": filtered.get("razaoSocial"),
            "mes": pd.NA,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": historico,
            "modalidade": first_non_empty(filtered.get("fonteRecurso"), filtered.get("naturezaDespesa")),
            "data_inicio": filtered.get("dataEmpenho"),
            "data_fim": pd.NA,
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def build_legacy_focus_mask(source_df: pd.DataFrame) -> pd.Series:
    nome = clean_text(source_df.get("Nome Proponente")).fillna("")
    modalidade = clean_text(source_df.get("Modalidade")).fillna("")
    executora = clean_text(source_df.get("Executora")).fillna("")
    return (
        (executora.str.upper().eq("OSC") | nome.str.contains(LEGACY_OSC_PATTERN, na=False))
        & ~nome.str.contains(LEGACY_PUBLIC_PATTERN, na=False)
        & modalidade.str.contains(r"CONVENIO|FOMENTO|PARCERIA", case=False, na=False)
    )


def build_rr_budget_frame_legacy(source_df: pd.DataFrame) -> pd.DataFrame:
    filtered = source_df.loc[build_legacy_focus_mask(source_df)].copy()
    mapped = pd.DataFrame(
        {
            "uf": "RR",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": filtered.get("Ano Assinatura"),
            "valor_total": first_non_empty(filtered.get("Valor Global"), filtered.get("Valor Repasse")),
            "cnpj": pd.NA,
            "nome_osc": filtered.get("Nome Proponente"),
            "mes": pd.NA,
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": filtered.get("Objeto"),
            "modalidade": filtered.get("Modalidade"),
            "data_inicio": filtered.get("Data Início de Vigência Conv."),
            "data_fim": filtered.get("Data Fim de Vigência Conv."),
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input) if args.input else default_input_path(args.scope)
    if not input_path.exists() or (input_path.suffix.lower() == ".json" and input_path.stat().st_size == 0):
        input_path = default_legacy_input_path()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df, source_kind = read_source(input_path)
    if source_kind == "legacy_xlsx":
        mapped = build_rr_budget_frame_legacy(source_df)
        normalized = normalize_preview(mapped, "RR", require_cnpj=False)
    else:
        mapped = build_rr_budget_frame(source_df)
        normalized = normalize_preview(mapped, "RR", require_cnpj=True)

    output_path = output_dir / default_output_name("RR", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_path}")
    print(f"Tipo de origem: {source_kind}")
    print(f"Saida: {output_path}")
    print(f"Linhas origem: {len(source_df)}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
