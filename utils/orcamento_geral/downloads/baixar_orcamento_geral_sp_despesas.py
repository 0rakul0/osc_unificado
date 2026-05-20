from __future__ import annotations

import argparse
import csv
import gzip
from pathlib import Path
import sys

from lxml import etree as ET
import requests
import urllib3

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_ORCAMENTO_GERAL_DIR, cli_default


SERVICE_URL = "https://webservices.fazenda.sp.gov.br/WSTransparencia/TransparenciaServico.asmx"
SOAP_ACTION = "http://fazenda.sp.gov.br/wstransparencia/ConsultarDespesas"
NAMESPACE = "{http://fazenda.sp.gov.br/wstransparencia}"
DEFAULT_YEARS = tuple(str(year) for year in range(2010, 2027))
CSV_COLUMNS = [
    "ano_consulta",
    "CodigoNomeOrgao",
    "CodigoNomeUo",
    "CodigoNomeUg",
    "CodigoNomeFonteRecursos",
    "CodigoNomeTipoLicitacao",
    "CodigoNomeFuncao",
    "CodigoNomeSubFuncao",
    "CodigoNomePrograma",
    "CodigoNomeAcao",
    "CodigoNomeProgramaTrabalho",
    "CodigoNomeMunicipio",
    "CgcCpfFavorecido",
    "CodigoNomeElemento",
    "NaturezaDespesaNomeItem",
    "ValorDotacaoInicial",
    "ValorDotacaoAtual",
    "ValorEmpenhado",
    "ValorLiquidado",
    "ValorPago",
    "ValorPagoAnosAnteriores",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa despesas gerais do Web Service oficial da Fazenda/SP."
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(BASES_ORCAMENTO_GERAL_DIR / "SP"),
        help="Pasta de saida para os CSVs brutos de despesas gerais de SP.",
    )
    parser.add_argument(
        "--years",
        nargs="*",
        default=list(DEFAULT_YEARS),
        help="Anos a baixar. Padrao: 2010 a 2026.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rebaixa anos que ja tem CSV bruto no destino.",
    )
    parser.add_argument(
        "--verify-tls",
        action="store_true",
        help="Valida TLS. Por padrao fica desligado porque o certificado da SEFAZ/SP falha em alguns ambientes.",
    )
    return parser.parse_args()


def build_soap_body(year: str) -> bytes:
    filters = {
        "ano": year,
        "codigoOrgao": "",
        "codigoUo": "",
        "codigoUnidadeGestora": "",
        "codigoFonteRecursos": "",
        "codigoTipoLicitacao": "",
        "codigoFuncao": "",
        "codigoSubfuncao": "",
        "codigoPrograma": "",
        "codigoAcao": "",
        "codigoFuncionalProgramatica": "",
        "codigoMunicipio": "",
        "codigoCategoria": "",
        "codigoGrupo": "",
        "codigoModalidade": "",
        "codigoElemento": "",
        "naturezaDespesa": "",
        "flagCredor": "true",
        "cgcCpfCredor": "",
        "nomeCredor": "",
        "flagEmpenhado": "true",
        "flagLiquidado": "true",
        "flagPago": "true",
    }
    params = "".join(f"<{key}>{value}</{key}>" for key, value in filters.items())
    envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AutenticacaoHeader xmlns="http://fazenda.sp.gov.br/wstransparencia">
      <Usuario></Usuario>
      <Senha></Senha>
    </AutenticacaoHeader>
  </soap:Header>
  <soap:Body>
    <ConsultarDespesas xmlns="http://fazenda.sp.gov.br/wstransparencia">{params}</ConsultarDespesas>
  </soap:Body>
</soap:Envelope>"""
    return envelope.encode("utf-8")


def strip_namespace(tag: str) -> str:
    return tag.split("}", 1)[-1]


def item_to_row(item: ET.Element, year: str) -> dict[str, str]:
    row = {column: "" for column in CSV_COLUMNS}
    row["ano_consulta"] = year
    for child in item:
        column = strip_namespace(child.tag)
        if column in row:
            row[column] = (child.text or "").strip()
    return row


def fetch_year(session: requests.Session, year: str, output_path: Path, verify_tls: bool) -> int:
    if not verify_tls:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = session.post(
        SERVICE_URL,
        data=build_soap_body(year),
        headers={
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f'"{SOAP_ACTION}"',
            "User-Agent": "Mozilla/5.0",
        },
        stream=True,
        verify=verify_tls,
        timeout=600,
    )
    response.raise_for_status()
    response.raw.decode_content = True

    count = 0
    with gzip.open(output_path, "wt", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for _event, element in ET.iterparse(response.raw, events=("end",), recover=True, huge_tree=True):
            if element.tag == f"{NAMESPACE}ItemDespesa":
                writer.writerow(item_to_row(element, year))
                count += 1
                element.clear()
    return count


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    for year in args.years:
        output_path = output_dir / f"sp_despesas_webservice_{year}.csv.gz"
        if output_path.exists() and not args.overwrite:
            print(f"{year}: ja existe, pulando ({output_path})")
            continue
        count = fetch_year(session, str(year), output_path, verify_tls=args.verify_tls)
        print(f"{year}: {count} itens salvos em {output_path}")


if __name__ == "__main__":
    main()
