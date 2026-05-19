from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


EXPORT_URL = "https://api.transparencia.se.gov.br/api/relatorios/empenho/export"
EXPORT_COLUMNS = [
    {"key": "numeroEmpenho", "label": "numeroEmpenho"},
    {"key": "dataEmpenho", "label": "dataEmpenho"},
    {"key": "codigoFavorecido", "label": "codigoFavorecido"},
    {"key": "nomePessoa", "label": "nomePessoa"},
    {"key": "modalidade", "label": "modalidade"},
    {"key": "descricaoSolicitacao", "label": "descricaoSolicitacao"},
    {"key": "valorOriginal", "label": "valorOriginal"},
    {"key": "valorAnulado", "label": "valorAnulado"},
    {"key": "valorReforcado", "label": "valorReforcado"},
    {"key": "valorExecutado", "label": "valorExecutado"},
    {"key": "cdUnidadeGestora", "label": "cdUnidadeGestora"},
    {"key": "unidadeDespesa", "label": "unidadeDespesa"},
    {"key": "funcaoDespesa", "label": "funcaoDespesa"},
    {"key": "subFuncaoDespesa", "label": "subFuncaoDespesa"},
    {"key": "naturezaDespesa", "label": "naturezaDespesa"},
    {"key": "fonteRecursosDespesa", "label": "fonteRecursosDespesa"},
    {"key": "elementoDespesa", "label": "elementoDespesa"},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa empenhos de Sergipe pela API do portal de transparencia.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "SE"),
        help="Pasta onde os arquivos brutos de SE serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=[2026],
        help="Anos a baixar. Padrao: 2026.",
    )
    parser.add_argument(
        "--months",
        nargs="*",
        type=int,
        default=list(range(1, 13)),
        help="Meses a baixar. Padrao: 1 a 12.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    return session


def fetch_month(session: requests.Session, year: int, month: int) -> list[dict[str, object]]:
    params = {
        "ano": year,
        "mes": month,
        "format": "json",
        "columns": json.dumps(EXPORT_COLUMNS, ensure_ascii=False),
        "filenamePrefix": f"se-empenhos-{year}-{month:02d}",
    }
    response = session.get(EXPORT_URL, params=params, timeout=180)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"Resposta inesperada para SE {year}-{month:02d}: {type(payload).__name__}.")
    return [row for row in payload if isinstance(row, dict)]


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    manifest: list[dict[str, object]] = []
    for year in args.years:
        year_rows: list[dict[str, object]] = []
        month_counts: dict[str, int] = {}
        for month in args.months:
            rows = fetch_month(session, year, month)
            if rows:
                year_rows.extend(rows)
            month_counts[f"{month:02d}"] = len(rows)
            print(f"{year}-{month:02d}: {len(rows)} registros")

        output_path = output_dir / f"se_empenhos_api_{year}.json"
        write_json(output_path, year_rows)
        manifest.append(
            {
                "ano": year,
                "arquivo": output_path.name,
                "registros": len(year_rows),
                "meses": month_counts,
                "fonte": EXPORT_URL,
            }
        )
        print(f"{year}: {len(year_rows)} registros -> {output_path}")

    write_json(output_dir / "se_empenhos_api_manifest.json", manifest)


if __name__ == "__main__":
    main()
