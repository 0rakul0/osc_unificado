from __future__ import annotations

import argparse
import html
import re
import time
from pathlib import Path
import sys

import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, cli_default


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://transparencia.teresina.pi.gov.br/bp/parcerias"
ROW_KEYS = ("0_0", "0_1", "0_2", "0_3")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa os relatorios brutos de parcerias de Teresina."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR / "Teresina"),
        help="Pasta de saida para os relatorios baixados.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=4,
        help="Quantidade de tentativas por etapa do portal.",
    )
    return parser.parse_args()


def fetch_with_retry(session: requests.Session, method: str, url: str, retries: int, **kwargs) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = session.request(method, url, verify=False, **kwargs)
            response.raise_for_status()
            return response
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == retries:
                raise
            time.sleep(min(5 * attempt, 20))
    assert last_error is not None
    raise last_error


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    landing = fetch_with_retry(session, "GET", BASE_URL, args.retries, timeout=(30, 180))
    viewstate_match = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', landing.text)
    if not viewstate_match:
        raise RuntimeError("Nao foi possivel localizar o ViewState da pagina de parcerias de Teresina.")

    viewstate = viewstate_match.group(1)
    for rowkey in ROW_KEYS:
        ajax_response = fetch_with_retry(
            session,
            "POST",
            BASE_URL,
            args.retries,
            headers={"Faces-Request": "partial/ajax"},
            data={
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "pasta",
                "javax.faces.partial.execute": "pasta",
                "javax.faces.partial.render": "j_idt20",
                "javax.faces.behavior.event": "select",
                "javax.faces.partial.event": "select",
                "j_idt20": "j_idt20",
                "pasta": "pasta",
                "pasta_selection": rowkey,
                "javax.faces.ViewState": viewstate,
            },
            timeout=(30, 180),
        )
        redirect_match = re.search(r'redirect url="([^"]+)"', ajax_response.text)
        if not redirect_match:
            raise RuntimeError(f"Nao foi possivel obter o link de download do item {rowkey}.")

        redirect_url = html.unescape(redirect_match.group(1))
        filename_match = re.search(r"filename=([^&]+)", redirect_url)
        filename = filename_match.group(1) if filename_match else f"{rowkey}.bin"
        target_path = output_dir / filename

        file_response = fetch_with_retry(
            session,
            "GET",
            requests.compat.urljoin(BASE_URL, redirect_url),
            args.retries,
            timeout=(30, 300),
        )
        target_path.write_bytes(file_response.content)
        print(f"Arquivo salvo: {target_path}")


if __name__ == "__main__":
    main()
