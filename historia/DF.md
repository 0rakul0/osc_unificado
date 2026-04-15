# Distrito Federal (DF)

## Visao geral

Distrito Federal soma 5.026 registros e R$ 2.184.086.233,35 em valor total. No ranking geral da base, a UF esta em 16o lugar por valor, 13o por quantidade de registros, 15o por ticket medio e 19o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e base mais distribuida. O ticket medio e de R$ 434.557,55, a mediana e de R$ 164.084,00 e os 5 maiores beneficiarios concentram 22,5% do valor total.

_Fonte local deste bloco: `processada/DF.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, DF aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Distrito Federal cresce principalmente por base mais distribuida. A participacao da UF no total nacional desta pasta e de 0,6%.

_Fonte local deste bloco: `processada/DF.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `02290594000148` - CENTRO SOCIAL COMUNITARIO TIA ANGELINA: R$ 124.434.636,92 em 185 registros.
2. `62382395000604` - ASSOCIACAO DAS OBRAS PAVONIANAS DE ASSISTENCIA: R$ 112.442.459,41 em 122 registros.
3. `00077255000152` - CASA DE ISMAEL - LAR DA CRIANCA: R$ 101.961.347,57 em 256 registros.
4. `08106714000190` - INSTITUTO SOCIO CULTURAL AMB E TECNOL DE PROJ DE E: R$ 77.871.355,66 em 27 registros.
5. `03604394000185` - SOCIEDADE ESPIRITA DE AMPARO AO MENOR CASA DO CAMI: R$ 73.649.373,82 em 150 registros.

_Fonte local deste bloco: `processada/DF.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `FEDERAL, DISTRITO, TRANSFERENCIA, SOCIAL, PROTECAO, REDE, INFANTIL, ADOLESCENTE, CRIANCA, ESPECIAL, ACOLHIMENTO, PROJETOS`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `INSTITUTO SOCIO CULTURAL AMB E TECNOL DE PROJ DE E` - R$ 10.101.600,00 (ano 2021): TRANSFERENCIA PARA PROTECAO SOCIAL ESPECIAL-DEMAIS INDIVIDUOS E FAMILIAS-DISTRITO FEDERAL.
2. `OBRAS SOCIAIS DO CENTRO ESPIRITA JERONIMO CANDINHO` - R$ 10.062.655,29 (ano 2022): ASSISTENCIA AO JOVEM-JOVEM CANDANGO-DISTRITO FEDERAL.
3. `INSTITUTO SOCIO CULTURAL AMB E TECNOL DE PROJ DE E` - R$ 8.418.000,00 (ano 2024): TRANSFERENCIA PARA PROTECAO SOCIAL ESPECIAL-DEMAIS INDIVIDUOS E FAMILIAS-DISTRITO FEDERAL.
4. `INSTITUTO ROSA DOS VENTOS DE ARTE, CULTURA E CIDAD` - R$ 8.400.000,00 (ano 2025): TRANSFERENCIA DE RECURSOS PARA PROJETOS CULTURAIS-SECRETARIA DE CULTURA-DISTRITO FEDERAL.
5. `INSTITUTO SOCIO CULTURAL AMB E TECNOL DE PROJ DE E` - R$ 8.161.628,40 (ano 2022): TRANSFERENCIA PARA PROTECAO SOCIAL ESPECIAL-DEMAIS INDIVIDUOS E FAMILIAS-DISTRITO FEDERAL.

O maior registro individual da UF foi para `INSTITUTO SOCIO CULTURAL AMB E TECNOL DE PROJ DE E` no valor de R$ 10.101.600,00. O objeto associado foi: TRANSFERENCIA PARA PROTECAO SOCIAL ESPECIAL-DEMAIS INDIVIDUOS E FAMILIAS-DISTRITO FEDERAL.

_Fonte local deste bloco: `processada/DF.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2022` - R$ 269.809.535,60 em 486 registros.
2. `2023` - R$ 226.233.392,48 em 528 registros.
3. `2025` - R$ 224.453.856,57 em 339 registros.

Ultimos anos da serie:

- `2021`: R$ 197.986.586,97 em 346 registros, variacao n/d.
- `2022`: R$ 269.809.535,60 em 486 registros, variacao 36,3%.
- `2023`: R$ 226.233.392,48 em 528 registros, variacao -16,2%.
- `2024`: R$ 220.942.305,87 em 387 registros, variacao -2,3%.
- `2025`: R$ 224.453.856,57 em 339 registros, variacao 1,6%.

_Fonte local deste bloco: `processada/DF.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 492 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/DF.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/DF.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `CENTRO SOCIAL COMUNITARIO TIA ANGELINA` (02290594000148): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/02290594000148) - situacao ATIVA; municipio/UF BRASILIA/DF; porte DEMAIS; atividade principal Educacao infantil - creche.
- `ASSOCIACAO DAS OBRAS PAVONIANAS DE ASSISTENCIA` (62382395000604): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/62382395000604) - situacao ATIVA; municipio/UF BRASILIA/DF; porte DEMAIS; atividade principal Servicos de assistencia social sem alojamento.
- `CASA DE ISMAEL - LAR DA CRIANCA` (00077255000152): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/00077255000152) - situacao ATIVA; municipio/UF BRASILIA/DF; porte DEMAIS; atividade principal Servicos de assistencia social sem alojamento.
- `INSTITUTO SOCIO CULTURAL AMB E TECNOL DE PROJ DE E` (08106714000190): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/08106714000190) - situacao ATIVA; municipio/UF BRASILIA/DF; porte DEMAIS; atividade principal Atividades de organizacoes associativas ligadas a cultura e a arte.
- `SOCIEDADE ESPIRITA DE AMPARO AO MENOR CASA DO CAMI` (03604394000185): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/03604394000185) - situacao ATIVA; municipio/UF BRASILIA/DF; porte DEMAIS; atividade principal Educacao infantil - creche.

