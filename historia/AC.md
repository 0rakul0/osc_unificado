# Acre (AC)

## Visao geral

Acre soma 87 registros e R$ 255.822.845,79 em valor total. No ranking geral da base, a UF esta em 25o lugar por valor, 25o por quantidade de registros, 5o por ticket medio e 1o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e ticket medio e concentracao. O ticket medio e de R$ 2.940.492,48, a mediana e de R$ 850.000,00 e os 5 maiores beneficiarios concentram 100,0% do valor total.

_Fonte local deste bloco: `processada/AC.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, AC aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Acre cresce principalmente por ticket medio e concentracao. A participacao da UF no total nacional desta pasta e de 0,1%.

_Fonte local deste bloco: `processada/AC.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `07458465000130` - FUNDO ESTADUAL DE SAUDE - FUNDES: R$ 245.967.292,25 em 69 registros.
2. `15449024000108` - FUNDACAO DE AMPARO A PESQUISA DO ESTADO DO ACRE - FAPAC: R$ 7.473.900,00 em 12 registros.
3. `34035114000199` - INSTITUTO DE PROTECAO E DEFESA DO CONSUMIDOR DO ESTADO DO ACRE - PROCON: R$ 1.062.166,61 em 2 registros.
4. `10584440000197` - POLICIA CIVIL DO ESTADO DO ACRE - PCAC: R$ 849.486,93 em 2 registros.
5. `49869110000183` - SECRETARIA DE ESTADO DA MULHER - SEMULHER: R$ 470.000,00 em 2 registros.

_Fonte local deste bloco: `processada/AC.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `SAUDE, UNIDADE, ATENCAO, ESPECIALIZADA, REFORMA, HOSPITAL, AMPLIACAO, ACRE, PESQUISA, MISTA, CONSTRUCAO, PROGRAMA`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `FUNDO ESTADUAL DE SAUDE - FUNDES` - R$ 45.000.000,00 (ano 2020): CONSTRUCAO DE UNIDADE DE ATENCAO ESPECIALIZADA EM SAUDE - (NOVA MATERNIDADE - OBSTETRICA E NEONATAL) II fase.
2. `FUNDO ESTADUAL DE SAUDE - FUNDES` - R$ 39.000.000,00 (ano 2011): CONSTRUCAO DO HOSPITAL REGIONAL DE BRASILEIA.
3. `FUNDO ESTADUAL DE SAUDE - FUNDES` - R$ 17.000.010,00 (ano 2024): CONSTRUCAO DE UNIDADE DE ATENCAO ESPECIALIZADA EM SAUDE..
4. `FUNDO ESTADUAL DE SAUDE - FUNDES` - R$ 16.598.400,00 (ano 2024): CONSTRUCAO DE UNIDADE DE ATENCAO ESPECIALIZADA EM SAUDE.
5. `FUNDO ESTADUAL DE SAUDE - FUNDES` - R$ 15.668.000,00 (ano 2019): CONSTRUCAO DE UNIDADE DE ATENCAO ESPECIALIZADA EM SAUDE - (NOVA MATERNIDADE ).

O maior registro individual da UF foi para `FUNDO ESTADUAL DE SAUDE - FUNDES` no valor de R$ 45.000.000,00. O objeto associado foi: CONSTRUCAO DE UNIDADE DE ATENCAO ESPECIALIZADA EM SAUDE - (NOVA MATERNIDADE - OBSTETRICA E NEONATAL) II fase.

_Fonte local deste bloco: `processada/AC.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2020` - R$ 61.049.037,93 em 17 registros.
2. `2011` - R$ 47.433.200,00 em 3 registros.
3. `2024` - R$ 46.170.576,61 em 5 registros.

Ultimos anos da serie:

- `2020`: R$ 61.049.037,93 em 17 registros, variacao n/d.
- `2021`: R$ 2.798.900,00 em 1 registros, variacao -95,4%.
- `2022`: R$ 20.206.433,00 em 4 registros, variacao 621,9%.
- `2023`: R$ 8.865.730,00 em 4 registros, variacao -56,1%.
- `2024`: R$ 46.170.576,61 em 5 registros, variacao 420,8%.

_Fonte local deste bloco: `processada/AC.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `RIO BRANCO` - R$ 255.822.845,79 em 87 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 100,0%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 0 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/AC.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/AC.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `FUNDO ESTADUAL DE SAUDE - FUNDES` (07458465000130): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/07458465000130) - situacao ATIVA; municipio/UF RIO BRANCO/AC; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `FUNDACAO DE AMPARO A PESQUISA DO ESTADO DO ACRE - FAPAC` (15449024000108): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/15449024000108) - situacao ATIVA; municipio/UF RIO BRANCO/AC; porte DEMAIS; atividade principal Pesquisa e desenvolvimento experimental em ciencias sociais e humanas.
- `INSTITUTO DE PROTECAO E DEFESA DO CONSUMIDOR DO ESTADO DO ACRE - PROCON` (34035114000199): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/34035114000199) - situacao ATIVA; municipio/UF RIO BRANCO/AC; porte DEMAIS; atividade principal Regulacao das atividades economicas.
- `POLICIA CIVIL DO ESTADO DO ACRE - PCAC` (10584440000197): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/10584440000197) - situacao ATIVA; municipio/UF RIO BRANCO/AC; porte DEMAIS; atividade principal Seguranca e ordem publica.
- `SECRETARIA DE ESTADO DA MULHER - SEMULHER` (49869110000183): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/49869110000183) - situacao ATIVA; municipio/UF RIO BRANCO/AC; porte DEMAIS; atividade principal Administracao publica em geral.

