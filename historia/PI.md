# Piaui (PI)

## Visao geral

Piaui soma 2.633 registros e R$ 720.384.932,94 em valor total. No ranking geral da base, a UF esta em 23o lugar por valor, 17o por quantidade de registros, 21o por ticket medio e 20o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e base mais distribuida. O ticket medio e de R$ 273.598,53, a mediana e de R$ 127.605,03 e os 5 maiores beneficiarios concentram 20,3% do valor total.

_Fonte local deste bloco: `processada/PI.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, PI aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Piaui cresce principalmente por base mais distribuida. A participacao da UF no total nacional desta pasta e de 0,2%.

_Fonte local deste bloco: `processada/PI.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- No Piaui, a base final manteve apenas o arquivo de convenios. Uma planilha separada de execucao orcamentaria ficou fora do parquet para nao misturar despesa geral com instrumento de parceria.

_Fonte local deste bloco: `processada/PI.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `01019517000195` - INSTITUTO DE GESTAO E DESENVOLVIMENTO SOCIAL - IGDS: R$ 43.981.016,00 em 3 registros.
2. `PREFEITURA MUNICIPAL DE TERESINA` - PREFEITURA MUNICIPAL DE TERESINA: R$ 28.232.405,00 em 6 registros.
3. `20124920000129` - INSTITUTO DE DESENVOLVIMENTO DO NORDESTE (IDENE): R$ 24.874.680,36 em 3 registros.
4. `06553937000170` - PREFEITURA MUNICIPAL DE OEIRAS: R$ 23.262.300,77 em 37 registros.
5. `01386084000106` - FUNDACAO HOSPITALAR JOAQUIM SIMEAO FILHO - HOSPITAL BENEFICENCIA CHAPADA DO ARARIPE: R$ 18.000.000,00 em 1 registros.

_Fonte local deste bloco: `processada/PI.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `MUNICIPIO, PIAUI, AQUISICAO, CONSTRUCAO, REALIZACAO, SAUDE, ZONA, RECUPERACAO, ATRAVES, CULTURA, COMO, ESCOLAR`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `INSTITUTO DE GESTAO E DESENVOLVIMENTO SOCIAL - IGDS` - R$ 29.725.410,00 (ano 2024): Ofertar refeicoes diarias a precos populares em 05 (cinco) novos Restaurantes Populares, sendo 04 (quatro) em Teresina e 01 (um) em Parnaiba, voltados a atender prioritariamente, a populacao em situacao de vulnerabilidade social, fortalecendo assim o Direito Humano a Alimentacao Adequada  DHAA.
2. `INSTITUTO DE DESENVOLVIMENTO DO NORDESTE (IDENE)` - R$ 22.928.537,16 (ano 2025): Implementar acoes itinerantes especializadas voltadas ao rastreamento e diagnostico precoce dos canceres de pele, prostata e colo do utero, em carater complementar e articulado ao Sistema Unico de Saude (SUS), contemplando os 12 territorios de saude do Estado do Piaui..
3. `PREFEITURA MUNICIPAL DE TERESINA` - R$ 20.000.000,00 (ano 2008): Interligar as zonas centro e leste da cidade de Teresina, atraves das Avenidas Alameda Parnaiba(centro) e Dom Severino (leste).
4. `FUNDACAO HOSPITALAR JOAQUIM SIMEAO FILHO - HOSPITAL BENEFICENCIA CHAPADA DO ARARIPE` - R$ 18.000.000,00 (ano 2025): Recurso de Custeio para servicos de Media e Alta Complexidade, prestados no HOSPITAL BENEFICENCIA CHAPADA DO ARARIPE..
5. `INSTITUTO DE GESTAO E DESENVOLVIMENTO SOCIAL - IGDS` - R$ 12.000.000,00 (ano 2024): A implementacao de 05 (cinco) novos Restaurantes Populares,.

O maior registro individual da UF foi para `INSTITUTO DE GESTAO E DESENVOLVIMENTO SOCIAL - IGDS` no valor de R$ 29.725.410,00. O objeto associado foi: Ofertar refeicoes diarias a precos populares em 05 (cinco) novos Restaurantes Populares, sendo 04 (quatro) em Teresina e 01 (um) em Parnaiba, voltados a atender prioritariamente, a populacao em situacao de vulnerabilidade social, fortalecendo assim o Direito Humano a Alimentacao Adequada  DHAA.

