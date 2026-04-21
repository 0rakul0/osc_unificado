from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import gc
import json
import re
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable, Iterable, Iterator

import pandas as pd
import pyarrow.parquet as pq

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import BASES_CONVENIOS_CAPITAIS_DIR, CAPITAIS_PROCESSADA_DIR, cli_default
from utils.common import STANDARD_COLUMNS
from utils.convenios.unificador import build_parquet_table, normalize_preview
from utils.orcamento_geral.registry import capital_parquet_name


ORIGEM_CAPITAIS = "capitais"
JSON_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class CapitalConfig:
    key: str
    uf: str
    municipio: str
    folder: str
    file_glob: str
    format: str
    mapper: Callable[[pd.DataFrame, "CapitalConfig"], pd.DataFrame]
    csv_sep: str = ";"
    csv_encoding: str = "utf-8"
    csv_skiprows: int = 0
    excel_skiprows: int = 0
    require_cnpj: bool = True
    html_table_index: int = 0
    latest_only: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Processa os dados brutos das capitais para parquets no schema padrao."
    )
    parser.add_argument(
        "--base-dir",
        default=cli_default(BASES_CONVENIOS_CAPITAIS_DIR),
        help="Diretorio raiz com as subpastas das capitais.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(CAPITAIS_PROCESSADA_DIR),
        help="Diretorio de saida para os arquivos UF_NOMECAPITAL.parquet.",
    )
    parser.add_argument(
        "--capitais",
        nargs="*",
        help="Lista opcional de capitais/chaves a processar. Ex.: riobranco maceio manaus",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20000,
        help="Quantidade de registros por lote para JSON e CSV.",
    )
    return parser.parse_args()


def city_series(frame: pd.DataFrame, value: str) -> pd.Series:
    return pd.Series(value, index=frame.index, dtype="string")


def clean_text(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="string")
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )


def clean_wrapped_json_text(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    cleaned = cleaned.str.replace(r'^\s*"', "", regex=True)
    cleaned = cleaned.str.replace(r'"\s*$', "", regex=True)
    cleaned = cleaned.str.strip()
    return cleaned.replace({"": pd.NA})


def first_non_empty(*series: pd.Series | None) -> pd.Series:
    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = clean_text(current)
        result = cleaned if result is None else result.combine_first(cleaned)
    if result is None:
        return pd.Series(dtype="string")
    return result


def first_non_empty_wrapped(*series: pd.Series | None) -> pd.Series:
    result: pd.Series | None = None
    for current in series:
        if current is None:
            continue
        cleaned = clean_wrapped_json_text(current)
        result = cleaned if result is None else result.combine_first(cleaned)
    if result is None:
        return pd.Series(dtype="string")
    return result


def extract_year_month(date_series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if date_series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    parsed = pd.to_datetime(date_series, errors="coerce", dayfirst=True, utc=True, format="mixed")
    ano = pd.Series(parsed.dt.year, index=date_series.index, dtype="Int64").astype("string")
    mes = pd.Series(parsed.dt.month, index=date_series.index, dtype="Int64").astype("string")
    return ano, mes


def clean_document(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    digits = cleaned.str.replace(r"\D", "", regex=True)
    return digits.mask(digits.eq("")).mask(digits.str.len().lt(11))


def normalize_scientific_document(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned

    def convert(value: object) -> object:
        if pd.isna(value):
            return pd.NA

        text = str(value).strip()
        if not text:
            return pd.NA

        if "E+" not in text.upper():
            digits = re.sub(r"\D", "", text)
            return digits if digits else pd.NA

        normalized = text.replace(".", "").replace(",", ".")
        try:
            number = Decimal(normalized)
        except InvalidOperation:
            digits = re.sub(r"\D", "", text)
            return digits if digits else pd.NA

        digits = format(number, "f").split(".")[0]
        return digits if digits else pd.NA

    return cleaned.map(convert).astype("string")


def normalize_year_reference(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    normalized = cleaned.str.replace(r"^((?:19|20)\d{2})[_-]\d+$", r"\1", regex=True)
    return normalized


def excel_serial_to_date(series: pd.Series | None) -> pd.Series:
    cleaned = clean_text(series)
    if cleaned.empty:
        return cleaned
    numeric = pd.to_numeric(cleaned.str.replace(",", ".", regex=False), errors="coerce")
    parsed = pd.to_datetime(numeric, unit="D", origin="1899-12-30", errors="coerce")
    return parsed.dt.strftime("%Y-%m-%d").astype("string")


def split_vigencia_series(series: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    if series is None:
        empty = pd.Series(dtype="string")
        return empty, empty
    cleaned = clean_text(series)
    split = cleaned.str.split(r"\s*(?:-\s*|At(?:é|e|Ã©)\s+)", n=1, expand=True)
    if split.empty:
        empty = pd.Series(pd.NA, index=series.index, dtype="string")
        return empty, empty
    start = split[0].astype("string")
    end = split[1].astype("string") if 1 in split.columns else pd.Series(pd.NA, index=series.index, dtype="string")
    return start, end


def standardize_frame(mapped: pd.DataFrame) -> pd.DataFrame:
    for column in STANDARD_COLUMNS:
        if column not in mapped.columns:
            mapped[column] = pd.NA
    return mapped[STANDARD_COLUMNS]


def map_rio_branco(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": normalize_year_reference(frame.get("ano_referencia")),
                "valor_total": first_non_empty(frame.get("pago_rs"), frame.get("liquidado_rs"), frame.get("empenhado_rs")),
                "cnpj": frame.get("cpf/cpnj"),
                "nome_osc": first_non_empty(frame.get("nome/razão_social"), frame.get("pessoa")),
                "mes": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "modalidade": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "data_inicio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_maceio(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": frame.get("ano"),
                "valor_total": first_non_empty(frame.get("valor_pago"), frame.get("valor_liquidado"), frame.get("valor_empenhado")),
                "cnpj": frame.get("cnpj"),
                "nome_osc": frame.get("credor"),
                "mes": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": first_non_empty(frame.get("municipio")).fillna(config.municipio),
                "objeto": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "modalidade": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "data_inicio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_macapa(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    movement_date = first_non_empty(frame.get("dataMovimento"), frame.get("dataEmpenho"))
    ano, mes = extract_year_month(movement_date)
    ano = ano.combine_first(clean_text(frame.get("exercicio")))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": clean_text(frame.get("valor")),
                "cnpj": frame.get("cpfcnpj"),
                "nome_osc": first_non_empty(frame.get("contribuinte2"), frame.get("contribuinte")),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("historicoMov"), frame.get("historico"), frame.get("especificacao")),
                "modalidade": first_non_empty(frame.get("modalidade"), frame.get("tipoEmpenho")),
                "data_inicio": movement_date,
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_manaus(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": frame.get("EmpAno"),
                "valor_total": first_non_empty(frame.get("EmpTotalPago"), frame.get("EmpTotalLiquidado"), frame.get("EmpValorEmpenho")),
                "cnpj": frame.get("EmpFornCpfCnpj"),
                "nome_osc": frame.get("EmpFornNome"),
                "mes": frame.get("EmpMes"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("EmpDescr"), frame.get("EMPPROJETOATIVDESCR"), frame.get("NaturezaNome")),
                "modalidade": first_non_empty(frame.get("EmpTipoEmpenho"), frame.get("NaturezaNome")),
                "data_inicio": frame.get("EmpData"),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_salvador(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_empenho = clean_wrapped_json_text(frame.get("Credor"))
    ano, mes = extract_year_month(data_empenho)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": clean_wrapped_json_text(frame.get("Valor Liquidado")),
                "cnpj": clean_wrapped_json_text(frame.get("Data do Lançamento")),
                "nome_osc": clean_wrapped_json_text(frame.get("Convenio Sigef")),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": clean_wrapped_json_text(frame.get("Valor Pago")),
                "modalidade": first_non_empty_wrapped(frame.get("Modalidade"), frame.get("Licitação Sigef")),
                "data_inicio": data_empenho,
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_vitoria(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": frame.get("AnoConvenio"),
                "valor_total": first_non_empty(frame.get("ValorContratado"), frame.get("ValorOriginal"), frame.get("ValorAditivo")),
                "cnpj": frame.get("CPFCNPJ"),
                "nome_osc": frame.get("EntidadeProponente"),
                "mes": extract_year_month(frame.get("DataCelebracao"))[1].combine_first(extract_year_month(frame.get("DataInicio"))[1]),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("Objeto"),
                "modalidade": first_non_empty(frame.get("TipoConvenio"), frame.get("Modalidade"), frame.get("Situacao")),
                "data_inicio": first_non_empty(frame.get("DataCelebracao"), frame.get("DataInicio")),
                "data_fim": frame.get("DataFinal"),
            }
        )
    )


def map_fortaleza(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio, data_fim = split_vigencia_series(frame.get("Vigência"))
    ano, mes = extract_year_month(frame.get("Data Celebração"))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano.combine_first(clean_text(frame.get("AnoArquivo"))),
                "valor_total": frame.get("Valor do Convenio"),
                "cnpj": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "nome_osc": frame.get("Convenente"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("Nº Convenio"),
                "modalidade": first_non_empty(frame.get("Tipo"), frame.get("Unidade Orçamentária Concedente")),
                "data_inicio": data_inicio.combine_first(clean_text(frame.get("Data Celebração"))),
                "data_fim": data_fim,
            }
        )
    )


def map_cuiaba(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    ano, mes = extract_year_month(frame.get("ConvenioDataAssinatura"))
    nome_osc = clean_text(frame.get("ConvenioCredorNome"))
    credor = clean_text(frame.get("ConvenioCredor"))
    credor = credor.mask(credor.str.fullmatch(r"-+", na=False))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("ConvenioAno")).combine_first(ano),
                "valor_total": first_non_empty(
                    frame.get("ConvenioValorTotal"),
                    frame.get("ConvenioValor"),
                    frame.get("ConvenioValorAditivado"),
                ),
                "cnpj": frame.get("ConvenioCredorDoc"),
                "nome_osc": nome_osc.combine_first(credor),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("ConvenioObjeto"),
                "modalidade": first_non_empty(frame.get("ConvenioModalidade"), frame.get("ConvenioTipoDsc")),
                "data_inicio": first_non_empty(frame.get("ConvenioDataVigenciaIni"), frame.get("ConvenioDataAssinatura")),
                "data_fim": frame.get("ConvenioDataVigenciaFim"),
            }
        )
    )


def map_belem(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio, data_fim = split_vigencia_series(frame.get("Vigência"))
    ano_vigencia, mes_vigencia = extract_year_month(data_inicio)
    ano_convenio = clean_text(frame.get("Ano do Convênio")).replace({"0": pd.NA})
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano_convenio.combine_first(ano_vigencia),
                "valor_total": first_non_empty(frame.get("Vlr. Previsto"), frame.get("Vlr. Repassado")),
                "cnpj": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "nome_osc": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "mes": mes_vigencia,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("Objeto"),
                "modalidade": frame.get("Cedente"),
                "data_inicio": data_inicio,
                "data_fim": data_fim,
            }
        )
    )


