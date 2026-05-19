from utils.capitais.shared import CapitalConfig, map_teresina

CONFIG = CapitalConfig(
    "teresina",
    "PI",
    "Teresina",
    "Teresina",
    "despesas_teresina_20*.csv",
    "csv",
    map_teresina,
    csv_sep=",",
)
