from __future__ import annotations

import argparse
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq
import requests

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import ORCAMENTO_GERAL_PROCESSADA_DIR, cli_default
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.common import STANDARD_COLUMNS, clean_document, normalize_name
from utils.orcamento_geral.paths import add_scope_argument, default_output_name, uf_raw_dir


ORIGEM_ORCAMENTO_GERAL = "orcamento_geral"
DETAIL_URL = "https://api-notas-empenho.sistemas.pa.gov.br/notas-empenho/detalhe"
THREAD_LOCAL = threading.local()
ENTITY_LIKE_PATTERN = re.compile(
    r"(ASSOCIAC|INSTITUT|FUNDAC|COOPERAT|LTDA|EIRELI|S/A| SA$| SA |MEI|EPP|ME$|ME |"
    r"PREFEITURA|MUNICIP|SECRETARIA|TRIBUNAL|BANCO|CAIXA|UNIAO|ESTADO|SERVICOS|SERVIÇOS|"
    r"CONSTRUT|ENGENHARIA|COMERCIO|COMÉRCIO|HOSPITAL|SANTA CASA|CLINICA|CLÍNICA|UNIVERSIDADE|"
    r"FACULDADE|EMPRESA|CIA|COMPANHIA|CONSORCIO|CONSÓRCIO|FARMACIA|FARMÁCIA|LABORATORIO|"
    r"LABORATÓRIO|PAROQUIA|IGREJA|MINISTERIO|MINISTÉRIO|ORGANIZACAO|ORGANIZAÇÃO|SOCIEDADE|"
    r"FEDERACAO|FEDERAÇÃO|SINDICATO|APAE|PESTALOZZI|LIGA |CLUBE |CARTORIO|CARTÓRIO|CASA |"
    r"FUNDO |DEPARTAMENTO|INSTITUICAO|INSTITUIÇÃO|SEBRAE|SESC|SENAI|SENAC|SEST|SENAT|"
    r"CONSELHO|ORDEM DOS ADVOGADOS|OAB|MUSEU|ACADEMIA|CENTRO |COLEGIO|COLÉGIO)",
    re.IGNORECASE,
)
PERSON_LIKE_PATTERN = re.compile(r"^[A-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]+(?: [A-ZÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]+){1,5}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa a trilha oficial de notas de empenho do PA para parquet no schema padrao."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--input-dir",
        help="Pasta com os CSVs anuais do PA. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida para os parquets da trilha de orcamento geral.",
    )
    parser.add_argument(
        "--cache-path",
        help="CSV de cache/resumo do resolvedor nome -> CNPJ. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--representatives-path",
        help="CSV com um id_ne representativo por nome de favorecido. Se omitido, usa o caminho padrao do escopo escolhido.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        help="Lista opcional de anos a processar, ex.: --years 2024 2025 2026",
    )
    parser.add_argument(
        "--max-names",
        type=int,
        help="Limita quantos nomes ainda nao resolvidos serao consultados na API neste run.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Numero de workers para consultar o detalhe da API do PA.",
    )
    parser.add_argument(
        "--skip-resolve",
        action="store_true",
        help="Nao consulta a API; apenas usa o cache existente para montar o parquet.",
    )
    parser.add_argument(
        "--entity-like-only",
        action="store_true",
        help="Resolve e considera como pendentes apenas nomes com cara de entidade/CNPJ.",
    )
    return parser.parse_args()


def default_input_dir(scope: str) -> Path:
    return uf_raw_dir("PA", scope)


def default_cache_path(scope: str) -> Path:
    return uf_raw_dir("PA", scope) / "cnpj_por_nome_resolvido.csv"


def default_representatives_path(scope: str) -> Path:
    return uf_raw_dir("PA", scope) / "nomes_representativos.csv"