def map_joao_pessoa(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    ano, mes = extract_year_month(frame.get("data_publicacao"))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano.combine_first(clean_text(frame.get("AnoArquivo"))),
                "valor_total": first_non_empty(frame.get("valor_pactuado"), frame.get("valor_contrapartida")),
                "cnpj": frame.get("convenente_cnpj"),
                "nome_osc": first_non_empty(frame.get("convenente_nome"), frame.get("nome")),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("objeto"),
                "modalidade": first_non_empty(frame.get("tipo"), frame.get("concedente")),
                "data_inicio": first_non_empty(frame.get("inicio_vigencia"), frame.get("data_celebracao")),
                "data_fim": frame.get("fim_vigencia"),
            }
        )
    )


def map_goiania(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    numero_ano = clean_text(frame.get("Número/Ano"))
    ano_instr = numero_ano.str.extract(r"(\d{4})$", expand=False).astype("string")
    ano, mes = extract_year_month(frame.get("Data Publicação"))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("AnoArquivo")).combine_first(ano).combine_first(ano_instr),
                "valor_total": frame.get("Valor Total"),
                "cnpj": frame.get("Beneficiário CNPJ Destino"),
                "nome_osc": frame.get("Beneficiário Nome Destino"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": numero_ano,
                "modalidade": numero_ano,
                "data_inicio": first_non_empty(frame.get("Vigência Inicio"), frame.get("Data Publicação")),
                "data_fim": frame.get("Vigencia Fim"),
            }
        )
    )


def map_sao_luis(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    nome_osc = clean_text(frame.get("NOME OSC.")).str.replace(r"^\d+\s*-\s*", "", regex=True)
    ano_instr = clean_text(frame.get("ANO INSTRUMENTO")).str.extract(r"(\d{4})", expand=False).astype("string")
    ano_data, mes = extract_year_month(frame.get("DATA INICIO"))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano_instr.combine_first(ano_data),
                "valor_total": first_non_empty(frame.get("VALOR PAGO"), frame.get("VALOR TOTAL")),
                "cnpj": frame.get("CNPJ OSC."),
                "nome_osc": nome_osc,
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("OBJETO"),
                "modalidade": frame.get("INSTRUMENTO"),
                "data_inicio": frame.get("DATA INICIO"),
                "data_fim": frame.get("DATA ENCERRAMENTO"),
            }
        )
    )


