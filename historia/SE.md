# Sergipe (SE)

## Visao geral

Sergipe soma 175.232 registros e R$ 33.038.111.310,94 em valor total. No ranking geral da base, a UF esta em 5o lugar por valor, 1o por quantidade de registros, 26o por ticket medio e 17o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 188.539,26, a mediana e de R$ 9.470,12 e os 5 maiores beneficiarios concentram 27,3% do valor total.

_Fonte local deste bloco: `processada/SE.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, SE aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Sergipe cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 9,4%.

_Fonte local deste bloco: `processada/SE.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- A serie disponivel nesta UF esta concentrada em um intervalo curto (2023 a 2025), o que limita comparacoes historicas mais longas.

_Fonte local deste bloco: `processada/SE.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `34841195000114` - SECRETARIA DE ESTADO DA EDUCACAO: R$ 2.784.396.056,27 em 3.895 registros.
2. `10436979000107` - FUNDACAO HOSPITALAR DE SAUDE: R$ 1.842.667.089,49 em 172 registros.
3. `09314825000155` - FUNDO FINANCEIRO DE PREVIDENCIA DO ESTADO DE SERGIPE: R$ 1.667.473.269,45 em 2.606 registros.
4. `34850014000116` - POLICIA MILITAR DO ESTADO DE SERGIPE: R$ 1.408.287.145,24 em 255 registros.
5. `08042552000174` - INSTITUTO DE PREVIDENCIA DOS SERVIDORES DO ESTADO DE SERGIPE: R$ 1.308.274.613,41 em 655 registros.

_Fonte local deste bloco: `processada/SE.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `SERVICOS, CONTRATACAO, PRESTACAO, SAUDE, EMPRESA, SERGIPE, FORNECIMENTO, ESPECIALIZADA, REGISTRO, ASSISTENCIAIS, PRECO, VISANDO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `FUNDACAO HOSPITALAR DE SAUDE` - R$ 50.000.000,00 (ano 2025): EXECUCAO DE SERVICOS DE SAUDE EM TODOS OS NIVEIS DE ASSISTENCIA HOSPITALAR.
2. `FUNDACAO HOSPITALAR DE SAUDE` - R$ 50.000.000,00 (ano 2025): EXECUCAO DE SERVICOS DE SAUDE EM TODOS OS NIVEIS DE ASSISTENCIA HOSPITALAR.
3. `FUNDACAO HOSPITALAR DE SAUDE` - R$ 50.000.000,00 (ano 2025): EXECUCAO DE SERVICOS DE SAUDE EM TODOS OS NIVEIS DE ASSISTENCIA HOSPITALAR.
4. `FUNDACAO HOSPITALAR DE SAUDE` - R$ 50.000.000,00 (ano 2025): EXECUCAO DE SERVICOS DE SAUDE EM TODOS OS NIVEIS DE ASSISTENCIA HOSPITALAR.
5. `FUNDACAO HOSPITALAR DE SAUDE` - R$ 49.334.999,99 (ano 2025): EXECUCAO DE SERVICOS DE SAUDE EM TODOS OS NIVEIS DE ASSISTENCIA HOSPITALAR.

O maior registro individual da UF foi para `BRB - BANCO DE BRASILIA S.A.` no valor de R$ 170.625.000,00. O objeto associado foi: .

_Fonte local deste bloco: `processada/SE.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2025` - R$ 14.416.643.832,97 em 64.562 registros.
2. `2024` - R$ 12.268.667.766,78 em 64.459 registros.
3. `2023` - R$ 6.352.799.711,19 em 46.211 registros.

Ultimos anos da serie:

- `2023`: R$ 6.352.799.711,19 em 46.211 registros, variacao n/d.
- `2024`: R$ 12.268.667.766,78 em 64.459 registros, variacao 93,1%.
- `2025`: R$ 14.416.643.832,97 em 64.562 registros, variacao 17,5%.

_Fonte local deste bloco: `processada/SE.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 25,3% e modalidade em 100,0%. Ha 0 registros negativos e 24.821 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/SE.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/SE.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `SECRETARIA DE ESTADO DA EDUCACAO` (34841195000114): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/34841195000114) - situacao ATIVA; municipio/UF ARACAJU/SE; porte DEMAIS; atividade principal Administracao publica em geral.
- `FUNDACAO HOSPITALAR DE SAUDE` (10436979000107): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/10436979000107) - situacao ATIVA; municipio/UF ARACAJU/SE; porte DEMAIS; atividade principal Atividades de atendimento em pronto-socorro e unidades hospitalares para atendimento a urgencias.
- `FUNDO FINANCEIRO DE PREVIDENCIA DO ESTADO DE SERGIPE` (09314825000155): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/09314825000155) - situacao ATIVA; municipio/UF ARACAJU/SE; porte DEMAIS; atividade principal Seguridade social obrigatoria.
- `POLICIA MILITAR DO ESTADO DE SERGIPE` (34850014000116): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/34850014000116) - situacao ATIVA; municipio/UF ARACAJU/SE; porte DEMAIS; atividade principal Seguranca e ordem publica.
- `INSTITUTO DE PREVIDENCIA DOS SERVIDORES DO ESTADO DE SERGIPE` (08042552000174): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/08042552000174) - situacao ATIVA; municipio/UF ARACAJU/SE; porte DEMAIS; atividade principal Seguridade social obrigatoria.

