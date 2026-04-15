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


PAGE_URL = "https://transparencia.ac.gov.br/convenios"
DETAIL_URL = "https://transparencia.ac.gov.br/convenios/detalhamento-pdf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa o detalhamento oficial de convenios do portal de transparencia do Acre."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "AC"),
        help="Pasta onde os arquivos brutos do Acre serao salvos.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = build_session()
    page_response = session.get(PAGE_URL, timeout=120)
    page_response.raise_for_status()

    csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', page_response.text)
    if not csrf_match:
        raise ValueError("Nao foi possivel localizar o csrf-token da pagina de convenios do Acre.")

    csrf_token = csrf_match.group(1)
    post_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": PAGE_URL,
        "X-CSRF-TOKEN": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
    }
    payload = {
        "situacao": "",
        "ano": "",
        "orgao": "",
        "busca": "",
        "filtro": "0",
        "fonte": "",
        "periodo": "",
        "inicio": "",
        "fim": "",
        "mes": "",
        "bimestre": "",
        "trimestre": "",
        "quadrimestre": "",
        "semestre": "",
    }

    details_response = session.post(DETAIL_URL, data=payload, headers=post_headers, timeout=300)
    details_response.raise_for_status()
    rows = details_response.json()
    if not isinstance(rows, list):
        raise ValueError(f"Resposta inesperada em {DETAIL_URL}: {type(rows).__name__}")

    summary = {
        "fonte_pagina": PAGE_URL,
        "fonte_detalhamento": DETAIL_URL,
        "total_registros": len(rows),
        "atualizado_em": re.search(r"Dados atualizados em:</b>\s*([^<]+)", page_response.text).group(1).strip()
        if re.search(r"Dados atualizados em:</b>\s*([^<]+)", page_response.text)
        else "",
    }

    write_json(output_dir / "ac_convenios_detalhamento.json", rows)
    write_json(output_dir / "ac_convenios_resumo.json", summary)

    print(f"Fonte oficial: {PAGE_URL}")
    print(f"Detalhamento: {DETAIL_URL}")
    print(f"Registros baixados: {len(rows)}")
    print(f"Saida principal: {output_dir / 'ac_convenios_detalhamento.json'}")


if __name__ == "__main__":
    main()
