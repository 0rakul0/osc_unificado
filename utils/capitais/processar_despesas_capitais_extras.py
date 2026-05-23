from __future__ import annotations

import re
import sys
import unicodedata
from io import StringIO
import json
from pathlib import Path

import pandas as pd
import polars as pl
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, CAPITAIS_PROCESSADA_DIR


STANDARD_COLUMNS = [
    "uf",
    "origem",
    "ano",
    "valor_total",
    "cnpj",
    "nome_osc",
    "mes",
    "cod_municipio",
    "municipio",
    "objeto",
    "modalidade",
    "data_inicio",
    "data_fim",
]


def only_cnpj(value: object) -> str | None:
    if pd.isna(value):
        return None
    digits = re.sub(r"\D+", "", str(value))
    if len(digits) == 14:
        return digits
    if 12 <= len(digits) <= 14:
        return digits.zfill(14)
    return None


def parse_money(value: object) -> float:
    if pd.isna(value):
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    text = text.replace("R$", "").strip()
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def normalize_name(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    return " ".join(text.split())


def normalize_key(value: object) -> str | None:
    text = normalize_name(value)
    if not text:
        return None
    text = unicodedata.normalize("NFKD", text.upper()).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def write_standard(frame: pd.DataFrame, path: Path) -> None:
    for column in STANDARD_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    frame = frame[STANDARD_COLUMNS].drop_duplicates().reset_index(drop=True)
    table = pl.from_pandas(frame)
    table = table.with_columns(
        pl.col("valor_total").cast(pl.Decimal(20, 2), strict=False),
        *[pl.col(column).cast(pl.String) for column in STANDARD_COLUMNS if column != "valor_total"],
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    table.write_parquet(path)


def process_curitiba() -> tuple[Path, int]:
    source_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Curitiba" / "despesas_historico"
    sources = sorted(source_dir.glob("*Despesas_-_Base_de_Dados.csv"))
    if not sources:
        sources = [BASES_CONVENIOS_CAPITAIS_DIR / "Curitiba" / "curitiba_Despesas_-_Base_de_Dados.csv"]
    chunks: list[pd.DataFrame] = []
    for source in sources:
        for chunk in pd.read_csv(source, sep=";", dtype=str, encoding="latin1", chunksize=200_000):
            chunk = chunk[chunk["ANO_EMPENHO"].str.match(r"^\d{4}$", na=False)].copy()
            chunk["cnpj"] = chunk["CPF_CNPJ"].map(only_cnpj)
            chunk = chunk.dropna(subset=["cnpj"]).copy()
            value = chunk["VL_PAGO"].map(parse_money)
            fallback = chunk["VL_LIQUIDADO"].map(parse_money)
            chunk["valor_total"] = value.where(value.ne(0), fallback)
            mapped = pd.DataFrame(
                {
                    "uf": "PR",
                    "origem": "capitais",
                    "ano": chunk["ANO_EMPENHO"],
                    "valor_total": chunk["valor_total"],
                    "cnpj": chunk["cnpj"],
                    "nome_osc": pd.NA,
                    "mes": pd.to_datetime(chunk["DT_TRANSACAO"], errors="coerce").dt.month.astype("Int64").astype("string"),
                    "cod_municipio": pd.NA,
                    "municipio": "Curitiba",
                    "objeto": chunk["DS_ACAO"].fillna(chunk["DS_DESPESA"]),
                    "modalidade": "despesa",
                    "data_inicio": chunk["DT_EMPENHO"],
                    "data_fim": pd.NA,
                }
            )
            chunks.append(mapped)
    output = CAPITAIS_PROCESSADA_DIR / "PR_CURITIBA_DESPESAS.parquet"
    frame = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=STANDARD_COLUMNS)
    write_standard(frame, output)
    return output, len(frame)


def parse_porto_alegre_file(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="latin1", errors="replace")
    lines = [line for line in text.splitlines() if line.strip()]
    header_index = next(index for index, line in enumerate(lines) if "Exerc" in line and ";" in line)
    return pd.read_csv(StringIO("\n".join(lines[header_index:])), sep=";", dtype=str)


def process_porto_alegre() -> tuple[Path, int]:
    raw_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Porto Alegre" / "despesas_por_favorecido_raw"
    frames: list[pd.DataFrame] = []
    for path in sorted(raw_dir.glob("portoalegre_despesas_favorecido_*.csv")):
        raw = parse_porto_alegre_file(path)
        raw["valor_total"] = raw["Despesa_Paga"].map(parse_money)
        mapped = pd.DataFrame(
            {
                "uf": "RS",
                "origem": "capitais",
                "ano": raw["Exercício"],
                "valor_total": raw["valor_total"],
                "cnpj": pd.NA,
                "nome_osc": raw["Nome/Razão Social Favorecidos"].map(normalize_name),
                "mes": pd.to_datetime(raw["Ponto de Corte"], errors="coerce", dayfirst=True).dt.month.astype("Int64").astype("string"),
                "cod_municipio": pd.NA,
                "municipio": "Porto Alegre",
                "objeto": pd.NA,
                "modalidade": "despesa",
                "data_inicio": raw["Ponto de Corte"],
                "data_fim": pd.NA,
            }
        )
        frames.append(mapped)
    output = CAPITAIS_PROCESSADA_DIR / "RS_PORTO_ALEGRE_DESPESAS.parquet"
    frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=STANDARD_COLUMNS)
    write_standard(frame, output)
    return output, len(frame)


