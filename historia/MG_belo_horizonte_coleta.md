# Belo Horizonte (MG) - Roteiro de Coleta

Levantamento atualizado em 2026-04-19 com foco em `despesas`, `convenios` e `parcerias` da Prefeitura de Belo Horizonte.

## 1. Despesas - links diretos ja fechados

Pagina principal:

- [Dados abertos de despesas municipais](https://prefeitura.pbh.gov.br/transparencia/contas-publicas/dados-abertos-despesa-municipal)

Links diretos por exercicio identificados na pagina oficial:

- 2024: [CSV](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/despesas_2024_12_07_2024.csv)
- 2023: [CSV](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/transparencia_despesas_2023.csv)
- 2022: [CSV](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/transparencia_despesas_2022.csv)
- 2021: [CSV](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/transparencia_despesas_2021.csv)
- 2020: [CSV](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/transparencia_despesas_2020.csv)
- 2019: [CSV](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/transparencia_despesas_2019.csv)
- 2018: [CSV](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/transparencia_despesas_2018.csv)

Observacoes:

- A pagina informa que os dados sao atualizados diariamente.
- A propria pagina de [Despesas](https://prefeitura.pbh.gov.br/transparencia/contas-publicas/despesas) diz que o sistema esta vinculado ao sistema municipal de contratos, convenios e congeners.

## 2. Ordem cronologica de pagamento

Paginas oficiais por ano:

- [Ordem cronologica 2024](https://prefeitura.pbh.gov.br/transparencia/contas-publicas/dados-abertos-despesa-municipal/ordem-cronologica/2024)
- [Ordem cronologica 2025](https://prefeitura.pbh.gov.br/transparencia/contas-publicas/dados-abertos-despesa-municipal/ordem-cronologica/2025)
- [Pagina principal da ordem cronologica](https://prefeitura.pbh.gov.br/transparencia/contas-publicas/dados-abertos-despesa-municipal/ordem-cronologica)

Exemplos de arquivos diretos identificados via pagina oficial:

- jan/2024: [XLSX](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/transparencia/2024/ordem-cronologica-de-pagamentos-01_2024.xlsx)
- jan/2025: [XLSX](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/fazenda/2025/ordem_cronologica-de-pagamentos-jan_2025.xlsx)

Uso recomendado:

- esta trilha ajuda a complementar pagamentos e priorizacao temporal
- eu trataria como trilha auxiliar, nao como base principal

## 3. Parcerias / OSC

Portais oficiais:

- [Portal das Parcerias](https://prefeitura.pbh.gov.br/portaldasparcerias)
- [Parcerias - sistema atual](https://prefeitura.pbh.gov.br/transparencia/parcerias)
- [Parcerias - registros anteriores](https://prefeitura.pbh.gov.br/portaldasparcerias/parcerias)
- [Alteracao das Parcerias](https://prefeitura.pbh.gov.br/transparencia/parcerias/alteracao)
- [Chamamentos Publicos, Dispensas e Inexigibilidades](https://prefeitura.pbh.gov.br/portaldasparcerias/chamamentos-publicos)

Sinais uteis encontrados:

- a pagina do sistema atual informa explicitamente que parte das parcerias foi migrada para um novo sistema e remete aos registros anteriores quando necessario
- a pagina de registros anteriores permite filtrar por:
  - orgao
  - numero do instrumento juridico
  - nome da organizacao
  - CNPJ da organizacao
  - palavra-chave
- a pagina de chamamentos tambem permite filtrar por:
  - orgao
  - origem
  - modalidade
  - situacao
  - ano

## 4. Coleta minima recomendada

Ordem mais simples para gerar ganho rapido:

1. Baixar os CSVs anuais de despesas `2018` a `2024`.
2. Filtrar por favorecidos com sinal de OSC no nome e por CNPJ valido.
3. Usar o Portal das Parcerias para validar instrumentos e ampliar contexto de `termo de colaboracao`, `termo de fomento` e `acordo de cooperacao`.
4. Se faltar recorte de 2025 em diante, complementar com a ordem cronologica e com o sistema atual de parcerias.

## 5. Leitura pratica

Belo Horizonte e o melhor caso para comecar porque:

- ja tem links diretos de `despesas` por exercicio
- tem portal proprio para `parcerias`
- o ecossistema oficial deixa claro que `despesas`, `convenios` e `congeners` fazem parte da mesma trilha administrativa

Conclusao:

- para o proximo passo tecnico, a rota mais facil e automatizar o download dos CSVs anuais de despesas primeiro
- depois vale montar uma segunda coleta focada no `Portal das Parcerias`
