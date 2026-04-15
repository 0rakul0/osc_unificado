from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from html import unescape
from io import StringIO
from pathlib import Path
import re
import sys
import time
from typing import Any

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


LIST_URL = "https://www2.natal.rn.gov.br/transparencia/contratos.php"
DETAIL_URL = "https://www2.natal.rn.gov.br/transparencia/contratosVisualizar.php"
DEFAULT_WORKERS = 4
MAX_RETRIES = 3
OSC_NAME_PATTERN = re.compile(
    r"associ|apae|funda[cç][aã]o|institut|sociedade|grupo reviver|liga|cooperativa|federa[cç][aã]o|centro social",
    re.IGNORECASE,
)
PRIVATE_COMPANY_PATTERN = re.compile(
    r"ltda|s/?a\b|eireli|me\b|epp\b|comerc|constr|engenharia|servi[cç]os|empreend",
    re.IGNORECASE,
)
PUBLIC_NAME_PATTERN = re.compile(
    r"prefeitura|secretaria|governo|estado|tribunal|universidade|c[âa]mara|fundo municipal",
    re.IGNORECASE,
)
CNPJ_PATTERN = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")


@dataclass(frozen=True)
class SearchRow:
    ano_pesquisa: str
    unidade_orcamentaria: str
    codigo_contrato: str
    numero_contrato: str
    orgao_contratante: str
    objeto_lista: str
    numero_processo: str
    forma_contratacao: str
    contratado_raw: str
    contratado_cnpj: str
    contratado_nome: str
    data_assinatura_lista: str
    vigencia_lista: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa o recorte oficial de contratos com sinal de OSC da capital Natal."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Natal"),
        help="Pasta onde os arquivos oficiais consolidados da capital serao salvos.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Quantidade de requisicoes paralelas para buscar os detalhes dos contratos candidatos.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def normalize_text(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return " ".join(str(value).split())


def column_label(value: object) -> str:
    if isinstance(value, tuple):
        parts = [str(item) for item in value if str(item) != "nan"]
        return " ".join(parts)
    return str(value)


def split_contratado(value: object) -> tuple[str, str]:
    text = normalize_text(value)
    match = CNPJ_PATTERN.search(text)
    if not match:
        return "", text
    cnpj = match.group(0)
    nome = normalize_text(text.replace(cnpj, ""))
    return cnpj, nome


def fetch_search_options(session: requests.Session) -> tuple[list[str], list[str]]:
    response = session.get(LIST_URL, timeout=120)
    response.raise_for_status()
    html = response.text

    year_block = re.search(r'name="pesquisaAno"[^>]*>(.*?)</select>', html, re.IGNORECASE | re.DOTALL)
    unit_block = re.search(r'name="pesquisaUnidade"[^>]*>(.*?)</select>', html, re.IGNORECASE | re.DOTALL)
    if not year_block or not unit_block:
        raise ValueError("Nao foi possivel localizar os filtros de ano/unidade na pagina de contratos de Natal.")

    years = re.findall(r'value="(\d{4})"', year_block.group(1))
    units = [
        value
        for value in re.findall(r'value="([^"]+)"', unit_block.group(1))
        if value and "Selecione" not in value
    ]
    return years, units


