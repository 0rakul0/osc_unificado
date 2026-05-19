from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Iterable

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


API_URL = "https://transparencia.e-publica.net/epublica-portal/rest/florianopolis/api/v1/despesa"
PORTAL_URL = (
    "https://transparencia.e-publica.net/epublica-portal/#/florianopolis/portal/"
    "dadosAbertos/despesaView?params=%7B%22mode%22%3A%22INFO%22%7D&entidade=2002"
)
DEFAULT_START_YEAR = 2016


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa despesas abertas de Florianopolis pela API oficial do e-publica."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Florianopolis"),
        help="Pasta onde os JSONs de despesas da capital serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=list(range(DEFAULT_START_YEAR, datetime.now().year + 1)),
        help="Anos a consultar. Padrao: 2016 ate o ano corrente.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=5000,
        help="Quantidade de registros por pagina da API.",
    )
    return parser.parse_args()


def nested_get(data: dict[str, object], path: Iterable[str]) -> object:
    current: object = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def month_period(year: int, month: int) -> str:
    return f"{month:02d}/{year}"


def sum_movements(registro: dict[str, object], token: str) -> float:
    movimentos = registro.get("listMovimentos")
    if not isinstance(movimentos, list):
        return 0.0
    total = 0.0
    token_lower = token.lower()
    for movimento in movimentos:
        if not isinstance(movimento, dict):
            continue
        tipo = str(movimento.get("tipoMovimento") or "").lower()
        if token_lower not in tipo:
            continue
        try:
            total += float(movimento.get("valorMovimento") or 0)
        except (TypeError, ValueError):
            continue
    return total


def flatten_record(item: dict[str, object], year: int, month: int) -> dict[str, object]:
    registro = item.get("registro")
    if not isinstance(registro, dict):
        registro = item

    valor_pago = sum_movements(registro, "pagamento")
    valor_liquidado = sum_movements(registro, "liquida")
    valor_empenhado = sum_movements(registro, "empenho")
    valor_total = valor_pago or valor_liquidado or valor_empenhado

    return {
        "ano_consulta": year,
        "mes_consulta": month,
        "ano": nested_get(registro, ("exercicio", "exercicio")) or year,
        "mes": month,
        "valor_total": valor_total,
        "valor_pago": valor_pago,
        "valor_liquidado": valor_liquidado,
        "valor_empenhado": valor_empenhado,
        "cnpj": nested_get(registro, ("fornecedor", "pessoa", "cpfCnpj")),
        "nome_osc": nested_get(registro, ("fornecedor", "pessoa", "nome")),
        "objeto": nested_get(registro, ("empenho", "objetoResumido")),
        "modalidade": nested_get(registro, ("naturezaDespesa", "detalhamento", "denominacao"))
        or nested_get(registro, ("naturezaDespesa", "elemento", "denominacao")),
        "data_inicio": nested_get(registro, ("empenho", "emissao")),
        "unidade_gestora_codigo": nested_get(registro, ("unidadeOrcamentaria", "unidadeGestora", "codigo")),
        "unidade_gestora": nested_get(registro, ("unidadeOrcamentaria", "unidadeGestora", "denominacao")),
        "unidade_orcamentaria_codigo": nested_get(registro, ("unidadeOrcamentaria", "codigo")),
        "unidade_orcamentaria": nested_get(registro, ("unidadeOrcamentaria", "denominacao")),
        "empenho_numero": nested_get(registro, ("empenho", "numero")),
        "contrato": nested_get(registro, ("empenho", "contrato")),
        "licitacao": nested_get(registro, ("empenho", "licitacao")),
        "fonte_portal": PORTAL_URL,
        "fonte_api": API_URL,
    }


def fetch_month(session: requests.Session, year: int, month: int, page_size: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    pages: list[dict[str, object]] = []
    start = 0
    period = month_period(year, month)

    while True:
        params = {
            "periodo_inicial": period,
            "periodo_final": period,
            "inicio_registro": start,
            "quantidade_registro": page_size,
        }
        response = session.get(API_URL, params=params, timeout=300)
        response.raise_for_status()
        raw_bytes = response.content
        payload = response.json()
        registros = payload.get("registros") if isinstance(payload, dict) else None
        if not isinstance(registros, list):
            raise ValueError(f"Resposta inesperada para Florianopolis {period}.")

        rows.extend(flatten_record(item, year, month) for item in registros if isinstance(item, dict))
        pages.append(
            {
                "periodo": period,
                "inicio_registro": start,
                "quantidade_registro": page_size,
                "registros": len(registros),
                "status_code": response.status_code,
                "url": response.url,
                "bytes": len(raw_bytes),
                "sha256": sha256(raw_bytes).hexdigest(),
                "ultima_atualizacao": payload.get("ultimaAtualizacao") if isinstance(payload, dict) else None,
            }
        )

        if len(registros) < page_size:
            break
        start += page_size

    return rows, pages


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_existing_manifest(path: Path) -> dict[int, dict[str, object]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    years = payload.get("anos") if isinstance(payload, dict) else None
    if not isinstance(years, list):
        return {}
    result: dict[int, dict[str, object]] = {}
    for item in years:
        if not isinstance(item, dict):
            continue
        try:
            year = int(item.get("ano"))
        except (TypeError, ValueError):
            continue
        result[year] = item
    return result


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "florianopolis_despesas_manifest.json"

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    manifest_by_year = load_existing_manifest(manifest_path)
    try:
        for year in sorted(set(args.years)):
            year_rows: list[dict[str, object]] = []
            year_pages: list[dict[str, object]] = []
            for month in range(1, 13):
                rows, pages = fetch_month(session, year, month, args.page_size)
                year_rows.extend(rows)
                year_pages.extend(pages)
                print(f"Florianopolis {year}-{month:02d}: {len(rows)} registros")

            data_path = output_dir / f"florianopolis_despesas_{year}.json"
            write_json(data_path, year_rows)
            manifest_by_year[year] = {
                "ano": year,
                "arquivo": data_path.name,
                "registros": len(year_rows),
                "paginas": year_pages,
            }
            print(f"Florianopolis {year}: {len(year_rows)} registros -> {data_path}")
    finally:
        session.close()

    write_json(
        manifest_path,
        {
            "fonte_portal": PORTAL_URL,
            "fonte_api": API_URL,
            "anos": [manifest_by_year[year] for year in sorted(manifest_by_year)],
        },
    )


if __name__ == "__main__":
    main()