### Investigacao complementar

- [CENTRO SOCIAL COMUNITARIO TIA ANGELINA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=02290594000148+CENTRO+SOCIAL+COMUNITARIO+TIA+ANGELINA+Distrito+Federal+convenio+contrato+gestao)
- [ASSOCIACAO DAS OBRAS PAVONIANAS DE ASSISTENCIA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=62382395000604+ASSOCIACAO+DAS+OBRAS+PAVONIANAS+DE+ASSISTENCIA+Distrito+Federal+convenio+contrato+gestao)
- [CASA DE ISMAEL - LAR DA CRIANCA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=00077255000152+CASA+DE+ISMAEL+-+LAR+DA+CRIANCA+Distrito+Federal+convenio+contrato+gestao)
- [INSTITUTO SOCIO CULTURAL AMB E TECNOL DE PROJ DE E - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=08106714000190+INSTITUTO+SOCIO+CULTURAL+AMB+E+TECNOL+DE+PROJ+DE+E+Distrito+Federal+convenio+contrato+gestao)
- [SOCIEDADE ESPIRITA DE AMPARO AO MENOR CASA DO CAMI - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=03604394000185+SOCIEDADE+ESPIRITA+DE+AMPARO+AO+MENOR+CASA+DO+CAMI+Distrito+Federal+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\DF.parquet` (2901 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\DF`.
- Exemplos de arquivos brutos estaduais: `despesa_df_2025.json`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_df.py`.
- Fontes oficiais registradas para o estado: [dados.df.gov.br/](https://dados.df.gov.br/).

### Capital (Brasilia)

- Parquet da capital consolidado: `E:\dados\capitais_processada\DF_BRASILIA.parquet` (1011 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Brasilia`.
- Exemplos de arquivos brutos da capital: `brasilia_convenios_2020.csv`, `brasilia_convenios_2021.csv`, `brasilia_convenios_2022.csv`, `brasilia_convenios_2023.csv`, `brasilia_convenios_2024.csv`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_brasilia.py`.
- Fontes oficiais registradas para a capital: [dados.df.gov.br/](https://dados.df.gov.br/).

## Conclusao

Distrito Federal deve ser lido como uma UF puxada por base mais distribuida. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
