from importlib import import_module

from .common import ParserConfig, WorkbookParser


def get_parser(uf: str) -> WorkbookParser:
    module = import_module(f"utils.{uf.upper()}")
    parser = getattr(module, "PARSER", None)
    if parser is None:
        raise ValueError(f"Parser da UF {uf} nao encontrado.")
    return parser


__all__ = ["ParserConfig", "WorkbookParser", "get_parser"]
