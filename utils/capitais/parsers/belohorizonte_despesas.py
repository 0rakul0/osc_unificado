from utils.capitais.shared import CapitalConfig, map_belo_horizonte_despesas


CONFIG = CapitalConfig(
    "belohorizonte_despesas",
    "MG",
    "Belo Horizonte",
    "Belo Horizonte",
    "*despesas*.csv",
    "csv",
    map_belo_horizonte_despesas,
    csv_sep=";",
    csv_encoding="cp1252",
    require_cnpj=True,
)
