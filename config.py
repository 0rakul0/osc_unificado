from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PathsConfig:
    base_dir: Path
    external_data_root: Path
    bases_convenios_dir: Path
    bases_convenios_capitais_dir: Path
    bases_orcamento_geral_dir: Path
    bases_orcamento_geral_capitais_dir: Path
    capitais_processada_dir: Path
    orcamento_geral_processada_dir: Path
    processada_dir: Path
    governo_federal_dir: Path
    historia_dir: Path
    historia_data_dir: Path
    auditoria_xlsx_path: Path
    sqlite_path: Path


@dataclass(frozen=True)
class DatabaseTablesConfig:
    transferencias: str = "transferencias"
    transferencias_analitica: str = "transferencias_analitica"
    arquivos_origem: str = "arquivos_origem"
    historias: str = "historias"
    auditoria_resumo: str = "auditoria_resumo"


@dataclass(frozen=True)
class DatabaseViewsConfig:
    resumo_uf: str = "vw_resumo_uf"
    top_entidades: str = "vw_top_entidades"
    serie_anual: str = "vw_serie_anual"
    alertas_qualidade: str = "vw_alertas_qualidade"


@dataclass(frozen=True)
class DatabaseConfig:
    path: Path
    tables: DatabaseTablesConfig
    views: DatabaseViewsConfig


BASE_DIR = Path(__file__).resolve().parent
EXTERNAL_DATA_ROOT = Path(r"E:\dados")

ENV_VARS = {
    "bases_convenios_dir": "OSC_BASES_CONVENIOS_DIR",
    "bases_convenios_capitais_dir": "OSC_BASES_CONVENIOS_CAPITAIS_DIR",
    "bases_orcamento_geral_dir": "OSC_BASES_ORCAMENTO_GERAL_DIR",
    "bases_orcamento_geral_capitais_dir": "OSC_BASES_ORCAMENTO_GERAL_CAPITAIS_DIR",
    "capitais_processada_dir": "OSC_CAPITAIS_PROCESSADA_DIR",
    "orcamento_geral_processada_dir": "OSC_ORCAMENTO_GERAL_PROCESSADA_DIR",
    "processada_dir": "OSC_PROCESSADA_DIR",
    "governo_federal_dir": "OSC_GOVERNO_FEDERAL_DIR",
    "historia_dir": "OSC_HISTORIA_DIR",
    "historia_data_dir": "OSC_HISTORIA_DATA_DIR",
    "auditoria_xlsx_path": "OSC_AUDITORIA_XLSX_PATH",
    "sqlite_path": "OSC_SQLITE_PATH",
}


def _resolve_configured_path(
    env_name: str,
    local_default_relative_path: str,
    external_candidates: list[str] | None = None,
) -> Path:
    configured = os.getenv(env_name, "").strip()
    if configured:
        return Path(configured).expanduser()

    if external_candidates:
        for relative_path in external_candidates:
            candidate = EXTERNAL_DATA_ROOT / relative_path
            if candidate.exists() or candidate.parent.exists():
                return candidate

    return BASE_DIR / local_default_relative_path


