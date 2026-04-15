# Minas Gerais (MG)

## Visao geral

Minas Gerais soma 81.990 registros e R$ 24.871.732.492,85 em valor total. No ranking geral da base, a UF esta em 7o lugar por valor, 3o por quantidade de registros, 20o por ticket medio e 23o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 303.350,80, a mediana e de R$ 90.000,00 e os 5 maiores beneficiarios concentram 12,0% do valor total.

_Fonte local deste bloco: `processada/MG.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, MG aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Minas Gerais cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 7,1%.

_Fonte local deste bloco: `processada/MG.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `18715383000140` - MUNICIPIO DE BELO HORIZONTE: R$ 827.155.931,64 em 205 registros.
2. `09104426000160` - COPASA - SERVICOS DE SANEAMENTO INTEGRADO DO NORTE E NORDESTE DE MINAS GERAIS S/A: R$ 661.441.413,00 em 2 registros.
3. `06981180000116` - CEMIG DISTRIBUICAO S.A: R$ 578.456.683,47 em 5 registros.
4. `18720938000141` - FUNDACAO DE DESENVOLVIMENTO DA PESQUISA: R$ 509.489.491,54 em 59 registros.
5. `17281106000103` - COMPANHIA DE SANEAMENTO DE MINAS GERAIS COPASA MG: R$ 419.524.162,47 em 54 registros.

_Fonte local deste bloco: `processada/MG.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `FONT, SPAN, AQUISICAO, STYLE, EXECUCAO, RECURSOS, LSDEXCEPTION, ESCOLAR, MEIO, SIZE, MUNICIPIO, PROGRAMA`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `COPASA - SERVICOS DE SANEAMENTO INTEGRADO DO NORTE E NORDESTE DE MINAS GERAIS S/A` - R$ 653.441.413,00 (ano 2007): PROMOCAO DE PROGRAMAS E ACOES NA AREA DE SAUDE VISANDO A AMPLIACAO DO SERVICO DE SANEAMENTO BASICO, COMPREENDENDO A IMPLANTACAO E OPERACAO DE ESTACOES DE ABASTECIMENTO DE AGUA E ESGOTAMENTO SANITARIO, EM MUNICIPIOS COMPREENDIDOS NA REGIAO DAS BACIAS HIDROGRAFICAS DOS RIOS JEQUITINHONHA, MUCURI, SAO MATEUS, BURANHEM, ITANHEM E JUCURUCU..
2. `CEMIG DISTRIBUICAO S.A` - R$ 554.762.000,00 (ano 2008): O convenio tem por objeto a cooperacao financeira entre o Estado de Minas Gerais, por meio da SEDE e a CEMIG D, para viabilizar obras de infra-estrutura, dentre outras acoes coordenadas no ambito do programa ?Luz Para Todos?. Composicao do Projeto: Obras de Distribuicao..
3. `FUNDACAO DE DESENVOLVIMENTO DA PESQUISA` - R$ 357.236.470,57 (ano 2007): O PRESENTE TERMO DE COOPERACAO TEM POR OBJETO A COLABORACAO ENTRE OS PARTICIPES PARA O GERENCIAMENTO DAS ATIVIDADES ASSISTENCIAIS DE SAUDE DA UNIDADE DE PRONTO ATENDIMENTO DE JUSTINOPOLIS E O DESENVOLVIMENTO DE PROGRAMAS DE ENSINO, PESQUISA E EXTENSAO, POR MEIO DE INVESTIMENTO E CUSTEIO..
4. `MUNICIPIO DE BELO HORIZONTE` - R$ 265.213.331,00 (ano 2009): Constitui objeto deste convenio a conjugacao de esforcos e efetiva participacao dos convenentes para a execucao, mediante cooperacao tecnica e financeira, das obras de alargamento da Avenida Antonio Carlos, no trecho compreendido entre a Rua Operarios, no Bairro Cachoeirinha, ate o complexo da Lagoinha, no Municipio de Belo Horizonte..
5. `MUNICIPIO DE BELO HORIZONTE` - R$ 144.000.000,00 (ano 2011): Avenidas Pedro I Desapropriacoes para a duplicacao deste corredor viario de articulacao entre as regioes Norte, Pampulha, Venda Nova e Centro, possibilitando a implantacao do BRT ??Bus Rapid Transit?. Avenida Pedro II / Av Carlos Luz Desapropriacoes para execucao de obras de melhoria operacional nas avenidas, possibilitando a implantacao do BRT ??Bus Rapid Transit? por ser estas vias de grande importancia de articulacao entre as regioes Noroeste, Oeste, Pampulha e Centro, Via 710 Desapropriacoes para obras de implantacao de parte desta via ligando a Av Cristiano Machado a Av Jose Candido da Silveira extendendo se ate a Avenida dos Andradas articulando acesso as regionais Nordeste, Noroeste, .

O maior registro individual da UF foi para `COPASA - SERVICOS DE SANEAMENTO INTEGRADO DO NORTE E NORDESTE DE MINAS GERAIS S/A` no valor de R$ 653.441.413,00. O objeto associado foi: PROMOCAO DE PROGRAMAS E ACOES NA AREA DE SAUDE VISANDO A AMPLIACAO DO SERVICO DE SANEAMENTO BASICO, COMPREENDENDO A IMPLANTACAO E OPERACAO DE ESTACOES DE ABASTECIMENTO DE AGUA E ESGOTAMENTO SANITARIO, EM MUNICIPIOS COMPREENDIDOS NA REGIAO DAS BACIAS HIDROGRAFICAS DOS RIOS JEQUITINHONHA, MUCURI, SAO MATEUS, BURANHEM, ITANHEM E JUCURUCU..

_Fonte local deste bloco: `processada/MG.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2022` - R$ 4.190.397.656,32 em 6.654 registros.
2. `2023` - R$ 2.051.394.330,38 em 4.521 registros.
3. `2007` - R$ 1.811.210.773,95 em 5.088 registros.

Ultimos anos da serie:

- `2021`: R$ 1.255.124.804,00 em 3.733 registros, variacao n/d.
- `2022`: R$ 4.190.397.656,32 em 6.654 registros, variacao 233,9%.
- `2023`: R$ 2.051.394.330,38 em 4.521 registros, variacao -51,0%.
- `2024`: R$ 1.735.710.850,08 em 4.428 registros, variacao -15,4%.
- `2025`: R$ 1.468.285.578,74 em 4.921 registros, variacao -15,4%.

_Fonte local deste bloco: `processada/MG.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `BELO HORIZONTE` - R$ 3.925.347.591,39 em 3.275 registros.
2. `TEOFILO OTONI` - R$ 806.570.320,18 em 311 registros.
3. `JUIZ DE FORA` - R$ 608.431.098,35 em 536 registros.
4. `MONTES CLAROS` - R$ 356.515.797,34 em 724 registros.
5. `UBERLANDIA` - R$ 350.696.849,12 em 417 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 100,0%, objeto em 82,2% e modalidade em 25,7%. Ha 0 registros negativos e 102 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/MG.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/MG.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `MUNICIPIO DE BELO HORIZONTE` (18715383000140): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/18715383000140) - status da consulta 429.
- `COPASA - SERVICOS DE SANEAMENTO INTEGRADO DO NORTE E NORDESTE DE MINAS GERAIS S/A` (09104426000160): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/09104426000160) - status da consulta 429.
- `CEMIG DISTRIBUICAO S.A` (06981180000116): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/06981180000116) - status da consulta 429.
- `FUNDACAO DE DESENVOLVIMENTO DA PESQUISA` (18720938000141): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/18720938000141) - status da consulta 429.
- `COMPANHIA DE SANEAMENTO DE MINAS GERAIS COPASA MG` (17281106000103): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/17281106000103) - status da consulta 429.

