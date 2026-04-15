from __future__ import annotations

from collections import Counter, defaultdict
import re
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import dashboard_parquets as app
import gerar_historias as gh
from project_paths import HISTORIA_DIR, ORCAMENTO_GERAL_PROCESSADA_DIR, PROCESSADA_DIR


TARGET_UFS = ("AL", "BA", "CE", "ES", "PA", "PB", "MT")
UPDATED_UFS = set(TARGET_UFS)
DUP_COLS = ["uf", "ano", "mes", "valor_total", "cnpj", "nome_osc", "municipio", "objeto", "modalidade"]
READ_COLUMNS = app.STANDARD_COLUMNS
UPDATE_NOTES: dict[str, list[str]] = {
    "AL": [
        "A trilha de orcamento geral de Alagoas segue como base inicial do projeto e foi mantida como referencia operacional.",
        "A saida canonica atual esta em `{source}`, com {rows} linhas e serie de {year_range}.",
    ],
    "BA": [
        "Foi criado o parser `utils/orcamento_geral/processar_orcamento_geral_ba.py` para consolidar pagamentos e cruzar recebedores com a trilha local de convenios.",
        "A saida canonica atual esta em `{source}`, com {rows} linhas, {cnpjs} CNPJs e serie de {year_range}.",
        "A versao final da Bahia manteve o recorte amplo decidido na revisao, inclusive com casos de heuristica baixa.",
    ],
    "CE": [
        "Foi criado o parser `utils/orcamento_geral/processar_orcamento_geral_ce.py` a partir da compilacao dos contratos e do cruzamento com a base de convenios sem fins lucrativos.",
        "A saida canonica atual esta em `{source}`, com {rows} linhas, {cnpjs} CNPJs e serie de {year_range}.",
        "O `valor_total` usa `Valor pago`, com fallback para `Valor atualizado` quando o pagamento vier vazio.",
    ],
    "ES": [
        "Foi criado o parser `utils/orcamento_geral/processar_orcamento_geral_es.py` para consolidar a trilha de despesas do Espirito Santo e cruzar com os arquivos de convenios em `E:\\dados\\bases_convenios\\ES\\saida`.",
        "A saida canonica atual esta em `{source}`, com {rows} linhas, {cnpjs} CNPJs e serie de {year_range}.",
        "A base final do ES ficou apenas com documentos de 14 digitos no campo `cnpj`.",
    ],
    "PA": [
        "Foi criado o parser `utils/orcamento_geral/processar_orcamento_geral_pa.py` usando a trilha oficial de notas de empenho do Para e a resolucao complementar de CNPJ por nome via API de detalhe.",
        "A saida canonica atual esta em `{source}`, com {rows} linhas, {cnpjs} CNPJs e serie de {year_range}.",
        "O fechamento do PA respeitou a regra de manter apenas CNPJ valido no parquet final.",
    ],
    "PB": [
        "Foi consolidada uma pipeline unica em `utils/orcamento_geral/processar_orcamento_geral_pb.py`, que baixa e processa a trilha de empenhos da PB.",
        "A saida canonica atual esta em `{source}`, com {rows} linhas, {cnpjs} CNPJs e serie de {year_range}.",
        "O `valor_total` ficou preenchido em toda a base final e a trilha foi fechada sem CPF no parquet.",
    ],
    "MT": [
        "A trilha de Mato Grosso ficou restrita a uma unica pipeline oficial em `utils/orcamento_geral/processar_orcamento_geral_mt.py`.",
        "A saida canonica atual esta em `{source}`, com {rows} linhas, {cnpjs} CNPJs e cobertura valida de {year_range}.",
        "O ano de 2022 ficou fora do canone porque o layout oficial nao traz data da despesa, e a trilha atual exige no minimo `valor + data + cnpj`.",
    ],
}


