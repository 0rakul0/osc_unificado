# Rio de Janeiro (RJ)

## Visao geral

Rio de Janeiro soma 4.190 registros e R$ 15.442.916.014,99 em valor total. No ranking geral da base, a UF esta em 8o lugar por valor, 14o por quantidade de registros, 3o por ticket medio e 8o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e ticket medio. O ticket medio e de R$ 3.685.660,15, a mediana e de R$ 388,98 e os 5 maiores beneficiarios concentram 47,8% do valor total.

_Fonte local deste bloco: `processada/RJ.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, RJ aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Rio de Janeiro cresce principalmente por ticket medio. A participacao da UF no total nacional desta pasta e de 4,4%.

_Fonte local deste bloco: `processada/RJ.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `11715100000000` - Fundo Municipal De Saude Da Cidade Do Rj: R$ 2.014.827.386,65 em 29 registros.
2. `11128800000000` - Fundo Municipal De Saude De Duque De Caxias: R$ 1.827.681.125,74 em 50 registros.
3. `10497800000000` - Fundo Municipal De Saude De Nova Iguacu: R$ 1.343.286.602,48 em 49 registros.
4. `11128809000110` - Fundo Municipal De Saude De Duque De Caxias: R$ 579.655.650,01 em 2 registros.
5. `11884900000000` - Fundo Municipal De Saude De Sao Goncalo: R$ 524.731.580,67 em 40 registros.

_Fonte local deste bloco: `processada/RJ.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `ASSISTENCIA, GESTAO, SAUDE, SOCIAL, SUAS, FARMACEUTICA, DESENVOLVIMENTO, TERRITORIAL, COORDENACAO, FEDERATIVA, VIGILANCIA, PROMOCAO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `Fundo Municipal De Saude Da Cidade Do Rj` - R$ 688.370.948,00 (ano 2022): Coordenacao Federativa e Desenvolvimento Territorial.
2. `Fundo Municipal De Saude De Duque De Caxias` - R$ 566.572.350,81 (ano 2024): Estrategia e Gestao da Saude.
3. `Fundo Municipal De Saude De Duque De Caxias` - R$ 499.687.176,00 (ano 2023): Atencao a Saude.
4. `Fundo Municipal De Saude Da Cidade Do Rj` - R$ 408.774.851,00 (ano 2021): Coordenacao Federativa e Desenvolvimento Territorial.
5. `Fundo Municipal De Saude De Nova Iguacu` - R$ 352.681.949,00 (ano 2022): Coordenacao Federativa e Desenvolvimento Territorial.

O maior registro individual da UF foi para `Fundo Municipal De Saude Da Cidade Do Rj` no valor de R$ 688.370.948,00. O objeto associado foi: Coordenacao Federativa e Desenvolvimento Territorial.

_Fonte local deste bloco: `processada/RJ.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2022` - R$ 3.795.691.998,82 em 503 registros.
2. `2021` - R$ 3.412.727.388,38 em 627 registros.
3. `2023` - R$ 2.298.451.613,05 em 493 registros.

Ultimos anos da serie:

- `2020`: R$ 2.254.467.358,69 em 555 registros, variacao n/d.
- `2021`: R$ 3.412.727.388,38 em 627 registros, variacao 51,4%.
- `2022`: R$ 3.795.691.998,82 em 503 registros, variacao 11,2%.
- `2023`: R$ 2.298.451.613,05 em 493 registros, variacao -39,4%.
- `2024`: R$ 1.942.798.323,51 em 321 registros, variacao -15,5%.

_Fonte local deste bloco: `processada/RJ.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 100,0% e modalidade em 0,0%. Ha 0 registros negativos e 0 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/RJ.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/RJ.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `Fundo Municipal De Saude Da Cidade Do Rj` (11715100000000): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/11715100000000) - status da consulta 400.
- `Fundo Municipal De Saude De Duque De Caxias` (11128800000000): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/11128800000000) - status da consulta 400.
- `Fundo Municipal De Saude De Nova Iguacu` (10497800000000): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/10497800000000) - status da consulta 400.
- `Fundo Municipal De Saude De Duque De Caxias` (11128809000110): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/11128809000110) - situacao ATIVA; municipio/UF DUQUE DE CAXIAS/RJ; porte DEMAIS; atividade principal Regulacao das atividades de saude, educacao, servicos culturais e outros servicos sociais.
- `Fundo Municipal De Saude De Sao Goncalo` (11884900000000): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/11884900000000) - status da consulta 400.

### Investigacao complementar

- [Fundo Municipal De Saude Da Cidade Do Rj - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=11715100000000+Fundo+Municipal+De+Saude+Da+Cidade+Do+Rj+Rio+de+Janeiro+convenio+contrato+gestao)
- [Fundo Municipal De Saude De Duque De Caxias - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=11128800000000+Fundo+Municipal+De+Saude+De+Duque+De+Caxias+Rio+de+Janeiro+convenio+contrato+gestao)
- [Fundo Municipal De Saude De Nova Iguacu - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=10497800000000+Fundo+Municipal+De+Saude+De+Nova+Iguacu+Rio+de+Janeiro+convenio+contrato+gestao)
- [Fundo Municipal De Saude De Duque De Caxias - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=11128809000110+Fundo+Municipal+De+Saude+De+Duque+De+Caxias+Rio+de+Janeiro+convenio+contrato+gestao)
- [Fundo Municipal De Saude De Sao Goncalo - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=11884900000000+Fundo+Municipal+De+Saude+De+Sao+Goncalo+Rio+de+Janeiro+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\RJ.parquet` (96 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\RJ`.
- Exemplos de arquivos brutos estaduais: `controle-de-convenios-2025.xlsx`, `despesa2026.csv`, `Documento sem título.docx`, `transferencias-voluntarias-aos-municipios-2015-a-2023.csv`, `transferencias-voluntarias-aos-municipios-2024.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_rj.py`.
- Observacao de trilha: Serie montada a partir de planilhas e CSVs locais preservados em `bases_orcamento_geral/RJ`.

### Capital (Rio de Janeiro)

- Parquet da capital consolidado: `E:\dados\capitais_processada\RJ_RIO_DE_JANEIRO.parquet` (7940 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Rio de Janeiro`.
- Exemplos de arquivos brutos da capital: `rio_contratos_especies.csv`, `rio_contratos_especies_manifest.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_rio.py`.
- Fontes oficiais registradas para a capital: [riotransparente.rio.rj.gov.br/web/index.asp](https://riotransparente.rio.rj.gov.br/web/index.asp).

## Conclusao

Rio de Janeiro deve ser lido como uma UF puxada por ticket medio. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
