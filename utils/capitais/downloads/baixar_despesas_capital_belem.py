from __future__ import annotations

import argparse
from calendar import monthrange
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PORTAL_URL = "https://transparencia.belem.pa.gov.br/giig/portais/portaldatransparencia/despesas/wfrmConsultaDespesasParaSemLayout.aspx"
GRID_SELECTOR = "#ctl00_Content_wuc_GridEmpenhos_gvCad"
DEFAULT_YEARS = list(range(2020, datetime.now().year + 1))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa despesas detalhadas de Belem pela consulta oficial GIIG/WebForms."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Belem"),
        help="Pasta onde os JSONs de despesas da capital serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        default=DEFAULT_YEARS,
        help="Anos a consultar. Padrao: 2020 ate o ano corrente.",
    )
    parser.add_argument(
        "--months",
        nargs="*",
        type=int,
        default=None,
        help="Meses a consultar. Padrao: todos os meses aplicaveis em cada ano.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Abre o navegador em modo visivel para depuracao.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Pula meses que ja aparecem no manifesto, inclusive meses com zero registros.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reconsulta meses mesmo quando ja aparecem no manifesto.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def date_range_for_month(year: int, month: int) -> tuple[str, str]:
    last_day = monthrange(year, month)[1]
    return f"01/{month:02d}/{year}", f"{last_day:02d}/{month:02d}/{year}"


def applicable_months(year: int, selected_months: list[int] | None) -> list[int]:
    current = datetime.now()
    months = selected_months or list(range(1, 13))
    if year == current.year:
        months = [month for month in months if month <= current.month]
    return months


def validate_months(months: list[int] | None) -> None:
    if months is None:
        return
    invalid = [month for month in months if month < 1 or month > 12]
    if invalid:
        raise ValueError(f"Meses invalidos para Belem: {invalid}. Use valores entre 1 e 12.")


def wait_after_postback(page: Page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=180000)
    except PlaywrightTimeoutError:
        page.wait_for_timeout(2000)
    page.wait_for_timeout(1000)


def open_query(page: Page, year: int, month: int) -> None:
    start_date, end_date = date_range_for_month(year, month)
    page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=120000)
    page.select_option("#ctl00_Content_ddl_nrAno", str(year))
    page.wait_for_timeout(2000)
    page.fill("#ctl00_Content_wuc_dataInicial_txtData", start_date)
    page.fill("#ctl00_Content_wuc_dataFinal_txtData", end_date)
    page.click("#ctl00_Content_btn_GerarConsulta", timeout=30000)
    wait_after_postback(page)


def extract_rows(page: Page, year: int, month: int, page_number: int) -> list[dict[str, Any]]:
    if page.locator(GRID_SELECTOR).count() == 0:
        return []
    rows = page.eval_on_selector_all(
        f"{GRID_SELECTOR} tr",
        """trs => trs
            .map(tr => [...tr.cells].map(td => td.innerText.trim()))
            .filter(cells => cells.length === 10 && cells[1] && cells[1] !== 'Empenho')
            .map(cells => ({
                empenho: cells[1],
                data_empenho: cells[2],
                data_liquidacao: cells[3],
                unidade_gestora: cells[4],
                fornecedor: cells[5],
                situacao: cells[6],
                data_vencimento: cells[7],
                valor: cells[8],
                data_pagamento: cells[9]
            }))""",
    )
    for row in rows:
        row["ano_consulta"] = year
        row["mes_consulta"] = month
        row["pagina_consulta"] = page_number
        row["fonte_portal"] = PORTAL_URL
    return rows


def click_page(page: Page, page_number: int) -> bool:
    has_link = page.eval_on_selector_all(
        f"{GRID_SELECTOR} a",
        """(links, pageNumber) => links.some(link =>
            link.getAttribute('href')?.includes(`Page$${pageNumber}`))""",
        page_number,
    )
    if not has_link:
        return False

    first_before = page.eval_on_selector_all(
        f"{GRID_SELECTOR} tr",
        """trs => JSON.stringify(trs
            .map(tr => [...tr.cells].map(td => td.innerText.trim()))
            .filter(cells => cells.length === 10 && cells[1] && cells[1] !== 'Empenho')
            .slice(0, 1))""",
    )
    page.eval_on_selector_all(
        f"{GRID_SELECTOR} a",
        """(links, pageNumber) => {
            const link = links.find(item => item.getAttribute('href')?.includes(`Page$${pageNumber}`));
            if (!link) return false;
            link.click();
            return true;
        }""",
        page_number,
    )
    try:
        page.wait_for_function(
            """before => JSON.stringify([...document.querySelectorAll('#ctl00_Content_wuc_GridEmpenhos_gvCad tr')]
                .map(tr => [...tr.cells].map(td => td.innerText.trim()))
                .filter(cells => cells.length === 10 && cells[1] && cells[1] !== 'Empenho')
                .slice(0, 1)) !== before""",
            arg=first_before,
            timeout=60000,
        )
    except PlaywrightTimeoutError:
        page.wait_for_timeout(2000)
    return True


