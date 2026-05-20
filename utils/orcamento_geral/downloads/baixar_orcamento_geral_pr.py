from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
from time import sleep

from bs4 import BeautifulSoup
import requests

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


DOCUMENTADOR_BASE_URL = "https://www.fazenda.pr.gov.br"
DOCUMENTADOR_ROUTE = "despesas-exercicios-anteriores"
DOCUMENTADOR_PAGE_URL = f"{DOCUMENTADOR_BASE_URL}/webservices/documentador/{DOCUMENTADOR_ROUTE}"
DOCUMENTADOR_DOWNLOAD_DIR = BASES_ORCAMENTO_GERAL_DIR / "PR" / "documentador"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa pagamentos por credor do documentador oficial da SEFA/PR.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(DOCUMENTADOR_DOWNLOAD_DIR),
        help="Pasta de saida para os arquivos baixados do documentador PR.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        default=["2018", "2019", "2021", "2022", "2023"],
        help="Anos a baixar do documentador. Padrao: anos que complementam os ZIPs locais.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Rebaixa arquivos existentes.")
    return parser.parse_args()


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip()


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": DOCUMENTADOR_PAGE_URL})
    return session


def documentador_html(session: requests.Session, kind: str, folder: str) -> BeautifulSoup:
    response = session.post(
        f"{DOCUMENTADOR_BASE_URL}/webservices/documentador/{DOCUMENTADOR_ROUTE}/{kind}/",
        data={"rota": DOCUMENTADOR_ROUTE, "pasta": folder},
        timeout=120,
    )
    response.raise_for_status()
    return BeautifulSoup(response.json(), "html.parser")


def collect_links(session: requests.Session, years: set[str]) -> list[dict[str, str]]:
    seen_folders: set[str] = set()
    links: list[dict[str, str]] = []

    def walk(folder: str) -> None:
        if folder in seen_folders:
            return
        seen_folders.add(folder)

        files = documentador_html(session, "arquivo", folder)
        for anchor in files.find_all("a"):
            name = anchor.get_text(strip=True)
            url = anchor.get("href")
            if not url or not name or name.lower().startswith("selecione"):
                continue
            year_match = re.search(r"(20\d{2})", folder)
            if not year_match or year_match.group(1) not in years:
                continue
            lowered = f"{folder} {name}".lower()
            if "pagamentos_efetuados" in lowered and name.lower().endswith((".csv", ".xlsx")):
                links.append({"ano": year_match.group(1), "pasta": folder, "arquivo": name, "url": url})

        folders = documentador_html(session, "pasta", folder)
        for anchor in folders.find_all("a"):
            subfolder = anchor.get("id")
            if subfolder:
                walk(subfolder)

    walk("")
    return links


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    links = collect_links(session, {str(year) for year in args.years})
    manifest: list[dict[str, str | int]] = []
    print(f"Arquivos de pagamento encontrados: {len(links)}")

    for index, item in enumerate(links, start=1):
        year_dir = output_dir / item["ano"]
        year_dir.mkdir(parents=True, exist_ok=True)
        output_path = year_dir / safe_filename(item["arquivo"])
        if output_path.exists() and output_path.stat().st_size > 1024 and not args.overwrite:
            print(f"[{index}/{len(links)}] Ja existe: {output_path.name}")
        else:
            print(f"[{index}/{len(links)}] Baixando: {item['ano']} {output_path.name}")
            response = session.get(item["url"], timeout=300)
            response.raise_for_status()
            output_path.write_bytes(response.content)
            sleep(0.2)
        manifest.append({**item, "path": str(output_path), "bytes": output_path.stat().st_size})

    manifest_path = output_dir / "manifest_pagamentos_documentador.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["ano", "pasta", "arquivo", "url", "path", "bytes"])
        writer.writeheader()
        writer.writerows(manifest)
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
