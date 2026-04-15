# Rondonia (RO)

## Visao geral

Rondonia soma 3.862 registros e R$ 1.601.523.745,14 em valor total. No ranking geral da base, a UF esta em 18o lugar por valor, 15o por quantidade de registros, 16o por ticket medio e 18o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e base mais distribuida. O ticket medio e de R$ 414.687,66, a mediana e de R$ 100.000,00 e os 5 maiores beneficiarios concentram 25,4% do valor total.

_Fonte local deste bloco: `processada/RO.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, RO aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Rondonia cresce principalmente por base mais distribuida. A participacao da UF no total nacional desta pasta e de 0,5%.

_Fonte local deste bloco: `processada/RO.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- A serie atual de Rondonia foi recomposta apos a separacao de arquivos que estavam armazenados na pasta de Roraima. A versao atual do parquet ja reflete essa limpeza de origem.
- 24,4% dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros.

_Fonte local deste bloco: `processada/RO.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `49150352001607` - FUNDACAO PIO XII: R$ 138.930.010,25 em 7 registros.
2. `O MUNICIPIO DE  NOVA BRASILANDIA D  OESTE-RO` - O MUNICIPIO DE  NOVA BRASILANDIA D  OESTE-RO: R$ 118.650.000,00 em 1 registros.
3. `ASSOCIACAO ASSISTENCIAL A SAUDE SAO DANIEL COMBONI - ASSDACO` - ASSOCIACAO ASSISTENCIAL A SAUDE SAO DANIEL COMBONI - ASSDACO: R$ 51.715.713,13 em 10 registros.
4. `04092714000128` - MUNICIPIO DE CACOAL: R$ 48.505.154,27 em 89 registros.
5. `04104816000116` - MUNICIPIO DE ARIQUEMES: R$ 48.463.686,47 em 92 registros.

_Fonte local deste bloco: `processada/RO.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `AQUISICAO, MUNICIPIO, SERVICOS, RURAIS, PRODUTORES, CONVENENTE, REALIZACAO, PEQUENOS, COMO, TRANSPORTE, PRODUCAO, ENTRE`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `O MUNICIPIO DE  NOVA BRASILANDIA D  OESTE-RO` - R$ 118.650.000,00 (ano 2017): O objeto do acordo entre as partes e a liberacao de recursos que serao aplicados na construcao de 02 (duas) salas de aulas na Escola Marechal Hermes da Fonseca, conforme especificado no projeto basico de fls. 18/21, no Municipio de Nova Brasilandia D'Oeste-RO..
2. `FUNDACAO PIO XII` - R$ 46.408.308,51 (ano 2020): Apoio financeiro do Estado para custear as despesas com aquisicao de material de consumo medico/hospitalar, servico e pessoal de qualidade e quantidade necessarias para atender a demanda de pacientes oncologicos, visando garantir a resolubilidade e integralidade dos atendimentos e manutencao da Unidade de Porto Velho..
3. `FUNDACAO PIO XII` - R$ 28.180.665,81 (ano 2018): Apoio financeiro do Estado para custear as despesas com aquisicao de material de consumo medico/hospitalar, servico e pessoal de qualidade e quantidade necessarias para atender a demanda de pacientes oncologicos, visando garantir a resolubilidade e integralidade dos atendimentos e manutencao da Unidade de Porto Velho..
4. `FUNDACAO PIO XII` - R$ 25.400.000,00 (ano 2021): Apoio financeiro do Estado para custear as despesas adquiridas na prestacao de servicos de oncologia.
5. `ASSOCIACAO ASSISTENCIAL A SAUDE SAO DANIEL COMBONI - ASSDACO` - R$ 24.000.000,00 (ano 2023): Custeio de equipe multiprofissional para a prestacao de servicos de saude em Oncologia, especificamente, quimioterapia, radioterapia, exames diagnosticos e acompanhamento ambulatorial, de forma continua e complementar, para atender as necessidades dos usuarios do Sistema Unico de Saude (SUS), residentes na Macrorregiao de Saude II do Estado de Rondonia..

