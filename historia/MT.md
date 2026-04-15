# Mato Grosso (MT)

## Atualizacao de orcamento geral

- A trilha legada de Mato Grosso foi substituida pela base oficial rica do portal de transparencia.
- A saida canonica atual esta em `E:\dados\orcamento_geral_processada\MT.parquet`, com 14.195.271 linhas, 26.002 CNPJs e cobertura valida de 2010 a 2021 e 2023 a 2026.
- O ano de 2022 ficou fora do canone porque o layout oficial nao traz data da despesa, e a trilha atual exige no minimo `valor + data + cnpj`.

## Visao geral

Mato Grosso soma 14.195.271 registros e R$ 4.827.481.230.349,19 em valor total. No ranking geral da base, a UF esta em 1o lugar por valor, 1o por quantidade de registros, 18o por ticket medio e 26o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 340.076,72, a mediana e de R$ 1.500,00 e os 5 maiores beneficiarios concentram 10,4% do valor total.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\MT.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, MT aparece entre as UFs lideres por valor em `MT, PB, PA, AL, BA`, por volume em `MT, PB, PA, ES, SE`, por ticket medio em `PE, BA, RR, RJ, AM` e por concentracao em `AC, RR, PE, CE, AM`.

Na pratica, isso indica que Mato Grosso cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 85,8%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\MT.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- A serie canonica de Mato Grosso passou a usar a base oficial rica do portal de transparencia. O ano de 2022 ficou fora do parquet principal porque o layout oficial nao traz data da despesa, e a trilha atual exige no minimo valor, data e cnpj.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\MT.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `03507415000578` - TESOURO DO ESTADO/IMPOSTO DE RENDA/CF/88 ARTo 157: R$ 127.314.968.720,25 em 1.082.357 registros.
2. `22594192000144` - MTPREV - MATO GROSSO PREVIDENCIA - PLANO FINANCEIRO: R$ 121.179.384.004,82 em 171.390 registros.
3. `59285411000113` - BANCO PANAMERICANO S/A: R$ 96.560.295.754,84 em 194.363 registros.
4. `22594192000144` - MATO GROSSO PREVIDENCIA MTPREV: R$ 74.126.025.636,06 em 16.369 registros.
5. `62232889000190` - BANCO DAYCOVAL SA: R$ 71.460.274.000,42 em 141.591 registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\MT.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `PAGAMENTO, EMPENHO, LIQUIDACAO, FOLHA, NORMAL, CIVIL, 2024, 2023, SEDUC, ATIVO, 2025, PROCESSO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `TESOURO DO ESTADO/IMPOSTO DE RENDA/CF/88 ARTo 157` - R$ 2.072.269.331,79 (ano 2024): FATURA COM DETALHAMENTO VENCIDO..
2. `MT GOVERNO DO ESTADO - FPM/ICMS` - R$ 1.100.000.000,00 (ano 2011): EMPENHO DO PED N 30102.0001.11.00088-1.
3. `MT GOVERNO DO ESTADO - FPM/ICMS` - R$ 1.000.000.000,00 (ano 2012): EMPENHO DO PED N 30102.0001.12.000016-2.
4. `CONSORCIO VLT CUIABA - VARZEA GRANDE` - R$ 726.893.091,00 (ano 2014): EMPENHO DO PED N 04103.0001.14.000144-9.
5. `MT GOVERNO DO ESTADO - FPM/ICMS` - R$ 700.000.000,00 (ano 2010): EMPENHO DO PED N 30102.0001.10.00054-4.

O maior registro individual da UF foi para `TESOURO DO ESTADO/IMPOSTO DE RENDA/CF/88 ARTo 157` no valor de R$ 2.072.269.331,79. O objeto associado foi: FATURA COM DETALHAMENTO VENCIDO..

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\MT.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2016` - R$ 890.552.393.288,62 em 860.723 registros.
2. `2018` - R$ 599.785.169.673,07 em 1.071.711 registros.
3. `2025` - R$ 598.636.262.469,27 em 1.217.411 registros.

Ultimos anos da serie:

