# Mato Grosso do Sul (MS)

## Visao geral

Mato Grosso do Sul soma 33.493 registros e R$ 33.327.466.871,17 em valor total. No ranking geral da base, a UF esta em 4o lugar por valor, 7o por quantidade de registros, 10o por ticket medio e 6o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 995.057,68, a mediana e de R$ 62.800,00 e os 5 maiores beneficiarios concentram 62,6% do valor total.

_Fonte local deste bloco: `processada/MS.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, MS aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Mato Grosso do Sul cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 9,5%.

_Fonte local deste bloco: `processada/MS.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `15457856000168` - AGENCIA ESTADUAL DE GESTAO E EMPREENDIMENTOS: R$ 8.141.240.725,38 em 1.629 registros.
2. `02585924000122` - SECRETARIA DE ESTADO DE EDUCACAO: R$ 5.141.880.275,78 em 658 registros.
3. `03517102000177` - FUNDO ESPECIAL DE SAUDE: R$ 4.314.685.948,43 em 864 registros.
4. `03015475000140` - SEJUSP/MS: R$ 1.847.678.656,56 em 754 registros.
5. `03981081000146` - AGENCIA DE DES.AGRARIO E EXTENSAO RURAL-AGRAE: R$ 1.424.029.335,44 em 414 registros.

_Fonte local deste bloco: `processada/MS.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Nao ha objetos suficientes para aprofundar os objetivos do gasto.
O maior registro individual da UF foi para `FUNDO ESPECIAL DE SAUDE` no valor de R$ 193.991.028,00. O objeto associado foi: .

_Fonte local deste bloco: `processada/MS.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2023` - R$ 3.205.836.563,09 em 2.822 registros.
2. `2022` - R$ 3.108.714.822,62 em 2.792 registros.
3. `2024` - R$ 2.711.354.176,88 em 1.906 registros.

Ultimos anos da serie:

- `2021`: R$ 2.461.410.202,18 em 2.137 registros, variacao n/d.
- `2022`: R$ 3.108.714.822,62 em 2.792 registros, variacao 26,3%.
- `2023`: R$ 3.205.836.563,09 em 2.822 registros, variacao 3,1%.
- `2024`: R$ 2.711.354.176,88 em 1.906 registros, variacao -15,4%.
- `2025`: R$ 1.934.379.659,45 em 934 registros, variacao -28,7%.

_Fonte local deste bloco: `processada/MS.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 0,0% e modalidade em 100,0%. Ha 0 registros negativos e 4.921 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/MS.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/MS.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `AGENCIA ESTADUAL DE GESTAO E EMPREENDIMENTOS` (15457856000168): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/15457856000168) - status da consulta 429.
- `SECRETARIA DE ESTADO DE EDUCACAO` (02585924000122): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/02585924000122) - status da consulta 429.
- `FUNDO ESPECIAL DE SAUDE` (03517102000177): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/03517102000177) - status da consulta 429.
- `SEJUSP/MS` (03015475000140): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/03015475000140) - status da consulta 429.
- `AGENCIA DE DES.AGRARIO E EXTENSAO RURAL-AGRAE` (03981081000146): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/03981081000146) - status da consulta 429.

### Investigacao complementar

- [AGENCIA ESTADUAL DE GESTAO E EMPREENDIMENTOS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=15457856000168+AGENCIA+ESTADUAL+DE+GESTAO+E+EMPREENDIMENTOS+Mato+Grosso+do+Sul+convenio+contrato+gestao)
- [SECRETARIA DE ESTADO DE EDUCACAO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=02585924000122+SECRETARIA+DE+ESTADO+DE+EDUCACAO+Mato+Grosso+do+Sul+convenio+contrato+gestao)
- [FUNDO ESPECIAL DE SAUDE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=03517102000177+FUNDO+ESPECIAL+DE+SAUDE+Mato+Grosso+do+Sul+convenio+contrato+gestao)
- [SEJUSP/MS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=03015475000140+SEJUSP%2FMS+Mato+Grosso+do+Sul+convenio+contrato+gestao)
- [AGENCIA DE DES.AGRARIO E EXTENSAO RURAL-AGRAE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=03981081000146+AGENCIA+DE+DES.AGRARIO+E+EXTENSAO+RURAL-AGRAE+Mato+Grosso+do+Sul+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\MS.parquet` (4324 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\MS`.
- Exemplos de arquivos brutos estaduais: `despesas-2018.csv`, `despesas-2019.csv`, `despesas-2020.csv`, `despesas-2021.csv`, `despesas-2022.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_ms.py`.
- Observacao de trilha: Serie derivada dos CSVs locais preservados em `bases_orcamento_geral/MS`.

### Capital (Campo Grande)

- Parquet da capital consolidado: `E:\dados\capitais_processada\MS_CAMPO_GRANDE.parquet` (20 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Campo Grande`.
- Exemplos de arquivos brutos da capital: `campogrande_repasses_estaduais_2023.csv`, `campogrande_repasses_estaduais_2024.csv`, `campogrande_repasses_estaduais_2025.csv`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_campo_grande.py`.
- Fontes oficiais registradas para a capital: [sig-transparencia.campogrande.ms.gov.br/repasses-estaduais/consulta](https://sig-transparencia.campogrande.ms.gov.br/repasses-estaduais/consulta).

## Conclusao

Mato Grosso do Sul deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