### Investigacao complementar

- [SECRETARIA DE ESTADO DA EDUCACAO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=34841195000114+SECRETARIA+DE+ESTADO+DA+EDUCACAO+Sergipe+convenio+contrato+gestao)
- [FUNDACAO HOSPITALAR DE SAUDE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=10436979000107+FUNDACAO+HOSPITALAR+DE+SAUDE+Sergipe+convenio+contrato+gestao)
- [FUNDO FINANCEIRO DE PREVIDENCIA DO ESTADO DE SERGIPE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=09314825000155+FUNDO+FINANCEIRO+DE+PREVIDENCIA+DO+ESTADO+DE+SERGIPE+Sergipe+convenio+contrato+gestao)
- [POLICIA MILITAR DO ESTADO DE SERGIPE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=34850014000116+POLICIA+MILITAR+DO+ESTADO+DE+SERGIPE+Sergipe+convenio+contrato+gestao)
- [INSTITUTO DE PREVIDENCIA DOS SERVIDORES DO ESTADO DE SERGIPE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=08042552000174+INSTITUTO+DE+PREVIDENCIA+DOS+SERVIDORES+DO+ESTADO+DE+SERGIPE+Sergipe+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\SE.parquet` (7389 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\SE`.
- Exemplos de arquivos brutos estaduais: `empenhos_2023.xlsx`, `empenhos_2024.xlsx`, `empenhos_2025.xlsx`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_se.py`.
- Observacao de trilha: Serie montada a partir de planilhas locais preservadas em `bases_orcamento_geral/SE`.

### Capital (Aracaju)

- Parquet da capital consolidado: `E:\dados\capitais_processada\SE_ARACAJU.parquet` (626 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Aracaju`.
- Exemplos de arquivos brutos da capital: `aracaju_repasse_ongs_2017.pdf`, `aracaju_repasse_ongs_2018.pdf`, `aracaju_repasse_ongs_2019.pdf`, `aracaju_repasse_ongs_2020.pdf`, `aracaju_repasse_ongs_2021.pdf`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_aracaju.py`.
- Fontes oficiais registradas para a capital: [transparencia.aracaju.se.gov.br/prefeitura/convenios-e-outros-ajustes/](https://transparencia.aracaju.se.gov.br/prefeitura/convenios-e-outros-ajustes/).

## Conclusao

Sergipe deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