def canonical_parquet_map() -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for base_dir in (PROCESSADA_DIR, ORCAMENTO_GERAL_PROCESSADA_DIR):
        if not base_dir.exists():
            continue
        for path in sorted(base_dir.glob("*.parquet")):
            mapping[path.stem.upper()] = path
    return mapping


def source_label(path: Path) -> str:
    path = path.resolve()
    try:
        rel = path.relative_to(Path.cwd())
        return rel.as_posix()
    except ValueError:
        return str(path)


def preprocess_chunk(frame: pd.DataFrame) -> pd.DataFrame:
    frame = app.ensure_schema(frame)
    for column in app.STANDARD_COLUMNS:
        frame[column] = app.clean_text(frame[column])
    frame["origem"] = frame["origem"].fillna(app.ORIGEM_PADRAO)
    frame["valor_num"] = frame["valor_total"].map(app.parse_money_to_centavos).astype("Float64") / 100.0
    frame["ano_num"] = app.parse_int_like(frame["ano"])
    frame["mes_num"] = app.parse_int_like(frame["mes"])
    current_year = pd.Timestamp.today().year
    frame["tem_cnpj_valido"] = frame["cnpj"].str.replace(r"\D", "", regex=True).str.len().eq(14)
    frame["tem_municipio"] = frame["municipio"].notna()
    frame["tem_objeto"] = frame["objeto"].notna()
    frame["tem_modalidade"] = frame["modalidade"].notna()
    frame["valor_negativo"] = frame["valor_num"].lt(0).fillna(False)
    frame["ano_valido"] = frame["ano_num"].between(1990, current_year + 2)
    frame["municipio_base"] = frame["municipio"].fillna("Nao informado")
    return frame


def tokenize_objects(series: pd.Series) -> Counter[str]:
    tokens = (
        series.dropna()
        .astype("string")
        .str.upper()
        .str.replace(r"[^A-Z0-9À-Ú]+", " ", regex=True)
        .str.split()
        .explode()
    )
    if tokens.empty:
        return Counter()
    tokens = tokens[tokens.notna()]
    tokens = tokens[tokens.str.len().ge(4)]
    tokens = tokens[~tokens.str.lower().isin(app.STOPWORDS)]
    return Counter(tokens.tolist())