def process_aracaju() -> tuple[Path, int]:
    url = "https://www.municipioonline.com.br/se/prefeitura/aracaju/cidadao/despesa?tipo=empenho"
    output_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Aracaju"
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "aracaju_despesas_municipioonline_empenhos.html"
    response = requests.get(url, timeout=120, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    html_path.write_text(response.text, encoding="utf-8")

    table = pd.read_html(response.text)[0]
    table["cnpj"] = table["CPF/CNPJ Credor"].map(only_cnpj)
    table = table.dropna(subset=["cnpj"]).copy()
    paid = table["Pago"].map(parse_money)
    liquidated = table["Liquidado"].map(parse_money)
    committed = table["Empenhado"].map(parse_money)
    table["valor_total"] = paid.where(paid.ne(0), liquidated.where(liquidated.ne(0), committed))
    dates = pd.to_datetime(table["Data"], errors="coerce", dayfirst=True)

    mapped = pd.DataFrame(
        {
            "uf": "SE",
            "origem": "capitais",
            "ano": dates.dt.year.astype("Int64").astype("string"),
            "valor_total": table["valor_total"],
            "cnpj": table["cnpj"],
            "nome_osc": table["Credor"].map(normalize_name),
            "mes": dates.dt.month.astype("Int64").astype("string"),
            "cod_municipio": pd.NA,
            "municipio": "Aracaju",
            "objeto": table["Elemento"],
            "modalidade": "despesa",
            "data_inicio": table["Data"],
            "data_fim": pd.NA,
        }
    )
    output = CAPITAIS_PROCESSADA_DIR / "SE_ARACAJU_DESPESAS.parquet"
    write_standard(mapped, output)
    return output, len(mapped)


def process_cuiaba() -> tuple[Path, int]:
    raw_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Cuiaba" / "despesas_por_credor"
    frames: list[pd.DataFrame] = []
    for path in sorted(raw_dir.glob("cuiaba_despesas_credor_*.json")):
        year_match = re.search(r"(\d{4})", path.name)
        year = year_match.group(1) if year_match else None
        records = json.loads(path.read_text(encoding="utf-8"))
        if not records:
            continue
        raw = pd.DataFrame(records)
        raw["cnpj"] = raw["DespesaCredorDoc"].map(only_cnpj)
        raw = raw.dropna(subset=["cnpj"]).copy()
        paid = raw["DespesaPagamento"].map(parse_money)
        liquidated = raw["DespesaLiquidacao"].map(parse_money)
        committed = raw["DespesaEmpenho"].map(parse_money)
        raw["valor_total"] = paid.where(paid.ne(0), liquidated.where(liquidated.ne(0), committed))
        mapped = pd.DataFrame(
            {
                "uf": "MT",
                "origem": "capitais",
                "ano": year,
                "valor_total": raw["valor_total"],
                "cnpj": raw["cnpj"],
                "nome_osc": raw["DespesaCredorNome"].map(normalize_name),
                "mes": pd.NA,
                "cod_municipio": pd.NA,
                "municipio": "Cuiaba",
                "objeto": pd.NA,
                "modalidade": "despesa",
                "data_inicio": pd.NA,
                "data_fim": pd.NA,
            }
        )
        frames.append(mapped)
    output = CAPITAIS_PROCESSADA_DIR / "MT_CUIABA_DESPESAS.parquet"
    frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=STANDARD_COLUMNS)
    write_standard(frame, output)
    return output, len(frame)


def read_goiania_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, sep=";", dtype=str, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, sep=";", dtype=str, encoding="latin1")


def process_goiania() -> tuple[Path, int]:
    raw_dir = BASES_CONVENIOS_CAPITAIS_DIR / "Goiania" / "despesas"
    frames: list[pd.DataFrame] = []
    for path in sorted(raw_dir.glob("goiania_despesas_*.csv")):
        raw = read_goiania_csv(path)
        if raw.empty or "CNPJ" not in raw.columns:
            continue
        raw["cnpj"] = raw["CNPJ"].map(only_cnpj)
        raw = raw.dropna(subset=["cnpj"]).copy()
        if raw.empty:
            continue
        paid = raw["VlPago"].map(parse_money)
        liquidated = raw["VlLiquidado"].map(parse_money)
        committed = raw["VlEmpenhado"].map(parse_money)
        raw["valor_total"] = paid.where(paid.ne(0), liquidated.where(liquidated.ne(0), committed))
        dates = pd.to_datetime(raw["DataEmpenho"], errors="coerce", dayfirst=True)
        mapped = pd.DataFrame(
            {
                "uf": "GO",
                "origem": "capitais",
                "ano": dates.dt.year.astype("Int64").astype("string"),
                "valor_total": raw["valor_total"],
                "cnpj": raw["cnpj"],
                "nome_osc": raw["NmFavorecido"].map(normalize_name),
                "mes": dates.dt.month.astype("Int64").astype("string"),
                "cod_municipio": pd.NA,
                "municipio": "Goiania",
                "objeto": raw.get("Objeto"),
                "modalidade": "despesa",
                "data_inicio": raw["DataEmpenho"],
                "data_fim": pd.NA,
            }
        )
        frames.append(mapped)
    output = CAPITAIS_PROCESSADA_DIR / "GO_GOIANIA_DESPESAS.parquet"
    frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=STANDARD_COLUMNS)
    write_standard(frame, output)
    return output, len(frame)


def main() -> None:
    for output, rows in [
        process_curitiba(),
        process_porto_alegre(),
        process_aracaju(),
        process_cuiaba(),
        process_goiania(),
    ]:
        print(f"{output}: {rows} linhas")


if __name__ == "__main__":
    main()
