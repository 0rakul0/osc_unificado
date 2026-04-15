# Espirito Santo (ES)

## Atualizacao de orcamento geral

- Foi criado o parser `processar_orcamento_geral_es.py` para consolidar a trilha de despesas do Espirito Santo e cruzar com os arquivos de convenios em `E:\dados\bases_convenios\ES\saida`.
- A saida canonica atual esta em `E:\dados\orcamento_geral_processada\ES.parquet`, com 247.128 linhas, 1.844 CNPJs e serie de 2009 a 2025.
- A base final do ES ficou apenas com documentos de 14 digitos no campo `cnpj`.

## Visao geral

Espirito Santo soma 247.128 registros e R$ 18.296.350.060,20 em valor total. No ranking geral da base, a UF esta em 11o lugar por valor, 4o por quantidade de registros, 27o por ticket medio e 13o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 74.035,92, a mediana e de R$ 0,00 e os 5 maiores beneficiarios concentram 43,2% do valor total.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\ES.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, ES aparece entre as UFs lideres por valor em `MT, PB, PA, AL, BA`, por volume em `MT, PB, PA, ES, SE`, por ticket medio em `PE, BA, RR, RJ, AM` e por concentracao em `AC, RR, PE, CE, AM`.

Na pratica, isso indica que Espirito Santo cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 0,3%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\ES.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- A serie atual do Espirito Santo foi recomposta a partir da trilha de despesas e pagamentos cruzada com convenios. Comparacoes com a versao historica anterior devem considerar essa mudanca de origem no bruto.
- 67,4% dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\ES.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `28127926000242` - ASSOCIACAO EVANG. BENEF. ESPIRITO SANTENSE - AEBES: R$ 2.607.483.323,17 em 1.982 registros.
2. `28127926000161` - ASSOCIACAO EVANGELICA BENEFICENTE E.SANTENSE: R$ 1.937.368.042,58 em 8.285 registros.
3. `28141190000186` - SANTA CASA DE MISERICORDIA DE VITORIA: R$ 1.406.005.391,99 em 4.603 registros.
4. `28137925000106` - AFECC - HOSPITAL SANTA RITA DE CASSIA: R$ 973.139.468,46 em 3.713 registros.
5. `27193705000129` - HOSP.EVANGELICO DE CACHOEIRO DE ITAPEMIRIM: R$ 965.723.271,78 em 5.342 registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\ES.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `SAUDE, SERVICOS, REDE, QUAL, ATENCAO, DODE, INTEGRAM, FICHA, DESPESAS, HOSPITAL, PRESENTE, SISTEMA`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `FUNDACAO DOS ECONOMIARIOS FEDERAIS-FUNCEF` - R$ 37.569.000,00 (ano 2022): IMOVEL URBANO PARA ABRIGAR UNIDADES ADMINISTRATIVAS DO TRIBUNAL DE JUSTICA DO ESTADO DO ESPIRITO SANTO. CONFORME INFORMACAO DA COORDENADORIA DE FISCALIZACAO DE OBRAS (1434940) E AUTORIZADO PELO SECRETARIO GERAL (1434956)..
2. `FUNDACAO BUTANTAN` - R$ 26.415.000,00 (ano 2021): PAGAMENTO DAS NF 22043 E 22340 AS PC 72 E 73 COM DE  AQUISICAO 500.000 (quinhentos mil) DOSES DE VACINA INATIVADA CONTRA O SARSCOV-2  COVID-19 -ARP 2519 - CONTRATO No 0097/2021, VIGENTE ATE 31/12/2021000000.
3. `ASSOCIACAO EVANG. BENEF. ESPIRITO SANTENSE - AEBES` - R$ 20.337.966,66 (ano 2022): PAGAMENTO DA NF0129 PCS#637 REF. DESPESAS COM OPERACIONALIZACAO DO HOSPITAL ESTADUAL DR. JAYME SANTOS NEVES -  44o TERMO ADITIVO AO CONTRATO DE GESTAO No 001/2012 - AEBES - COMPETENCIA DE JAN/2022 - ENFRENTAMENTO A COVID-19 - RECURSO ESTADUAL,  CONFORME SOLICITADO PCS#658 E AUTORIZACAO DO SUBSECRETARIO DA SSERCAS, PECA #660..
4. `ASSOCIACAO EVANG. BENEF. ESPIRITO SANTENSE - AEBES` - R$ 20.337.966,66 (ano 2021): PAGTO DA NOTA FISCAL 111 FEVEREIRO/2021 DESPESAS COM OPERACIONALIZACAO DAS ACOES E SERVICOS DE SAUDE NO HOSPITAL ESTADUAL DR. JAYME SANTOS NEVES PARA ENFRENTAMENTO A COVID-19 -  34o TERMO ADITIVO AO CONTRATO DE GESTAO No 001/12 - EM FAVOR DA ASSOCIACAO EVANGELICA BENEFICENTE ESPIRITO SANTENSE - AEBES - RECURSO ESTADUAL - CUSTEIO - EXERC. 2021 - CONFORME SOLICITACAO DA GECORP, FLS. 2248, E AUTORIZACAO DO SUBSECRETARIO DA SERCAS, FLS. 2249000000.
5. `ASSOCIACAO EVANG. BENEF. ESPIRITO SANTENSE - AEBES` - R$ 20.337.966,66 (ano 2021): PAGTO NOTA FISCAL 112, FLS. 57 -  COMPETENCIA   MARCO/2021 ,  PARTE  RECURSO ESTADUAL -  REFERENTE DESPESAS COM OPERACIONALIZACAO DAS ACOES E SERVICOS DE SAUDE NO HOSPITAL ESTADUAL DR. JAYME SANTOS NEVES PARA ENFRENTAMENTO A COVID-19 -  CONFORME  35o TERMO ADITIVO AO CONTRATO DE GESTAO No 001/12 - FLS. 59 -  - CONFORME SOLICITACAO DA GECORP, FLS. 66, E AUTORIZACAO DO SUBSECRETARIO DA SERCAS, FLS. 69.000000.

