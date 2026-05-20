from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


INDEX_URL = "https://www.transparencia.ap.gov.br/informacoes/dados-aberto"
DEFAULT_OUTPUT_DIR = BASES_ORCAMENTO_GERAL_DIR / "AP"
DESPESA_LINK_PATTERN = re.compile(
    r'href=["\'](?P<url>[^"\']*relatorios/dados-aberto/despesas/[^"\']+)["\']',
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baixa arquivos oficiais de despesas gerais do Amapa.")
    parser.add_argument(
        "--output-dir",
        default=cli_default(DEFAULT_OUTPUT_DIR),
        help="Pasta de saida para os arquivos brutos de despesas do AP.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Rebaixa arquivos ja existentes.")
    return parser.parse_args()


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def collect_links(session: requests.Session) -> list[str]:
    response = session.get(INDEX_URL, timeout=120)
    response.raise_for_status()
    links: list[str] = []
    for match in DESPESA_LINK_PATTERN.finditer(response.text):
        url = match.group("url")
        if url.startswith("/"):
            url = f"https://www.transparencia.ap.gov.br{url}"
        if url not in links:
            links.append(url)
    return links


def filename_from_url(url: str) -> str:
    return unquote(url.rsplit("/", 1)[-1]).replace("/", "_").replace("\\", "_")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    session = build_session()

    links = collect_links(session)
    print(f"Links de despesas encontrados: {len(links)}")
    for url in links:
        output_path = output_dir / filename_from_url(url)
        if output_path.exists() and not args.overwrite:
            print(f"Ja existe, pulando: {output_path.name}")
            continue
        response = session.get(url, timeout=300)
        response.raise_for_status()
        output_path.write_bytes(response.content)
        print(f"Baixado: {output_path.name} ({len(response.content)} bytes)")


if __name__ == "__main__":
    main()
