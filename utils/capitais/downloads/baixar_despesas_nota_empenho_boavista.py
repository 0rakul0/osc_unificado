from __future__ import annotations

import json
import re
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, ensure_parent_dir


BASE_URL = "https://transparencia.pmbv.rr.gov.br/transparencia/"
LANDING_URL = f"{BASE_URL}?AcessoIndividual=lnkDespesasPor_NotaEmpenho"
PAGE_METHOD_URL = f"{BASE_URL}default.aspx/RecuperarDados"
PANEL_URL = f"{BASE_URL}DespesasPorEntidade.aspx"
OUTPUT_DIR = BASES_CONVENIOS_CAPITAIS_DIR / "Boa Vista"
YEARS = list(range(2016, 2027))
ENTITY_CODE = "1"
LINK_BUTTON_ID = "lnkDespesasPor_NotaEmpenho"


def extract_hidden_inputs(html: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in re.finditer(r'<input[^>]+name="([^"]+)"[^>]*value="([^"]*)"', html, re.IGNORECASE):
        fields[match.group(1)] = match.group(2)
    return fields


def configure_panel(session: requests.Session, year: int) -> None:
    payload = {
        "strLnkButtonID": LINK_BUTTON_ID,
        "strExercicio": str(year),
        "strEmpresa": ENTITY_CODE,
    }
    response = session.post(
        PAGE_METHOD_URL,
        headers={
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        },
        data=json.dumps(payload),
        timeout=120,
    )
    response.raise_for_status()


def export_csv(session: requests.Session) -> requests.Response:
    page_response = session.get(PANEL_URL, timeout=120)
    page_response.raise_for_status()
    fields = extract_hidden_inputs(page_response.text)
    fields["btnExportarCSV.x"] = "10"
    fields["btnExportarCSV.y"] = "10"

    export_response = session.post(PANEL_URL, data=fields, timeout=240)
    export_response.raise_for_status()
    content_type = export_response.headers.get("Content-Type", "")
    if "csv" not in content_type.lower():
        raise RuntimeError(f"Exportacao nao retornou CSV. Content-Type: {content_type}")
    return export_response


def main() -> None:
    ensure_parent_dir(OUTPUT_DIR / "placeholder.txt")
    session = requests.Session()
    landing_response = session.get(LANDING_URL, timeout=120)
    landing_response.raise_for_status()

    for year in YEARS:
        configure_panel(session, year)
        export_response = export_csv(session)
        output_path = OUTPUT_DIR / f"boavista_despesas_nota_empenho_{year}.csv"
        output_path.write_bytes(export_response.content)
        print(f"{year}: salvo em {output_path}")


if __name__ == "__main__":
    main()