def map_campo_grande(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio = clean_text(frame.get("dataempenho"))
    ano, mes = extract_year_month(data_inicio)
    ano = clean_text(frame.get("ano")).combine_first(ano)
    modalidade = first_non_empty(
        frame.get("elementodespesa"),
        frame.get("orgao"),
        frame.get("nomeunidadegestora"),
    )
    documento = clean_document(frame.get("cnpjfornecedor"))
    pessoa_fisica = modalidade.str.contains(r"Pessoa F[ií]sica", case=False, na=False)
    documento = documento.mask(pessoa_fisica)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": first_non_empty(
                    frame.get("total_pago"),
                    frame.get("total_liquidado"),
                    frame.get("total_empenhado"),
                ),
                "cnpj": documento,
                "nome_osc": frame.get("nomefornecedor"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(
                    frame.get("itemclassificacaodespesa"),
                    frame.get("fonte"),
                    frame.get("orgao"),
                ),
                "modalidade": modalidade,
                "data_inicio": data_inicio,
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_brasilia(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    publicacao = first_non_empty(frame.get("Publicação"), frame.get("Celebração"))
    ano, mes = extract_year_month(publicacao)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("Exercício")).combine_first(ano),
                "valor_total": first_non_empty(frame.get("Valor Transferência"), frame.get("Valor Pactuado")),
                "cnpj": frame.get("CPF/CNPJ Convenente"),
                "nome_osc": frame.get("Convenente"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("Objeto Resumido"), frame.get("Justificativa")),
                "modalidade": first_non_empty(frame.get("Espécie"), frame.get("Situação"), frame.get("Gestão")),
                "data_inicio": first_non_empty(frame.get("Celebração"), frame.get("Início Vigência")),
                "data_fim": frame.get("Fim Vigência"),
            }
        )
    )


def map_belo_horizonte(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    fornecedor = clean_text(frame.get("fornecedor"))
    nome_osc = (
        fornecedor.str.replace(r"^\d+\s*-\s*", "", regex=True)
        .str.replace(r"\s*\(R\$\s*[^)]*\)", "", regex=True)
        .str.replace(r"\s*/\s*\d+\s*-\s*", " / ", regex=True)
        .str.strip()
    )
    ano, mes = extract_year_month(first_non_empty(frame.get("data_publicacao"), frame.get("data_inicio_vigencia")))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("ano_ij")).combine_first(ano),
                "valor_total": frame.get("valor_ij"),
                "cnpj": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "nome_osc": nome_osc,
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("objeto"),
                "modalidade": first_non_empty(frame.get("natureza"), frame.get("tipo_contrato"), frame.get("situao")),
                "data_inicio": frame.get("data_inicio_vigencia"),
                "data_fim": frame.get("data_fim_vigencia"),
            }
        )
    )


def map_belo_horizonte_despesas(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_referencia = first_non_empty(
        frame.get("data_op"),
        frame.get("DATA_OP"),
        frame.get("data_liquidacao"),
        frame.get("DATA_LIQUIDACAO"),
        frame.get("dt_lancamento"),
        frame.get("DT_LANCAMENTO"),
    )
    ano, mes = extract_year_month(data_referencia)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": first_non_empty(
                    frame.get("ano_op"),
                    frame.get("ANO_OP"),
                    frame.get("ano_liquidacao"),
                    frame.get("ANO_LIQUIDACAO"),
                    frame.get("ano_empenho"),
                    frame.get("ANO_EMPENHO"),
                ).combine_first(ano),
                "valor_total": first_non_empty(
                    frame.get("valor_bruto_op"),
                    frame.get("VALOR_BRUTO_OP"),
                    frame.get("vl_npd"),
                    frame.get("VL_NPD"),
                    frame.get("vl_empenhado"),
                    frame.get("VL_EMPENHADO"),
                ),
                "cnpj": normalize_scientific_document(first_non_empty(frame.get("numero_documento"), frame.get("NUMERO_DOCUMENTO"))),
                "nome_osc": first_non_empty(frame.get("nome_credor"), frame.get("NOME_CREDOR")),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("justificativa_sucinta"), frame.get("JUSTIFICATIVA_SUCINTA")),
                "modalidade": first_non_empty(
                    frame.get("modalidade_licitacao"),
                    frame.get("MODALIDADE_LICITACAO"),
                    frame.get("nome_natureza_despesa"),
                    frame.get("NOME_NATUREZA_DESPESA"),
                    frame.get("natureza_despesa"),
                    frame.get("NATUREZA_DESPESA"),
                ),
                "data_inicio": data_referencia,
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_curitiba(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio, data_fim = split_vigencia_series(frame.get("vigencia"))
    ano, mes = extract_year_month(data_inicio)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("ano")).combine_first(ano),
                "valor_total": first_non_empty(frame.get("valor_total"), frame.get("valor_concedente")),
                "cnpj": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "nome_osc": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("objeto"),
                "modalidade": first_non_empty(frame.get("termo_ajuste"), frame.get("orgao_gestor")),
                "data_inicio": data_inicio,
                "data_fim": data_fim,
            }
        )
    )


