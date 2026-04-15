# Alagoas (AL)

## Atualizacao de orcamento geral

- A trilha de orcamento geral de Alagoas segue como base inicial do projeto e foi mantida como referencia operacional.
- A saida canonica atual esta em `E:\dados\orcamento_geral_processada\AL.parquet`, com 144.411 linhas e serie de 2018 a 2026.

## Visao geral

Alagoas soma 144.411 registros e R$ 112.424.385.263,39 em valor total. No ranking geral da base, a UF esta em 4o lugar por valor, 6o por quantidade de registros, 12o por ticket medio e 7o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 778.502,92, a mediana e de R$ 3.460,00 e os 5 maiores beneficiarios concentram 55,9% do valor total.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\AL.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, AL aparece entre as UFs lideres por valor em `MT, PB, PA, AL, BA`, por volume em `MT, PB, PA, ES, SE`, por ticket medio em `PE, BA, RR, RJ, AM` e por concentracao em `AC, RR, PE, CE, AM`.

Na pratica, isso indica que Alagoas cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 2,0%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\AL.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- 11,0% dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros.
- A cobertura de CNPJ valido nesta UF esta em 48,7%. Parte das identificacoes pode ter sido recuperada por cruzamento com base externa, mas ainda ha linhas sem identificacao cadastral completa.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\AL.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `FOLHA PAGTOPESSOAL` - FOLHA PAGTOPESSOAL: R$ 31.497.974.999,04 em 736 registros.
2. `INATIVOS E PENSIONI` - INATIVOS E PENSIONI: R$ 19.105.993.358,61 em 96 registros.
3. `FUNDO FINANCEIRO DO ESTADO DE ALAGOAS` - FUNDO FINANCEIRO DO ESTADO DE ALAGOAS: R$ 4.786.747.225,65 em 496 registros.
4. `PLANTOES EXTRAS` - PLANTOES EXTRAS: R$ 4.293.052.447,17 em 69 registros.
5. `LEI 9496  ROLAGEM` - LEI 9496  ROLAGEM: R$ 3.191.998.249,42 em 16 registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\AL.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `MANUTENCAO, ATIVIDADES, ORGAO, EDUCACAO, ASSISTENCIA, FORTALECIMENTO, QUALIFICACAO, UNIDADES, MEDIA, ALTA, COMPLEXIDADE, EXPANSAO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `INATIVOS E PENSIONI` - R$ 1.237.792.718,02 (ano 2018): GESTAO DE PESSOAS.
2. `INATIVOS E PENSIONI` - R$ 1.105.067.677,12 (ano 2025): ENCARGOS DE INATIVOS E PENSIONISTAS DO PODER EXECUTIVO.
3. `FOLHA PAGTOPESSOAL` - R$ 925.062.366,55 (ano 2025): GESTAO DE PESSOAS.
4. `INATIVOS E PENSIONI` - R$ 916.040.300,42 (ano 2023): ENCARGOS DE INATIVOS E PENSIONISTAS DO PODER EXECUTIVO.
5. `INATIVOS E PENSIONI` - R$ 891.956.627,41 (ano 2024): ENCARGOS DE INATIVOS E PENSIONISTAS DO PODER EXECUTIVO.

O maior registro individual da UF foi para `INATIVOS E PENSIONI` no valor de R$ 1.237.792.718,02. O objeto associado foi: GESTAO DE PESSOAS.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\AL.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2025` - R$ 19.708.570.869,27 em 15.356 registros.
2. `2024` - R$ 17.530.409.065,15 em 17.491 registros.
3. `2023` - R$ 15.866.625.903,30 em 19.309 registros.

Ultimos anos da serie:

- `2022`: R$ 14.974.112.715,49 em 17.173 registros, variacao 24,0%.
- `2023`: R$ 15.866.625.903,30 em 19.309 registros, variacao 6,0%.
- `2024`: R$ 17.530.409.065,15 em 17.491 registros, variacao 10,5%.
- `2025`: R$ 19.708.570.869,27 em 15.356 registros, variacao 12,4%.
- `2026`: R$ 4.368.110.351,45 em 6.037 registros, variacao -77,8%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\AL.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 48,7%, municipio em 0,0%, objeto em 100,0% e modalidade em 0,0%. Ha 0 registros negativos e 3.435 registros marcados como duplicado aparente.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\AL.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `E:\dados\orcamento_geral_processada\AL.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `FOLHA PAGTOPESSOAL` (): sem URL externa verificada.
- `INATIVOS E PENSIONI` (): sem URL externa verificada.
- `FUNDO FINANCEIRO DO ESTADO DE ALAGOAS` (): sem URL externa verificada.
- `PLANTOES EXTRAS` (): sem URL externa verificada.
- `LEI 9496  ROLAGEM` (): sem URL externa verificada.

### Investigacao complementar

- [FOLHA PAGTOPESSOAL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=FOLHA+PAGTOPESSOAL+Alagoas+convenio+contrato+gestao)
- [INATIVOS E PENSIONI - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=INATIVOS+E+PENSIONI+Alagoas+convenio+contrato+gestao)
- [FUNDO FINANCEIRO DO ESTADO DE ALAGOAS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=FUNDO+FINANCEIRO+DO+ESTADO+DE+ALAGOAS+Alagoas+convenio+contrato+gestao)
- [PLANTOES EXTRAS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=PLANTOES+EXTRAS+Alagoas+convenio+contrato+gestao)
- [LEI 9496  ROLAGEM - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=LEI+9496++ROLAGEM+Alagoas+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\AL.parquet` (144411 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\AL`.
- Exemplos de arquivos brutos estaduais: `AL_dados_gerais.py`, `despesas_alagoas.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_al.py`.
- Observacao de trilha: Serie montada a partir de base legada local preservada em `bases_convenios/AL`.

### Capital (Maceio)

- Parquet da capital consolidado: `E:\dados\capitais_processada\AL_MACEIO.parquet` (11236 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Maceio`.
- Exemplos de arquivos brutos da capital: `maceio_2005.json`, `maceio_2006.json`, `maceio_2007.json`, `maceio_2008.json`, `maceio_2009.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`.
- Observacao de trilha: Capital consolidada a partir de base legada local preservada em `bases_convenios_capitais/Maceio`.

## Conclusao

Alagoas deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
