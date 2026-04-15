# Roraima (RR)

## Visao geral

Roraima soma 447 registros e R$ 1.896.488.219,69 em valor total. No ranking geral da base, a UF esta em 17o lugar por valor, 23o por quantidade de registros, 2o por ticket medio e 2o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e ticket medio e concentracao. O ticket medio e de R$ 4.242.702,95, a mediana e de R$ 1.164.995,41 e os 5 maiores beneficiarios concentram 94,9% do valor total.

_Fonte local deste bloco: `processada/RR.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, RR aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Roraima cresce principalmente por ticket medio e concentracao. A participacao da UF no total nacional desta pasta e de 0,5%.

_Fonte local deste bloco: `processada/RR.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- A base atual de Roraima usa apenas a fonte propria do estado. Arquivos que, na pasta bruta, pertenciam a Rondonia foram removidos da consolidacao do `RR`.

_Fonte local deste bloco: `processada/RR.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `84012012000126` - ESTADO DE RORAIMA: R$ 1.405.366.913,28 em 286 registros.
2. `05370016000100` - FUNDO ESTADUAL DE SAUDE DO ESTADO RORAIMA: R$ 294.409.753,83 em 43 registros.
3. `07026157000135` - INSTITUTO BRASILEIRO DE CIDADANIA E ACAO SOCIAL: R$ 52.459.980,00 em 8 registros.
4. `08240695000190` - UNIVERSIDADE ESTADUAL DE RORAIMA: R$ 24.482.810,42 em 13 registros.
5. `06092354000190` - SECRETARIA DE ESTADO DE EDUCACAO E DESPORTO: R$ 22.569.819,27 em 2 registros.

_Fonte local deste bloco: `processada/RR.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `RORAIMA, AQUISICAO, MUNICIPIO, CONSTRUCAO, SAUDE, VISTA, UNIDADE, EQUIPAMENTOS, ACOES, REFORMA, MEIO, ATENCAO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `FUNDO ESTADUAL DE SAUDE DO ESTADO RORAIMA` - R$ 95.155.948,20 (ano 2024): ampliacao de unidade de atencao especializada em saude.
2. `ESTADO DE RORAIMA` - R$ 89.186.505,54 (ano 2020): pavimentacao de vias publicas..
3. `FUNDO ESTADUAL DE SAUDE DO ESTADO RORAIMA` - R$ 58.664.015,06 (ano 2024): construcao de unidade de atencao especializada em saude.
4. `ESTADO DE RORAIMA` - R$ 57.525.911,00 (ano 2021): construcao de ponte em concreto armado com 700m de extensao e implantacao de 3km de pavimentacao asfaltica na rodovia rr-319 (regiao do projeto passarao) municipio de boa vista - rr..
5. `ESTADO DE RORAIMA` - R$ 41.474.139,96 (ano 2022): adequacao de estradas vicinais.

O maior registro individual da UF foi para `FUNDO ESTADUAL DE SAUDE DO ESTADO RORAIMA` no valor de R$ 95.155.948,20. O objeto associado foi: ampliacao de unidade de atencao especializada em saude.

_Fonte local deste bloco: `processada/RR.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2024` - R$ 360.812.975,88 em 57 registros.
2. `2020` - R$ 344.790.867,49 em 62 registros.
3. `2019` - R$ 271.528.788,40 em 45 registros.

Ultimos anos da serie:

- `2021`: R$ 160.442.780,05 em 17 registros, variacao n/d.
- `2022`: R$ 168.676.002,15 em 24 registros, variacao 5,1%.
- `2023`: R$ 196.170.129,66 em 42 registros, variacao 16,3%.
- `2024`: R$ 360.812.975,88 em 57 registros, variacao 83,9%.
- `2025`: R$ 6.652.850,88 em 6 registros, variacao -98,2%.

_Fonte local deste bloco: `processada/RR.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `BOA VISTA` - R$ 1.860.624.736,28 em 412 registros.
2. `Nao informado` - R$ 33.529.215,80 em 22 registros.
3. `IRACEMA` - R$ 749.870,61 em 5 registros.
4. `CANTA` - R$ 730.007,00 em 2 registros.
5. `CARACARAI` - R$ 635.000,00 em 4 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 95,1%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 5 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/RR.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/RR.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `ESTADO DE RORAIMA` (84012012000126): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/84012012000126) - situacao ATIVA; municipio/UF BOA VISTA/RR; porte DEMAIS; atividade principal Administracao publica em geral.
- `FUNDO ESTADUAL DE SAUDE DO ESTADO RORAIMA` (05370016000100): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/05370016000100) - situacao ATIVA; municipio/UF BOA VISTA/RR; porte DEMAIS; atividade principal Outras atividades de atencao a saude humana nao especificadas anteriormente.
- `INSTITUTO BRASILEIRO DE CIDADANIA E ACAO SOCIAL` (07026157000135): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/07026157000135) - situacao ATIVA; municipio/UF BOA VISTA/RR; porte DEMAIS; atividade principal Atividades de associacoes de defesa de direitos sociais.
- `UNIVERSIDADE ESTADUAL DE RORAIMA` (08240695000190): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/08240695000190) - situacao ATIVA; municipio/UF BOA VISTA/RR; porte DEMAIS; atividade principal Educacao superior - graduacao e pos-graduacao.
- `SECRETARIA DE ESTADO DE EDUCACAO E DESPORTO` (06092354000190): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/06092354000190) - situacao ATIVA; municipio/UF BOA VISTA/RR; porte DEMAIS; atividade principal Administracao publica em geral.