def map_rio_de_janeiro(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio = clean_text(frame.get("Data Início Previsto"))
    ano, mes = extract_year_month(data_inicio)
    nome_osc = clean_text(frame.get("Favorecidos"))
    nome_osc = nome_osc.str.replace(r"^\d{11,14}", "", regex=True).str.strip()
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": first_non_empty(
                    frame.get("Valor Atualizado do  Instrumento"),
                    frame.get("Valor Instrumento"),
                ),
                "cnpj": clean_document(frame.get("CNPJ/CPF")),
                "nome_osc": nome_osc,
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("Número do Instrumento"),
                "modalidade": frame.get("Espécie"),
                "data_inicio": data_inicio,
                "data_fim": frame.get("Data Término Previsto"),
            }
        )
    )


def map_porto_alegre(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio = clean_text(frame.get("data_inicio_lista")).combine_first(clean_text(frame.get("data_inicio")))
    ano, mes = extract_year_month(data_inicio)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("ano")).combine_first(ano),
                "valor_total": first_non_empty(frame.get("valor_lista"), frame.get("valor_previsto_total"), frame.get("valor_repasse")),
                "cnpj": clean_document(frame.get("cnpj")),
                "nome_osc": first_non_empty(frame.get("executor"), frame.get("convenente")),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("objeto"), frame.get("objeto_lista"), frame.get("numero_lista")),
                "modalidade": first_non_empty(frame.get("tipo_convenio"), frame.get("status"), frame.get("status_lista"), frame.get("orgao_lista")),
                "data_inicio": data_inicio,
                "data_fim": frame.get("data_fim"),
            }
        )
    )


def map_aracaju(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": frame.get("ano"),
                "valor_total": first_non_empty(frame.get("valor_mes"), frame.get("valor_total_ano")),
                "cnpj": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "nome_osc": frame.get("nome_osc"),
                "mes": frame.get("mes"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("objeto"), frame.get("fonte_pdf")),
                "modalidade": frame.get("secretaria"),
                "data_inicio": frame.get("data_inicio"),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_boavista(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio = clean_text(frame.get("DATAE"))
    ano = clean_text(frame.get("DATAE")).str.extract(r"((?:19|20)\d{2})", expand=False).astype("string")
    _, mes = extract_year_month(data_inicio)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": first_non_empty(
                    frame.get("PAGO"),
                    frame.get("LIQUIDADO"),
                    frame.get("EMPENHADO"),
                ),
                "cnpj": frame.get("CPFFORMATADO"),
                "nome_osc": frame.get("NOMEFOR"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(
                    frame.get("PRODU"),
                    frame.get("PROJETO_ATIVIDADE_NOME"),
                    frame.get("PROGRAMANOME"),
                    frame.get("PROC"),
                ),
                "modalidade": first_non_empty(
                    frame.get("DESCLICIT_DETALHESEMPENHO"),
                    frame.get("NATUREZA"),
                    frame.get("FUNCAONOME"),
                ),
                "data_inicio": data_inicio,
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_recife(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    ano = clean_text(frame.get("AnoArquivo"))
    if ano.empty:
        ano = pd.Series("2023", index=frame.index, dtype="string")
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano.combine_first(clean_text(frame.get("ano"))),
                "valor_total": frame.get("VALOR MÊS"),
                "cnpj": frame.get("CNPJ"),
                "nome_osc": frame.get("Contratada"),
                "mes": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("Objeto"), frame.get("Observaçoes"), frame.get("Contrato")),
                "modalidade": first_non_empty(frame.get("Tipo de Repasse"), frame.get("Unidade")),
                "data_inicio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "data_fim": pd.Series(pd.NA, index=frame.index, dtype="string"),
            }
        )
    )


def map_porto_velho(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    ano, mes = extract_year_month(first_non_empty(frame.get("data_vigencia_inicio"), frame.get("data_assinatura")))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("contrato_ano")).combine_first(ano),
                "valor_total": first_non_empty(frame.get("valor_total"), frame.get("valor_executado")),
                "cnpj": frame.get("fornecedor_documento"),
                "nome_osc": first_non_empty(frame.get("fornecedor_razao_social"), frame.get("fornecedor_nome")),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("objeto"), frame.get("numero"), frame.get("numero_processo")),
                "modalidade": first_non_empty(frame.get("modelo"), frame.get("categoria"), frame.get("situacao")),
                "data_inicio": first_non_empty(frame.get("data_vigencia_inicio"), frame.get("data_assinatura")),
                "data_fim": frame.get("data_vigencia_fim"),
            }
        )
    )


