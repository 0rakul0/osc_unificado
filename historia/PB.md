# Paraiba (PB)

## Atualizacao de orcamento geral

- Foi criado o downloader `baixar_orcamento_geral_pb_dados_abertos.py` e, em seguida, o parser `processar_orcamento_geral_pb.py` para consolidar a trilha de empenhos.
- A saida canonica atual esta em `E:\dados\orcamento_geral_processada\PB.parquet`, com 1.794.815 linhas, 44.848 CNPJs e serie de 2000 a 2026.
- O `valor_total` ficou preenchido em toda a base final e a trilha foi fechada sem CPF no parquet.

## Visao geral

Paraiba soma 1.794.815 registros e R$ 217.624.267.388,24 em valor total. No ranking geral da base, a UF esta em 2o lugar por valor, 2o por quantidade de registros, 26o por ticket medio e 14o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 121.251,64, a mediana e de R$ 3.406,90 e os 5 maiores beneficiarios concentram 42,0% do valor total.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PB.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, PB aparece entre as UFs lideres por valor em `MT, PB, PA, AL, BA`, por volume em `MT, PB, PA, ES, SE`, por ticket medio em `PE, BA, RR, RJ, AM` e por concentracao em `AC, RR, PE, CE, AM`.

Na pratica, isso indica que Paraiba cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 3,9%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PB.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `06121067000160` - PBPREV PARAIBA PREVIDENCIA: R$ 47.187.858.385,73 em 36.549 registros.
2. `08778250000169` - SECRETARIA DE ESTADO DA EDUCACAO: R$ 15.382.775.867,78 em 6.659 registros.
3. `08907776000100` - POLICIA MILITAR DO ESTADO DA PARAIBA: R$ 10.221.307.455,17 em 1.689 registros.
4. `08778268000160` - SECRETARIA DA SAUDE: R$ 9.474.701.546,16 em 1.681 registros.
5. `00000000001163` - BANCO DO BRASIL SA: R$ 9.210.467.351,55 em 36.837 registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PB.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `IMPORTANCIA, EMPENHADA, VALOR, CONFORME, AQUISICAO, PAGAMENTO, DESPESAS, EMPENHA, CONF, PROCESSO, FACE, ACIMA`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `SECRETARIA DE ESTADO DA EDUCACAO` - R$ 118.097.640,31 (ano 2019): VALOR DA FOLHA DE PESSOAL - MAGISTERIO DO ENSINO FUNDAMENTALREFERENTE AO MESES DE JULHO, AGOSTO E SETEMBRO/2019-VENCIMENTOS E VANT. FIXAS- PESSOAL ATIVO..
2. `TRIBUNAL DE JUSTICA DA PARAIBA` - R$ 104.063.973,50 (ano 2022): IMPORTANCIA RELACIONADA A     PRECATORIOS COM OS SEGUINTES  DADOS: PROTOCOLO:62281049,    BENEFICIARIO:JOAO PESSOA      TRIBUNAL DE JUSTIC(CPF CNPJ9283185000163) , PROCESSO:EC  62/2009 - 360.001-7.
3. `POLICIA MILITAR DO ESTADO DA PARAIBA` - R$ 96.644.786,87 (ano 2026): FOLHA DE PAGAMENTO DO MES DE  FEVEREIRO 2026, VENCIMENTOS E VANTAGENS FIXAS PESSOAL       MILITAR..
4. `PBPREV PARAIBA PREVIDENCIA` - R$ 93.021.564,40 (ano 2026): FOPAG ADMINISTRACAO DIRETA REFAO MES DE FEVEREIRO/26 -      INATIVOS DO MAGISTERIO.
5. `PBPREV PARAIBA PREVIDENCIA` - R$ 89.342.121,71 (ano 2025): FOPAG ADMINISTRACAO DIRETA    REFERENTE AO MES DE           SETEMBRO/25 - INATIVOS        MAGISTERIO..