- `2021`: R$ 198.419.497.513,86 em 938.868 registros, variacao 76,2%.
- `2023`: R$ 221.900.486.011,25 em 1.112.581 registros, variacao 11,8%.
- `2024`: R$ 255.467.793.705,61 em 1.197.271 registros, variacao 15,1%.
- `2025`: R$ 598.636.262.469,27 em 1.217.411 registros, variacao 134,3%.
- `2026`: R$ 11.880.125.240,04 em 82.311 registros, variacao -98,0%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\MT.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 100,0% e modalidade em 100,0%. Ha 51.366 registros negativos e 1.054.255 registros marcados como duplicado aparente.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\MT.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `E:\dados\orcamento_geral_processada\MT.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `TESOURO DO ESTADO/IMPOSTO DE RENDA/CF/88 ARTo 157` (03507415000578): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/03507415000578) - situacao ATIVA; municipio/UF CUIABA/MT; porte DEMAIS; atividade principal Administracao publica em geral.
- `MTPREV - MATO GROSSO PREVIDENCIA - PLANO FINANCEIRO` (22594192000144): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/22594192000144) - situacao ATIVA; municipio/UF CUIABA/MT; porte DEMAIS; atividade principal Seguridade social obrigatoria.
- `BANCO PANAMERICANO S/A` (59285411000113): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/59285411000113) - situacao ATIVA; municipio/UF SAO PAULO/SP; porte DEMAIS; atividade principal Bancos multiplos, com carteira comercial.
- `MATO GROSSO PREVIDENCIA MTPREV` (22594192000144): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/22594192000144) - situacao ATIVA; municipio/UF CUIABA/MT; porte DEMAIS; atividade principal Seguridade social obrigatoria.
- `BANCO DAYCOVAL SA` (62232889000190): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/62232889000190) - situacao ATIVA; municipio/UF SAO PAULO/SP; porte DEMAIS; atividade principal Bancos multiplos, com carteira comercial.

### Investigacao complementar

- [TESOURO DO ESTADO/IMPOSTO DE RENDA/CF/88 ARTo 157 - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=03507415000578+TESOURO+DO+ESTADO%2FIMPOSTO+DE+RENDA%2FCF%2F88+ARTo+157+Mato+Grosso+convenio+contrato+gestao)
- [MTPREV - MATO GROSSO PREVIDENCIA - PLANO FINANCEIRO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=22594192000144+MTPREV+-+MATO+GROSSO+PREVIDENCIA+-+PLANO+FINANCEIRO+Mato+Grosso+convenio+contrato+gestao)
- [BANCO PANAMERICANO S/A - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=59285411000113+BANCO+PANAMERICANO+S%2FA+Mato+Grosso+convenio+contrato+gestao)
- [MATO GROSSO PREVIDENCIA MTPREV - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=22594192000144+MATO+GROSSO+PREVIDENCIA+MTPREV+Mato+Grosso+convenio+contrato+gestao)
- [BANCO DAYCOVAL SA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=62232889000190+BANCO+DAYCOVAL+SA+Mato+Grosso+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\MT.parquet` (14195271 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\MT`.
- Exemplos de arquivos brutos estaduais: `2010_mt_despesas.csv`, `2011_mt_despesas.csv`, `2012_mt_despesas.csv`, `2013_mt_despesas.csv`, `2014_mt_despesas.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_mt.py`.
- Fontes oficiais registradas para o estado: [consultas.transparencia.mt.gov.br/dados_abertos_consultas/despesa/](https://consultas.transparencia.mt.gov.br/dados_abertos_consultas/despesa/), [consultas.transparencia.mt.gov.br/dados_abertos/despesa/Despesa_{year}.csv](https://consultas.transparencia.mt.gov.br/dados_abertos/despesa/Despesa_{year}.csv).

### Capital (Cuiaba)

- Parquet da capital consolidado: `E:\dados\capitais_processada\MT_CUIABA.parquet` (118 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Cuiaba`.
- Exemplos de arquivos brutos da capital: `cuiaba_convenio_recebido.json`, `cuiaba_filter_convenio_recebido.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_cuiaba.py`.
- Fontes oficiais registradas para a capital: [transparencia.cuiaba.mt.gov.br/portaltransparencia/servlet/a](http://transparencia.cuiaba.mt.gov.br/portaltransparencia/servlet/a).

## Conclusao

Mato Grosso deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
