from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PORTAL_URL = "https://prodata.palmas.to.gov.br/sig/app.html#/transparencia/contratos/"
API_URL = "https://prodata.palmas.to.gov.br/sig/rest/transparenciaContratosController/getContratos"
DEFAULT_YEARS = [str(year) for year in range(2019, 2027)]
OSC_NAME_PATTERN = re.compile(
    r"associ|instit|funda[cç][aã]o|apae|sociedade|centro |casa |lar |comunit|ong|osc|irmandade",
    re.IGNORECASE,
)
PRIVATE_COMPANY_PATTERN = re.compile(
    r"ltda|s\.?/?a\.?\b|eireli|me\b|epp\b|comerc|engenharia|servi[cç]os|loca[cç][aã]o|filmes|distribui[cç][aã]o",
    re.IGNORECASE,
)
PUBLIC_NAME_PATTERN = re.compile(
    r"prefeitura|secretaria|municipio|governo|estado|fundo municipal|camara|tribunal|universidade",
    re.IGNORECASE,
)
PARTNERSHIP_PATTERN = re.compile(
    r"termo de fomento|termo de colabora[cç][aã]o|termo de parceria|acordo de coopera[cç][aã]o|conv[eê]nio|parceria",
    re.IGNORECASE,
)
MODALITY_PATTERN = re.compile(r"conveni", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa o recorte oficial de contratos/parcerias com OSC da capital Palmas."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Palmas"),
        help="Pasta onde os JSONs consolidados da capital serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        default=DEFAULT_YEARS,
        help="Lista de anos a consultar no portal oficial.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def is_osc_candidate(row: dict[str, object]) -> bool:
    name = normalize_text(row.get("nome_fornecedor"))
    if not name or PUBLIC_NAME_PATTERN.search(name) or PRIVATE_COMPANY_PATTERN.search(name):
        return False
    if not OSC_NAME_PATTERN.search(name):
        return False
    text = " ".join(
        normalize_text(row.get(field))
        for field in ("objetivo", "modalidade")
    )
    return bool(PARTNERSHIP_PATTERN.search(text) or MODALITY_PATTERN.search(normalize_text(row.get("modalidade"))))


def payload_for_year(year: int) -> dict[str, object]:
    return {
        "isCorona": 0,
        "limiteRegistros": 1000,
        "exercicio": year,
        "mes_inicial": 1,
        "mes_final": 12,
        "tabela": {"ano_contrato": year},
        "isConsultaText": False,
        "nomeTelaAtualAutocomplete": None,
        "moduloAtual": "TRANSPARENCIA",
        "descricaoModuloAtual": "transparencia",
    }


def fetch_year_rows(page, year: int) -> list[dict[str, object]]:
    page.locator("input[id$='inputAno']").fill(str(year))
    mes_inputs = page.locator("input[id$='inputMes']")
    mes_inputs.nth(0).fill("1")
    mes_inputs.nth(1).fill("12")
    with page.expect_response(lambda response: response.url == API_URL and response.request.method == "POST", timeout=120000) as info:
        page.get_by_role("button", name="Pesquisar").click(timeout=30000)
    response = info.value
    if response.status != 200:
        raise RuntimeError(f"Falha ao consultar Palmas para o ano {year}: status={response.status}")
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"Resposta inesperada para Palmas no ano {year}: {type(payload).__name__}")
    return payload


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, object]] = []
    selected_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    failed_years: list[dict[str, str]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for year_text in args.years:
            year = int(year_text)
            page = browser.new_page(ignore_https_errors=True)
            try:
                page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=120000)
                page.wait_for_timeout(5000)
                rows = fetch_year_rows(page, year)
                picked = [row for row in rows if isinstance(row, dict) and is_osc_candidate(row)]
                for item in picked:
                    item["ano_consulta"] = str(year)
                all_rows.extend(rows)
                selected_rows.extend(picked)
                summary_rows.append({"ano": str(year), "rows": len(rows), "rows_osc": len(picked), "status": "ok"})
                print(f"Palmas {year}: total={len(rows)} osc={len(picked)}")
            except Exception as exc:  # noqa: BLE001
                failed_years.append({"ano": str(year), "erro": f"{type(exc).__name__}: {exc}"})
                summary_rows.append({"ano": str(year), "rows": 0, "rows_osc": 0, "status": "erro"})
                print(f"Palmas {year}: erro={type(exc).__name__}")
            finally:
                page.close()

        browser.close()

    summary = {
        "anos": summary_rows,
        "falhas": failed_years,
        "total_bruto": len(all_rows),
        "total_osc": len(selected_rows),
        "com_cnpj": sum(1 for item in selected_rows if normalize_text(item.get("nr_cgc_cpf2")) or normalize_text(item.get("nr_cgc_cpf"))),
        "fonte_portal": PORTAL_URL,
        "fonte_api": API_URL,
    }

    write_json(output_dir / "palmas_contratos_brutos.json", all_rows)
    write_json(output_dir / "palmas_convenios_osc.json", selected_rows)
    write_json(output_dir / "palmas_convenios_resumo.json", summary)


if __name__ == "__main__":
    main()