def fetch_month(page: Page, year: int, month: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    open_query(page, year, month)
    all_rows: list[dict[str, Any]] = []
    page_number = 1
    while True:
        rows = extract_rows(page, year, month, page_number)
        all_rows.extend(rows)
        if not rows or not click_page(page, page_number + 1):
            break
        page_number += 1

    return all_rows, {"ano": year, "mes": month, "paginas": page_number, "registros": len(all_rows)}


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


def load_existing_year_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def replace_month_rows(
    existing_rows: list[dict[str, Any]], year: int, month: int, new_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    kept = [
        row
        for row in existing_rows
        if not (str(row.get("ano_consulta")) == str(year) and str(row.get("mes_consulta")) == str(month))
    ]
    kept.extend(new_rows)
    return kept


def replace_month_summary(
    summaries: list[dict[str, Any]], year: int, month: int, new_summary: dict[str, Any]
) -> list[dict[str, Any]]:
    kept = [
        item
        for item in summaries
        if not (str(item.get("ano")) == str(year) and str(item.get("mes")) == str(month))
    ]
    kept.append(new_summary)
    return sorted(kept, key=lambda item: (int(item.get("ano", 0)), int(item.get("mes", 0))))


def collected_months(summaries: list[dict[str, Any]]) -> set[int]:
    months: set[int] = set()
    for item in summaries:
        try:
            months.add(int(item.get("mes")))
        except (TypeError, ValueError):
            continue
    return months


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "belem_despesas_manifest.json"
    selected_months = sorted(set(args.months)) if args.months else None
    validate_months(selected_months)
    manifest_by_year = load_existing_manifest(manifest_path)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        page = browser.new_page(ignore_https_errors=True)
        try:
            for year in sorted(set(args.years)):
                data_path = output_dir / f"belem_despesas_{year}.json"
                year_rows = load_existing_year_rows(data_path)
                month_summaries = list(manifest_by_year.get(year, {}).get("meses", []))
                already_collected = collected_months(month_summaries)
                for month in applicable_months(year, selected_months):
                    if args.resume and not args.force and month in already_collected:
                        print(f"Belem {year}-{month:02d}: pulado (ja consta no manifesto)", flush=True)
                        continue
                    rows, summary = fetch_month(page, year, month)
                    year_rows = replace_month_rows(year_rows, year, month, rows)
                    month_summaries = replace_month_summary(month_summaries, year, month, summary)
                    write_json(data_path, year_rows)
                    manifest_by_year[year] = {
                        "ano": year,
                        "arquivo": data_path.name,
                        "registros": len(year_rows),
                        "meses": month_summaries,
                    }
                    write_json(
                        manifest_path,
                        {
                            "fonte_portal": PORTAL_URL,
                            "metodo": "Consulta WebForms oficial, paginada mes a mes pela grade de despesas detalhadas.",
                            "anos": [manifest_by_year[item_year] for item_year in sorted(manifest_by_year)],
                        },
                    )
                    already_collected.add(month)
                    print(f"Belem {year}-{month:02d}: {len(rows)} registros em {summary['paginas']} paginas", flush=True)

                print(f"Belem {year}: {len(year_rows)} registros -> {data_path}", flush=True)
        finally:
            browser.close()

    write_json(
        manifest_path,
        {
            "fonte_portal": PORTAL_URL,
            "metodo": "Consulta WebForms oficial, paginada mes a mes pela grade de despesas detalhadas.",
            "anos": [manifest_by_year[year] for year in sorted(manifest_by_year)],
        },
    )


if __name__ == "__main__":
    main()