def map_natal(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio, data_fim = split_vigencia_series(frame.get("vigencia"))
    ano, mes = extract_year_month(first_non_empty(frame.get("data_assinatura"), data_inicio))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("exercicio")).combine_first(clean_text(frame.get("ano_pesquisa"))).combine_first(ano),
                "valor_total": frame.get("valor_total"),
                "cnpj": frame.get("contratado_cnpj"),
                "nome_osc": frame.get("contratado_nome"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("objeto"), frame.get("objeto_lista")),
                "modalidade": first_non_empty(frame.get("fundamentacao_legal"), frame.get("forma_contratacao_lista")),
                "data_inicio": first_non_empty(frame.get("data_assinatura"), data_inicio),
                "data_fim": data_fim,
            }
        )
    )


def map_florianopolis(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio = first_non_empty(frame.get("inicioVigencia"), frame.get("assinatura"))
    data_fim = frame.get("vencimento")
    ano, mes = extract_year_month(data_inicio)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": first_non_empty(frame.get("valorTotal"), frame.get("valorPagoTotal"), frame.get("valorEmpenhadoTotal")),
                "cnpj": frame.get("recebedor_cnpj"),
                "nome_osc": frame.get("recebedor_nome"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("objetoResumido"),
                "modalidade": first_non_empty(frame.get("tipo"), frame.get("numero")),
                "data_inicio": data_inicio,
                "data_fim": data_fim,
            }
        )
    )


def map_sao_paulo(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio = excel_serial_to_date(frame.get("Data Início"))
    data_fim = excel_serial_to_date(frame.get("Data Término"))
    data_referencia = first_non_empty(data_inicio, excel_serial_to_date(frame.get("Data Lavratura do Termo")))
    ano, mes = extract_year_month(data_referencia)
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": frame.get("Valor Mensal Total (R$)"),
                "cnpj": frame.get("CNPJ"),
                "nome_osc": frame.get("OSC Parceira"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": first_non_empty(frame.get("Unidade Educacional"), frame.get("Processo")),
                "modalidade": first_non_empty(frame.get("Situação Parceria"), pd.Series("PARCERIA EDUCACIONAL", index=frame.index, dtype="string")),
                "data_inicio": data_inicio,
                "data_fim": data_fim,
            }
        )
    )


def map_teresina(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    data_inicio = frame.get("Data assinatura")
    data_fim = pd.Series(pd.NA, index=frame.index, dtype="string")
    ano, mes = extract_year_month(first_non_empty(frame.get("Data da liberação da última parcela"), data_inicio))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": ano,
                "valor_total": first_non_empty(frame.get("Valor total"), frame.get("Valor liberado")),
                "cnpj": frame.get("CNPJ"),
                "nome_osc": frame.get("Nome da entidade"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("Objeto da parceria"),
                "modalidade": frame.get("Instrumento de parceria"),
                "data_inicio": data_inicio,
                "data_fim": data_fim,
            }
        )
    )


def map_palmas(frame: pd.DataFrame, config: CapitalConfig) -> pd.DataFrame:
    ano, mes = extract_year_month(frame.get("data_assinatura"))
    return standardize_frame(
        pd.DataFrame(
            {
                "uf": city_series(frame, config.uf),
                "origem": city_series(frame, ORIGEM_CAPITAIS),
                "ano": clean_text(frame.get("ano_contrato")).combine_first(ano),
                "valor_total": frame.get("valor_contrato"),
                "cnpj": first_non_empty(frame.get("nr_cgc_cpf2"), frame.get("nr_cgc_cpf")),
                "nome_osc": frame.get("nome_fornecedor"),
                "mes": mes,
                "cod_municipio": pd.Series(pd.NA, index=frame.index, dtype="string"),
                "municipio": city_series(frame, config.municipio),
                "objeto": frame.get("objetivo"),
                "modalidade": frame.get("modalidade"),
                "data_inicio": frame.get("data_assinatura"),
                "data_fim": frame.get("data_vencimento"),
            }
        )
    )