O maior registro individual da UF foi para `FUNDACAO DOS ECONOMIARIOS FEDERAIS-FUNCEF` no valor de R$ 37.569.000,00. O objeto associado foi: IMOVEL URBANO PARA ABRIGAR UNIDADES ADMINISTRATIVAS DO TRIBUNAL DE JUSTICA DO ESTADO DO ESPIRITO SANTO. CONFORME INFORMACAO DA COORDENADORIA DE FISCALIZACAO DE OBRAS (1434940) E AUTORIZADO PELO SECRETARIO GERAL (1434956)..

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\ES.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2024` - R$ 2.127.139.186,20 em 29.396 registros.
2. `2023` - R$ 1.773.692.187,97 em 17.670 registros.
3. `2022` - R$ 1.532.476.272,61 em 27.037 registros.

Ultimos anos da serie:

- `2021`: R$ 1.416.433.145,76 em 11.120 registros, variacao 4,1%.
- `2022`: R$ 1.532.476.272,61 em 27.037 registros, variacao 8,2%.
- `2023`: R$ 1.773.692.187,97 em 17.670 registros, variacao 15,7%.
- `2024`: R$ 2.127.139.186,20 em 29.396 registros, variacao 19,9%.
- `2025`: R$ 1.440.493.812,62 em 24.608 registros, variacao -32,3%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\ES.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `SEM MUNICIPIO INFORMADO` - R$ 6.302.295.074,02 em 66.794 registros.
2. `Nao informado` - R$ 5.969.447.372,77 em 73.224 registros.
3. `CACHOEIRO DE ITAPEMIRIM` - R$ 1.777.747.884,15 em 18.393 registros.
4. `VILA VELHA` - R$ 1.510.337.395,58 em 11.151 registros.
5. `VITORIA` - R$ 1.168.726.834,35 em 22.271 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 70,4%, objeto em 100,0% e modalidade em 100,0%. Ha 3.599 registros negativos e 147.483 registros marcados como duplicado aparente.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\ES.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `E:\dados\orcamento_geral_processada\ES.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `ASSOCIACAO EVANG. BENEF. ESPIRITO SANTENSE - AEBES` (28127926000242): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/28127926000242) - situacao ATIVA; municipio/UF SERRA/ES; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `ASSOCIACAO EVANGELICA BENEFICENTE E.SANTENSE` (28127926000161): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/28127926000161) - status da consulta 429.
- `SANTA CASA DE MISERICORDIA DE VITORIA` (28141190000186): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/28141190000186) - situacao ATIVA; municipio/UF VITORIA/ES; porte DEMAIS; atividade principal Atividades de atendimento em pronto-socorro e unidades hospitalares para atendimento a urgencias.
- `AFECC - HOSPITAL SANTA RITA DE CASSIA` (28137925000106): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/28137925000106) - status da consulta 429.
- `HOSP.EVANGELICO DE CACHOEIRO DE ITAPEMIRIM` (27193705000129): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/27193705000129) - status da consulta 429.

### Investigacao complementar

- [ASSOCIACAO EVANG. BENEF. ESPIRITO SANTENSE - AEBES - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=28127926000242+ASSOCIACAO+EVANG.+BENEF.+ESPIRITO+SANTENSE+-+AEBES+Espirito+Santo+convenio+contrato+gestao)
- [ASSOCIACAO EVANGELICA BENEFICENTE E.SANTENSE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=28127926000161+ASSOCIACAO+EVANGELICA+BENEFICENTE+E.SANTENSE+Espirito+Santo+convenio+contrato+gestao)
- [SANTA CASA DE MISERICORDIA DE VITORIA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=28141190000186+SANTA+CASA+DE+MISERICORDIA+DE+VITORIA+Espirito+Santo+convenio+contrato+gestao)
- [AFECC - HOSPITAL SANTA RITA DE CASSIA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=28137925000106+AFECC+-+HOSPITAL+SANTA+RITA+DE+CASSIA+Espirito+Santo+convenio+contrato+gestao)
- [HOSP.EVANGELICO DE CACHOEIRO DE ITAPEMIRIM - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=27193705000129+HOSP.EVANGELICO+DE+CACHOEIRO+DE+ITAPEMIRIM+Espirito+Santo+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\ES.parquet` (247128 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\ES`.
- Exemplos de arquivos brutos estaduais: `despesas-2004.csv`, `despesas-2005.csv`, `despesas-2006.csv`, `despesas-2007.csv`, `despesas-2008.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_es.py`.
- Observacao de trilha: Serie recomposta a partir de arquivos CSV legados preservados em `bases_orcamento_geral/ES`.

### Capital (Vitoria)

- Parquet da capital consolidado: `E:\dados\capitais_processada\ES_VITORIA.parquet` (1204 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Vitoria`.
- Exemplos de arquivos brutos da capital: `vitoria_convenios_ug12_2021.csv`, `vitoria_convenios_ug12_2022.csv`, `vitoria_convenios_ug12_2025.csv`, `vitoria_convenios_ug14_2021.csv`, `vitoria_convenios_ug14_2022.csv`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_vitoria.py`.
- Fontes oficiais registradas para a capital: [wstransparencia.vitoria.es.gov.br](https://wstransparencia.vitoria.es.gov.br).

## Conclusao

Espirito Santo deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
