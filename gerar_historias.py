from __future__ import annotations

import json
from pathlib import Path
import unicodedata
from urllib.parse import quote_plus

import pandas as pd
import requests

import dashboard_parquets as app
from project_paths import HISTORIA_DATA_DIR, HISTORIA_DIR


BASE_DIR = Path(__file__).resolve().parent
HISTORY_DIR = HISTORIA_DIR
HISTORY_DATA_DIR = HISTORIA_DATA_DIR
CNPJ_CACHE_PATH = HISTORY_DATA_DIR / "cnpj_cache.json"
RECEITA_SERVICE_URL = "https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas"
RECEITA_PROOF_URL = "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp"
TRANSFEREGOV_URL = "https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias"
BRASILAPI_CNPJ_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
STATE_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AM": "Amazonas",
    "AP": "Amapa",
    "BA": "Bahia",
    "CE": "Ceara",
    "DF": "Distrito Federal",
    "ES": "Espirito Santo",
    "GO": "Goias",
    "MA": "Maranhao",
    "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso",
    "PA": "Para",
    "PB": "Paraiba",
    "PE": "Pernambuco",
    "PI": "Piaui",
    "PR": "Parana",
    "RJ": "Rio de Janeiro",
    "RO": "Rondonia",
    "RR": "Roraima",
    "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina",
    "SE": "Sergipe",
    "SP": "Sao Paulo",
    "TO": "Tocantins",
}


def classify_driver(row: pd.Series, benchmark: pd.DataFrame) -> str:
    high_rows = row["registros"] >= benchmark["registros"].quantile(0.75)
    high_ticket = row["ticket_medio"] >= benchmark["ticket_medio"].quantile(0.75)
    high_concentration = row["top5_share_pct"] >= benchmark["top5_share_pct"].quantile(0.75)
    if high_rows and high_ticket:
        return "volume e ticket medio"
    if high_rows:
        return "volume de dados"
    if high_ticket and high_concentration:
        return "ticket medio e concentracao"
    if high_ticket:
        return "ticket medio"
    if high_concentration:
        return "concentracao"
    return "base mais distribuida"


def ascii_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    if "Ã" in text or "â" in text:
        try:
            text = text.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def quality_sentence(state_df: pd.DataFrame) -> str:
    return (
        f"Cobertura observada: CNPJ valido em {app.format_pct(state_df['tem_cnpj_valido'].mean() * 100)}, "
        f"municipio em {app.format_pct(state_df['tem_municipio'].mean() * 100)}, "
        f"objeto em {app.format_pct(state_df['tem_objeto'].mean() * 100)} e "
        f"modalidade em {app.format_pct(state_df['tem_modalidade'].mean() * 100)}. "
        f"Ha {app.format_int(int(state_df['valor_negativo'].sum()))} registros negativos e "
        f"{app.format_int(int(state_df['duplicado_aparente'].sum()))} registros marcados como duplicado aparente."
    )


def search_url(query: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(query)}"


def local_source_line(uf: str, fields: str) -> str:
    parquet_path = f"processada/{uf}.parquet"
    return f"_Fonte local deste bloco: `{parquet_path}`; campos e agregacoes usados: {fields}._"


def load_cnpj_cache() -> dict[str, dict[str, object]]:
    if not CNPJ_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CNPJ_CACHE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_cnpj_cache(cache: dict[str, dict[str, object]]) -> None:
    HISTORY_DATA_DIR.mkdir(parents=True, exist_ok=True)
    CNPJ_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_cnpj_profile(cnpj: str, cache: dict[str, dict[str, object]]) -> dict[str, object]:
    clean = "".join(ch for ch in str(cnpj) if ch.isdigit())
    if len(clean) != 14:
        return {}
    if clean in cache:
        return cache[clean]
    url = BRASILAPI_CNPJ_URL.format(cnpj=clean)
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            data["_source_url"] = url
            cache[clean] = data
            return data
        cache[clean] = {"_source_url": url, "_status_code": response.status_code}
        return cache[clean]
    except requests.RequestException:
        cache[clean] = {"_source_url": url, "_status_code": "request_error"}
        return cache[clean]