### Investigacao complementar

- [FUNDO ESTADUAL DE SAUDE - FUNDES - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=07458465000130+FUNDO+ESTADUAL+DE+SAUDE+-+FUNDES+Acre+convenio+contrato+gestao)
- [FUNDACAO DE AMPARO A PESQUISA DO ESTADO DO ACRE - FAPAC - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=15449024000108+FUNDACAO+DE+AMPARO+A+PESQUISA+DO+ESTADO+DO+ACRE+-+FAPAC+Acre+convenio+contrato+gestao)
- [INSTITUTO DE PROTECAO E DEFESA DO CONSUMIDOR DO ESTADO DO ACRE - PROCON - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=34035114000199+INSTITUTO+DE+PROTECAO+E+DEFESA+DO+CONSUMIDOR+DO+ESTADO+DO+ACRE+-+PROCON+Acre+convenio+contrato+gestao)
- [POLICIA CIVIL DO ESTADO DO ACRE - PCAC - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=10584440000197+POLICIA+CIVIL+DO+ESTADO+DO+ACRE+-+PCAC+Acre+convenio+contrato+gestao)
- [SECRETARIA DE ESTADO DA MULHER - SEMULHER - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=49869110000183+SECRETARIA+DE+ESTADO+DA+MULHER+-+SEMULHER+Acre+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\AC.parquet` (7 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\AC`.
- Exemplos de arquivos brutos estaduais: `ac_convenios_detalhamento.json`, `ac_convenios_resumo.json`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_ac.py`, `utils/orcamento_geral/baixar_orcamento_geral_ac.py`.
- Fontes oficiais registradas para o estado: [transparencia.ac.gov.br/convenios](https://transparencia.ac.gov.br/convenios), [transparencia.ac.gov.br/convenios/detalhamento-pdf](https://transparencia.ac.gov.br/convenios/detalhamento-pdf).

### Capital (Rio Branco)

- Parquet da capital consolidado: `E:\dados\capitais_processada\AC_RIO_BRANCO.parquet` (5397 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Rio Branco`.
- Exemplos de arquivos brutos da capital: `dados_riobranco.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`.
- Fontes oficiais registradas para a capital: [portalcgm.riobranco.ac.gov.br/portal/](https://portalcgm.riobranco.ac.gov.br/portal/).

## Conclusao

Acre deve ser lido como uma UF puxada por ticket medio e concentracao. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
