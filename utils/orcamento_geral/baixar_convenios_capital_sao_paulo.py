from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


PACKAGE_ID = "0fe868fc-4d8d-468a-a3e0-a2b512da96e3"
PACKAGE_SHOW_URL = "https://dados.prefeitura.sp.gov.br/api/3/action/package_show"
PORTAL_URL = f"https://dados.prefeitura.sp.gov.br/dataset/{PACKAGE_ID}"
MONTHS = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa o CSV mais recente de parcerias de educacao infantil da capital Sao Paulo."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Sao Paulo"),
        help="Pasta onde o CSV oficial da capital sera salvo.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def parse_resource_period(resource: dict[str, object]) -> tuple[int, int]:
    text = " ".join(
        str(resource.get(field) or "")
        for field in ("name", "description", "url")
    ).lower()
    year_match = re.search(r"(20\d{2})", text)
    month = 0
    for label, value in MONTHS.items():
        if re.search(rf"\b{label}\b", text):
            month = value
            break
    year = int(year_match.group(1)) if year_match else 0
    return year, month


def pick_latest_csv(resources: list[dict[str, object]]) -> dict[str, object]:
    candidates = [
        resource
        for resource in resources
        if str(resource.get("format") or "").upper() == "CSV"
        and "dicion" not in str(resource.get("name") or "").lower()
        and resource.get("url")
    ]
    if not candidates:
        raise ValueError("Nenhum CSV util foi encontrado no dataset de Sao Paulo.")
    candidates.sort(key=parse_resource_period, reverse=True)
    return candidates[0]


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    try:
        response = session.get(PACKAGE_SHOW_URL, params={"id": PACKAGE_ID}, timeout=120)
        response.raise_for_status()
        payload = response.json()
        result = payload.get("result") if isinstance(payload, dict) else None
        if not isinstance(result, dict):
            raise ValueError("Resposta inesperada do CKAN de Sao Paulo.")
        resources = result.get("resources") if isinstance(result.get("resources"), list) else []
        latest = pick_latest_csv(resources)

        csv_url = str(latest.get("url"))
        csv_response = session.get(csv_url, timeout=120)
        csv_response.raise_for_status()
    finally:
        session.close()

    year, month = parse_resource_period(latest)
    suffix = f"{year}_{month:02d}" if year else str(latest.get("id") or "atual")
    output_path = output_dir / f"sao_paulo_parcerias_educacao_infantil_{suffix}.csv"
    output_path.write_bytes(csv_response.content)

    manifest = {
        "dataset_id": PACKAGE_ID,
        "dataset_titulo": result.get("title"),
        "resource_id": latest.get("id"),
        "resource_name": latest.get("name"),
        "resource_format": latest.get("format"),
        "resource_url": csv_url,
        "arquivo_local": str(output_path),
        "periodo": {"ano": year, "mes": month},
        "fonte_portal": PORTAL_URL,
    }
    write_json(output_dir / "sao_paulo_parcerias_manifest.json", manifest)

    print(f"Sao Paulo: {latest.get('name')} -> {output_path}")


if __name__ == "__main__":
    main()
