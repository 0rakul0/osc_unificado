from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path
import sys
from urllib.parse import urljoin, urlparse

import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_DIR, cli_default


BASE_URL = "https://dadosabertos.go.gov.br"
SEARCH_PAGES = (
    f"{BASE_URL}/dataset/?q=convenios",
    f"{BASE_URL}/dataset/?page=2&q=convenios",
)
GO_DIR = BASES_CONVENIOS_DIR / "GO"
DOWNLOADS_DIRNAME = "dadosabertos_goias_convenios"
LEGACY_ZIP_NAME = "convenios_2008_2018.zip"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os datasets de convenios do portal Dados Abertos de Goias e organiza na base local."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(GO_DIR),
        help="Diretorio raiz de saida da base de convenios de GO.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout em segundos para requisicoes HTTP.",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", text.lower()).strip("-")


def download_file(url: str, destination: Path, timeout: int) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=HEADERS, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    return destination.stat().st_size


def extract_legacy_zip(zip_path: Path, extract_dir: Path) -> None:
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)


def scrape_dataset_urls(timeout: int) -> list[str]:
    dataset_urls: list[str] = []
    seen: set[str] = set()
    for page_url in SEARCH_PAGES:
        html = requests.get(page_url, headers=HEADERS, timeout=timeout).text
        for href in re.findall(r'href="(/(?:pt_BR/)?dataset/[^"#?]+)"', html):
            dataset_url = urljoin(BASE_URL, href)
            if "/resource/" in dataset_url:
                continue
            slug = dataset_url.rstrip("/").rsplit("/", 1)[-1].lower()
            if not re.search(r"conveni|convenio|conveniada", slug):
                continue
            if dataset_url in seen:
                continue
            seen.add(dataset_url)
            dataset_urls.append(dataset_url)
    return dataset_urls


def scrape_resource_urls(dataset_url: str, timeout: int) -> list[str]:
    html = requests.get(dataset_url, headers=HEADERS, timeout=timeout).text
    resources = [
        urljoin(BASE_URL, href.replace("&amp;", "&"))
        for href in re.findall(r'href="([^"]+/download/[^"]+)"', html)
    ]
    deduped: list[str] = []
    seen: set[str] = set()
    for resource_url in resources:
        if resource_url in seen:
            continue
        seen.add(resource_url)
        deduped.append(resource_url)
    return deduped


def download_go_convenios(output_dir: Path, timeout: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir = output_dir / DOWNLOADS_DIRNAME
    downloads_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, object]] = []
    dataset_urls = scrape_dataset_urls(timeout)

    for dataset_url in dataset_urls:
        dataset_slug = dataset_url.rstrip("/").rsplit("/", 1)[-1]
        dataset_dir = downloads_dir / dataset_slug
        resource_urls = scrape_resource_urls(dataset_url, timeout)

        for resource_url in resource_urls:
            file_name = Path(urlparse(resource_url).path).name
            destination = dataset_dir / file_name
            size = download_file(resource_url, destination, timeout)
            manifest_rows.append(
                {
                    "dataset_url": dataset_url,
                    "dataset_slug": dataset_slug,
                    "resource_url": resource_url,
                    "file_name": file_name,
                    "local_path": str(destination),
                    "size_bytes": size,
                }
            )

            if file_name == LEGACY_ZIP_NAME:
                legacy_zip_path = output_dir / LEGACY_ZIP_NAME
                shutil.copy2(destination, legacy_zip_path)
                extract_legacy_zip(legacy_zip_path, output_dir / legacy_zip_path.stem)

    manifest_path = downloads_dir / "manifest_go_convenios.json"
    manifest_payload = {
        "source_query_pages": list(SEARCH_PAGES),
        "dataset_count": len(dataset_urls),
        "resource_count": len(manifest_rows),
        "resources": manifest_rows,
    }
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    manifest_path = download_go_convenios(output_dir, args.timeout)
    print(f"Diretorio GO: {output_dir}")
    print(f"Manifesto: {manifest_path}")


if __name__ == "__main__":
    main()