O maior registro individual da UF foi para `SECRETARIA DE ESTADO DA EDUCACAO` no valor de R$ 118.097.640,31. O objeto associado foi: VALOR DA FOLHA DE PESSOAL - MAGISTERIO DO ENSINO FUNDAMENTALREFERENTE AO MESES DE JULHO, AGOSTO E SETEMBRO/2019-VENCIMENTOS E VANT. FIXAS- PESSOAL ATIVO..

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PB.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2024` - R$ 18.547.095.885,77 em 94.258 registros.
2. `2023` - R$ 18.366.763.161,71 em 100.334 registros.
3. `2022` - R$ 16.681.364.545,77 em 90.855 registros.

Ultimos anos da serie:

- `2022`: R$ 16.681.364.545,77 em 90.855 registros, variacao 23,1%.
- `2023`: R$ 18.366.763.161,71 em 100.334 registros, variacao 10,1%.
- `2024`: R$ 18.547.095.885,77 em 94.258 registros, variacao 1,0%.
- `2025`: R$ 14.092.808.462,66 em 55.099 registros, variacao -24,0%.
- `2026`: R$ 4.161.722.044,95 em 11.465 registros, variacao -70,5%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PB.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `JOAO PESSOA` - R$ 186.795.899.981,79 em 1.006.711 registros.
2. `Nao informado` - R$ 13.937.788.588,95 em 374.812 registros.
3. `CAMPINA GRANDE` - R$ 7.115.964.865,34 em 125.778 registros.
4. `CABEDELO` - R$ 3.509.310.510,66 em 35.721 registros.
5. `PATOS` - R$ 606.376.124,17 em 33.489 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 79,1%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 31.332 registros marcados como duplicado aparente.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PB.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `E:\dados\orcamento_geral_processada\PB.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `PBPREV PARAIBA PREVIDENCIA` (06121067000160): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/06121067000160) - situacao ATIVA; municipio/UF JOAO PESSOA/PB; porte DEMAIS; atividade principal Seguridade social obrigatoria.
- `SECRETARIA DE ESTADO DA EDUCACAO` (08778250000169): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/08778250000169) - situacao ATIVA; municipio/UF JOAO PESSOA/PB; porte DEMAIS; atividade principal Administracao publica em geral.
- `POLICIA MILITAR DO ESTADO DA PARAIBA` (08907776000100): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/08907776000100) - situacao ATIVA; municipio/UF JOAO PESSOA/PB; porte DEMAIS; atividade principal Seguranca e ordem publica.
- `SECRETARIA DA SAUDE` (08778268000160): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/08778268000160) - situacao ATIVA; municipio/UF JOAO PESSOA/PB; porte DEMAIS; atividade principal Administracao publica em geral.
- `BANCO DO BRASIL SA` (00000000001163): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/00000000001163) - situacao ATIVA; municipio/UF JOAO PESSOA/PB; porte DEMAIS; atividade principal Bancos comerciais.

### Investigacao complementar

- [PBPREV PARAIBA PREVIDENCIA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=06121067000160+PBPREV+PARAIBA+PREVIDENCIA+Paraiba+convenio+contrato+gestao)
- [SECRETARIA DE ESTADO DA EDUCACAO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=08778250000169+SECRETARIA+DE+ESTADO+DA+EDUCACAO+Paraiba+convenio+contrato+gestao)
- [POLICIA MILITAR DO ESTADO DA PARAIBA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=08907776000100+POLICIA+MILITAR+DO+ESTADO+DA+PARAIBA+Paraiba+convenio+contrato+gestao)
- [SECRETARIA DA SAUDE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=08778268000160+SECRETARIA+DA+SAUDE+Paraiba+convenio+contrato+gestao)
- [BANCO DO BRASIL SA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=00000000001163+BANCO+DO+BRASIL+SA+Paraiba+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\PB.parquet` (1794815 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\PB`.
- Exemplos de arquivos brutos estaduais: `Documento sem título.docx`, `LiquidacoesLista (1).xlsx`, `LiquidacoesLista.xlsx`, `orcamento_cnpj_nome_nao_em_convenios.csv`, `orcamento_cnpjs_nao_em_convenios.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_pb.py`.
- Fontes oficiais registradas para o estado: [www.dados.pb.gov.br/](https://www.dados.pb.gov.br/).

### Capital (Joao Pessoa)

- Parquet da capital consolidado: `E:\dados\capitais_processada\PB_JOAO_PESSOA.parquet` (392 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Joao Pessoa`.
- Exemplos de arquivos brutos da capital: `joaopessoa_convenios_2022.csv`, `joaopessoa_convenios_2022.html`, `joaopessoa_convenios_2022.json`, `joaopessoa_convenios_2023.csv`, `joaopessoa_convenios_2023.html`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`.
- Fontes oficiais registradas para a capital: [transparencia.joaopessoa.pb.gov.br/#/convenios/convenios-municipais](https://transparencia.joaopessoa.pb.gov.br/#/convenios/convenios-municipais), [transparencia.joaopessoa.pb.gov.br:8080/convenios/municipais](https://transparencia.joaopessoa.pb.gov.br:8080/convenios/municipais).

## Conclusao

Paraiba deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