_Fonte local deste bloco: `processada/PI.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2024` - R$ 104.245.308,05 em 148 registros.
2. `2025` - R$ 87.672.351,83 em 68 registros.
3. `2010` - R$ 73.097.829,24 em 427 registros.

Ultimos anos da serie:

- `2021`: R$ 21.406.876,09 em 64 registros, variacao n/d.
- `2022`: R$ 18.512.112,15 em 83 registros, variacao -13,5%.
- `2023`: R$ 34.370.708,70 em 102 registros, variacao 85,7%.
- `2024`: R$ 104.245.308,05 em 148 registros, variacao 203,3%.
- `2025`: R$ 87.672.351,83 em 68 registros, variacao -15,9%.

_Fonte local deste bloco: `processada/PI.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 66,1%, objeto em 100,0% e modalidade em 68,4%. Ha 0 registros negativos e 4 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/PI.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/PI.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `INSTITUTO DE GESTAO E DESENVOLVIMENTO SOCIAL - IGDS` (01019517000195): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01019517000195) - situacao ATIVA; municipio/UF TERESINA/PI; porte DEMAIS; atividade principal Atividades de associacoes de defesa de direitos sociais.
- `PREFEITURA MUNICIPAL DE TERESINA` (): sem URL externa verificada.
- `INSTITUTO DE DESENVOLVIMENTO DO NORDESTE (IDENE)` (20124920000129): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/20124920000129) - situacao ATIVA; municipio/UF TERESINA/PI; porte DEMAIS; atividade principal Atividade medica ambulatorial restrita a consultas.
- `PREFEITURA MUNICIPAL DE OEIRAS` (06553937000170): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/06553937000170) - situacao ATIVA; municipio/UF OEIRAS/PI; porte DEMAIS; atividade principal Administracao publica em geral.
- `FUNDACAO HOSPITALAR JOAQUIM SIMEAO FILHO - HOSPITAL BENEFICENCIA CHAPADA DO ARARIPE` (01386084000106): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01386084000106) - situacao ATIVA; municipio/UF MARCOLANDIA/PI; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.

### Investigacao complementar

- [INSTITUTO DE GESTAO E DESENVOLVIMENTO SOCIAL - IGDS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01019517000195+INSTITUTO+DE+GESTAO+E+DESENVOLVIMENTO+SOCIAL+-+IGDS+Piaui+convenio+contrato+gestao)
- [PREFEITURA MUNICIPAL DE TERESINA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=PREFEITURA+MUNICIPAL+DE+TERESINA+Piaui+convenio+contrato+gestao)
- [INSTITUTO DE DESENVOLVIMENTO DO NORDESTE (IDENE) - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=20124920000129+INSTITUTO+DE+DESENVOLVIMENTO+DO+NORDESTE+%28IDENE%29+Piaui+convenio+contrato+gestao)
- [PREFEITURA MUNICIPAL DE OEIRAS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=06553937000170+PREFEITURA+MUNICIPAL+DE+OEIRAS+Piaui+convenio+contrato+gestao)
- [FUNDACAO HOSPITALAR JOAQUIM SIMEAO FILHO - HOSPITAL BENEFICENCIA CHAPADA DO ARARIPE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01386084000106+FUNDACAO+HOSPITALAR+JOAQUIM+SIMEAO+FILHO+-+HOSPITAL+BENEFICENCIA+CHAPADA+DO+ARARIPE+Piaui+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\PI.parquet` (17 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\PI`.
- Exemplos de arquivos brutos estaduais: `dados_consolidados_pi.xlsx`, `Documento sem título.docx`, `pi_2022.json`, `pi_2023.json`, `pi_2024.json`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_pi.py`.
- Observacao de trilha: Serie montada a partir da planilha consolidada local preservada em `bases_orcamento_geral/PI`.

### Capital (Teresina)

- Parquet da capital consolidado: `E:\dados\capitais_processada\PI_TERESINA.parquet` (47 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Teresina`.
- Exemplos de arquivos brutos da capital: `Relatório consolidado 04.2019.xls`, `Relatório consolidado 05.2019.xls`, `Relatório consolidado 06.2019.xls`, `Relatório consolidado 08.2019.xlsx`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_teresina.py`.
- Fontes oficiais registradas para a capital: [transparencia.teresina.pi.gov.br/bp/parcerias](https://transparencia.teresina.pi.gov.br/bp/parcerias).

## Conclusao

Piaui deve ser lido como uma UF puxada por base mais distribuida. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
