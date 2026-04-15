# Sao Paulo (SP)

## Visao geral

Sao Paulo soma 37.813 registros e R$ 49.819.926.969,99 em valor total. No ranking geral da base, a UF esta em 2o lugar por valor, 6o por quantidade de registros, 8o por ticket medio e 14o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 1.317.534,37, a mediana e de R$ 100.000,00 e os 5 maiores beneficiarios concentram 31,6% do valor total.

_Fonte local deste bloco: `processada/SP.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, SP aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Sao Paulo cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 14,1%.

_Fonte local deste bloco: `processada/SP.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `49607336000106` - FUNDACAO DE DESENVOLVIMENTO DA UNICAMP - FUNCAMP: R$ 3.957.490.592,00 em 21 registros.
2. `46068425000133` - UNICAMP - UNIVERSIDADE CAMPINAS. HOSPITAL UNIVERSITARIO MEC MPAS: R$ 3.810.402.708,96 em 367 registros.
3. `56577059000100` - FUNDACAO FACULDADE DE MEDICINA: R$ 3.331.587.318,07 em 386 registros.
4. `62779145000190` - IRMANDADE DA SANTA CASA DE MISERICORDIA DE SAO PAULO: R$ 2.299.643.679,50 em 220 registros.
5. `61699567000192` - SPDM - ASSOCIACAO PAULISTA PARA O DESENVOLVIMENTO DA MEDICINA: R$ 2.298.220.897,84 em 272 registros.

_Fonte local deste bloco: `processada/SP.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `CUSTEIO, AQUISICAO, RECURSOS, EQUIPAMENTOS, MATERIAL, CONSUMO, EMENDA, FINANCEIROS, INVESTIMENTO, CASA, REPASSE, TRANSFERENCIA`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `FUNDACAO BUTANTAN` - R$ 939.234.166,14 (ano 2015): ATIVIDADES DE PESQUISA, ENSINO, TECNOLOGIA, CULTURA, PRODUCAO DE IMUNOBIOLOGICOS E OUTROS PRODUTOS AFINS..
2. `FUNDACAO DE DESENVOLVIMENTO DA UNICAMP - FUNCAMP` - R$ 892.776.480,91 (ano 2023): TRANS. A INSTITUICAO PRIVADA SEM FINS LUCRATIVOS.
3. `FUNDACAO FACULDADE DE MEDICINA` - R$ 592.000.000,00 (ano 2014): ICESP.
4. `UNICAMP - UNIVERSIDADE CAMPINAS. HOSPITAL UNIVERSITARIO MEC MPAS` - R$ 552.648.947,23 (ano 2022): HOSPITAL SUMARE - TA DO CONVENIO DE PARCERIA 2022 - 2025.
5. `IRMANDADE DA SANTA CASA DE MISERICORDIA DE SAO PAULO` - R$ 544.320.000,00 (ano 2020): CONVENIO.

O maior registro individual da UF foi para `FUNDACAO BUTANTAN` no valor de R$ 939.234.166,14. O objeto associado foi: ATIVIDADES DE PESQUISA, ENSINO, TECNOLOGIA, CULTURA, PRODUCAO DE IMUNOBIOLOGICOS E OUTROS PRODUTOS AFINS..

_Fonte local deste bloco: `processada/SP.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2020` - R$ 6.443.959.593,77 em 2.115 registros.
2. `2022` - R$ 5.827.501.437,58 em 1.300 registros.
3. `2017` - R$ 4.847.948.344,10 em 1.250 registros.

Ultimos anos da serie:

- `2021`: R$ 2.478.033.499,39 em 2.215 registros, variacao n/d.
- `2022`: R$ 5.827.501.437,58 em 1.300 registros, variacao 135,2%.
- `2023`: R$ 2.916.717.780,10 em 1.145 registros, variacao -49,9%.
- `2024`: R$ 1.435.574.063,23 em 1.871 registros, variacao -50,8%.
- `2025`: R$ 1.453.246.298,25 em 844 registros, variacao 1,2%.

_Fonte local deste bloco: `processada/SP.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `0100 - SAO PAULO` - R$ 20.669.314.981,16 em 7.750 registros.
2. `0244 - CAMPINAS` - R$ 5.128.375.244,61 em 1.078 registros.
3. `0647 - SAO JOSE DO RIO PRETO` - R$ 2.496.503.755,45 em 764 registros.
4. `0688 - TAUBATE` - R$ 1.598.262.024,86 em 208 registros.
5. `0209 - BAURU` - R$ 1.253.935.920,84 em 261 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 100,0%, objeto em 100,0% e modalidade em 72,6%. Ha 37 registros negativos e 968 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/SP.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/SP.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `FUNDACAO DE DESENVOLVIMENTO DA UNICAMP - FUNCAMP` (49607336000106): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/49607336000106) - situacao ATIVA; municipio/UF CAMPINAS/SP; porte DEMAIS; atividade principal Atividades de apoio a educacao, exceto caixas escolares.
- `UNICAMP - UNIVERSIDADE CAMPINAS. HOSPITAL UNIVERSITARIO MEC MPAS` (46068425000133): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/46068425000133) - situacao ATIVA; municipio/UF CAMPINAS/SP; porte DEMAIS; atividade principal Educacao superior - graduacao e pos-graduacao.
- `FUNDACAO FACULDADE DE MEDICINA` (56577059000100): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/56577059000100) - situacao ATIVA; municipio/UF SAO PAULO/SP; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `IRMANDADE DA SANTA CASA DE MISERICORDIA DE SAO PAULO` (62779145000190): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/62779145000190) - situacao ATIVA; municipio/UF SAO PAULO/SP; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `SPDM - ASSOCIACAO PAULISTA PARA O DESENVOLVIMENTO DA MEDICINA` (61699567000192): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/61699567000192) - situacao ATIVA; municipio/UF SAO PAULO/SP; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.

