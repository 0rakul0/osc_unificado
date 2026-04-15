from utils.capitais.shared import CapitalConfig, map_campo_grande

CONFIG = CapitalConfig("campogrande", "MS", "Campo Grande", "Campo Grande", "campogrande_repasses_estaduais_*.csv", "csv", map_campo_grande, require_cnpj=False)
