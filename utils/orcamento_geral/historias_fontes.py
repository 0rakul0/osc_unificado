from __future__ import annotations

from pathlib import Path
import re
import unicodedata

import pandas as pd

from project_paths import (
    BASES_CONVENIOS_CAPITAIS_DIR,
    BASES_CONVENIOS_DIR,
    BASES_ORCAMENTO_GERAL_DIR,
    CAPITAIS_PROCESSADA_DIR,
    ORCAMENTO_GERAL_PROCESSADA_DIR,
)
from utils.orcamento_geral.registry import STATE_CAPITALS, capital_parquet_name


STATE_SOURCE_URLS: dict[str, list[str]] = {
    "AC": [
        "https://transparencia.ac.gov.br/convenios",
        "https://transparencia.ac.gov.br/convenios/detalhamento-pdf",
    ],
    "AP": ["https://www.transparencia.ap.gov.br/"],
    "AM": ["https://www.transparencia.am.gov.br/"],
    "DF": ["https://dados.df.gov.br/"],
    "MT": [
        "https://consultas.transparencia.mt.gov.br/dados_abertos_consultas/despesa/",
        "https://consultas.transparencia.mt.gov.br/dados_abertos/despesa/Despesa_{year}.csv",
    ],
    "PA": ["https://api-notas-empenho.sistemas.pa.gov.br/notas-empenho/detalhe"],
    "PB": ["https://www.dados.pb.gov.br/"],
    "RN": ["http://convenios.control.rn.gov.br/conveniorelsite.aspx"],
    "RO": ["https://transparencia.ro.gov.br/convenios/filtrartransferencias"],
    "RR": ["https://api.transparencia.rr.gov.br/api/v1/portal/transparencia/visualizar-despesa-detalhada"],
    "SC": [
        "https://consultas.sctransferencias.cge.sc.gov.br/",
        "https://sctransf-api.prod.okd4.ciasc.sc.gov.br/csv/transferencias",
    ],
    "SP": [
        "http://www.parceriassociais.sp.gov.br",
        "http://www.parceriassociais.sp.gov.br/OSC/Termos_Acordos",
    ],
}

STATE_NOTES: dict[str, str] = {
    "AL": "Serie montada a partir de base legada local preservada em `bases_convenios/AL`.",
    "AM": "Serie consolidada com planilhas legadas preservadas em `bases_convenios/AM`.",
    "AP": "Serie consolidada a partir de planilha legada preservada em `bases_convenios/AP/TERMO DE FOMENTO.xlsx`.",
    "BA": "Serie montada a partir de arquivos locais legados preservados em `bases_convenios/BA`.",
    "CE": "Serie montada a partir de arquivos locais legados preservados em `bases_convenios/CE`.",
    "ES": "Serie recomposta a partir de arquivos CSV legados preservados em `bases_orcamento_geral/ES`.",
    "GO": "Serie consolidada a partir de planilha historica local preservada em `bases_convenios/GO`.",
    "MA": "Serie derivada do bruto local preservado em `bases_orcamento_geral/MA`.",
    "MG": "Serie derivada dos CSVs enriquecidos preservados em `bases_orcamento_geral/MG`.",
    "MS": "Serie derivada dos CSVs locais preservados em `bases_orcamento_geral/MS`.",
    "PA": "Serie complementada com CSVs locais preservados em `bases_orcamento_geral/PA`.",
    "PE": "Serie montada a partir do acervo local preservado em `bases_orcamento_geral/PE`.",
    "PI": "Serie montada a partir da planilha consolidada local preservada em `bases_orcamento_geral/PI`.",
    "PR": "Serie derivada dos zips historicos preservados em `bases_orcamento_geral/PR`.",
    "RJ": "Serie montada a partir de planilhas e CSVs locais preservados em `bases_orcamento_geral/RJ`.",
    "RS": "Serie derivada dos zips historicos preservados em `bases_orcamento_geral/RS`.",
    "SE": "Serie montada a partir de planilhas locais preservadas em `bases_orcamento_geral/SE`.",
    "TO": "Serie consolidada a partir da planilha legada `bases_convenios/TO/convenios_completo.xlsx`.",
}