### Investigacao complementar

- [FUNDACAO DE DESENVOLVIMENTO DA UNICAMP - FUNCAMP - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=49607336000106+FUNDACAO+DE+DESENVOLVIMENTO+DA+UNICAMP+-+FUNCAMP+Sao+Paulo+convenio+contrato+gestao)
- [UNICAMP - UNIVERSIDADE CAMPINAS. HOSPITAL UNIVERSITARIO MEC MPAS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=46068425000133+UNICAMP+-+UNIVERSIDADE+CAMPINAS.+HOSPITAL+UNIVERSITARIO+MEC+MPAS+Sao+Paulo+convenio+contrato+gestao)
- [FUNDACAO FACULDADE DE MEDICINA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=56577059000100+FUNDACAO+FACULDADE+DE+MEDICINA+Sao+Paulo+convenio+contrato+gestao)
- [IRMANDADE DA SANTA CASA DE MISERICORDIA DE SAO PAULO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=62779145000190+IRMANDADE+DA+SANTA+CASA+DE+MISERICORDIA+DE+SAO+PAULO+Sao+Paulo+convenio+contrato+gestao)
- [SPDM - ASSOCIACAO PAULISTA PARA O DESENVOLVIMENTO DA MEDICINA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=61699567000192+SPDM+-+ASSOCIACAO+PAULISTA+PARA+O+DESENVOLVIMENTO+DA+MEDICINA+Sao+Paulo+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\SP.parquet` (1079 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\SP`.
- Exemplos de arquivos brutos estaduais: `sp_parcerias_osc_enriquecido.csv`, `sp_parcerias_osc_enriquecido.json`, `sp_parcerias_osc_resumo.json`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_sp.py`, `utils/orcamento_geral/baixar_orcamento_geral_sp.py`.
- Fontes oficiais registradas para o estado: [www.parceriassociais.sp.gov.br](http://www.parceriassociais.sp.gov.br), [www.parceriassociais.sp.gov.br/OSC/Termos_Acordos](http://www.parceriassociais.sp.gov.br/OSC/Termos_Acordos).

### Capital (Sao Paulo)

- Parquet da capital consolidado: `E:\dados\capitais_processada\SP_SAO_PAULO.parquet` (5706 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Sao Paulo`.
- Exemplos de arquivos brutos da capital: `sao_paulo_parcerias_educacao_infantil_2025_12.csv`, `sao_paulo_parcerias_manifest.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_sao_paulo.py`.
- Fontes oficiais registradas para a capital: [dados.prefeitura.sp.gov.br/api/3/action/package_show](https://dados.prefeitura.sp.gov.br/api/3/action/package_show), [dados.prefeitura.sp.gov.br/dataset/0fe868fc-4d8d-468a-a3e0-a2b512da96e3](https://dados.prefeitura.sp.gov.br/dataset/0fe868fc-4d8d-468a-a3e0-a2b512da96e3).

## Conclusao

Sao Paulo deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