def summarize_parquet(uf: str, path: Path) -> dict[str, object]:
    parquet = pq.ParquetFile(path)
    value_arrays: list[np.ndarray] = []
    entity_name_sums: defaultdict[str, float] = defaultdict(float)
    entity_pair_sums: defaultdict[tuple[str, str], float] = defaultdict(float)
    entity_pair_counts: defaultdict[tuple[str, str], int] = defaultdict(int)
    year_stats: defaultdict[int, dict[str, float]] = defaultdict(lambda: {"registros": 0, "valor_total": 0.0})
    municipality_stats: defaultdict[str, dict[str, float]] = defaultdict(lambda: {"registros": 0, "valor_total": 0.0})
    hash_counts: Counter[int] = Counter()
    object_terms: Counter[str] = Counter()
    cnpjs_validos: set[str] = set()
    top_objective_rows: list[dict[str, object]] = []
    max_row: dict[str, object] | None = None

    registros = 0
    valor_total_sum = 0.0
    valor_zero = 0
    negativos = 0
    tem_cnpj = 0
    tem_municipio = 0
    tem_objeto = 0
    tem_modalidade = 0
    ano_valido = 0

    for row_group in range(parquet.metadata.num_row_groups):
        chunk = parquet.read_row_group(row_group, columns=READ_COLUMNS).to_pandas()
        chunk = preprocess_chunk(chunk)
        registros += len(chunk)

        numeric_values = pd.to_numeric(chunk["valor_num"], errors="coerce").dropna()
        if not numeric_values.empty:
            arr = numeric_values.to_numpy(dtype=np.float64, copy=True)
            value_arrays.append(arr)
            valor_total_sum += float(arr.sum())
        valor_zero += int(chunk["valor_num"].fillna(0).eq(0).sum())
        negativos += int(chunk["valor_negativo"].sum())
        tem_cnpj += int(chunk["tem_cnpj_valido"].sum())
        tem_municipio += int(chunk["tem_municipio"].sum())
        tem_objeto += int(chunk["tem_objeto"].sum())
        tem_modalidade += int(chunk["tem_modalidade"].sum())
        ano_valido += int(chunk["ano_valido"].sum())

        valid_cnpj = chunk.loc[chunk["tem_cnpj_valido"], "cnpj"].str.replace(r"\D", "", regex=True)
        cnpjs_validos.update(valid_cnpj.dropna().tolist())

        pair_frame = chunk[["nome_osc", "cnpj", "valor_num"]].copy()
        pair_frame["nome_osc"] = pair_frame["nome_osc"].fillna("Sem identificacao")
        pair_frame["cnpj"] = pair_frame["cnpj"].fillna("")
        pair_agg = pair_frame.groupby(["nome_osc", "cnpj"], dropna=False).agg(
            registros=("nome_osc", "size"),
            valor_total=("valor_num", "sum"),
        )
        for (nome, cnpj), row in pair_agg.iterrows():
            key = (str(nome), str(cnpj))
            entity_pair_sums[key] += float(row["valor_total"] or 0.0)
            entity_pair_counts[key] += int(row["registros"])

        name_agg = pair_frame.groupby("nome_osc", dropna=False)["valor_num"].sum()
        for nome, valor in name_agg.items():
            entity_name_sums[str(nome)] += float(valor or 0.0)

        valid_years = chunk.loc[chunk["ano_valido"], ["ano_num", "valor_num"]].copy()
        if not valid_years.empty:
            year_agg = valid_years.groupby("ano_num", dropna=False).agg(registros=("ano_num", "size"), valor_total=("valor_num", "sum"))
            for ano_num, row in year_agg.iterrows():
                year_stats[int(ano_num)]["registros"] += int(row["registros"])
                year_stats[int(ano_num)]["valor_total"] += float(row["valor_total"] or 0.0)

        city_agg = chunk.groupby("municipio_base", dropna=False).agg(registros=("municipio_base", "size"), valor_total=("valor_num", "sum"))
        for municipio, row in city_agg.iterrows():
            municipality_stats[str(municipio)]["registros"] += int(row["registros"])
            municipality_stats[str(municipio)]["valor_total"] += float(row["valor_total"] or 0.0)

        object_terms.update(tokenize_objects(chunk["objeto"]))

        objective_candidates = chunk.loc[chunk["objeto"].notna(), ["nome_osc", "objeto", "valor_num", "ano_num"]].copy()
        if not objective_candidates.empty:
            objective_candidates = objective_candidates.sort_values(["valor_num", "ano_num"], ascending=[False, False]).head(10)
            top_objective_rows.extend(objective_candidates.to_dict("records"))
            top_objective_rows = sorted(
                top_objective_rows,
                key=lambda row: (
                    float("-inf") if pd.isna(row.get("valor_num")) else float(row.get("valor_num") or 0.0),
                    float("-inf") if pd.isna(row.get("ano_num")) else float(row.get("ano_num") or 0.0),
                ),
                reverse=True,
            )[:5]

        if not chunk.empty:
            idx = pd.to_numeric(chunk["valor_num"], errors="coerce").idxmax()
            if pd.notna(idx):
                candidate = chunk.loc[idx, ["nome_osc", "objeto", "valor_num", "ano_num"]].to_dict()
                if max_row is None or float(candidate.get("valor_num") or 0.0) > float(max_row.get("valor_num") or 0.0):
                    max_row = candidate

        dup_hashes = pd.util.hash_pandas_object(chunk[DUP_COLS].fillna("<vazio>"), index=False)
        hash_counts.update(dup_hashes.astype("uint64").tolist())

    duplicate_rows = int(sum(count for count in hash_counts.values() if count > 1))
    values = np.concatenate(value_arrays) if value_arrays else np.array([], dtype=np.float64)
    ticket_medio = float(values.mean()) if values.size else 0.0
    ticket_mediano = float(np.median(values)) if values.size else 0.0

    top_entities = sorted(
        (
            {
                "nome_osc": nome,
                "cnpj": cnpj,
                "registros": entity_pair_counts[(nome, cnpj)],
                "valor_total": entity_pair_sums[(nome, cnpj)],
            }
            for nome, cnpj in entity_pair_sums.keys()
        ),
        key=lambda row: (row["valor_total"], row["registros"]),
        reverse=True,
    )[:5]

    top5_share = 0.0
    if valor_total_sum:
        top5_share = sum(sorted(entity_name_sums.values(), reverse=True)[:5]) / valor_total_sum * 100.0

    years_df = pd.DataFrame(
        [{"ano_num": ano, **stats} for ano, stats in sorted(year_stats.items())]
    )
    if not years_df.empty:
        years_df = years_df.sort_values("ano_num").reset_index(drop=True)
        years_df["var_pct"] = years_df["valor_total"].pct_change() * 100

    municipalities_df = pd.DataFrame(
        [{"municipio_base": municipio, **stats} for municipio, stats in municipality_stats.items()]
    )
    if not municipalities_df.empty:
        municipalities_df = municipalities_df.sort_values("valor_total", ascending=False).head(5).reset_index(drop=True)

    top_terms = [gh.ascii_text(term) for term, _ in object_terms.most_common(12)]
    year_range = "n/d"
    if not years_df.empty:
        years_sorted = [int(value) for value in years_df["ano_num"].tolist()]
        ranges: list[str] = []
        start = years_sorted[0]
        prev = years_sorted[0]
        for year in years_sorted[1:]:
            if year == prev + 1:
                prev = year
                continue
            ranges.append(f"{start} a {prev}" if start != prev else f"{start}")
            start = prev = year
        ranges.append(f"{start} a {prev}" if start != prev else f"{start}")
        year_range = " e ".join(ranges)

    benchmark_row = {
        "uf": uf,
        "registros": registros,
        "valor_total": valor_total_sum,
        "ticket_medio": ticket_medio,
        "ticket_mediano": ticket_mediano,
        "entidades": len(entity_name_sums),
        "cnpjs": len(cnpjs_validos),
        "cob_municipio": (tem_municipio / registros * 100) if registros else 0.0,
        "cob_objeto": (tem_objeto / registros * 100) if registros else 0.0,
        "cob_modalidade": (tem_modalidade / registros * 100) if registros else 0.0,
        "top1_share_pct": (max(entity_name_sums.values()) / valor_total_sum * 100) if valor_total_sum and entity_name_sums else 0.0,
        "top5_share_pct": top5_share,
        "top10_share_pct": (sum(sorted(entity_name_sums.values(), reverse=True)[:10]) / valor_total_sum * 100) if valor_total_sum else 0.0,
    }

    return {
        "uf": uf,
        "path": path,
        "source": source_label(path),
        "registros": registros,
        "cnpjs": len(cnpjs_validos),
        "year_range": year_range,
        "benchmark_row": benchmark_row,
        "rows_zero_share": (valor_zero / registros * 100) if registros else 0.0,
        "cnpj_share": (tem_cnpj / registros * 100) if registros else 0.0,
        "missing_year_share": ((registros - ano_valido) / registros * 100) if registros else 0.0,
        "tem_municipio_share": (tem_municipio / registros * 100) if registros else 0.0,
        "tem_objeto_share": (tem_objeto / registros * 100) if registros else 0.0,
        "tem_modalidade_share": (tem_modalidade / registros * 100) if registros else 0.0,
        "negativos": negativos,
        "duplicados": duplicate_rows,
        "top_entities": top_entities,
        "top_terms": top_terms,
        "top_objectives": top_objective_rows,
        "max_row": max_row or {"nome_osc": "", "objeto": "", "valor_num": 0.0, "ano_num": pd.NA},
        "years_df": years_df,
        "municipalities_df": municipalities_df,
    }