CAPITAL_SOURCE_URLS: dict[str, list[str]] = {
    "AC": ["https://portalcgm.riobranco.ac.gov.br/portal/"],
    "AP": ["https://macapa.ap.gov.br/portaldatransparencia/"],
    "AM": ["https://transparencia.manaus.am.gov.br/transparencia/"],
    "CE": ["https://transparencia.fortaleza.ce.gov.br/index.php/convenio"],
    "DF": ["https://dados.df.gov.br/"],
    "ES": ["https://wstransparencia.vitoria.es.gov.br"],
    "GO": ["https://www10.goiania.go.gov.br/transweb/Portal_DespesasTransferencias.aspx"],
    "MA": ["https://saoluis.giap.com.br/ords/saoluis/f?p=839:104"],
    "MG": ["https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/controladoria/convenios-de-repasse-31-10-2024-csv.csv"],
    "MT": ["http://transparencia.cuiaba.mt.gov.br/portaltransparencia/servlet/a"],
    "MS": ["https://sig-transparencia.campogrande.ms.gov.br/repasses-estaduais/consulta"],
    "PA": ["https://transparencia.belem.pa.gov.br/giig/portais/portaldatransparencia/Despesas/wfrmConsultaConveniosSemLayout.aspx"],
    "PB": [
        "https://transparencia.joaopessoa.pb.gov.br/#/convenios/convenios-municipais",
        "https://transparencia.joaopessoa.pb.gov.br:8080/convenios/municipais",
    ],
    "PE": [
        "https://dados.recife.pe.gov.br/",
        "https://dados.recife.pe.gov.br/tr/dataset/contratos-de-gestao",
    ],
    "PI": ["https://transparencia.teresina.pi.gov.br/bp/parcerias"],
    "PR": ["https://www.transparencia.curitiba.pr.gov.br/conteudo/convenios.aspx"],
    "RJ": ["https://riotransparente.rio.rj.gov.br/web/index.asp"],
    "RN": [
        "https://www2.natal.rn.gov.br/transparencia/contratos.php",
        "https://www2.natal.rn.gov.br/transparencia/contratosVisualizar.php",
    ],
    "RS": ["https://cnc.procempa.com.br/cnc/servlet/cnc.procempa.com.br.wwconvenios_portal"],
    "RO": [
        "https://transparencia.portovelho.ro.gov.br/contratos?modelo_nome=7",
        "https://api.portovelho.ro.gov.br/api/v1/contratos",
    ],
    "RR": ["https://transparencia.boavista.rr.gov.br/convenios"],
    "SC": ["https://transparencia.e-publica.net/epublica-portal/#/florianopolis/portal/despesa/convenioRepassadoTable?entidade=2002"],
    "SE": ["https://transparencia.aracaju.se.gov.br/prefeitura/convenios-e-outros-ajustes/"],
    "SP": [
        "https://dados.prefeitura.sp.gov.br/api/3/action/package_show",
        "https://dados.prefeitura.sp.gov.br/dataset/0fe868fc-4d8d-468a-a3e0-a2b512da96e3",
    ],
    "TO": [
        "https://prodata.palmas.to.gov.br/sig/app.html#/transparencia/contratos/",
        "https://prodata.palmas.to.gov.br/sig/rest/transparenciaContratosController/getContratos",
    ],
}

CAPITAL_NOTES: dict[str, str] = {
    "AL": "Capital consolidada a partir de base legada local preservada em `bases_convenios_capitais/Maceio`.",
    "BA": "Capital consolidada a partir de base legada local preservada em `bases_convenios_capitais/Salvador`.",
}

CAPITAL_DOWNLOADER_OVERRIDES = {
    "MG": "belo_horizonte",
    "MS": "campo_grande",
    "RJ": "rio",
    "RO": "porto_velho",
    "RS": "porto_alegre",
    "SP": "sao_paulo",
    "MA": "sao_luis",
}


