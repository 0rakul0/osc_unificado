from __future__ import annotations

from io import StringIO
from pathlib import Path
import re
import sys

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, HISTORIA_DATA_DIR


PORTO_ALEGRE_DIR = BASES_CONVENIOS_CAPITAIS_DIR / "Porto Alegre"
CONVENIOS_PATH = PORTO_ALEGRE_DIR / "portoalegre_convenios.csv"
OUTPUT_CSV = HISTORIA_DATA_DIR / "porto_alegre_auditoria_fontes.csv"
OUTPUT_XLSX = HISTORIA_DATA_DIR / "porto_alegre_auditoria_fontes.xlsx"

PESQUISA_URL = "https://portaltransparenciapmpa.procempa.com.br/portalpmpa/despEmpDiaPesquisa.do?viaMenu=true"
RELATORIO_URL = "https://portaltransparenciapmpa.procempa.com.br/portalpmpa/despEmpDiaRelatorio.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": PESQUISA_URL,
}
MONTH_ORDER = {
    "Janeiro": 1,
    "Fevereiro": 2,
    "Marco": 3,
    "Marcoo": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12,
}


def normalize_month_label(value: str) -> str:
    return (
        value.replace("ç", "c")
        .replace("Ç", "C")
        .replace("ã", "a")
        .replace("Ã", "A")
        .replace("á", "a")
        .replace("Á", "A")
        .strip()
    )


def parse_money_br(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype("string")
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(r"[^0-9.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)


def parse_csv_payload(text: str) -> pd.DataFrame:
    lines = [line for line in text.splitlines() if line.strip()]
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if "Exerc" in line and ";" in line
        ),
        None,
    )
    if header_index is None:
        raise ValueError("Cabecalho CSV nao encontrado na resposta do portal.")
    payload = "\n".join(lines[header_index:])
    return pd.read_csv(StringIO(payload), sep=";", dtype=str)


def collect_latest_controls(session: requests.Session) -> list[tuple[int, str]]:
    response = session.get(PESQUISA_URL, headers=HEADERS, timeout=120)
    response.raise_for_status()
    controls = sorted(set(re.findall(r'value="((?:19|20)\d{2}[A-Za-z]+)"', response.text)))

    latest_by_year: dict[int, tuple[int, str]] = {}
    for control in controls:
        year = int(control[:4])
        if year < 2000:
            continue
        month_name = normalize_month_label(control[4:])
        month_order = MONTH_ORDER.get(month_name, 0)
        current = latest_by_year.get(year)
        if current is None or month_order >= current[0]:
            latest_by_year[year] = (month_order, control)

    return [(year, latest_by_year[year][1]) for year in sorted(latest_by_year)]


def load_despesas_summary() -> pd.DataFrame:
    session = requests.Session()
    controls = collect_latest_controls(session)
    rows: list[dict[str, object]] = []

    for year, control in controls:
        response = session.get(
            RELATORIO_URL,
            params={
                "perform": "run",
                "criterioFavorecido": "",
                "despControleDOSelecionado": control,
                "acao": "CSV",
            },
            headers=HEADERS,
            timeout=180,
        )
        response.raise_for_status()
        frame = parse_csv_payload(response.text)

        empenhado = parse_money_br(frame.get("Despesa_Empenhada", pd.Series(dtype="string")))
        liquidado = parse_money_br(frame.get("Despesa_Liquidada", pd.Series(dtype="string")))
        pago = parse_money_br(frame.get("Despesa_Paga", pd.Series(dtype="string")))

        rows.append(
            {
                "ano": year,
                "corte_despesa": control,
                "qtd_favorecidos_despesa": int(len(frame)),
                "valor_empenhado_despesa": float(empenhado.sum()),
                "valor_liquidado_despesa": float(liquidado.sum()),
                "valor_pago_despesa": float(pago.sum()),
            }
        )

    return pd.DataFrame(rows)


def load_convenios_summary() -> pd.DataFrame:
    if not CONVENIOS_PATH.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {CONVENIOS_PATH}")

    frame = pd.read_csv(CONVENIOS_PATH, dtype=str, encoding="utf-8-sig")
    if "ano" not in frame.columns:
        frame["ano"] = pd.to_datetime(
            frame.get("data_inicio_lista"),
            errors="coerce",
            dayfirst=True,
        ).dt.year.astype("Int64").astype("string")

    frame["ano"] = pd.to_numeric(frame["ano"], errors="coerce").astype("Int64")
    frame["valor_convenio_num"] = parse_money_br(frame.get("valor_lista", pd.Series(dtype="string")))

    grouped = (
        frame.dropna(subset=["ano"])
        .groupby("ano", dropna=True)
        .agg(
            qtd_convenios=("ano", "size"),
            valor_total_convenios=("valor_convenio_num", "sum"),
        )
        .reset_index()
    )
    grouped["ano"] = grouped["ano"].astype(int)
    return grouped


def build_audit_matrix() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    convenios = load_convenios_summary()
    despesas = load_despesas_summary()

    audit = convenios.merge(despesas, on="ano", how="outer").sort_values("ano").reset_index(drop=True)

    for column in [
        "qtd_convenios",
        "valor_total_convenios",
        "qtd_favorecidos_despesa",
        "valor_empenhado_despesa",
        "valor_liquidado_despesa",
        "valor_pago_despesa",
    ]:
        if column in audit.columns:
            audit[column] = audit[column].fillna(0)

    audit["qtd_convenios"] = audit["qtd_convenios"].astype(int)
    audit["qtd_favorecidos_despesa"] = audit["qtd_favorecidos_despesa"].astype(int)
    audit["fonte_convenios"] = audit["qtd_convenios"].gt(0)
    audit["fonte_despesa"] = audit["qtd_favorecidos_despesa"].gt(0)
    audit["fontes_disponiveis"] = audit.apply(
        lambda row: "convenios+despesas"
        if row["fonte_convenios"] and row["fonte_despesa"]
        else "convenios"
        if row["fonte_convenios"]
        else "despesas"
        if row["fonte_despesa"]
        else "sem_dados",
        axis=1,
    )

    return audit, convenios, despesas


def save_outputs(audit: pd.DataFrame, convenios: pd.DataFrame, despesas: pd.DataFrame) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        audit.to_excel(writer, index=False, sheet_name="matriz")
        convenios.to_excel(writer, index=False, sheet_name="convenios")
        despesas.to_excel(writer, index=False, sheet_name="despesas")


def main() -> None:
    audit, convenios, despesas = build_audit_matrix()
    save_outputs(audit, convenios, despesas)

    print(f"Convenios: {CONVENIOS_PATH}")
    print(f"Saida CSV: {OUTPUT_CSV}")
    print(f"Saida XLSX: {OUTPUT_XLSX}")
    print()
    print(audit.to_string(index=False))


if __name__ == "__main__":
    main()
