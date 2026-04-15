from importlib import import_module


def get_parser(uf: str):
    module = import_module(f"utils.convenios.parsers.{uf.upper()}")
    parser = getattr(module, "PARSER", None)
    if parser is None:
        raise ValueError(f"Parser da UF {uf} nao encontrado.")
    return parser
