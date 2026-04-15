from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR


SOURCE_URL = "https://www.transparencia.curitiba.pr.gov.br/conteudo/convenios.aspx"


def repair_mojibake(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if not text:
        return pd.NA
    try:
        repaired = text.encode("latin1").decode("utf-8")
        return repaired.strip() or pd.NA
    except UnicodeError:
        return text


def tuple_text(value: object) -> object:
    if isinstance(value, tuple):
        return value[0]
    return value


def tuple_link(value: object) -> object:
    if isinstance(value, tuple):
        return value[1]
    return pd.NA


def main() -> None:
    output_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Curitiba"
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "curitiba_convenios.html"
    csv_path = output_dir / "curitiba_convenios.csv"

    response = requests.get(SOURCE_URL, timeout=120)
    response.raise_for_status()
    html_path.write_text(response.text, encoding="utf-8")

    frame = pd.read_html(html_path, flavor="lxml", extract_links="all")[0]
    normalized = pd.DataFrame(
        {
            "orgao_gestor": frame.iloc[:, 0].map(tuple_text),
            "termo_ajuste": frame.iloc[:, 1].map(tuple_text),
            "siafi_transfereg_sit": frame.iloc[:, 2].map(tuple_text),
            "numero": frame.iloc[:, 3].map(tuple_text),
            "ano": frame.iloc[:, 4].map(tuple_text),
            "objeto": frame.iloc[:, 5].map(tuple_text),
            "valor_concedente": frame.iloc[:, 6].map(tuple_text),
            "valor_contrapartida": frame.iloc[:, 7].map(tuple_text),
            "valor_total": frame.iloc[:, 8].map(tuple_text),
            "vigencia": frame.iloc[:, 9].map(tuple_text),
            "fiscal": frame.iloc[:, 10].map(tuple_text),
            "contrato_texto": frame.iloc[:, 11].map(tuple_text),
            "contrato_url": frame.iloc[:, 11].map(tuple_link),
        }
    )

    for column in normalized.columns:
        normalized[column] = normalized[column].map(repair_mojibake)

    normalized.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(html_path)
    print(csv_path)


if __name__ == "__main__":
    main()
