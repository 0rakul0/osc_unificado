from __future__ import annotations

import json
from pathlib import Path
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR


PACKAGE_ID = "4be26342-7e53-447c-8816-f6a609655d0c"
API_URL = f"https://dados.df.gov.br/api/3/action/package_show?id={PACKAGE_ID}"


def main() -> None:
    output_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Brasilia"
    output_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(API_URL, timeout=120)
    response.raise_for_status()
    payload = response.json()["result"]

    manifest: list[dict[str, str]] = []
    for resource in payload.get("resources", []):
        name = str(resource.get("name", ""))
        url = str(resource.get("url", ""))
        if "Convênios de Despesa -" not in name or not url.lower().endswith(".csv"):
            continue

        year = "".join(ch for ch in name if ch.isdigit())[-4:]
        output_path = output_dir / f"brasilia_convenios_{year}.csv"
        download = requests.get(url, timeout=120)
        download.raise_for_status()
        output_path.write_bytes(download.content)
        manifest.append({"name": name, "url": url, "path": str(output_path)})
        print(output_path)

    manifest_path = output_dir / "brasilia_convenios_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