def top_objectives(state_df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    if state_df.empty:
        return pd.DataFrame()
    objectives = (
        state_df.loc[state_df["objeto"].notna(), ["nome_osc", "objeto", "valor_num", "ano_num"]]
        .sort_values(["valor_num", "ano_num"], ascending=[False, False])
        .head(limit)
        .copy()
    )
    return objectives


def dominant_terms(state_df: pd.DataFrame, limit: int = 12) -> list[str]:
    freq = app.build_word_frequency(state_df["objeto"], top_n=limit)
    if freq.empty:
        return []
    return [ascii_text(term) for term in freq["termo"].tolist()]


def source_caveats(uf: str, state_df: pd.DataFrame) -> list[str]:
    manual_caveats: dict[str, list[str]] = {
        "GO": [
            "Na fonte bruta de Goias, o campo `VALOR_TOTAL` fica zerado na maior parte dos registros ate 2016. O parquet manteve esse mesmo campo para preservar aderencia ao dado publicado, entao os totais financeiros de 2008 a 2016 devem ser lidos como subestimados pela propria fonte.",
            "Nos arquivos brutos do `GO`, os campos com melhor cobertura financeira sao `VALOR_PLANO_TOTAL` e `VALOR_CONCEDENTE`, mas eles nao foram promovidos a `valor_total` para evitar trocar a definicao oficial que ja vinha sendo trabalhada no projeto.",
        ],
        "ES": [
            "A fonte do Espirito Santo mudou de estrutura ao longo do tempo. O parquet atual recompõe a serie a partir de arquivos de convenios, aditivos e execucao orcamentaria, por isso comparacoes de longo prazo devem considerar essa mudanca de schema no bruto.",
        ],
        "PI": [
            "No Piaui, a base final manteve apenas o arquivo de convenios. Uma planilha separada de execucao orcamentaria ficou fora do parquet para nao misturar despesa geral com instrumento de parceria.",
        ],
        "PR": [
            "No bruto do Parana, a tabela relacional de entidade identificava o concedente, e nao o tomador. O parquet atual passou a usar o `tomador` como beneficiario e reteve apenas linhas com CNPJ recuperavel no enriquecimento.",
        ],
        "RO": [
            "A serie atual de Rondonia foi recomposta apos a separacao de arquivos que estavam armazenados na pasta de Roraima. A versao atual do parquet ja reflete essa limpeza de origem.",
        ],
        "RR": [
            "A base atual de Roraima usa apenas a fonte propria do estado. Arquivos que, na pasta bruta, pertenciam a Rondonia foram removidos da consolidacao do `RR`.",
        ],
        "MT": [
            "A serie de Mato Grosso foi complementada com um CSV recente de transparencia para reforcar a cobertura de 2025, sem substituir a planilha historica principal.",
        ],
        "AP": [
            "No Amapa, a consolidacao atual considera apenas as abas de convenios e termos de fomento. Abas de diario e datas zeradas foram retiradas da modelagem principal para evitar anos artificiais.",
        ],
    }
    caveats = list(manual_caveats.get(uf, []))
    if uf == "ES":
        caveats = [
            "A serie atual do Espirito Santo foi recomposta a partir da trilha de despesas e pagamentos cruzada com convenios. Comparacoes com a versao historica anterior devem considerar essa mudanca de origem no bruto.",
        ]
    if uf == "MT":
        caveats = [
            "A serie canonica de Mato Grosso passou a usar a base oficial rica do portal de transparencia. O ano de 2022 ficou fora do parquet principal porque o layout oficial nao traz data da despesa, e a trilha atual exige no minimo valor, data e cnpj.",
        ]

    zero_share = float((state_df["valor_num"].fillna(0) == 0).mean() * 100)
    cnpj_share = float(state_df["tem_cnpj_valido"].mean() * 100)
    missing_years = float((~state_df["ano_valido"]).mean() * 100)
    valid_years = state_df.loc[state_df["ano_valido"], "ano_num"]

    if zero_share >= 10:
        caveats.append(
            f"{app.format_pct(zero_share)} dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros."
        )
    if cnpj_share < 100:
        caveats.append(
            f"A cobertura de CNPJ valido nesta UF esta em {app.format_pct(cnpj_share)}. Parte das identificacoes pode ter sido recuperada por cruzamento com base externa, mas ainda ha linhas sem identificacao cadastral completa."
        )
    if missing_years > 0:
        caveats.append(
            f"{app.format_pct(missing_years)} dos registros ficaram sem ano valido no parquet, entao as secoes temporais usam apenas a parcela com `ano` reconhecido."
        )
    if not valid_years.empty and int(valid_years.max() - valid_years.min()) <= 3 and len(state_df) >= 1000:
        caveats.append(
            f"A serie disponivel nesta UF esta concentrada em um intervalo curto ({int(valid_years.min())} a {int(valid_years.max())}), o que limita comparacoes historicas mais longas."
        )

    return caveats


def build_state_story(uf: str, data: pd.DataFrame, benchmark: pd.DataFrame, cnpj_cache: dict[str, dict[str, object]]) -> str:
    state_df = data[data["uf"] == uf].copy()
    state_name = STATE_NAMES.get(uf, uf)
    if state_df.empty:
        return f"# {state_name} ({uf})\n\nSem dados disponiveis.\n"

    row = benchmark.loc[benchmark["uf"] == uf].iloc[0]
    driver = classify_driver(row, benchmark)

    years = (
        state_df.loc[state_df["ano_valido"]]
        .groupby("ano_num")
        .agg(registros=("ano_num", "size"), valor_total=("valor_num", "sum"))
        .reset_index()
        .sort_values("ano_num")
    )
    top_years = years.sort_values("valor_total", ascending=False).head(3)
    last_years = years.tail(5).copy()
    if not last_years.empty:
        last_years["var_pct"] = last_years["valor_total"].pct_change() * 100

    entities = (
        state_df.groupby(["nome_osc", "cnpj"], dropna=False)
        .agg(registros=("nome_osc", "size"), valor_total=("valor_num", "sum"), ticket_medio=("valor_num", "mean"))
        .reset_index()
        .sort_values(["valor_total", "registros"], ascending=[False, False])
    )
    top_entities = entities.head(5).copy()
    objective_rows = top_objectives(state_df, limit=5)
    terms = dominant_terms(state_df, limit=12)
    top_entities_sources: list[dict[str, object]] = []
    for _, entity in top_entities.iterrows():
        cnpj = ascii_text(entity["cnpj"]) if pd.notna(entity["cnpj"]) else ""
        profile = fetch_cnpj_profile(cnpj, cnpj_cache) if cnpj else {}
        top_entities_sources.append(
            {
                "cnpj": cnpj,
                "nome": ascii_text(entity["nome_osc"]),
                "profile": profile,
            }
        )

    max_row = state_df.loc[state_df["valor_num"].idxmax()]
    municipalities = (
        state_df.groupby("municipio_base", dropna=False)
        .agg(registros=("municipio_base", "size"), valor_total=("valor_num", "sum"))
        .reset_index()
        .sort_values("valor_total", ascending=False)
        .head(5)
    )

    top_value = benchmark.sort_values("valor_total", ascending=False).head(5)["uf"].tolist()
    top_rows = benchmark.sort_values("registros", ascending=False).head(5)["uf"].tolist()
    top_ticket = benchmark.sort_values("ticket_medio", ascending=False).head(5)["uf"].tolist()
    top_concentration = benchmark.sort_values("top5_share_pct", ascending=False).head(5)["uf"].tolist()

    lines: list[str] = []
    lines.append(f"# {state_name} ({uf})")
    lines.append("")
    lines.append("## Visao geral")
    lines.append("")
    lines.append(
        f"{state_name} soma {app.format_int(len(state_df))} registros e {app.format_money(state_df['valor_num'].sum())} em valor total. "
        f"No ranking geral da base, a UF esta em {int(row['rank_valor_total'])}o lugar por valor, {int(row['rank_registros'])}o por quantidade de registros, "
        f"{int(row['rank_ticket_medio'])}o por ticket medio e {int(row['rank_concentracao'])}o por concentracao dos 5 maiores beneficiarios."
    )
    lines.append("")
    lines.append(
        f"O perfil dominante da UF e {driver}. O ticket medio e de {app.format_money(row['ticket_medio'])}, "
        f"a mediana e de {app.format_money(row['ticket_mediano'])} e os 5 maiores beneficiarios concentram {app.format_pct(row['top5_share_pct'])} do valor total."
    )
    lines.append("")
    lines.append(local_source_line(uf, "`valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios"))
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
    lines.append(local_source_line(uf, "benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`"))
    lines.append("")
    caveats = source_caveats(uf, state_df)
    if caveats:
        lines.append("## Ressalvas da fonte")
        lines.append("")
        for caveat in caveats:
            lines.append(f"- {caveat}")
        lines.append("")
        lines.append(local_source_line(uf, "auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet"))
        lines.append("")
    lines.append("## Principais entidades")
    lines.append("")
    for idx, entity in top_entities.iterrows():
        rank = top_entities.index.get_loc(idx) + 1
        identifier = ascii_text(entity["cnpj"]) if pd.notna(entity["cnpj"]) else ascii_text(entity["nome_osc"])
        lines.append(
            f"{rank}. `{identifier}` - {ascii_text(entity['nome_osc'])}: {app.format_money(entity['valor_total'])} em {app.format_int(entity['registros'])} registros."
        )
    lines.append("")
    lines.append(local_source_line(uf, "agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros"))
    lines.append("")
    lines.append("## Gastos e objetivos")
    lines.append("")
    if terms:
        lines.append(f"Termos mais frequentes nos objetos da UF: `{', '.join(terms)}`.")
        lines.append("")
    if objective_rows.empty:
        lines.append("Nao ha objetos suficientes para aprofundar os objetivos do gasto.")
    else:
        lines.append("Registros de maior valor que ajudam a explicar os objetivos do gasto:")
        lines.append("")
        for idx, objective in objective_rows.iterrows():
            rank = objective_rows.index.get_loc(idx) + 1
            lines.append(
                f"{rank}. `{ascii_text(objective['nome_osc'])}` - {app.format_money(objective['valor_num'])} "
                f"(ano {int(objective['ano_num']) if pd.notna(objective['ano_num']) else 'n/d'}): "
                f"{ascii_text(objective['objeto'])[:700]}."
            )
        lines.append("")
    lines.append(
        f"O maior registro individual da UF foi para `{ascii_text(max_row['nome_osc'])}` no valor de {app.format_money(max_row['valor_num'])}. "
        f"O objeto associado foi: {ascii_text(max_row['objeto'])[:500]}."
    )
    lines.append("")
    lines.append(local_source_line(uf, "campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`"))
    lines.append("")
    lines.append("## Evolucao temporal")
    lines.append("")
    if top_years.empty:
        lines.append("Nao ha anos validos suficientes para analise temporal.")
    else:
        lines.append("Anos de maior volume:")
        lines.append("")
        for idx, year_row in top_years.iterrows():
            rank = top_years.index.get_loc(idx) + 1
            lines.append(
                f"{rank}. `{int(year_row['ano_num'])}` - {app.format_money(year_row['valor_total'])} em {app.format_int(year_row['registros'])} registros."
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
    lines.append(local_source_line(uf, "agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual"))
    lines.append("")
    lines.append("## Territorio e cobertura")
    lines.append("")
    if municipalities.empty or municipalities.iloc[0]["municipio_base"] == "Nao informado":
        lines.append("A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.")
    else:
        lines.append("Municipios com maior valor acumulado no recorte:")
        lines.append("")
        for idx, city_row in municipalities.iterrows():
            rank = municipalities.index.get_loc(idx) + 1
            lines.append(
                f"{rank}. `{ascii_text(city_row['municipio_base'])}` - {app.format_money(city_row['valor_total'])} em {app.format_int(city_row['registros'])} registros."
            )
    lines.append("")
    lines.append(quality_sentence(state_df))
    lines.append("")
    lines.append(local_source_line(uf, "campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`"))
    lines.append("")
    lines.append("## Fontes extras")
    lines.append("")
    lines.append("### Dados locais")
    lines.append("")
    lines.append(f"- Arquivo principal desta historia: `processada/{uf}.parquet`.")
    lines.append("- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.")
    lines.append("")
    lines.append("### Fontes externas verificadas por entidade")
    lines.append("")
    lines.append(
        f"- [Consulta oficial de CNPJ (gov.br)]({RECEITA_SERVICE_URL})"
    )
    lines.append(
        f"- [Comprovante de inscricao e situacao cadastral (Receita)]({RECEITA_PROOF_URL})"
    )
    lines.append(
        f"- [Convenios e transferencias federais (gov.br / Transferegov)]({TRANSFEREGOV_URL})"
    )
    lines.append("")
    for source in top_entities_sources:
        profile = source["profile"] or {}
        source_url = profile.get("_source_url", BRASILAPI_CNPJ_URL.format(cnpj=source["cnpj"])) if source["cnpj"] else ""
        situacao = ascii_text(profile.get("descricao_situacao_cadastral") or profile.get("descricao_situacao_cadastral", ""))
        municipio = ascii_text(profile.get("municipio", ""))
        uf_ext = ascii_text(profile.get("uf", ""))
        atividade = ascii_text(profile.get("cnae_fiscal_descricao", ""))
        porte = ascii_text(profile.get("porte", ""))
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
        lines.append(f"- [{source['nome']} - busca complementar por CNPJ/nome/UF]({search_url(query)})")
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


def build_index(ufs: list[str]) -> str:
    lines = ["# Historias por UF", "", "Colecao de narrativas geradas a partir dos arquivos `.parquet` em `processada/`.", ""]
    for uf in ufs:
        state_name = STATE_NAMES.get(uf, uf)
        lines.append(f"- [{state_name} ({uf})]({uf}.md)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    signatures = app.build_sources_signature((str(app.DEFAULT_STATE_DATA_DIR),))
    data, _ = app.load_data((str(app.DEFAULT_STATE_DATA_DIR),), signatures)
    benchmark = app.build_state_benchmark(data)
    HISTORY_DIR.mkdir(exist_ok=True)
    cnpj_cache = load_cnpj_cache()

    ufs = sorted(data["uf"].dropna().unique().tolist())
    for uf in ufs:
        content = build_state_story(uf, data, benchmark, cnpj_cache)
        (HISTORY_DIR / f"{uf}.md").write_text(content, encoding="utf-8")

    (HISTORY_DIR / "index.md").write_text(build_index(ufs), encoding="utf-8")
    save_cnpj_cache(cnpj_cache)
    print(f"Historias geradas em {HISTORY_DIR}")
    print(f"Arquivos: {len(ufs) + 1}")


if __name__ == "__main__":
    main()
