from utils.capitais.shared import CapitalConfig, map_belo_horizonte

CONFIG = CapitalConfig("belohorizonte", "MG", "Belo Horizonte", "Belo Horizonte", "belohorizonte_convenios_repasse.csv", "csv", map_belo_horizonte, csv_sep=",", require_cnpj=False)