def normalize_token(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def state_capital_entry(uf: str):
    for entry in STATE_CAPITALS:
        if entry.uf == uf:
            return entry
    raise KeyError(f"UF nao encontrada: {uf}")


def find_state_raw_dir(uf: str) -> Path | None:
    for root in (BASES_ORCAMENTO_GERAL_DIR, BASES_CONVENIOS_DIR):
        candidate = root / uf
        if candidate.exists():
            return candidate
    return None


def find_capital_raw_dir(uf: str) -> Path | None:
    entry = state_capital_entry(uf)
    target = normalize_token(entry.capital)
    for child in BASES_CONVENIOS_CAPITAIS_DIR.iterdir():
        if child.is_dir() and normalize_token(child.name) == target:
            return child
    return None


def preview_files(directory: Path | None, limit: int = 5) -> list[str]:
    if directory is None or not directory.exists():
        return []
    return [item.name for item in sorted(directory.iterdir()) if item.is_file()][:limit]


def count_parquet_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return len(pd.read_parquet(path))
    except Exception:
        return None


def existing_paths(paths: list[Path]) -> list[Path]:
    return [path for path in paths if path.exists()]


def state_script_paths(uf: str) -> list[Path]:
    base = Path("utils/orcamento_geral")
    lower = uf.lower()
    return existing_paths(
        [
            base / f"processar_orcamento_geral_{lower}.py",
            base / f"baixar_orcamento_geral_{lower}.py",
        ]
    )


def capital_script_paths(uf: str) -> list[Path]:
    entry = state_capital_entry(uf)
    base = Path("utils/orcamento_geral")
    suffix = CAPITAL_DOWNLOADER_OVERRIDES.get(uf, normalize_token(entry.capital))
    return existing_paths(
        [
            base / "processar_orcamento_geral_capitais.py",
            base / f"baixar_convenios_capital_{suffix}.py",
        ]
    )


def markdown_links(urls: list[str]) -> list[str]:
    links: list[str] = []
    for url in urls:
        label = url.replace("https://", "").replace("http://", "")
        links.append(f"[{label}]({url})")
    return links


def provenance_section(uf: str) -> str:
    entry = state_capital_entry(uf)
    state_parquet = ORCAMENTO_GERAL_PROCESSADA_DIR / f"{uf}.parquet"
    capital_parquet = CAPITAIS_PROCESSADA_DIR / capital_parquet_name(uf, entry.capital)
    state_raw_dir = find_state_raw_dir(uf)
    capital_raw_dir = find_capital_raw_dir(uf)
    state_rows = count_parquet_rows(state_parquet)
    capital_rows = count_parquet_rows(capital_parquet)
    state_urls = STATE_SOURCE_URLS.get(uf, [])
    capital_urls = CAPITAL_SOURCE_URLS.get(uf, [])
    state_examples = preview_files(state_raw_dir)
    capital_examples = preview_files(capital_raw_dir)
    state_scripts = state_script_paths(uf)
    capital_scripts = capital_script_paths(uf)

    lines: list[str] = []
    lines.append("## Proveniencia das fontes")
    lines.append("")
    lines.append("### Estado")
    lines.append("")
    lines.append(
        f"- Parquet estadual consolidado: `{state_parquet}`"
        + (f" ({state_rows} linhas)." if state_rows is not None else ".")
    )
    if state_raw_dir is not None:
        lines.append(f"- Pasta bruta usada no pipeline estadual: `{state_raw_dir}`.")
    if state_examples:
        lines.append(f"- Exemplos de arquivos brutos estaduais: `{ '`, `'.join(state_examples) }`.")
    if state_scripts:
        lines.append(
            f"- Scripts associados ao estado: `{ '`, `'.join(path.as_posix() for path in state_scripts) }`."
        )
    if state_urls:
        lines.append(f"- Fontes oficiais registradas para o estado: {', '.join(markdown_links(state_urls))}.")
    note = STATE_NOTES.get(uf)
    if note:
        lines.append(f"- Observacao de trilha: {note}")
    lines.append("")
    lines.append(f"### Capital ({entry.capital})")
    lines.append("")
    lines.append(
        f"- Parquet da capital consolidado: `{capital_parquet}`"
        + (f" ({capital_rows} linhas)." if capital_rows is not None else ".")
    )
    if capital_raw_dir is not None:
        lines.append(f"- Pasta bruta usada no pipeline da capital: `{capital_raw_dir}`.")
    if capital_examples:
        lines.append(f"- Exemplos de arquivos brutos da capital: `{ '`, `'.join(capital_examples) }`.")
    if capital_scripts:
        lines.append(
            f"- Scripts associados a capital: `{ '`, `'.join(path.as_posix() for path in capital_scripts) }`."
        )
    if capital_urls:
        lines.append(f"- Fontes oficiais registradas para a capital: {', '.join(markdown_links(capital_urls))}.")
    capital_note = CAPITAL_NOTES.get(uf)
    if capital_note:
        lines.append(f"- Observacao de trilha: {capital_note}")
    lines.append("")
    return "\n".join(lines)

