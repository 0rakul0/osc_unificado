from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata

import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


API_URL = "https://dados.recife.pe.gov.br/api/3/action/package_show"
DATASET_ID = "despesas-orcamentarias"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa todos os recursos de despesas do dataset oficial do Recife."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Recife"),
        help="Pasta de saida para os arquivos brutos consolidados da capital.",
    )
    return parser.parse_args()


def ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return re.sub(r"-+", "-", text)


def is_expense_resource(resource: dict[str, object]) -> bool:
    name = str(resource.get("name") or "")
    name_lower = name.lower()
    if "metadado" in name_lower or "dicion" in name_lower:
        return False
    if "despesa" not in name_lower:
        return False
    resource_format = str(resource.get("format") or "").lower()
    return resource_format == "csv"


def target_filename(resource: dict[str, object]) -> str:
    name = str(resource.get("name") or resource.get("id") or "recurso")
    url = str(resource.get("url") or "")
    extension = Path(url).suffix or ".csv"
    slug = ascii_slug(name)
    if not slug:
        slug = "recurso"
    return f"recife_{slug}{extension}"


def load_resources() -> list[dict[str, object]]:
    response = requests.get(API_URL, params={"id": DATASET_ID}, timeout=120)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError("API do Recife retornou sucesso=false.")

    resources = payload["result"].get("resources", [])
    deduped: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for resource in resources:
        resource_id = str(resource.get("id") or "")
        resource_url = str(resource.get("url") or "")
        if resource_id and resource_id in seen_ids:
            continue
        if resource_url and resource_url in seen_urls:
            continue
        if resource_id:
            seen_ids.add(resource_id)
        if resource_url:
            seen_urls.add(resource_url)
        if is_expense_resource(resource):
            deduped.append(resource)
    return deduped


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    resources = load_resources()
    if not resources:
        raise RuntimeError("Nenhum recurso de despesa foi encontrado no dataset do Recife.")

    session = requests.Session()
    manifest: list[dict[str, object]] = []

    for resource in resources:
        name = str(resource.get("name") or "")
        url = str(resource.get("url") or "")
        filename = target_filename(resource)
        target_path = output_dir / filename

        response = session.get(url, timeout=300)
        response.raise_for_status()
        target_path.write_bytes(response.content)

        manifest.append(
            {
                "id": resource.get("id"),
                "nome": name,
                "arquivo": filename,
                "url": url,
                "formato": resource.get("format"),
                "bytes": len(response.content),
            }
        )
        print(f"Arquivo salvo: {target_path}")

    manifest_path = output_dir / "recife_despesas_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest salvo: {manifest_path}")
    print(f"Arquivos baixados: {len(manifest)}")


if __name__ == "__main__":
    main()
