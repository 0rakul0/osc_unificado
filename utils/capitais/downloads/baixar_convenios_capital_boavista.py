from __future__ import annotations

import argparse
import json
import re
from html import unescape
from pathlib import Path
import sys

import pandas as pd
import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PORTAL_URL = "https://transparencia.boavista.rr.gov.br/convenios"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os detalhes oficiais de convenios e transferencias especiais da capital Boa Vista."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Boa Vista"),
        help="Pasta de saida para os arquivos brutos consolidados da capital.",
    )
    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").strip()
    return " ".join(text.split())


def html_to_lines(html_text: str) -> list[str]:
    plain = re.sub(r"<script.*?</script>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
    plain = re.sub(r"<style.*?</style>", " ", plain, flags=re.IGNORECASE | re.DOTALL)
    plain = re.sub(r"<[^>]+>", "\n", plain)
    plain = unescape(plain)
    return [clean_text(line) for line in plain.splitlines() if clean_text(line)]


def capture_after_label(lines: list[str], label: str) -> str:
    for index, line in enumerate(lines):
        if line == label and index + 1 < len(lines):
            return lines[index + 1]
    return ""


def extract_money(value: object) -> str:
    text = clean_text(value)
    match = re.search(r"R\$\s*[\d\.\,]+", text)
    return match.group(0) if match else text


def parse_detail(session: requests.Session, detail_url: str) -> dict[str, object]:
    response = session.get(detail_url, timeout=120, verify=False)
    response.raise_for_status()
    lines = html_to_lines(response.text)
    tables = pd.read_html(detail_url)

    tipo_instr = ""
    numero = ""
    for index, line in enumerate(lines):
        if line in {"Transferencia Especial :", "Convênios :", "Emenda Parlamentares :"} and index + 1 < len(lines):
            tipo_instr = line.replace(" :", "")
            numero = lines[index + 1]
            break

    codigo_plano = capture_after_label(lines, "Código Plano Ação:")
    orgao = capture_after_label(lines, "Orgão")

    objeto = ""
    if "Código Plano Ação:" in lines and "Orgão" in lines:
        start = lines.index("Código Plano Ação:") + 2
        end = lines.index("Orgão")
        objeto = " ".join(lines[start:end]).strip()

    status = ""
    data_inicio = ""
    data_fim = ""
    valor_total = ""
    modalidade = ""
    ano = ""

    if len(tables) >= 2 and not tables[1].empty:
        status = clean_text(tables[1].iloc[0].get("Status"))
        data_inicio = clean_text(tables[1].iloc[0].get("Início da vigência"))
        data_fim = clean_text(tables[1].iloc[0].get("Fim da vigência"))
        year_match = re.search(r"(19|20)\d{2}", data_inicio)
        if year_match:
            ano = year_match.group(0)

    for table in tables:
        if table.empty:
            continue
        columns = [clean_text(column) for column in table.columns]
        first_row = table.iloc[0].to_dict()

        if "Ano Plano Ação" in columns and not ano:
            ano = clean_text(first_row.get("Ano Plano Ação"))
            continue

        if "Categoria Despesa Plano Ação" in columns:
            modalidade = " | ".join(
                clean_text(first_row.get(key))
                for key in ["Categoria Despesa Plano Ação", "Situação Plano Ação"]
                if clean_text(first_row.get(key))
            )
            continue

        if "Valor do Transferencia Especial" in columns:
            valor_total = extract_money(first_row.get("Valor do Transferencia Especial"))
            if not modalidade:
                modalidade = " | ".join(clean_text(value) for value in first_row.values() if clean_text(value))
            continue

        if "Valor Empenhado" in columns or "Valor Liberado" in columns:
            valor_total = extract_money(first_row.get("Valor Empenhado") or first_row.get("Valor Liberado"))
            if not modalidade:
                modalidade = " | ".join(clean_text(value) for value in first_row.values() if clean_text(value))

    if not ano:
        for table in tables:
            if table.empty:
                continue
            first_row = table.iloc[0].to_dict()
            for value in first_row.values():
                year_match = re.search(r"(19|20)\d{2}", clean_text(value))
                if year_match:
                    ano = year_match.group(0)
                    break
            if ano:
                break

    return {
        "ano": ano,
        "tipo_instrumento": tipo_instr,
        "numero": numero or codigo_plano,
        "codigo_plano_acao": codigo_plano,
        "orgao": orgao,
        "status": status,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "objeto": objeto,
        "valor_total": valor_total,
        "modalidade": modalidade,
        "fonte_url": detail_url,
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    main_response = session.get(PORTAL_URL, timeout=120, verify=False)
    main_response.raise_for_status()
    detail_urls = sorted(
        set(
            re.findall(
                r"https://transparencia\.boavista\.rr\.gov\.br/convenios/detalhe/\d+",
                main_response.text,
                flags=re.IGNORECASE,
            )
        )
    )

    records = [parse_detail(session, detail_url) for detail_url in detail_urls]
    csv_path = output_dir / "boavista_convenios.csv"
    manifest_path = output_dir / "boavista_convenios_manifest.json"
    pd.DataFrame(records).to_csv(csv_path, index=False, encoding="utf-8-sig")
    manifest_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saida CSV: {csv_path}")
    print(f"Saida manifest: {manifest_path}")
    print(f"Linhas consolidadas: {len(records)}")


if __name__ == "__main__":
    main()