def get_session() -> requests.Session:
    session = getattr(THREAD_LOCAL, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update({"User-Agent": "osc_unificado/pa-orcamento-geral"})
        THREAD_LOCAL.session = session
    return session


def list_source_csvs(input_dir: Path, years: list[str] | None) -> list[Path]:
    files = []
    allowed = {str(year) for year in years} if years else None
    for path in sorted(input_dir.glob("20*.csv")):
        if allowed and path.stem not in allowed:
            continue
        files.append(path)
    return files


def read_pa_source_csv(path: Path, usecols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype=str,
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip",
        usecols=usecols,
    )


def clean_text_series(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def clean_money_like_series(series: pd.Series) -> pd.Series:
    cleaned = clean_text_series(series)
    money_pattern = r"[R$\s0-9.,()\-]+"
    valid_mask = cleaned.str.fullmatch(money_pattern, na=False)
    cleaned.loc[~valid_mask] = pd.NA
    return cleaned


def is_entity_like_name(value: object) -> bool:
    text = str(value or "").strip().upper()
    if not text:
        return False
    if ENTITY_LIKE_PATTERN.search(text):
        return True
    return PERSON_LIKE_PATTERN.fullmatch(text) is None


def build_representatives_frame(source_paths: list[Path]) -> pd.DataFrame:
    seen_names: set[str] = set()
    records: list[dict[str, str]] = []

    for path in source_paths:
        df = read_pa_source_csv(path, usecols=["ds_sigla_orgao", "ds_credor"])
        subset = df.rename(columns={"ds_sigla_orgao": "nome_osc", "ds_credor": "id_ne_representativo"})
        subset["nome_osc"] = clean_text_series(subset["nome_osc"])
        subset["id_ne_representativo"] = clean_text_series(subset["id_ne_representativo"])
        subset = subset.dropna(subset=["nome_osc", "id_ne_representativo"]).drop_duplicates(subset=["nome_osc"])

        for row in subset.itertuples(index=False):
            if row.nome_osc in seen_names:
                continue
            seen_names.add(row.nome_osc)
            records.append(
                {
                    "nome_osc": row.nome_osc,
                    "id_ne_representativo": row.id_ne_representativo,
                }
            )

    return pd.DataFrame(records, columns=["nome_osc", "id_ne_representativo"])


def load_or_build_representatives(representatives_path: Path, source_paths: list[Path]) -> pd.DataFrame:
    representatives = build_representatives_frame(source_paths)
    representatives_path.parent.mkdir(parents=True, exist_ok=True)
    representatives.to_csv(representatives_path, index=False, encoding="utf-8-sig")
    return representatives


def choose_cnpj_from_detail_rows(rows: list[dict[str, object]], original_name: str) -> tuple[str | None, str | None]:
    normalized_original = normalize_name(original_name)
    preferred_name: str | None = None

    for row in rows:
        if str(row.get("ds_tipo_nota") or "").strip().upper() != "EMPENHO DA DESPESA":
            continue
        raw_name = str(row.get("razao_social") or "").strip()
        if not raw_name:
            continue
        normalized_detail_name = normalize_name(raw_name)
        if normalized_detail_name != normalized_original:
            continue
        raw_document = clean_document(row.get("cpf_cnpj"))
        if pd.isna(raw_document):
            continue
        document = str(raw_document).strip()
        if len(document) != 14 or "*" in document:
            continue
        preferred_name = raw_name
        return document, preferred_name

    return None, preferred_name


def resolve_single_name(record: dict[str, str]) -> dict[str, str | None]:
    session = get_session()
    response = session.get(DETAIL_URL, params={"idNE": record["id_ne_representativo"]}, timeout=60)
    response.raise_for_status()

    data = response.json().get("data", [])
    cnpj, detail_name = choose_cnpj_from_detail_rows(data, record["nome_osc"])
    return {
        "nome_osc": record["nome_osc"],
        "id_ne_representativo": record["id_ne_representativo"],
        "cnpj": cnpj,
        "nome_detalhe": detail_name,
        "status": "resolved_cnpj" if cnpj else "resolved_without_cnpj",
    }


def load_cache(cache_path: Path) -> pd.DataFrame:
    if not cache_path.exists():
        return pd.DataFrame(columns=["nome_osc", "id_ne_representativo", "cnpj", "nome_detalhe", "status"])

    cached = pd.read_csv(cache_path, dtype=str)
    for column in ["nome_osc", "id_ne_representativo", "cnpj", "nome_detalhe", "status"]:
        if column not in cached.columns:
            cached[column] = pd.NA
    cached["nome_osc"] = clean_text_series(cached["nome_osc"])
    return cached.dropna(subset=["nome_osc"]).drop_duplicates(subset=["nome_osc"], keep="last")


def save_cache(cache_df: pd.DataFrame, cache_path: Path) -> None:
    ordered = cache_df.sort_values("nome_osc", na_position="last")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    ordered.to_csv(cache_path, index=False, encoding="utf-8-sig")


def resolve_missing_names(
    representatives: pd.DataFrame,
    cache_df: pd.DataFrame,
    cache_path: Path,
    workers: int,
    max_names: int | None,
    entity_like_only: bool,
) -> pd.DataFrame:
    known_names = set(cache_df["nome_osc"].dropna().tolist())
    pending = representatives[~representatives["nome_osc"].isin(known_names)].copy()
    if entity_like_only:
        pending = pending[pending["nome_osc"].map(is_entity_like_name)]
    if max_names is not None:
        pending = pending.head(max_names)

    if pending.empty:
        return cache_df

    pending_records = pending.to_dict(orient="records")
    resolved_rows: list[dict[str, str | None]] = []

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {executor.submit(resolve_single_name, record): record for record in pending_records}
        for index, future in enumerate(as_completed(future_map), start=1):
            record = future_map[future]
            try:
                resolved_rows.append(future.result())
            except Exception as exc:  # pragma: no cover - network instability path
                resolved_rows.append(
                    {
                        "nome_osc": record["nome_osc"],
                        "id_ne_representativo": record["id_ne_representativo"],
                        "cnpj": None,
                        "nome_detalhe": None,
                        "status": f"error:{type(exc).__name__}",
                    }
                )

            if index % 500 == 0 or index == len(pending_records):
                batch_df = pd.concat([cache_df, pd.DataFrame(resolved_rows)], ignore_index=True)
                batch_df = batch_df.drop_duplicates(subset=["nome_osc"], keep="last")
                save_cache(batch_df, cache_path)
                print(f"Nomes resolvidos nesta execucao: {index}/{len(pending_records)}")

    final_cache = pd.concat([cache_df, pd.DataFrame(resolved_rows)], ignore_index=True)
    final_cache = final_cache.drop_duplicates(subset=["nome_osc"], keep="last")
    save_cache(final_cache, cache_path)
    return final_cache


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    if not series:
        return pd.Series(dtype="string")

    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = current.astype("string").str.strip().replace("", pd.NA)
        result = cleaned if result is None else result.combine_first(cleaned)

    if result is None:
        return pd.Series(dtype="string")
    return result


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty

    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, utc=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def build_pa_source_frame(source_paths: list[Path], cnpj_map: pd.DataFrame) -> pd.DataFrame:
    cnpj_lookup = cnpj_map[["nome_osc", "cnpj"]].dropna(subset=["nome_osc"]).drop_duplicates(subset=["nome_osc"])
    chunks: list[pd.DataFrame] = []

    for path in source_paths:
        df = read_pa_source_csv(
            path,
            usecols=["dt_despesa", "vlr_pago", "ds_orgao", "ds_sigla_orgao"],
        )
        df = df.rename(columns={"ds_sigla_orgao": "nome_osc", "ds_orgao": "objeto_raw"})
        df["nome_osc"] = clean_text_series(df["nome_osc"])
        df["objeto_raw"] = clean_text_series(df["objeto_raw"])
        df["dt_despesa"] = clean_text_series(df["dt_despesa"])
        df["vlr_pago"] = clean_money_like_series(df["vlr_pago"])
        df = df.dropna(subset=["nome_osc", "vlr_pago"])
        df = df.merge(cnpj_lookup, on="nome_osc", how="left")
        chunks.append(df)

    if not chunks:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    source_df = pd.concat(chunks, ignore_index=True)
    ano, mes = extract_year_month(source_df.get("dt_despesa"))

    mapped = pd.DataFrame(
        {
            "uf": "PA",
            "origem": ORIGEM_ORCAMENTO_GERAL,
            "ano": ano,
            "valor_total": source_df.get("vlr_pago"),
            "cnpj": source_df.get("cnpj"),
            "nome_osc": source_df.get("nome_osc"),
            "mes": mes,
            "objeto": first_non_empty(source_df.get("objeto_raw")),
            "data_inicio": source_df.get("dt_despesa"),
        }
    )

    mapped["cod_municipio"] = pd.NA
    mapped["municipio"] = pd.NA
    mapped["modalidade"] = pd.NA
    mapped["data_fim"] = pd.NA

    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir) if args.input_dir else default_input_dir(args.scope)
    output_dir = Path(args.output_dir)
    cache_path = Path(args.cache_path) if args.cache_path else default_cache_path(args.scope)
    representatives_path = (
        Path(args.representatives_path) if args.representatives_path else default_representatives_path(args.scope)
    )

    source_paths = list_source_csvs(input_dir, args.years)
    if not source_paths:
        raise FileNotFoundError(f"Nenhum CSV anual encontrado em {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    representatives = load_or_build_representatives(representatives_path, source_paths)
    cache_df = load_cache(cache_path)
    if not args.skip_resolve:
        cache_df = resolve_missing_names(
            representatives=representatives,
            cache_df=cache_df,
            cache_path=cache_path,
            workers=args.workers,
            max_names=args.max_names,
            entity_like_only=args.entity_like_only,
        )

    mapped = build_pa_source_frame(source_paths, cache_df)
    normalized = normalize_preview(mapped, "PA", require_cnpj=True)

    cached_names = set(cache_df["nome_osc"].dropna().tolist())
    pending_frame = representatives[~representatives["nome_osc"].isin(cached_names)]
    if args.entity_like_only:
        pending_frame = pending_frame[pending_frame["nome_osc"].map(is_entity_like_name)]
    pending_names = len(pending_frame)
    output_name = (
        default_output_name("PA", args.scope).replace(".parquet", ".partial.parquet")
        if pending_names > 0
        else default_output_name("PA", args.scope)
    )
    output_path = output_dir / output_name
    pq.write_table(build_parquet_table(normalized), output_path, compression="snappy")

    resolved_cnpj = cache_df["cnpj"].astype("string").str.len().eq(14).sum()
    print(f"Representantes: {len(representatives)}")
    print(f"Nomes em cache: {len(cache_df)}")
    print(f"Nomes com CNPJ resolvido: {resolved_cnpj}")
    print(f"Nomes pendentes: {pending_names}")
    print(f"Linhas parquet: {len(normalized)}")
    print(f"Saida: {output_path}")


if __name__ == "__main__":
    main()