### Investigacao complementar

- [MUNICIPIO DE BELO HORIZONTE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=18715383000140+MUNICIPIO+DE+BELO+HORIZONTE+Minas+Gerais+convenio+contrato+gestao)
- [COPASA - SERVICOS DE SANEAMENTO INTEGRADO DO NORTE E NORDESTE DE MINAS GERAIS S/A - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=09104426000160+COPASA+-+SERVICOS+DE+SANEAMENTO+INTEGRADO+DO+NORTE+E+NORDESTE+DE+MINAS+GERAIS+S%2FA+Minas+Gerais+convenio+contrato+gestao)
- [CEMIG DISTRIBUICAO S.A - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=06981180000116+CEMIG+DISTRIBUICAO+S.A+Minas+Gerais+convenio+contrato+gestao)
- [FUNDACAO DE DESENVOLVIMENTO DA PESQUISA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=18720938000141+FUNDACAO+DE+DESENVOLVIMENTO+DA+PESQUISA+Minas+Gerais+convenio+contrato+gestao)
- [COMPANHIA DE SANEAMENTO DE MINAS GERAIS COPASA MG - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=17281106000103+COMPANHIA+DE+SANEAMENTO+DE+MINAS+GERAIS+COPASA+MG+Minas+Gerais+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\MG.parquet` (11170046 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\MG`.
- Exemplos de arquivos brutos estaduais: `desktop.ini`, `ft_despesa_2002_enriquecido.csv`, `ft_despesa_2003_enriquecido.csv`, `ft_despesa_2004_enriquecido.csv`, `ft_despesa_2005_enriquecido.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_mg.py`.
- Observacao de trilha: Serie derivada dos CSVs enriquecidos preservados em `bases_orcamento_geral/MG`.

### Capital (Belo Horizonte)

- Parquet da capital consolidado: `E:\dados\capitais_processada\MG_BELO_HORIZONTE.parquet` (137 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Belo Horizonte`.
- Exemplos de arquivos brutos da capital: `belohorizonte_convenios_repasse.csv`, `belohorizonte_convenios_repasse_2024.csv`, `belohorizonte_convenios_repasse_raw.csv`, `belohorizonte_parcerias.html`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_belo_horizonte.py`.
- Fontes oficiais registradas para a capital: [prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/controladoria/convenios-de-repasse-31-10-2024-csv.csv](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/controladoria/convenios-de-repasse-31-10-2024-csv.csv).

## Conclusao

Minas Gerais deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
