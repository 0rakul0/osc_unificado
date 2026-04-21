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
