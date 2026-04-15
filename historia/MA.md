# Maranhao (MA)

## Visao geral

Maranhao soma 98 registros e R$ 83.399.373,14 em valor total. No ranking geral da base, a UF esta em 26o lugar por valor, 24o por quantidade de registros, 11o por ticket medio e 15o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e base mais distribuida. O ticket medio e de R$ 851.014,01, a mediana e de R$ 657.846,26 e os 5 maiores beneficiarios concentram 31,5% do valor total.

_Fonte local deste bloco: `processada/MA.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, MA aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Maranhao cresce principalmente por base mais distribuida. A participacao da UF no total nacional desta pasta e de 0,0%.

_Fonte local deste bloco: `processada/MA.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `01611400000104` - BOM LUGAR: R$ 8.590.827,28 em 5 registros.
2. `06115117000105` - PARNARAMA: R$ 5.244.368,10 em 4 registros.
3. `06189344000177` - PINDARE MIRIM: R$ 4.683.330,00 em 5 registros.
4. `05505839000103` - URBANO SANTOS: R$ 4.085.157,64 em 4 registros.
5. `01612328000121` - CENTRO DO GUILHERME: R$ 3.678.947,37 em 2 registros.

_Fonte local deste bloco: `processada/MA.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `PAVIMENTACAO, CONSTRUCAO, ASFALTICA, PRACA, MUNICIPIO, VIAS, REFORMA, RECUPERACAO, ESTRADAS, BLOQUETE, VICINAIS, URBANAS`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `SANTA RITA` - R$ 2.549.527,89 (ano 2018): CONSTRUCAO DAS CABECEIRAS DA PONTE SOBRE O RIO ITAPECURU.
2. `BOM LUGAR` - R$ 2.106.130,41 (ano 2021): PAVIMENTACAO EM BLOQUETE.
3. `BOM LUGAR` - R$ 2.106.130,41 (ano 2021): PAVIMENTACAO EM BLOQUETES E URBANIZACAO.
4. `PINDARE MIRIM` - R$ 2.100.000,00 (ano 2021): PAVIMENTACAO ASFALTICA.
5. `CENTRO DO GUILHERME` - R$ 2.100.000,00 (ano 2019): CONSTRUCAO DO CENTRO ADMINISTRATIVO.

O maior registro individual da UF foi para `SANTA RITA` no valor de R$ 2.549.527,89. O objeto associado foi: CONSTRUCAO DAS CABECEIRAS DA PONTE SOBRE O RIO ITAPECURU.

_Fonte local deste bloco: `processada/MA.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2021` - R$ 40.447.562,09 em 40 registros.
2. `2018` - R$ 20.252.499,58 em 26 registros.
3. `2022` - R$ 5.636.841,91 em 10 registros.

Ultimos anos da serie:

- `2019`: R$ 4.721.052,64 em 6 registros, variacao n/d.
- `2021`: R$ 40.447.562,09 em 40 registros, variacao 756,7%.
- `2022`: R$ 5.636.841,91 em 10 registros, variacao -86,1%.
- `2023`: R$ 880.516,72 em 2 registros, variacao -84,4%.
- `2024`: R$ 3.042.398,96 em 4 registros, variacao 245,5%.

_Fonte local deste bloco: `processada/MA.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `BOM LUGAR` - R$ 8.590.827,28 em 5 registros.
2. `PEDRO DO ROSARIO` - R$ 5.906.152,43 em 5 registros.
3. `PARNARAMA` - R$ 5.244.368,10 em 4 registros.
4. `PINDARE-MIRIM` - R$ 4.683.330,00 em 5 registros.
5. `Nao informado` - R$ 4.290.653,91 em 7 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 92,9%, objeto em 100,0% e modalidade em 20,4%. Ha 0 registros negativos e 0 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/MA.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/MA.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `BOM LUGAR` (01611400000104): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01611400000104) - status da consulta 429.
- `PARNARAMA` (06115117000105): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/06115117000105) - status da consulta 429.
- `PINDARE MIRIM` (06189344000177): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/06189344000177) - status da consulta 429.
- `URBANO SANTOS` (05505839000103): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/05505839000103) - status da consulta 429.
- `CENTRO DO GUILHERME` (01612328000121): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01612328000121) - status da consulta 429.

### Investigacao complementar

- [BOM LUGAR - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01611400000104+BOM+LUGAR+Maranhao+convenio+contrato+gestao)
- [PARNARAMA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=06115117000105+PARNARAMA+Maranhao+convenio+contrato+gestao)
- [PINDARE MIRIM - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=06189344000177+PINDARE+MIRIM+Maranhao+convenio+contrato+gestao)
- [URBANO SANTOS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=05505839000103+URBANO+SANTOS+Maranhao+convenio+contrato+gestao)
- [CENTRO DO GUILHERME - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01612328000121+CENTRO+DO+GUILHERME+Maranhao+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\MA.parquet` (117 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\MA`.
- Exemplos de arquivos brutos estaduais: `DESPESA_2026_01.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_ma.py`.
- Observacao de trilha: Serie derivada do bruto local preservado em `bases_orcamento_geral/MA`.

### Capital (Sao Luis)

- Parquet da capital consolidado: `E:\dados\capitais_processada\MA_SAO_LUIS.parquet` (891 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Sao Luis`.
- Exemplos de arquivos brutos da capital: `saoluis_10_2025.csv`, `saoluis_12_2022.csv`, `saoluis_12_2023.csv`, `saoluis_12_2024.csv`, `saoluis_12_2025.csv`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_sao_luis.py`.
- Fontes oficiais registradas para a capital: [saoluis.giap.com.br/ords/saoluis/f?p=839:104](https://saoluis.giap.com.br/ords/saoluis/f?p=839:104).

## Conclusao

Maranhao deve ser lido como uma UF puxada por base mais distribuida. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