def local_source_line(summary: dict[str, object], fields: str) -> str:
    return f"_Fonte local deste bloco: `{summary['source']}`; campos e agregacoes usados: {fields}._"


def build_update_section(uf: str, summary: dict[str, object]) -> list[str]:
    bullets = UPDATE_NOTES.get(uf, [])
    if not bullets:
        return []
    formatted = [
        bullet.format(
            source=summary["source"],
            rows=app.format_int(summary["registros"]),
            cnpjs=app.format_int(summary["cnpjs"]),
            year_range=summary["year_range"],
        )
        for bullet in bullets
    ]
    return ["## Atualizacao de orcamento geral", ""] + [f"- {line}" for line in formatted] + [""]


def source_caveats_for_summary(uf: str, summary: dict[str, object], years_df: pd.DataFrame) -> list[str]:
    caveats: list[str] = []
    if uf == "ES":
        caveats.append("A serie atual do Espirito Santo foi recomposta a partir da trilha de despesas e pagamentos cruzada com convenios. Comparacoes com a versao historica anterior devem considerar essa mudanca de origem no bruto.")
    if uf == "MT":
        caveats.append("A serie canonica de Mato Grosso passou a usar a base oficial rica do portal de transparencia. O ano de 2022 ficou fora do parquet principal porque o layout oficial nao traz data da despesa, e a trilha atual exige no minimo valor, data e cnpj.")
    if summary["rows_zero_share"] >= 10:
        caveats.append(
            f"{app.format_pct(summary['rows_zero_share'])} dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros."
        )
    if summary["cnpj_share"] < 100:
        caveats.append(
            f"A cobertura de CNPJ valido nesta UF esta em {app.format_pct(summary['cnpj_share'])}. Parte das identificacoes pode ter sido recuperada por cruzamento com base externa, mas ainda ha linhas sem identificacao cadastral completa."
        )
    if summary["missing_year_share"] > 0:
        caveats.append(
            f"{app.format_pct(summary['missing_year_share'])} dos registros ficaram sem ano valido no parquet, entao as secoes temporais usam apenas a parcela com `ano` reconhecido."
        )
    if not years_df.empty and int(years_df["ano_num"].max() - years_df["ano_num"].min()) <= 3 and summary["registros"] >= 1000:
        caveats.append(
            f"A serie disponivel nesta UF esta concentrada em um intervalo curto ({int(years_df['ano_num'].min())} a {int(years_df['ano_num'].max())}), o que limita comparacoes historicas mais longas."
        )
    return caveats


