from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import html
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata
import uuid

import fitz
from pypdf import PdfReader
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


BASE_URL = "http://www.parceriassociais.sp.gov.br"
LIST_URL = f"{BASE_URL}/OSC/_TermosAcordos"
DEFAULT_OUTPUT_DIR = BASES_ORCAMENTO_GERAL_DIR / "SP"
DEFAULT_WORKERS = 4
ROW_PATTERN = re.compile(
    r"<tr>\s*<td>(?P<nome_osc>.*?)</td>\s*<td>(?P<modalidade>.*?)</td>\s*<td>(?P<orgao>.*?)</td>\s*<td>\s*<a[^>]*href='(?P<detail_href>[^']+)'[^>]*>(?P<situacao>.*?)</a>\s*</td>\s*<td>(?P<data_cadastro>.*?)</td>",
    re.S,
)
DETAIL_FIELD_PATTERNS = {
    "orgao": re.compile(
        r"<b>\s*Órgão/Entidade:\s*</b>.*?</div>\s*<div class=\"col-md-\d+\">\s*<p>\s*(.*?)\s*</p>",
        re.S,
    ),
    "nome_osc": re.compile(
        r"<b>\s*OSC Parceira:\s*</b>.*?</div>\s*<div class=\"col-md-\d+\">\s*<p>\s*(.*?)\s*</p>",
        re.S,
    ),
    "objeto": re.compile(
        r"<b>\s*Objeto da Parceria:\s*</b>.*?</div>\s*<div class=\"col-md-\d+\">\s*<p>\s*(.*?)\s*</p>",
        re.S,
    ),
}
ATTACHMENT_PATTERN = re.compile(r'href="([^"]*Buscar_Anexo_PorId/[^"]+)"')
CNPJ_PATTERN = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")
VALUE_PATTERNS = (
    re.compile(r"valor total.*?R\$\s*([\d\.\,]+)", re.IGNORECASE),
    re.compile(r"montante.*?R\$\s*([\d\.\,]+)", re.IGNORECASE),
    re.compile(r"repasse.*?R\$\s*([\d\.\,]+)", re.IGNORECASE),
)
DATE_RANGE_PATTERNS = (
    re.compile(r"vig[êe]ncia[^0-9]{0,80}(\d{2}/\d{2}/\d{4})\s*(?:a|até|ate)\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE),
    re.compile(r"prazo de vig[êe]ncia[^0-9]{0,80}(\d{2}/\d{2}/\d{4})\s*(?:a|até|ate)\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa e enriquece os termos e acordos do Portal de Parcerias com OSC do estado de Sao Paulo."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(DEFAULT_OUTPUT_DIR),
        help="Pasta onde os arquivos brutos e enriquecidos de SP serao salvos.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Quantidade de requisicoes paralelas para detalhes e anexos.",
    )
    parser.add_argument(
        "--from-page",
        type=int,
        default=1,
        help="Pagina inicial da listagem oficial.",
    )
    parser.add_argument(
        "--to-page",
        type=int,
        default=None,
        help="Pagina final da listagem oficial. Se omitido, usa a ultima pagina encontrada.",
    )
    return parser.parse_args()


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def clean_html_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def ascii_fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return normalized.encode("ascii", "ignore").decode("ascii")


def extract_total_pages(list_html: str) -> int:
    pages = [int(value) for value in re.findall(r"pagina=(\d+)", list_html)]
    return max(pages) if pages else 1


def fetch_list_page(session: requests.Session, page: int) -> str:
    response = session.post(
        LIST_URL,
        data={
            "orgao_id": "0",
            "modalidade": "0",
            "prestacao": "0",
            "palavraChave": "",
            "pagina": str(page),
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.text


def parse_rows(list_html: str, page: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for match in ROW_PATTERN.finditer(list_html):
        row = {key: clean_html_text(value) for key, value in match.groupdict().items()}
        row["pagina_origem"] = str(page)
        row["detail_url"] = f"{BASE_URL}{match.group('detail_href')}"
        rows.append(row)
    return rows


def extract_detail_fields(detail_html: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for key, pattern in DETAIL_FIELD_PATTERNS.items():
        match = pattern.search(detail_html)
        fields[key] = clean_html_text(match.group(1)) if match else ""
    attachment_match = ATTACHMENT_PATTERN.search(detail_html)
    fields["anexo_url"] = f"{BASE_URL}{attachment_match.group(1)}" if attachment_match else ""
    return fields


def extract_cnpj(pdf_text: str, nome_osc: str = "") -> str:
    compact_text = normalize_whitespace(pdf_text)
    cnpj_ready_text = re.sub(r"(?<=\d)\s+(?=[\d./-])|(?<=[\d./-])\s+(?=\d)", "", compact_text)
    intro_matches = CNPJ_PATTERN.findall(cnpj_ready_text[:5000])
    if intro_matches:
        return intro_matches[-1]

    seen: list[str] = []
    for value in CNPJ_PATTERN.findall(cnpj_ready_text):
        if value not in seen:
            seen.append(value)
    if len(seen) >= 2:
        return seen[1]
    return seen[0] if seen else ""


def extract_valor_total(pdf_text: str) -> str:
    compact_text = normalize_whitespace(pdf_text)
    for pattern in VALUE_PATTERNS:
        match = pattern.search(compact_text)
        if match:
            return normalize_whitespace(match.group(1))
    return ""


def extract_date_range(pdf_text: str) -> tuple[str, str]:
    compact_text = normalize_whitespace(pdf_text)
    for pattern in DATE_RANGE_PATTERNS:
        match = pattern.search(compact_text)
        if match:
            return normalize_whitespace(match.group(1)), normalize_whitespace(match.group(2))
    return "", ""


def read_pdf_text(pdf_path: Path) -> str:
    try:
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages)
    except Exception:
        return ""


def ocr_pdf_text(pdf_path: Path, max_pages: int = 4) -> str:
    texts: list[str] = []
    document = fitz.open(pdf_path)
    try:
        for page_index in range(min(max_pages, len(document))):
            image_path = pdf_path.with_suffix(f".ocr.{page_index}.png")
            document[page_index].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(image_path)
            try:
                process = subprocess.run(
                    ["tesseract", str(image_path), "stdout", "-l", "por"],
                    capture_output=True,
                    timeout=180,
                    check=False,
                )
                texts.append(process.stdout.decode("utf-8", errors="ignore"))
            finally:
                image_path.unlink(missing_ok=True)
    finally:
        document.close()
    return "\n".join(text for text in texts if text)


def extract_pdf_payload(pdf_bytes: bytes, temp_dir: Path, nome_osc: str = "") -> dict[str, str]:
    pdf_path = temp_dir / f"{uuid.uuid4().hex}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    try:
        pdf_text = read_pdf_text(pdf_path)
        if len(pdf_text.strip()) < 150:
            pdf_text = ocr_pdf_text(pdf_path, max_pages=6)
        else:
            compact_text = normalize_whitespace(pdf_text)
            cnpj_count = len(CNPJ_PATTERN.findall(compact_text))
            has_value = bool(extract_valor_total(pdf_text))
            if cnpj_count < 2 or not has_value:
                ocr_text = ocr_pdf_text(pdf_path, max_pages=6)
                if ocr_text.strip():
                    pdf_text = f"{pdf_text}\n{ocr_text}"

        cnpj = extract_cnpj(pdf_text, nome_osc=nome_osc)
        valor_total = extract_valor_total(pdf_text)
        data_inicio, data_fim = extract_date_range(pdf_text)

        return {
            "cnpj": cnpj,
            "valor_total": valor_total,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "pdf_text_length": str(len(pdf_text)),
        }
    finally:
        pdf_path.unlink(missing_ok=True)


def fetch_enriched_row(row: dict[str, str], temp_dir: Path) -> dict[str, str]:
    session = build_session()
    try:
        detail_response = session.get(row["detail_url"], timeout=180)
        detail_response.raise_for_status()
        detail_fields = extract_detail_fields(detail_response.text)

        pdf_fields = {"cnpj": "", "valor_total": "", "data_inicio": "", "data_fim": "", "pdf_text_length": "0"}
        if detail_fields.get("anexo_url"):
            pdf_response = session.get(detail_fields["anexo_url"], timeout=300)
            pdf_response.raise_for_status()
            pdf_fields = extract_pdf_payload(pdf_response.content, temp_dir, nome_osc=detail_fields.get("nome_osc") or row.get("nome_osc", ""))

        enriched = dict(row)
        enriched.update(detail_fields)
        enriched.update(pdf_fields)
        enriched["erro_coleta"] = ""

        if not enriched.get("nome_osc"):
            enriched["nome_osc"] = row.get("nome_osc", "")
        if not enriched.get("orgao"):
            enriched["orgao"] = row.get("orgao", "")
        return enriched
    finally:
        session.close()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def cleanup_temp_dir(temp_dir: Path) -> None:
    for temp_file in temp_dir.glob("*"):
        try:
            temp_file.unlink(missing_ok=True)
        except PermissionError:
            pass
    try:
        temp_dir.rmdir()
    except OSError:
        pass


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "_tmp_pdf_extract"
    temp_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    try:
        first_html = fetch_list_page(session, args.from_page)
        total_pages = extract_total_pages(first_html)
        final_page = min(args.to_page or total_pages, total_pages)

        rows: list[dict[str, str]] = parse_rows(first_html, args.from_page)
        for page in range(args.from_page + 1, final_page + 1):
            rows.extend(parse_rows(fetch_list_page(session, page), page))
    finally:
        session.close()

    enriched_rows: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {
            executor.submit(fetch_enriched_row, row, temp_dir): row
            for row in rows
        }
        for future in as_completed(future_map):
            row = future_map[future]
            try:
                enriched_rows.append(future.result())
            except Exception as exc:
                failed_row = dict(row)
                failed_row["erro_coleta"] = str(exc)
                failed_row.setdefault("detail_url", row.get("detail_url", ""))
                failed_row.setdefault("anexo_url", "")
                failed_row.setdefault("cnpj", "")
                failed_row.setdefault("valor_total", "")
                failed_row.setdefault("data_inicio", "")
                failed_row.setdefault("data_fim", "")
                failed_row.setdefault("pdf_text_length", "0")
                enriched_rows.append(failed_row)

    enriched_rows.sort(
        key=lambda row: (
            int(row.get("pagina_origem") or 0),
            row.get("detail_url") or "",
        )
    )

    summary = {
        "fonte_lista": LIST_URL,
        "fonte_portal": f"{BASE_URL}/OSC/Termos_Acordos",
        "paginas_processadas": f"{args.from_page}-{final_page}",
        "total_paginas_portal": total_pages,
        "total_registros_lista": len(rows),
        "total_registros_enriquecidos": len(enriched_rows),
        "com_cnpj": sum(1 for row in enriched_rows if row.get("cnpj")),
        "com_valor_total": sum(1 for row in enriched_rows if row.get("valor_total")),
        "com_anexo": sum(1 for row in enriched_rows if row.get("anexo_url")),
        "com_erro_coleta": sum(1 for row in enriched_rows if row.get("erro_coleta")),
    }

    write_csv(output_dir / "sp_parcerias_osc_enriquecido.csv", enriched_rows)
    write_json(output_dir / "sp_parcerias_osc_enriquecido.json", enriched_rows)
    write_json(output_dir / "sp_parcerias_osc_resumo.json", summary)

    cleanup_temp_dir(temp_dir)

    print(f"Fonte oficial: {summary['fonte_portal']}")
    print(f"Paginas: {summary['paginas_processadas']} de {total_pages}")
    print(f"Linhas lista: {summary['total_registros_lista']}")
    print(f"Linhas enriquecidas: {summary['total_registros_enriquecidos']}")
    print(f"Com CNPJ: {summary['com_cnpj']}")
    print(f"Com valor_total: {summary['com_valor_total']}")
    print(f"Saida principal: {output_dir / 'sp_parcerias_osc_enriquecido.csv'}")


if __name__ == "__main__":
    main()
