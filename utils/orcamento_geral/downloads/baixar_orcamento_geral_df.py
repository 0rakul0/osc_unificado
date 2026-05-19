from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


PACKAGE_ID = "portal-da-transparencia-despesas-da-administracao-publica-do-distrito-federal"
PACKAGE_URL = f"https://www.dados.df.gov.br/api/3/action/package_show?id={PACKAGE_ID}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os ZIPs anuais de despesas do DF no portal oficial de dados abertos."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "DF"),
        help="Pasta onde os arquivos brutos do DF serao salvos.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        help="Anos a baixar. Se omitido, baixa todos os anos publicados.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def download_file(session: requests.Session, url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with session.get(url, stream=True, timeout=300) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    wanted_years = set(args.years or [])

    session = build_session()
    package_response = session.get(PACKAGE_URL, timeout=120)
    package_response.raise_for_status()
    package = package_response.json()["result"]

    manifest: list[dict[str, object]] = []
    for resource in package["resources"]:
        url = resource.get("url") or ""
        match = re.search(r"despesa((?:19|20)\d{2})\.zip", url)
        if not match:
            continue
        year = int(match.group(1))
        if wanted_years and year not in wanted_years:
            continue
        output_path = output_dir / f"despesa{year}.zip"
        if not output_path.exists() or output_path.stat().st_size == 0:
            download_file(session, url, output_path)
        manifest.append(
            {
                "ano": year,
                "arquivo": output_path.name,
                "url": url,
                "resource_id": resource.get("id"),
                "name": resource.get("name"),
            }
        )
        print(f"{year}: {output_path}")

    write_json(output_dir / "df_despesas_manifest.json", sorted(manifest, key=lambda item: item["ano"]))


if __name__ == "__main__":
    main()