def build_story(uf: str, summary: dict[str, object], benchmark: pd.DataFrame, cnpj_cache: dict[str, dict[str, object]]) -> str:
    state_name = gh.STATE_NAMES.get(uf, uf)
    row = benchmark.loc[benchmark["uf"] == uf].iloc[0]
    driver = gh.classify_driver(row, benchmark)
    top_value = benchmark.sort_values("valor_total", ascending=False).head(5)["uf"].tolist()
    top_rows = benchmark.sort_values("registros", ascending=False).head(5)["uf"].tolist()
    top_ticket = benchmark.sort_values("ticket_medio", ascending=False).head(5)["uf"].tolist()
    top_concentration = benchmark.sort_values("top5_share_pct", ascending=False).head(5)["uf"].tolist()
    years_df: pd.DataFrame = summary["years_df"]
    top_years = years_df.sort_values("valor_total", ascending=False).head(3) if not years_df.empty else pd.DataFrame()
    last_years = years_df.tail(5) if not years_df.empty else pd.DataFrame()
    municipalities_df: pd.DataFrame = summary["municipalities_df"]

    top_entities_sources: list[dict[str, object]] = []
    for entity in summary["top_entities"]:
        cnpj = gh.ascii_text(entity["cnpj"]) if entity["cnpj"] else ""
        profile = gh.fetch_cnpj_profile(cnpj, cnpj_cache) if cnpj else {}
        top_entities_sources.append({"cnpj": cnpj, "nome": gh.ascii_text(entity["nome_osc"]), "profile": profile})

    lines: list[str] = [f"# {state_name} ({uf})", ""]
    lines.extend(build_update_section(uf, summary))
    lines.append("## Visao geral")
    lines.append("")
    lines.append(
        f"{state_name} soma {app.format_int(summary['registros'])} registros e {app.format_money(row['valor_total'])} em valor total. "
        f"No ranking geral da base, a UF esta em {int(row['rank_valor_total'])}o lugar por valor, {int(row['rank_registros'])}o por quantidade de registros, "
        f"{int(row['rank_ticket_medio'])}o por ticket medio e {int(row['rank_concentracao'])}o por concentracao dos 5 maiores beneficiarios."
    )
    lines.append("")
    lines.append(
        f"O perfil dominante da UF e {driver}. O ticket medio e de {app.format_money(row['ticket_medio'])}, "
        f"a mediana e de {app.format_money(row['ticket_mediano'])} e os 5 maiores beneficiarios concentram {app.format_pct(row['top5_share_pct'])} do valor total."
    )
    lines.append("")
    lines.append(local_source_line(summary, "`valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios"))
    lines.append("")
    lines.append("## Leitura narrativa")
    lines.append("")
    lines.append(
        f"Comparando com o conjunto nacional, {uf} aparece entre as UFs lideres por valor em `{', '.join(top_value[:5])}`, "
        f"por volume em `{', '.join(top_rows[:5])}`, por ticket medio em `{', '.join(top_ticket[:5])}` e por concentracao em `{', '.join(top_concentration[:5])}`."
    )
    lines.append("")
    lines.append(
        f"Na pratica, isso indica que {state_name} cresce principalmente por {driver}. "
        f"A participacao da UF no total nacional desta pasta e de {app.format_pct(row['share_nacional_pct'])}."
    )
    lines.append("")
    lines.append(local_source_line(summary, "benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`"))
    lines.append("")

    caveats = source_caveats_for_summary(uf, summary, years_df)
    if caveats:
        lines.append("## Ressalvas da fonte")
        lines.append("")
        for caveat in caveats:
            lines.append(f"- {caveat}")
        lines.append("")
        lines.append(local_source_line(summary, "auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet"))
        lines.append("")

    lines.append("## Principais entidades")
    lines.append("")
    for idx, entity in enumerate(summary["top_entities"], start=1):
        identifier = gh.ascii_text(entity["cnpj"]) if entity["cnpj"] else gh.ascii_text(entity["nome_osc"])
        lines.append(
            f"{idx}. `{identifier}` - {gh.ascii_text(entity['nome_osc'])}: {app.format_money(entity['valor_total'])} em {app.format_int(entity['registros'])} registros."
        )
    lines.append("")
    lines.append(local_source_line(summary, "agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros"))
    lines.append("")

    lines.append("## Gastos e objetivos")
    lines.append("")
    if summary["top_terms"]:
        lines.append(f"Termos mais frequentes nos objetos da UF: `{', '.join(summary['top_terms'])}`.")
        lines.append("")
    if not summary["top_objectives"]:
        lines.append("Nao ha objetos suficientes para aprofundar os objetivos do gasto.")
    else:
        lines.append("Registros de maior valor que ajudam a explicar os objetivos do gasto:")
        lines.append("")
        for idx, objective in enumerate(summary["top_objectives"], start=1):
            ano = "n/d" if pd.isna(objective.get("ano_num")) else int(objective["ano_num"])
            lines.append(
                f"{idx}. `{gh.ascii_text(objective['nome_osc'])}` - {app.format_money(objective['valor_num'])} "
                f"(ano {ano}): {gh.ascii_text(objective['objeto'])[:700]}."
            )
        lines.append("")
    max_row = summary["max_row"]
    lines.append(
        f"O maior registro individual da UF foi para `{gh.ascii_text(max_row.get('nome_osc'))}` no valor de {app.format_money(max_row.get('valor_num'))}. "
        f"O objeto associado foi: {gh.ascii_text(max_row.get('objeto'))[:500]}."
    )
    lines.append("")
    lines.append(local_source_line(summary, "campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`"))
    lines.append("")

    lines.append("## Evolucao temporal")
    lines.append("")
    if top_years.empty:
        lines.append("Nao ha anos validos suficientes para analise temporal.")
    else:
        lines.append("Anos de maior volume:")
        lines.append("")
        for idx, (_, year_row) in enumerate(top_years.iterrows(), start=1):
            lines.append(
                f"{idx}. `{int(year_row['ano_num'])}` - {app.format_money(year_row['valor_total'])} em {app.format_int(year_row['registros'])} registros."
            )
        lines.append("")
        if not last_years.empty:
            lines.append("Ultimos anos da serie:")
            lines.append("")
            for _, year_row in last_years.iterrows():
                yoy = "n/d" if pd.isna(year_row["var_pct"]) else app.format_pct(year_row["var_pct"])
                lines.append(
                    f"- `{int(year_row['ano_num'])}`: {app.format_money(year_row['valor_total'])} em {app.format_int(year_row['registros'])} registros, variacao {yoy}."
                )
    lines.append("")
    lines.append(local_source_line(summary, "agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual"))
    lines.append("")

    lines.append("## Territorio e cobertura")
    lines.append("")
    if municipalities_df.empty or municipalities_df.iloc[0]["municipio_base"] == "Nao informado":
        lines.append("A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.")
    else:
        lines.append("Municipios com maior valor acumulado no recorte:")
        lines.append("")
        for idx, (_, city_row) in enumerate(municipalities_df.iterrows(), start=1):
            lines.append(
                f"{idx}. `{gh.ascii_text(city_row['municipio_base'])}` - {app.format_money(city_row['valor_total'])} em {app.format_int(city_row['registros'])} registros."
            )
    lines.append("")
    lines.append(
        f"Cobertura observada: CNPJ valido em {app.format_pct(summary['cnpj_share'])}, "
        f"municipio em {app.format_pct(summary['tem_municipio_share'])}, "
        f"objeto em {app.format_pct(summary['tem_objeto_share'])} e "
        f"modalidade em {app.format_pct(summary['tem_modalidade_share'])}. "
        f"Ha {app.format_int(summary['negativos'])} registros negativos e {app.format_int(summary['duplicados'])} registros marcados como duplicado aparente."
    )
    lines.append("")
    lines.append(local_source_line(summary, "campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`"))
    lines.append("")

    lines.append("## Fontes extras")
    lines.append("")
    lines.append("### Dados locais")
    lines.append("")
    lines.append(f"- Arquivo principal desta historia: `{summary['source']}`.")
    lines.append("- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.")
    lines.append("")
    lines.append("### Fontes externas verificadas por entidade")
    lines.append("")
    lines.append(f"- [Consulta oficial de CNPJ (gov.br)]({gh.RECEITA_SERVICE_URL})")
    lines.append(f"- [Comprovante de inscricao e situacao cadastral (Receita)]({gh.RECEITA_PROOF_URL})")
    lines.append(f"- [Convenios e transferencias federais (gov.br / Transferegov)]({gh.TRANSFEREGOV_URL})")
    lines.append("")
    for source in top_entities_sources:
        profile = source["profile"] or {}
        source_url = profile.get("_source_url", gh.BRASILAPI_CNPJ_URL.format(cnpj=source["cnpj"])) if source["cnpj"] else ""
        situacao = gh.ascii_text(profile.get("descricao_situacao_cadastral") or profile.get("descricao_situacao_cadastral", ""))
        municipio = gh.ascii_text(profile.get("municipio", ""))
        uf_ext = gh.ascii_text(profile.get("uf", ""))
        atividade = gh.ascii_text(profile.get("cnae_fiscal_descricao", ""))
        porte = gh.ascii_text(profile.get("porte", ""))
        status_code = profile.get("_status_code")
        extra = []
        if situacao:
            extra.append(f"situacao {situacao}")
        if municipio or uf_ext:
            extra.append(f"municipio/UF {municipio}/{uf_ext}".strip("/"))
        if porte:
            extra.append(f"porte {porte}")
        if atividade:
            extra.append(f"atividade principal {atividade}")
        if status_code and status_code != 200:
            extra.append(f"status da consulta {status_code}")
        detail = "; ".join(extra) if extra else "cadastro consultado"
        if source_url:
            lines.append(f"- `{source['nome']}` ({source['cnpj']}): [fonte externa verificada]({source_url}) - {detail}.")
        else:
            lines.append(f"- `{source['nome']}` ({source['cnpj']}): sem URL externa verificada.")
    lines.append("")
    lines.append("### Investigacao complementar")
    lines.append("")
    for source in top_entities_sources:
        query = " ".join(part for part in [source["cnpj"], source["nome"], state_name, "convenio contrato gestao"] if part)
        lines.append(f"- [{source['nome']} - busca complementar por CNPJ/nome/UF]({gh.search_url(query)})")
    lines.append("")
    lines.append("## Conclusao")
    lines.append("")
    lines.append(
        f"{state_name} deve ser lido como uma UF puxada por {driver}. "
        f"Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. "
        f"Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais."
    )
    lines.append("")
    return "\n".join(lines)


