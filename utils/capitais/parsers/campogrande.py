from utils.capitais.shared import CapitalConfig, map_campo_grande

CONFIG = CapitalConfig(
    "campogrande",
    "MS",
    "Campo Grande",
    "Campo Grande",
    "Consulta_de_Despesas__*.csv",
    "csv",
    map_campo_grande,
    csv_encoding="utf-8-sig",
    require_cnpj=True,
    latest_only=True,
)
