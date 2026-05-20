from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


BASE_URL = "https://transparencia.al.gov.br/despesa/json-despesa-avancada-filtro/"
DEFAULT_OUTPUT_DIR = BASES_ORCAMENTO_GERAL_DIR / "AL" / "coleta_2010_2026"
DEFAULT_COLUMNS = [
    "descricao_ug",
    "projeto_atividade_id__projeto_descricao",
    "fonte_mae_id__descricao_fonte_mae",
    "fonte_id__descricao_fonte",
    "nome_favorecido",
    "projeto_atividade_id",
    "codigo_favorecido",
    "fonte_mae_id",
    "fonte_id",
]
DEFAULT_VALORES = ["empenhado", "liquidado", "pago"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa despesas gerais de AL por ano.")
    parser.add_argument("--start-year", type=int, default=2010, help="Ano inicial da coleta.")
    parser.add_argument("--end-year", type=int, default=2026, help="Ano final da coleta.")
    parser.add_argument("--limit", type=int, default=100000, help="Limite de linhas por requisicao.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(DEFAULT_OUTPUT_DIR),
        help="Pasta onde os CSVs anuais e consolidado serao gravados.",
    )
    parser.add_argument(
        "--combined-name",
        default="despesas_alagoas_2010_2026.csv",
        help="Nome do CSV consolidado.",
    )
    return parser.parse_args()


def build_params(year: int, limit: int, offset: int) -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = [
        ("data_registro_dti_", f"01/01/{year}"),
        ("data_registro_dtf_", f"31/12/{year}"),
        ("nome_favorecido", ""),
    ]
    params.extend(("visualizar", column) for column in DEFAULT_COLUMNS)
    params.extend(("valor", column) for column in DEFAULT_VALORES)
    params.extend([("order", "asc"), ("limit", str(limit)), ("offset", str(offset))])
    return params


def fetch_year(session: requests.Session, year: int, limit: int) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    offset = 0
    total: int | None = None
    while total is None or offset < total:
        response = session.get(BASE_URL, params=build_params(year, limit, offset), timeout=120)
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Resposta inesperada para {year}: chave 'rows' ausente ou invalida.")
        total = int(payload.get("total") or len(rows))
        if not rows:
            break
        frame = pd.DataFrame(rows)
        frame["ano_consulta"] = str(year)
        frames.append(frame)
        offset += len(rows)
        if len(rows) < limit:
            break
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()


def main() -> None:
    args = parse_args()
    if args.start_year > args.end_year:
        raise ValueError("--start-year nao pode ser maior que --end-year")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    frames: list[pd.DataFrame] = []
    for year in range(args.start_year, args.end_year + 1):
        frame = fetch_year(session, year, args.limit)
        frames.append(frame)
        annual_path = output_dir / f"despesas_alagoas_{year}.csv"
        frame.to_csv(annual_path, index=False, encoding="utf-8-sig")
        print(f"{year}: {len(frame)} registros -> {annual_path}")

    combined = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    combined_path = output_dir / args.combined_name
    combined.to_csv(combined_path, index=False, encoding="utf-8-sig")
    print(f"Consolidado: {combined_path}")
    print(f"Total: {len(combined)}")


if __name__ == "__main__":
    main()