CAPITAL_CONFIGS = [
    CapitalConfig("riobranco", "AC", "Rio Branco", "Rio Branco", "*.json", "json", map_rio_branco),
    CapitalConfig("maceio", "AL", "Maceió", "Maceio", "maceio_*.json", "json", map_maceio),
    CapitalConfig("macapa", "AP", "Macapá", "MACAPA", "macapa_*.csv", "csv", map_macapa),
    CapitalConfig("manaus", "AM", "Manaus", "Manaus", "manaus_*.json", "json", map_manaus),
    CapitalConfig("salvador", "BA", "Salvador", "Salvador", "salvador_*.json", "json", map_salvador),
    CapitalConfig("fortaleza", "CE", "Fortaleza", "Fortaleza", "fortaleza_convenios_*.html", "html", map_fortaleza, require_cnpj=False),
    CapitalConfig("brasilia", "DF", "Brasilia", "Brasilia", "brasilia_convenios_*.csv", "csv", map_brasilia, csv_skiprows=1),
    CapitalConfig("vitoria", "ES", "Vitoria", "Vitoria", "vitoria_convenios_ug*_*.csv", "csv", map_vitoria, csv_sep=",", csv_encoding="latin1"),
    CapitalConfig("goiania", "GO", "Goiania", "Goiania", "goiania_convenios_20*.csv", "csv", map_goiania, csv_sep=","),
    CapitalConfig("saoluis", "MA", "Sao Luis", "Sao Luis", "saoluis_*.csv", "csv", map_sao_luis, csv_encoding="latin1"),
    CapitalConfig("belohorizonte", "MG", "Belo Horizonte", "Belo Horizonte", "belohorizonte_convenios_repasse.csv", "csv", map_belo_horizonte, csv_sep=",", require_cnpj=False),
    CapitalConfig("cuiaba", "MT", "Cuiaba", "Cuiaba", "cuiaba_convenio_*.json", "json", map_cuiaba, require_cnpj=False),
    CapitalConfig(
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
    ),
    CapitalConfig("belem", "PA", "Belem", "Belem", "belem_convenios_*.html", "html", map_belem, require_cnpj=False, html_table_index=5),
    CapitalConfig("joaopessoa", "PB", "Joao Pessoa", "Joao Pessoa", "joaopessoa_convenios_api_enriquecido.json", "json", map_joao_pessoa),
    CapitalConfig("recife", "PE", "Recife", "Recife", "recife_contratos_gestao_2023.csv", "csv", map_recife, csv_sep=";"),
    CapitalConfig("curitiba", "PR", "Curitiba", "Curitiba", "curitiba_convenios.csv", "csv", map_curitiba, csv_sep=",", require_cnpj=False),
    CapitalConfig("riodejaneiro", "RJ", "Rio de Janeiro", "Rio de Janeiro", "rio_contratos_especies.csv", "csv", map_rio_de_janeiro, csv_sep=","),
    CapitalConfig("natal", "RN", "Natal", "Natal", "natal_contratos_osc_enriquecido.json", "json", map_natal),
    CapitalConfig("portoalegre", "RS", "Porto Alegre", "Porto Alegre", "portoalegre_convenios.csv", "csv", map_porto_alegre, csv_sep=",", require_cnpj=False),
    CapitalConfig("portovelho", "RO", "Porto Velho", "Porto Velho", "portovelho_convenios_api_filtrado.json", "json", map_porto_velho),
    CapitalConfig("boavista", "RR", "Boa Vista", "Boa Vista", "boavista_despesas_gerais_*.json", "json", map_boavista),
    CapitalConfig("aracaju", "SE", "Aracaju", "Aracaju", "aracaju_repasses_ongs.csv", "csv", map_aracaju, csv_sep=",", require_cnpj=False),
    CapitalConfig("florianopolis", "SC", "Florianopolis", "Florianopolis", "florianopolis_convenios_enriquecido.json", "json", map_florianopolis),
    CapitalConfig("saopaulo", "SP", "Sao Paulo", "Sao Paulo", "sao_paulo_parcerias_educacao_infantil_*.csv", "csv", map_sao_paulo, csv_sep=";", csv_encoding="latin1"),
    CapitalConfig("teresina", "PI", "Teresina", "Teresina", "Relatório consolidado *.xls*", "excel", map_teresina, excel_skiprows=8, latest_only=True),
    CapitalConfig("palmas", "TO", "Palmas", "Palmas", "palmas_convenios_osc.json", "json", map_palmas),
]


def iter_json_array_records(path: Path) -> Iterator[dict[str, object]]:
    decoder = json.JSONDecoder()
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        buffer = ""
        started = False
        eof = False

        while True:
            if not eof and len(buffer) < JSON_CHUNK_SIZE:
                chunk = handle.read(JSON_CHUNK_SIZE)
                if chunk:
                    buffer += chunk
                else:
                    eof = True

            if not started:
                stripped = buffer.lstrip("\ufeff\r\n\t ")
                buffer = stripped
                if not buffer:
                    if eof:
                        return
                    continue
                if not buffer.startswith("["):
                    raise ValueError(f"{path} nao parece conter um array JSON na raiz.")
                buffer = buffer[1:]
                started = True

            buffer = buffer.lstrip("\r\n\t ,")
            if not buffer:
                if eof:
                    return
                continue

            if buffer.startswith("]"):
                return

            try:
                item, index = decoder.raw_decode(buffer)
            except json.JSONDecodeError:
                if eof:
                    raise
                continue

            if isinstance(item, dict):
                yield item
            buffer = buffer[index:]