O maior registro individual da UF foi para `O MUNICIPIO DE  NOVA BRASILANDIA D  OESTE-RO` no valor de R$ 118.650.000,00. O objeto associado foi: O objeto do acordo entre as partes e a liberacao de recursos que serao aplicados na construcao de 02 (duas) salas de aulas na Escola Marechal Hermes da Fonseca, conforme especificado no projeto basico de fls. 18/21, no Municipio de Nova Brasilandia D'Oeste-RO..

_Fonte local deste bloco: `processada/RO.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2017` - R$ 289.890.728,73 em 393 registros.
2. `2024` - R$ 207.076.045,08 em 510 registros.
3. `2022` - R$ 206.807.932,57 em 511 registros.

Ultimos anos da serie:

- `2021`: R$ 165.606.634,97 em 402 registros, variacao n/d.
- `2022`: R$ 206.807.932,57 em 511 registros, variacao 24,9%.
- `2023`: R$ 188.713.901,12 em 400 registros, variacao -8,7%.
- `2024`: R$ 207.076.045,08 em 510 registros, variacao 9,7%.
- `2025`: R$ 195.443.167,49 em 352 registros, variacao -5,6%.

_Fonte local deste bloco: `processada/RO.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 65,7%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 86 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/RO.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/RO.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `FUNDACAO PIO XII` (49150352001607): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/49150352001607) - situacao ATIVA; municipio/UF PORTO VELHO/RO; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `O MUNICIPIO DE  NOVA BRASILANDIA D  OESTE-RO` (): sem URL externa verificada.
- `ASSOCIACAO ASSISTENCIAL A SAUDE SAO DANIEL COMBONI - ASSDACO` (): sem URL externa verificada.
- `MUNICIPIO DE CACOAL` (04092714000128): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/04092714000128) - situacao ATIVA; municipio/UF CACOAL/RO; porte DEMAIS; atividade principal Administracao publica em geral.
- `MUNICIPIO DE ARIQUEMES` (04104816000116): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/04104816000116) - situacao ATIVA; municipio/UF ARIQUEMES/RO; porte DEMAIS; atividade principal Administracao publica em geral.

### Investigacao complementar

- [FUNDACAO PIO XII - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=49150352001607+FUNDACAO+PIO+XII+Rondonia+convenio+contrato+gestao)
- [O MUNICIPIO DE  NOVA BRASILANDIA D  OESTE-RO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=O+MUNICIPIO+DE++NOVA+BRASILANDIA+D++OESTE-RO+Rondonia+convenio+contrato+gestao)
- [ASSOCIACAO ASSISTENCIAL A SAUDE SAO DANIEL COMBONI - ASSDACO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=ASSOCIACAO+ASSISTENCIAL+A+SAUDE+SAO+DANIEL+COMBONI+-+ASSDACO+Rondonia+convenio+contrato+gestao)
- [MUNICIPIO DE CACOAL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=04092714000128+MUNICIPIO+DE+CACOAL+Rondonia+convenio+contrato+gestao)
- [MUNICIPIO DE ARIQUEMES - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=04104816000116+MUNICIPIO+DE+ARIQUEMES+Rondonia+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\RO.parquet` (4 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\RO`.
- Exemplos de arquivos brutos estaduais: `Documento sem título.docx`, `ro_transferencias_realizadas.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_ro.py`, `utils/orcamento_geral/baixar_orcamento_geral_ro.py`.
- Fontes oficiais registradas para o estado: [transparencia.ro.gov.br/convenios/filtrartransferencias](https://transparencia.ro.gov.br/convenios/filtrartransferencias).

### Capital (Porto Velho)

- Parquet da capital consolidado: `E:\dados\capitais_processada\RO_PORTO_VELHO.parquet` (673 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Porto Velho`.
- Exemplos de arquivos brutos da capital: `portovelho_convenios_api_filtrado.json`, `portovelho_convenios_api_resumo.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_porto_velho.py`.
- Fontes oficiais registradas para a capital: [transparencia.portovelho.ro.gov.br/contratos?modelo_nome=7](https://transparencia.portovelho.ro.gov.br/contratos?modelo_nome=7), [api.portovelho.ro.gov.br/api/v1/contratos](https://api.portovelho.ro.gov.br/api/v1/contratos).

## Conclusao

Rondonia deve ser lido como uma UF puxada por base mais distribuida. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
