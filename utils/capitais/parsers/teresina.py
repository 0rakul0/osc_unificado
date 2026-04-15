from utils.capitais.shared import CapitalConfig, map_teresina

CONFIG = CapitalConfig("teresina", "PI", "Teresina", "Teresina", "Relat?rio consolidado *.xls*", "excel", map_teresina, excel_skiprows=8, latest_only=True)