def iter_json_batches(paths: list[Path], batch_size: int) -> Iterator[pd.DataFrame]:
    batch: list[dict[str, object]] = []
    for path in paths:
        for record in iter_json_array_records(path):
            batch.append(record)
            if len(batch) >= batch_size:
                yield pd.DataFrame(batch)
                batch.clear()
    if batch:
        yield pd.DataFrame(batch)


def iter_csv_batches(config: CapitalConfig, paths: list[Path], batch_size: int) -> Iterator[pd.DataFrame]:
    for path in paths:
        try:
            reader = pd.read_csv(
                path,
                dtype=str,
                sep=config.csv_sep,
                encoding=config.csv_encoding,
                skiprows=config.csv_skiprows,
                chunksize=batch_size,
                engine="python",
                on_bad_lines="skip",
            )
            yield from reader
        except Exception as exc:
            print(f"Arquivo CSV ignorado por erro de leitura: {path.name} ({type(exc).__name__})")


def iter_html_batches(config: CapitalConfig, paths: list[Path]) -> Iterator[pd.DataFrame]:
    for path in paths:
        try:
            tables = pd.read_html(path)
        except Exception as exc:
            print(f"Arquivo HTML ignorado por erro de leitura: {path.name} ({type(exc).__name__})")
            continue
        if not tables:
            continue
        if config.html_table_index >= len(tables):
            print(
                f"Arquivo HTML ignorado por indice de tabela ausente: {path.name} "
                f"(indice={config.html_table_index}, tabelas={len(tables)})"
            )
            continue
        frame = tables[config.html_table_index].copy()
        year_match = re.search(r"(19|20)\d{2}", path.stem)
        if year_match:
            frame["AnoArquivo"] = year_match.group(0)
        yield frame


def iter_excel_batches(config: CapitalConfig, paths: list[Path]) -> Iterator[pd.DataFrame]:
    for path in paths:
        try:
            frame = pd.read_excel(path, sheet_name=0, dtype=str, skiprows=config.excel_skiprows)
            yield frame
        except Exception as exc:
            print(f"Arquivo Excel ignorado por erro de leitura: {path.name} ({type(exc).__name__})")


def iter_source_batches(config: CapitalConfig, paths: list[Path], batch_size: int) -> Iterator[pd.DataFrame]:
    if config.format == "json":
        yield from iter_json_batches(paths, batch_size)
        return
    if config.format == "csv":
        yield from iter_csv_batches(config, paths, batch_size)
        return
    if config.format == "html":
        yield from iter_html_batches(config, paths)
        return
    if config.format == "excel":
        yield from iter_excel_batches(config, paths)
        return
    raise ValueError(f"Formato nao suportado: {config.format}")


def find_source_files(base_dir: Path, config: CapitalConfig) -> list[Path]:
    city_dir = base_dir / config.folder
    if not city_dir.exists():
        return []
    paths = sorted(path for path in city_dir.glob(config.file_glob) if path.is_file())
    if config.latest_only and paths:
        return [paths[-1]]
    return paths


def write_capital_parquet(
    config: CapitalConfig,
    source_paths: list[Path],
    output_dir: Path,
    batch_size: int,
) -> tuple[Path, int, int]:
    if not source_paths:
        raise FileNotFoundError(f"Nenhum arquivo encontrado para {config.municipio}.")

    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / capital_parquet_name(config.uf, config.municipio)
    temp_path = output_dir / f"{final_path.stem}.tmp.parquet"

    if temp_path.exists():
        temp_path.unlink()
    if final_path.exists():
        final_path.unlink()

    writer: pq.ParquetWriter | None = None
    total_source_rows = 0
    total_parquet_rows = 0

    try:
        for source_df in iter_source_batches(config, source_paths, batch_size):
            total_source_rows += len(source_df)
            mapped = config.mapper(source_df, config)
            normalized = normalize_preview(mapped, config.uf, require_cnpj=config.require_cnpj)
            if normalized.empty:
                del source_df
                del mapped
                gc.collect()
                continue

            table = build_parquet_table(normalized)
            if writer is None:
                writer = pq.ParquetWriter(temp_path, table.schema, compression="snappy")
            writer.write_table(table)
            total_parquet_rows += len(normalized)

            del source_df
            del mapped
            del normalized
            del table
            gc.collect()
    finally:
        if writer is not None:
            writer.close()

    if not temp_path.exists():
        raise RuntimeError(f"Nenhuma linha valida foi gerada para {config.municipio}.")

    temp_path.replace(final_path)
    return final_path, total_source_rows, total_parquet_rows

