from __future__ import annotations

import argparse
from pathlib import Path

from project_paths import BASES_ORCAMENTO_GERAL_CAPITAIS_DIR, BASES_ORCAMENTO_GERAL_DIR


ORCAMENTO_SCOPE_ESTADO = "estado"
ORCAMENTO_SCOPE_CAPITAL = "capital"
ORCAMENTO_SCOPES = (ORCAMENTO_SCOPE_ESTADO, ORCAMENTO_SCOPE_CAPITAL)


def normalize_scope(scope: str) -> str:
    value = str(scope or ORCAMENTO_SCOPE_ESTADO).strip().lower()
    if value not in ORCAMENTO_SCOPES:
        allowed = ", ".join(ORCAMENTO_SCOPES)
        raise ValueError(f"Escopo invalido: {scope!r}. Use um destes valores: {allowed}.")
    return value


def raw_root_dir(scope: str = ORCAMENTO_SCOPE_ESTADO) -> Path:
    return (
        BASES_ORCAMENTO_GERAL_CAPITAIS_DIR
        if normalize_scope(scope) == ORCAMENTO_SCOPE_CAPITAL
        else BASES_ORCAMENTO_GERAL_DIR
    )


def uf_raw_dir(uf: str, scope: str = ORCAMENTO_SCOPE_ESTADO) -> Path:
    return raw_root_dir(scope) / uf.upper()


def default_output_name(uf: str, scope: str = ORCAMENTO_SCOPE_ESTADO) -> str:
    suffix = "_capital" if normalize_scope(scope) == ORCAMENTO_SCOPE_CAPITAL else ""
    return f"{uf.upper()}{suffix}.parquet"


def add_scope_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--scope",
        choices=ORCAMENTO_SCOPES,
        default=ORCAMENTO_SCOPE_ESTADO,
        help="Define se os arquivos desta execucao pertencem ao escopo estadual ou ao recorte da capital.",
    )