PATHS = PathsConfig(
    base_dir=BASE_DIR,
    external_data_root=EXTERNAL_DATA_ROOT,
    bases_convenios_dir=_resolve_configured_path(
        ENV_VARS["bases_convenios_dir"],
        "bases_convenios",
        ["bases_convenios"],
    ),
    bases_convenios_capitais_dir=_resolve_configured_path(
        ENV_VARS["bases_convenios_capitais_dir"],
        "bases_convenios_capitais",
        ["bases_convenios_capitais"],
    ),
    bases_orcamento_geral_dir=_resolve_configured_path(
        ENV_VARS["bases_orcamento_geral_dir"],
        "bases_orcamento_geral",
        ["bases_orcamento_geral", "bases_orcaomento_geral"],
    ),
    bases_orcamento_geral_capitais_dir=_resolve_configured_path(
        ENV_VARS["bases_orcamento_geral_capitais_dir"],
        "bases_orcamento_geral_capitais",
        ["bases_orcamento_geral_capitais"],
    ),
    capitais_processada_dir=_resolve_configured_path(
        ENV_VARS["capitais_processada_dir"],
        "capitais_processada",
        ["capitais_processada"],
    ),
    orcamento_geral_processada_dir=_resolve_configured_path(
        ENV_VARS["orcamento_geral_processada_dir"],
        "orcamento_geral_processada",
        ["orcamento_geral_processada"],
    ),
    processada_dir=_resolve_configured_path(
        ENV_VARS["processada_dir"],
        "processada",
        ["processada"],
    ),
    governo_federal_dir=_resolve_configured_path(
        ENV_VARS["governo_federal_dir"],
        "governo_federal",
        ["governo_federal"],
    ),
    historia_dir=_resolve_configured_path(
        ENV_VARS["historia_dir"],
        "historia",
    ),
    historia_data_dir=_resolve_configured_path(
        ENV_VARS["historia_data_dir"],
        "historia",
        ["historia"],
    ),
    auditoria_xlsx_path=_resolve_configured_path(
        ENV_VARS["auditoria_xlsx_path"],
        "auditoria_processada.xlsx",
        ["historia/auditoria_processada.xlsx", "auditoria_processada.xlsx"],
    ),
    sqlite_path=_resolve_configured_path(
        ENV_VARS["sqlite_path"],
        "osc_unificado.sqlite",
        ["sqlite/osc_unificado.sqlite"],
    ),
)

DB_TABLES = DatabaseTablesConfig()
DB_VIEWS = DatabaseViewsConfig()
DB = DatabaseConfig(
    path=PATHS.sqlite_path,
    tables=DB_TABLES,
    views=DB_VIEWS,
)

BASES_CONVENIOS_DIR = PATHS.bases_convenios_dir
BASES_CONVENIOS_CAPITAIS_DIR = PATHS.bases_convenios_capitais_dir
BASES_ORCAMENTO_GERAL_DIR = PATHS.bases_orcamento_geral_dir
BASES_ORCAMENTO_GERAL_CAPITAIS_DIR = PATHS.bases_orcamento_geral_capitais_dir
CAPITAIS_PROCESSADA_DIR = PATHS.capitais_processada_dir
ORCAMENTO_GERAL_PROCESSADA_DIR = PATHS.orcamento_geral_processada_dir
PROCESSADA_DIR = PATHS.processada_dir
GOVERNO_FEDERAL_DIR = PATHS.governo_federal_dir
HISTORIA_DIR = PATHS.historia_dir
HISTORIA_DATA_DIR = PATHS.historia_data_dir
AUDITORIA_XLSX_PATH = PATHS.auditoria_xlsx_path
SQLITE_PATH = PATHS.sqlite_path

TRANSFERENCIAS_TABLE = DB_TABLES.transferencias
TRANSFERENCIAS_ANALITICA_TABLE = DB_TABLES.transferencias_analitica
ARQUIVOS_ORIGEM_TABLE = DB_TABLES.arquivos_origem
HISTORIAS_TABLE = DB_TABLES.historias
AUDITORIA_RESUMO_TABLE = DB_TABLES.auditoria_resumo
VW_RESUMO_UF = DB_VIEWS.resumo_uf
VW_TOP_ENTIDADES = DB_VIEWS.top_entidades
VW_SERIE_ANUAL = DB_VIEWS.serie_anual
VW_ALERTAS_QUALIDADE = DB_VIEWS.alertas_qualidade

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


def cli_default(path: Path) -> str:
    return str(path)


def ensure_parent_dir(path: Path) -> None:
    parent = path.expanduser().resolve().parent
    parent.mkdir(parents=True, exist_ok=True)