def build_hybrid_benchmark(summaries: dict[str, dict[str, object]]) -> pd.DataFrame:
    signatures = app.build_sources_signature((str(PROCESSADA_DIR),))
    local_data, _ = app.load_data((str(PROCESSADA_DIR),), signatures)
    benchmark = app.build_state_benchmark(local_data)
    benchmark = benchmark[~benchmark["uf"].isin(UPDATED_UFS)].copy()
    for uf in TARGET_UFS:
        benchmark = pd.concat([benchmark, pd.DataFrame([summaries[uf]["benchmark_row"]])], ignore_index=True)
    national_total = benchmark["valor_total"].sum()
    benchmark["share_nacional_pct"] = benchmark["valor_total"] / national_total * 100
    benchmark["rank_valor_total"] = benchmark["valor_total"].rank(method="min", ascending=False).astype(int)
    benchmark["rank_registros"] = benchmark["registros"].rank(method="min", ascending=False).astype(int)
    benchmark["rank_ticket_medio"] = benchmark["ticket_medio"].rank(method="min", ascending=False).astype(int)
    benchmark["rank_concentracao"] = benchmark["top5_share_pct"].rank(method="min", ascending=False).astype(int)
    return benchmark.sort_values("valor_total", ascending=False).reset_index(drop=True)


def main() -> None:
    file_map = canonical_parquet_map()
    summaries = {uf: summarize_parquet(uf, file_map[uf]) for uf in TARGET_UFS}
    benchmark = build_hybrid_benchmark(summaries)
    HISTORIA_DIR.mkdir(exist_ok=True)
    cnpj_cache = gh.load_cnpj_cache()

    for uf in TARGET_UFS:
        content = build_story(uf, summaries[uf], benchmark, cnpj_cache)
        (HISTORIA_DIR / f"{uf}.md").write_text(content, encoding="utf-8")

    gh.save_cnpj_cache(cnpj_cache)
    print("Historias atualizadas:", ", ".join(TARGET_UFS))


if __name__ == "__main__":
    main()
