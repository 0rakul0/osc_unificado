# Fontes Prioritarias - Capitais Com Download Imediato

Levantamento feito em 2026-04-19 para as capitais que parecem mais promissoras para ampliar cobertura de despesas, convenios e parcerias com coleta municipal.

Objetivo:

- priorizar fontes oficiais com sinal claro de exportacao, dados abertos ou consulta estruturada
- reduzir a lacuna das capitais com baixa cobertura historica
- deixar uma ordem pratica para a proxima rodada de coleta

Legenda de status:

- `pronto para coleta`: ha portal oficial com caminho claro de consulta ou download
- `pronto com ressalva`: a fonte e forte, mas pode exigir navegacao adicional para achar o melhor export

## Resumo Operacional

| UF | Capital | Despesas | Convenios / Parcerias | Status | Melhor primeira acao |
| --- | --- | --- | --- | --- | --- |
| MG | Belo Horizonte | [Dados abertos de despesas municipais](https://prefeitura.pbh.gov.br/transparencia/contas-publicas/dados-abertos-despesa-municipal) | [Portal das Parcerias](https://prefeitura.pbh.gov.br/portaldasparcerias) | pronto para coleta | baixar despesas por exercicio e depois abrir parcerias antigas e atuais |
| PE | Recife | [Portal da Transparencia](https://transparencia.recife.pe.gov.br/) | [Dados Abertos do Recife](https://dados.recife.pe.gov.br/) | pronto para coleta | fechar export de despesas e convênios/repasses no portal e no catalogo aberto |
| MA | Sao Luis | [Portal da Transparencia](https://www.saoluis.ma.gov.br/portal/transparencia) | [Contas Publicas](https://www.saoluis.ma.gov.br/portal/contas_publicas) | pronto com ressalva | priorizar despesas por credor e transferencias voluntarias realizadas |
| MS | Campo Grande | [Despesas](https://sig-transparencia.campogrande.ms.gov.br/despesas/consulta) | [Repasses Estaduais Voluntarios](https://sig-transparencia.campogrande.ms.gov.br/repasses-estaduais/consulta) | pronto para coleta | puxar repasses estaduais e cruzar com contratos e despesas por favorecido |
| CE | Fortaleza | [Portal da Transparencia](https://transparencia.fortaleza.ce.gov.br/) | [Convenios](https://transparencia.fortaleza.ce.gov.br/index.php/convenio) | pronto com ressalva | explorar dados abertos, contratos, contratos de gestao e parcerias MROSC |
| RR | Boa Vista | [Portal da Transparencia](https://transparencia.boavista.rr.gov.br/) | [Convenios](https://transparencia.boavista.rr.gov.br/convenios) | pronto para coleta | usar dados abertos e consultas detalhadas de convenios e despesas |
| RS | Porto Alegre | [Despesas](https://transparencia.portoalegre.rs.gov.br/despesas) | [Parcerias](https://transparencia.portoalegre.rs.gov.br/parcerias) | pronto com ressalva | levantar despesa por favorecido e a listagem de convenios/parcerias |
| AP | Macapa | [Portal da Transparencia](https://transparencia.macapa.ap.gov.br/) | [Dados Abertos](https://transparencia.macapa.ap.gov.br/dados-abertos/) | pronto com ressalva | procurar export de convenios/transferencias voluntarias e contratos |

## Rodada de extracao iniciada em 2026-05-13

Prioridade definida a partir dos parquets de capitais com baixa cobertura:

| UF | Capital | Lacuna observada | Fonte de despesas testada | Status |
| --- | --- | --- | --- | --- |
| SC | Florianopolis | parquet local tinha apenas 2025 e 25 linhas | `https://transparencia.e-publica.net/epublica-portal/rest/florianopolis/api/v1/despesa` | coletor criado e validado para 2016-2026; convênios detalhados incorporados |
| PA | Belem | parquet local tinha apenas 2018 e 2 linhas | iframe oficial GIIG em `https://transparencia.belem.pa.gov.br/giig/portais/portaldatransparencia/despesas/wfrmConsultaDespesasParaSemLayout.aspx` | coletor criado; cobertura parcial validada para 2023, 2024 e 2025 |
| PI | Teresina | parquet local tinha 2018-2019 e 47 linhas | CSVs locais `despesas_teresina_20*.csv` | dados brutos incorporados para 2015-2026 |
| TO | Palmas | parquet local tinha 2023-2025 e 4 linhas | `https://prodata.palmas.to.gov.br/sig/rest/despesaSimplificadoController/pesquisarPorInteressado` | coletor criado e validado para despesas pagas 2023-2025 |

### Florianopolis (SC)

- Script criado: `utils/capitais/downloads/baixar_despesas_capital_florianopolis.py`.
- Parser atualizado: `utils/capitais/parsers/florianopolis.py` passa a ler `florianopolis_despesas_20*.json` e anexar `convenios_detalhe_20*.csv`.
- Fonte oficial documentada no proprio portal em `Dados Abertos > Despesa - Execucao`.
- Parametros oficiais usados: `periodo_inicial`, `periodo_final`, `inicio_registro`, `quantidade_registro`.
- Extracao inicial executada para `2016` a `2026`.
- Arquivos brutos gerados em `E:\dados\bases_convenios_capitais\Florianopolis`:
  - `florianopolis_despesas_2016.json`: 58.372 registros brutos
  - `florianopolis_despesas_2017.json`: 57.199 registros brutos
  - `florianopolis_despesas_2018.json`: 64.039 registros brutos
  - `florianopolis_despesas_2019.json`: 68.281 registros brutos
  - `florianopolis_despesas_2020.json`: 57.430 registros brutos
  - `florianopolis_despesas_2021.json`: 63.879 registros brutos
  - `florianopolis_despesas_2022.json`: 57.437 registros brutos
  - `florianopolis_despesas_2023.json`: 66.548 registros brutos
  - `florianopolis_despesas_2024.json`: 68.499 registros brutos
  - `florianopolis_despesas_2025.json`: 74.721 registros brutos
  - `florianopolis_despesas_2026.json`: 27.238 registros brutos
  - `florianopolis_despesas_manifest.json`: URLs, paginas, hashes e contagens
  - `convenios_detalhe_2016.csv` a `convenios_detalhe_2026.csv`: convênios/parcerias detalhados, anexados ao parquet
- Parquet processado gerado em `E:\dados\capitais_processada\SC_FLORIANOPOLIS.parquet`: 544.224 linhas validas depois da normalizacao.
- Cobertura anual processada: `2016` com 46.674 linhas, `2017` com 45.169, `2018` com 53.559, `2019` com 56.997, `2020` com 49.114, `2021` com 53.364, `2022` com 46.340, `2023` com 54.616, `2024` com 56.291, `2025` com 59.762 e `2026` com 22.338.

### Teresina (PI)

- Parser atualizado: `utils/capitais/parsers/teresina.py` passa a ler `despesas_teresina_20*.csv`.
- Fonte bruta incorporada: CSVs locais de despesas por empenho/favorecido em `E:\dados\bases_convenios_capitais\Teresina`.
- Arquivos brutos usados: `despesas_teresina_2015.csv` a `despesas_teresina_2026.csv`.
- Campos principais usados: `ano`, `data_empenho`, `data_pagamento`, `valor_pago`, `valor_empenho`, `favorecido_cpf_cnpj`, `favorecido_nome`, `orgao` e `empenho`.
- Parquet processado gerado em `E:\dados\capitais_processada\PI_TERESINA.parquet`: 501.849 linhas validas depois da normalizacao.
- Cobertura anual processada: `2015` com 48.849 linhas, `2016` com 50.164, `2017` com 46.701, `2018` com 49.582, `2019` com 51.790, `2020` com 43.819, `2021` com 40.343, `2022` com 45.806, `2023` com 42.405, `2024` com 37.979, `2025` com 33.392 e `2026` com 11.019.

### Palmas (TO)

- Script criado: `utils/capitais/downloads/baixar_despesas_capital_palmas.py`.
- Parser atualizado: `utils/capitais/parsers/palmas.py` passa a ler `palmas_despesas_20*.json`.
- Fonte oficial usada: Portal Prodata de Transparencia, tela `Despesa` / `Despesa simplificada`.
- Endpoint de consulta: `https://prodata.palmas.to.gov.br/sig/rest/despesaSimplificadoController/pesquisarPorInteressado`.
- Parametros oficiais usados: `fase_despesa=pago`, `agrupamento=fornecedor`, `exercicio`, `mesInicial=1`, `mesFinal=12`.
- Observacao tecnica: a API exige login publico em `loginController/validarLoginParaModuloPublico` e cabecalhos assinados `x-client-id`, `x-timestamp`, `x-request-signature` e `x-auth-token`.
- Extracao inicial executada para `2023` a `2025`.
- Arquivos brutos gerados em `E:\dados\bases_convenios_capitais\Palmas`:
  - `palmas_despesas_2023.json`: 51.460 registros brutos
  - `palmas_despesas_2024.json`: 48.206 registros brutos
  - `palmas_despesas_2025.json`: 43.122 registros brutos
  - `palmas_despesas_manifest.json`: URLs, hashes e contagens
- Parquet processado gerado em `E:\dados\capitais_processada\TO_PALMAS.parquet`: 133.848 linhas validas depois da normalizacao.
- Cobertura anual processada: `2023` com 47.224 linhas, `2024` com 45.780 e `2025` com 40.844.

### Belem (PA)

- Script criado: `utils/capitais/downloads/baixar_despesas_capital_belem.py`.
- Parser atualizado: `utils/capitais/parsers/belem.py` passa a ler `belem_despesas_20*.json`.
- Fonte oficial usada: Portal da Transparencia / GIIG, tela `Despesas Detalhadas`.
- URL da consulta: `https://transparencia.belem.pa.gov.br/giig/portais/portaldatransparencia/despesas/wfrmConsultaDespesasParaSemLayout.aspx`.
- Metodo: consulta WebForms oficial com filtros de ano e periodo, leitura da grade paginada mes a mes.
- Observacao tecnica: o botao Excel exporta apenas a pagina visivel; por isso o coletor percorre a paginacao da grade. Janeiro de 2025 teve 153 paginas.
- Extracao executada para os anos disponiveis no portal: `2020`, `2021`, `2022`, `2023`, `2024`, `2025` e `2026` ate maio.
- Arquivos brutos gerados em `E:\dados\bases_convenios_capitais\Belem`:
  - `belem_despesas_2020.json`: 39.868 registros brutos
  - `belem_despesas_2021.json`: 35.352 registros brutos
  - `belem_despesas_2022.json`: 39.443 registros brutos
  - `belem_despesas_2023.json`: 42.992 registros brutos
  - `belem_despesas_2024.json`: 50.084 registros brutos
  - `belem_despesas_2025.json`: 29.819 registros brutos
  - `belem_despesas_2026.json`: 10.887 registros brutos
  - `belem_despesas_manifest.json`: URL, metodo e contagens por mes
- Parquet processado gerado em `E:\dados\capitais_processada\PA_BELEM.parquet`: 248.445 linhas validas depois da normalizacao.
- Cobertura mensal processada: `2020` com abril a dezembro; `2021` com marco a julho e setembro a dezembro; `2022` com marco a dezembro; `2023` com janeiro a outubro e dezembro; `2024` com janeiro e marco a dezembro; `2025` com janeiro, abril, maio, julho a novembro; `2026` com fevereiro a maio. Os demais meses consultados retornaram zero no portal.
- Comando de retomada para buscar os meses faltantes sem refazer o que ja consta no manifesto: `python utils\capitais\downloads\baixar_despesas_capital_belem.py --years 2020 2021 2022 2023 2024 2025 2026 --resume`.
- Proximo passo tecnico opcional: investigar alternativa para extrair o DataTable interno do ViewState e reduzir o custo da paginacao.

## Notas Por Capital

### Belo Horizonte (MG)

- A pagina de despesas informa downloads por exercicio de `2018` a `2024` e atualizacao diaria.
- A pagina de despesas tambem informa integracao com o sistema municipal de contratos, convenios e congeners.
- O [Portal das Parcerias](https://prefeitura.pbh.gov.br/portaldasparcerias) e o melhor ponto para recorte OSC.
- Ordem sugerida:
  1. baixar despesas por ano
  2. localizar parcerias antigas e sistema atual
  3. cruzar por CNPJ / nome do parceiro

### Recife (PE)

- O portal municipal separa claramente `Despesa`, `Receita de Convenios`, `Repasses ou Transferencias` e `Dados Abertos`.
- O catalogo [Dados Abertos do Recife](https://dados.recife.pe.gov.br/) parece o caminho mais promissor para export reutilizavel.
- Ordem sugerida:
  1. localizar datasets de despesa por credor ou empenho
  2. localizar modulo ou dataset de convenios / transferencias
  3. revisar contratos de gestao se o recorte OSC continuar curto

### Sao Luis (MA)

- O portal informa `Despesa Total e Detalhada`, `Despesas por Credor`, `Transferencias Voluntarias Realizadas` e `Acordos, Convenios e Termos de Cooperacao`.
- A pagina [Conceitos e regras de utilizacao](https://www.saoluis.ma.gov.br/conceitos-e-regras-de-utilizacao) confirma que ha dados publicos em formato aberto no ecossistema do portal.
- Ordem sugerida:
  1. despesas por credor
  2. transferencias voluntarias realizadas
  3. acordos / convenios / termos de cooperacao

### Campo Grande (MS)

- A pagina de [Repasses Estaduais Voluntarios](https://sig-transparencia.campogrande.ms.gov.br/repasses-estaduais/consulta) informa que, entre `2022` e `30/09/2025`, a prefeitura possui apenas convenios voluntarios estaduais.
- O portal tambem expone consulta de despesas e contratos.
- Ordem sugerida:
  1. repasses estaduais
  2. despesas por favorecido
  3. contratos ligados aos mesmos favorecidos

### Fortaleza (CE)

- O portal municipal expone `Despesas`, `Convenios`, `Parcerias MROSC`, `Contratos de Gestao` e `Dados Abertos`.
- A pagina [Dados Abertos](https://transparencia.fortaleza.ce.gov.br/index.php/dadosAbertos) referencia o catalogo [dados.fortaleza.ce.gov.br](https://dados.fortaleza.ce.gov.br).
- Ha pagina de dados abertos de `Contratos` com `CSV` e dicionario de dados.
- Ordem sugerida:
  1. contratos em CSV
  2. convenios
  3. parcerias MROSC
  4. contratos de gestao

### Boa Vista (RR)

- O portal informa `Despesas`, `Convenios e Transferencias` e uma area de [Dados Abertos](https://transparencia.boavista.rr.gov.br/dados-aberto).
- A FAQ oficial informa que o portal oferece `despesas publicas`, `convênios e outros acordos` e que ha dois caminhos: consulta detalhada ou dados abertos.
- Ordem sugerida:
  1. usar dados abertos e exemplos de chamada para identificar endpoints
  2. baixar convenios
  3. cruzar com despesas

### Porto Alegre (RS)

- A secao [Parcerias](https://transparencia.portoalegre.rs.gov.br/parcerias) aponta para o Sistema de Gestao de Parcerias e para listagens de convenios municipais e federais.
- A secao [Despesas](https://transparencia.portoalegre.rs.gov.br/despesas) informa despesa mensal por favorecido, orgao e programa.
- Ordem sugerida:
  1. despesa por favorecido
  2. listagem de convenios
  3. sistema de parcerias

### Macapa (AP)

- O portal municipal lista `Contratos, Aditivos e Fiscais`, `Convenios / Transferencias Voluntarias` e `Dados Abertos`.
- A pagina de [Dados Abertos](https://transparencia.macapa.ap.gov.br/dados-abertos/) e a cartilha do portal reforcam que a estrutura deve suportar download direto ou endpoint.
- Ordem sugerida:
  1. convenios / transferencias voluntarias
  2. contratos
  3. despesas

## Ordem Pratica Sugerida

1. MG / Belo Horizonte
2. PE / Recife
3. MS / Campo Grande
4. RR / Boa Vista
5. CE / Fortaleza
6. AP / Macapa
7. MA / Sao Luis
8. RS / Porto Alegre

Motivo da ordem:

- as quatro primeiras combinam melhor sinal de dado estruturado com caminho de acesso mais claro
- Fortaleza e Macapa parecem muito promissoras, mas podem exigir mais navegacao para achar o export certo
- Sao Luis e Porto Alegre tem bom sinal institucional, mas a extracao pode pedir um pouco mais de trabalho manual
