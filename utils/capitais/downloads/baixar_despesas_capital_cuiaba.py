from __future__ import annotations

import argparse
import json
from math import ceil
from pathlib import Path
import sys
import time

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


API_URL = "http://transparencia.cuiaba.mt.gov.br/portaltransparencia/servlet/aapidespesacredor"
FILTER_URL = "http://transparencia.cuiaba.mt.gov.br/portaltransparencia/servlet/aapifilterdespesacredor"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa despesas por credor da capital Cuiaba pela API oficial.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Cuiaba" / "despesas_por_credor"),
    )
    parser.add_argument("--years", nargs="*", default=None, help="Anos a baixar. Padrao: anos do filtro oficial.")
    parser.add_argument("--records-per-page", type=int, default=1000)
    parser.add_argument("--sleep", type=float, default=0.2)
    return parser.parse_args()


def fetch_filters(session: requests.Session) -> dict[str, object]:
    response = session.get(FILTER_URL, headers=HEADERS, timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_page(session: requests.Session, year: str, page: int, records_per_page: int) -> dict[str, object]:
    payload = {
        "pagination": json.dumps(
            {
                "currentPage": page,
                "recordsPerPage": records_per_page,
                "totalRecords": 0,
                "columnOrder": "",
            },
            ensure_ascii=False,
        ),
        "filters": json.dumps(
            {
                "DespesaCredorDoc": "",
                "DespesaCredorNome": "",
                "Periodo": "mensal",
                "DespesaDataIni": None,
                "DespesaDataFim": None,
                "DespesaAno": str(year),
                "DespesaMes": "",
                "DespesaOrgaoNome": "",
                "DespesaUnidCod": "",
            },
            ensure_ascii=False,
        ),
    }
    response = session.post(
        API_URL,
        files={key: (None, value) for key, value in payload.items()},
        headers=HEADERS,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list) or not data:
        return {"totalRecords": 0, "registers": []}
    return data[0]


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    filters = fetch_filters(session)
    filter_path = output_dir / "cuiaba_despesas_filtros.json"
    filter_path.write_text(json.dumps(filters, ensure_ascii=False, indent=2), encoding="utf-8")

    official_years = [str(item["value"]) for item in filters.get("DespesaAno", [])]
    years = [str(year) for year in (args.years or official_years)]

    manifest: list[dict[str, object]] = []
    for year in years:
        first = fetch_page(session, year, 0, args.records_per_page)
        total = int(first.get("totalRecords") or len(first.get("registers", [])))
        pages = max(1, ceil(total / args.records_per_page))
        records = list(first.get("registers", []))
        for page in range(1, pages):
            time.sleep(args.sleep)
            payload = fetch_page(session, year, page, args.records_per_page)
            records.extend(payload.get("registers", []))

        output_path = output_dir / f"cuiaba_despesas_credor_{year}.json"
        output_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest.append({"ano": year, "total_portal": total, "linhas": len(records), "arquivo": output_path.name})
        print(f"Cuiaba {year}: {len(records)} linhas de {total} -> {output_path}")

    (output_dir / "cuiaba_despesas_manifest.json").write_text(
        json.dumps({"fonte": API_URL, "filtros": str(filter_path), "arquivos": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
