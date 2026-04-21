from __future__ import annotations

from hashlib import sha256
import json
from io import StringIO
from pathlib import Path
import re
import sys

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, ensure_parent_dir


PESQUISA_URL = "https://portaltransparenciapmpa.procempa.com.br/portalpmpa/despEmpDiaPesquisa.do?viaMenu=true"
RELATORIO_URL = "https://portaltransparenciapmpa.procempa.com.br/portalpmpa/despEmpDiaRelatorio.do"
OUTPUT_DIR = BASES_CONVENIOS_CAPITAIS_DIR / "Porto Alegre" / "despesas_por_favorecido_raw"
PAGE_SNAPSHOT_PATH = OUTPUT_DIR / "despEmpDiaPesquisa.html"
MANIFEST_PATH = OUTPUT_DIR / "manifesto.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": PESQUISA_URL,
}
MONTH_ORDER = {
    "Janeiro": 1,
    "Fevereiro": 2,
    "Marco": 3,
    "Marcoo": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12,
}


def normalize_month_label(value: str) -> str:
    return (
        value.replace("ç", "c")
        .replace("Ç", "C")
        .replace("ã", "a")
        .replace("Ã", "A")
        .replace("á", "a")
        .replace("Á", "A")
        .strip()
    )


def detect_encoding(response: requests.Response) -> str:
    return response.encoding or response.apparent_encoding or "latin-1"


def parse_csv_payload(text: str) -> pd.DataFrame:
    lines = [line for line in text.splitlines() if line.strip()]
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if "Exerc" in line and ";" in line
        ),
        None,
    )
    if header_index is None:
        raise ValueError("Cabecalho CSV nao encontrado na resposta do portal.")
    return pd.read_csv(StringIO("\n".join(lines[header_index:])), sep=";", dtype=str)


def collect_latest_controls(session: requests.Session) -> tuple[list[dict[str, object]], str]:
    response = session.get(PESQUISA_URL, headers=HEADERS, timeout=120)
    response.raise_for_status()
    html = response.text
    controls = sorted(set(re.findall(r'value="((?:19|20)\d{2}[A-Za-z]+)"', html)))

    latest_by_year: dict[int, tuple[int, str]] = {}
    for control in controls:
        year = int(control[:4])
        if year < 2000:
            continue
        month_name = normalize_month_label(control[4:])
        month_order = MONTH_ORDER.get(month_name, 0)
        current = latest_by_year.get(year)
        if current is None or month_order >= current[0]:
            latest_by_year[year] = (month_order, control)

    selected = [
        {
            "ano": year,
            "controle": latest_by_year[year][1],
            "ordem_mes": latest_by_year[year][0],
        }
        for year in sorted(latest_by_year)
    ]
    return selected, html


def main() -> None:
    ensure_parent_dir(MANIFEST_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    controls, html = collect_latest_controls(session)
    PAGE_SNAPSHOT_PATH.write_text(html, encoding="utf-8")

    manifest: list[dict[str, object]] = []
    for item in controls:
        year = int(item["ano"])
        control = str(item["controle"])
        response = session.get(
            RELATORIO_URL,
            params={
                "perform": "run",
                "criterioFavorecido": "",
                "despControleDOSelecionado": control,
                "acao": "CSV",
            },
            headers=HEADERS,
            timeout=180,
        )
        response.raise_for_status()

        raw_bytes = response.content
        output_path = OUTPUT_DIR / f"portoalegre_despesas_favorecido_{year}_{control}.csv"
        output_path.write_bytes(raw_bytes)

        encoding = detect_encoding(response)
        text = raw_bytes.decode(encoding, errors="replace")
        frame = parse_csv_payload(text)

        manifest.append(
            {
                "ano": year,
                "controle": control,
                "arquivo": output_path.name,
                "url": response.url,
                "encoding": encoding,
                "linhas": int(len(frame)),
                "bytes": int(len(raw_bytes)),
                "sha256": sha256(raw_bytes).hexdigest(),
            }
        )
        print(f"{year}: {len(frame)} linhas -> {output_path}")

    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "fonte": PESQUISA_URL,
                "relatorio": RELATORIO_URL,
                "arquivos": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Manifesto: {MANIFEST_PATH}")
    print(f"HTML de descoberta: {PAGE_SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