def fetch_listing_html(session: requests.Session, year: str, unit: str) -> str:
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.post(
                LIST_URL,
                data={"pesquisaAno": year, "pesquisaUnidade": unit, "pesquisar": "Pesquisar"},
                timeout=120,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(min(2 * attempt, 6))
    raise RuntimeError(f"Falha ao consultar Natal para ano={year} unidade={unit}: {last_error}") from last_error


def parse_listing_rows(html: str, year: str, unit: str) -> list[SearchRow]:
    tables = pd.read_html(StringIO(html))
    if not tables:
        return []

    frame = tables[0].copy()
    row_ids = re.findall(r'class="view_data"[^>]*id="([^"]+)"', html)
    if len(row_ids) < len(frame):
        row_ids.extend([""] * (len(frame) - len(row_ids)))

    rows: list[SearchRow] = []
    for index, item in frame.iterrows():
        contratado_cnpj, contratado_nome = split_contratado(item.get("Contratado"))
        rows.append(
            SearchRow(
                ano_pesquisa=str(year),
                unidade_orcamentaria=str(unit),
                codigo_contrato=str(row_ids[index]).strip(),
                numero_contrato=normalize_text(item.get("Número Contrato")),
                orgao_contratante=normalize_text(item.get("Órgão Contratante")),
                objeto_lista=normalize_text(item.get("Objeto")),
                numero_processo=normalize_text(item.get("Número Processo")),
                forma_contratacao=normalize_text(item.get("Forma Contratação")),
                contratado_raw=normalize_text(item.get("Contratado")),
                contratado_cnpj=contratado_cnpj,
                contratado_nome=contratado_nome,
                data_assinatura_lista=normalize_text(item.get("Data Assinatura")),
                vigencia_lista=normalize_text(item.get("Vigência")),
            )
        )
    return rows


def is_osc_candidate(row: SearchRow) -> bool:
    name = row.contratado_nome
    if not name:
        return False
    if PUBLIC_NAME_PATTERN.search(name):
        return False
    if PRIVATE_COMPANY_PATTERN.search(name):
        return False
    return bool(OSC_NAME_PATTERN.search(name))


def fetch_detail_html(session: requests.Session, row: SearchRow) -> str:
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.post(
                DETAIL_URL,
                data={
                    "codigoContrato": row.codigo_contrato,
                    "anoPesquisa": row.ano_pesquisa,
                    "unidadeOrcamentaria": row.unidade_orcamentaria,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(min(2 * attempt, 6))
    raise RuntimeError(
        f"Falha ao consultar detalhe de Natal para contrato={row.codigo_contrato} "
        f"ano={row.ano_pesquisa} unidade={row.unidade_orcamentaria}: {last_error}"
    ) from last_error


def detail_tables(html: str) -> list[pd.DataFrame]:
    return pd.read_html(StringIO(html))


def flatten_ident_table(frame: pd.DataFrame) -> dict[str, str]:
    columns = list(frame.columns)
    if len(columns) < 4 or frame.empty:
        return {}
    row = frame.iloc[0]
    return {
        "Exercício": normalize_text(row[columns[0]]),
        "Número Contrato": normalize_text(row[columns[1]]),
        "Data Assinatura": normalize_text(row[columns[2]]),
        "Número Processo": normalize_text(row[columns[3]]),
    }


def flatten_detail_table(frame: pd.DataFrame) -> dict[str, str]:
    columns = list(frame.columns)
    if len(columns) < 2:
        return {}
    result: dict[str, str] = {}
    for _, item in frame.iterrows():
        key = normalize_text(item[columns[0]])
        value = normalize_text(item[columns[1]])
        if key:
            result[key] = value
    return result


def parse_decimal(value: object) -> Decimal | None:
    text = normalize_text(value)
    if not text:
        return None
    compact = text.replace(".", "").replace(",", ".")
    try:
        return Decimal(compact)
    except InvalidOperation:
        return None


def sum_items_total(frame: pd.DataFrame) -> str | None:
    value_column = None
    for column in frame.columns:
        label = column_label(column)
        if "Valor Total" in label:
            value_column = column
            break
    if value_column is None:
        return None

    total = Decimal("0")
    found = False
    for value in frame[value_column]:
        parsed = parse_decimal(value)
        if parsed is None:
            continue
        total += parsed
        found = True
    if not found:
        return None
    return f"{total:.2f}".replace(".", ",")


def build_unique_records(tables: list[pd.DataFrame]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for index in range(len(tables) - 1):
        ident_label = column_label(tables[index].columns[0])
        detail_label = column_label(tables[index + 1].columns[0])
        if "IDENTIFICAÇÃO" not in ident_label or "DETALHAMENTO" not in detail_label:
            continue
        ident = flatten_ident_table(tables[index])
        detail = flatten_detail_table(tables[index + 1])
        if not ident or not detail:
            continue
        records.append({**ident, **detail})

    unique_records: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for record in records:
        key = (
            normalize_text(record.get("Número Contrato")),
            normalize_text(record.get("Número Processo")),
            normalize_text(record.get("Data Assinatura")),
            normalize_text(record.get("Contratado")),
            normalize_text(record.get("Objeto")),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_records.append(record)
    return unique_records


def row_matches_record(row: SearchRow, record: dict[str, str]) -> bool:
    process_match = normalize_text(row.numero_processo) == normalize_text(record.get("Número Processo"))
    date_match = normalize_text(row.data_assinatura_lista) == normalize_text(record.get("Data Assinatura"))
    cnpj_match = row.contratado_cnpj and row.contratado_cnpj in normalize_text(record.get("Contratado"))
    object_match = normalize_text(row.objeto_lista) and normalize_text(row.objeto_lista)[:40] in normalize_text(record.get("Objeto"))
    return process_match and (date_match or cnpj_match or object_match)


def enrich_candidate(row: SearchRow) -> dict[str, object] | None:
    session = build_session()
    try:
        html = fetch_detail_html(session, row)
    finally:
        session.close()

    tables = detail_tables(html)
    records = build_unique_records(tables)
    item_frames = [
        frame
        for frame in tables
        if any("ITEMS DAS AQUISIÇÕES" in column_label(column) for column in frame.columns)
    ]

    if len(records) == 1:
        record = records[0]
    else:
        matched = [current for current in records if row_matches_record(row, current)]
        if len(matched) != 1:
            return None
        record = matched[0]
    valor_total = sum_items_total(item_frames[0]) if len(item_frames) == 1 else None
    if not valor_total:
        return None

    contratado = normalize_text(record.get("Contratado"))
    cnpj, nome = split_contratado(contratado)

    return {
        "ano_pesquisa": row.ano_pesquisa,
        "unidade_orcamentaria": row.unidade_orcamentaria,
        "codigo_contrato": row.codigo_contrato,
        "numero_contrato": row.numero_contrato,
        "orgao_contratante": row.orgao_contratante,
        "objeto_lista": row.objeto_lista,
        "numero_processo_lista": row.numero_processo,
        "forma_contratacao_lista": row.forma_contratacao,
        "data_assinatura_lista": row.data_assinatura_lista,
        "vigencia_lista": row.vigencia_lista,
        "exercicio": normalize_text(record.get("Exercício")),
        "numero_processo": normalize_text(record.get("Número Processo")),
        "data_assinatura": normalize_text(record.get("Data Assinatura")),
        "vigencia": normalize_text(record.get("Vigência")),
        "objeto": normalize_text(record.get("Objeto")),
        "secretaria_orgao": normalize_text(record.get("Secretaria/Orgão")),
        "contratado_cnpj": cnpj or row.contratado_cnpj,
        "contratado_nome": nome or row.contratado_nome,
        "comissao": normalize_text(record.get("Comissão")),
        "fundamentacao_legal": normalize_text(record.get("Fundamentação Legal")),
        "valor_total": valor_total,
        "fonte_lista": LIST_URL,
        "fonte_detalhe": DETAIL_URL,
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    try:
        years, units = fetch_search_options(session)

        all_rows: list[SearchRow] = []
        listing_failures: list[dict[str, str]] = []
        for year in years:
            for unit in units:
                try:
                    html = fetch_listing_html(session, year, unit)
                except RuntimeError:
                    listing_failures.append({"ano": year, "unidade": unit})
                    continue
                all_rows.extend(parse_listing_rows(html, year, unit))

        candidates = [row for row in all_rows if row.codigo_contrato and is_osc_candidate(row)]

        enriched: list[dict[str, object]] = []
        detail_failures = 0
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            future_map = {executor.submit(enrich_candidate, row): row for row in candidates}
            for future in as_completed(future_map):
                try:
                    result = future.result()
                except RuntimeError:
                    detail_failures += 1
                    continue
                if result is not None:
                    enriched.append(result)
    finally:
        session.close()

    enriched = sorted(
        enriched,
        key=lambda item: (
            str(item.get("ano_pesquisa", "")),
            str(item.get("unidade_orcamentaria", "")),
            str(item.get("numero_contrato", "")),
            str(item.get("contratado_cnpj", "")),
        ),
    )

    summary = {
        "fonte_lista": LIST_URL,
        "fonte_detalhe": DETAIL_URL,
        "anos_consulta": years,
        "unidades_consulta": units,
        "total_linhas_lista": len(all_rows),
        "total_candidatas_osc": len(candidates),
        "total_enriquecidas": len(enriched),
        "com_cnpj": sum(1 for item in enriched if normalize_text(item.get("contratado_cnpj"))),
        "falhas_listagem": len(listing_failures),
        "falhas_detalhe": detail_failures,
    }

    write_json(output_dir / "natal_contratos_osc_enriquecido.json", enriched)
    write_json(output_dir / "natal_contratos_osc_resumo.json", summary)
    write_json(output_dir / "natal_contratos_osc_falhas_listagem.json", listing_failures)

    print(
        f"Natal: lista={summary['total_linhas_lista']} candidatas={summary['total_candidatas_osc']} "
        f"enriquecidas={summary['total_enriquecidas']}"
    )


if __name__ == "__main__":
    main()
