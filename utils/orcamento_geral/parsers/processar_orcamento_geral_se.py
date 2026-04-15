from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq
from openpyxl import load_workbook

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
OSC_NAME_PATTERN = re.compile(
    r"associ|instit|fundac|apae|pestalozzi|benefic|filantrop|matern|"
    r"santa casa|paroquia|igreja|oratorio|lar |casa |centro |hospital do tricentenario|"
    r"irma|irmandade|provincia nossa senhora|comunidade",
    flags=re.IGNORECASE,
)
PUBLIC_OR_FOR_PROFIT_PATTERN = re.compile(
    r"municipio|prefeitura|secretaria|governo|tribunal|camara|assembleia|"
    r"universidade federal|universidade estadual|servico autonomo|fundo |"
    r"seguro social|servidores|previdencia|autarquia|empresa municipal|"
    r"\bltda\b|\bme\b|\bepp\b|\bsa\b|comercio|servicos|construtora|engenharia|"
    r"veiculos|transportes|empreendimentos|telecom|energia|combustiveis",
    flags=re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa os empenhos do SE com foco em despesas do orcamento geral ligadas a OSC."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Diretorio com os arquivos empenhos_*.xlsx. Se omitido, usa o caminho padrao do escopo.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("SE", scope)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return ""
    return " ".join(text.split())


def normalize_document(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        text = str(int(value))
    else:
        text = clean_text(value)
    digits = re.sub(r"\D", "", text)
    if len(digits) == 13:
        digits = f"0{digits}"
    return digits


def first_non_empty(*values: object) -> object:
    for value in values:
        text = clean_text(value)
        if text:
            return text
    return pd.NA


def should_keep_record(nome_osc: str) -> bool:
    if not nome_osc:
        return False
    if PUBLIC_OR_FOR_PROFIT_PATTERN.search(nome_osc):
        return False
    return bool(OSC_NAME_PATTERN.search(nome_osc))


def iter_source_rows(path: Path) -> list[dict[str, object]]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook.active
    header = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True))
    columns = [clean_text(value) for value in header]
    index_by_name = {name: idx for idx, name in enumerate(columns) if name}
    rows: list[dict[str, object]] = []

    for values in worksheet.iter_rows(min_row=2, values_only=True):
        nome_osc = clean_text(values[index_by_name["nmRazaoSocialPessoa"]]) if "nmRazaoSocialPessoa" in index_by_name else ""
        if not should_keep_record(nome_osc):
            continue

        cnpj = normalize_document(values[index_by_name["nuDocumento"]]) if "nuDocumento" in index_by_name else ""
        if len(cnpj) != 14:
            continue

        row = {
            "uf": "SE",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": first_non_empty(
                values[index_by_name["dtAnoExercicioCtb"]] if "dtAnoExercicioCtb" in index_by_name else None,
                values[index_by_name["_ano"]] if "_ano" in index_by_name else None,
            ),
            "valor_total": first_non_empty(
                values[index_by_name["vlTotalPagoEmpenho"]] if "vlTotalPagoEmpenho" in index_by_name else None,
                values[index_by_name["vlTotalLiquidadoEmpenho"]] if "vlTotalLiquidadoEmpenho" in index_by_name else None,
                values[index_by_name["vlOriginalEmpenho"]] if "vlOriginalEmpenho" in index_by_name else None,
                values[index_by_name["vlSolicEmpenho"]] if "vlSolicEmpenho" in index_by_name else None,
            ),
            "cnpj": cnpj,
            "nome_osc": nome_osc,
            "mes": first_non_empty(values[index_by_name["_mes"]] if "_mes" in index_by_name else None),
            "cod_municipio": pd.NA,
            "municipio": pd.NA,
            "objeto": first_non_empty(values[index_by_name["dsObjetoLicitacao"]] if "dsObjetoLicitacao" in index_by_name else None),
            "modalidade": first_non_empty(values[index_by_name["nmModalidadeLicitacao"]] if "nmModalidadeLicitacao" in index_by_name else None),
            "data_inicio": first_non_empty(
                values[index_by_name["dtEmissaoEmpenho"]] if "dtEmissaoEmpenho" in index_by_name else None,
                values[index_by_name["dtLancamentoEmpenho"]] if "dtLancamentoEmpenho" in index_by_name else None,
                values[index_by_name["dtGeracaoEmpenho"]] if "dtGeracaoEmpenho" in index_by_name else None,
            ),
            "data_fim": pd.NA,
        }
        rows.append(row)

    workbook.close()
    return rows


def build_se_budget_frame(input_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(input_dir.glob("empenhos_*.xlsx")):
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

    mapped = build_se_budget_frame(input_dir)
    normalized = normalize_preview(mapped, "SE", require_cnpj=True)

    output_path = output_dir / default_output_name("SE", args.scope)
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    print(f"Entrada: {input_dir}")
    print(f"Saida: {output_path}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Origem aplicada: {ORIGEM_ORCAMENTO_GERAL}")


if __name__ == "__main__":
    main()