### Investigacao complementar

- [ESTADO DE RORAIMA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=84012012000126+ESTADO+DE+RORAIMA+Roraima+convenio+contrato+gestao)
- [FUNDO ESTADUAL DE SAUDE DO ESTADO RORAIMA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=05370016000100+FUNDO+ESTADUAL+DE+SAUDE+DO+ESTADO+RORAIMA+Roraima+convenio+contrato+gestao)
- [INSTITUTO BRASILEIRO DE CIDADANIA E ACAO SOCIAL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=07026157000135+INSTITUTO+BRASILEIRO+DE+CIDADANIA+E+ACAO+SOCIAL+Roraima+convenio+contrato+gestao)
- [UNIVERSIDADE ESTADUAL DE RORAIMA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=08240695000190+UNIVERSIDADE+ESTADUAL+DE+RORAIMA+Roraima+convenio+contrato+gestao)
- [SECRETARIA DE ESTADO DE EDUCACAO E DESPORTO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=06092354000190+SECRETARIA+DE+ESTADO+DE+EDUCACAO+E+DESPORTO+Roraima+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\RR.parquet` (50 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\RR`.
- Exemplos de arquivos brutos estaduais: `rr_despesa_detalhada.json`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_rr.py`, `utils/orcamento_geral/baixar_orcamento_geral_rr.py`.
- Fontes oficiais registradas para o estado: [api.transparencia.rr.gov.br/api/v1/portal/transparencia/visualizar-despesa-detalhada](https://api.transparencia.rr.gov.br/api/v1/portal/transparencia/visualizar-despesa-detalhada).

### Capital (Boa Vista)

- Parquet da capital consolidado: `E:\dados\capitais_processada\RR_BOA_VISTA.parquet` (15 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Boa Vista`.
- Exemplos de arquivos brutos da capital: `boavista_convenios.csv`, `boavista_convenios_manifest.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_boavista.py`.
- Fontes oficiais registradas para a capital: [transparencia.boavista.rr.gov.br/convenios](https://transparencia.boavista.rr.gov.br/convenios).

## Conclusao

Roraima deve ser lido como uma UF puxada por ticket medio e concentracao. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
