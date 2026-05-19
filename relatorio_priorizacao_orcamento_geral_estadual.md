# Priorizacao - Orcamento Geral Estadual

Base analisada: `E:\dados\orcamento_geral_processada`

Escopo deste relatorio: somente despesas/orcamento geral dos estados. Nao inclui `capitais_processada` nem a trilha estadual de `convenios`.

## Criterio

- Criticos: 1 a 5 anos cobertos no parquet canonico de `orcamento_geral`.
- Baixa cobertura: 6 a 9 anos cobertos.
- Media incompleta: 10 a 17 anos cobertos, ou com buracos internos relevantes.
- Melhor cobertura: acima de 20 anos cobertos.

## Criticos

| UF | Cobertura atual | Linhas | Situacao observada | Proxima acao |
| --- | ---: | ---: | --- | --- |
| DF | 18 anos: 2009-2026 | 38.356 | Ajustado em 19/05/2026: criado downloader oficial dos ZIPs anuais do portal de dados abertos do DF e parser passou a ler os empenhos historicos. | Saiu do grupo critico; manter acompanhamento mensal para 2026. |
| MA | 12 anos: 2015-2026 | 1.823 | Ajustado em 19/05/2026: criada coleta particionada no portal legado por ano e termo de busca, com 2015-2025 agregados por fornecedor; 2026 segue pelo CSV detalhado local. | Saiu do grupo critico; se necessario, aprofundar detalhe mensal/por orgao dos fornecedores historicos. |
| RJ | 9 anos: 2017, 2019-2026 | 365 | Ajustado em 19/05/2026: baixado ZIP oficial completo do TFE/Fazenda RJ (`despesa.zip`), parser processa CSVs anuais em chunks, normaliza colunas com acentos e usa valor pago/liquidado/empenhado em cascata. | Saiu do grupo critico; falta investigar ausencia de OSC em 2018 ou ajustar filtro se houver evidencia. |
| BA | 2 anos: 2022, 2026 | 13.994 | Ha brutos de despesas 2019-2026, mas o parser canonico usa `pagamentos_osc_candidatas_cruzadas.csv`, que ficou com 2022 e 2026. | Reprocessar a partir dos `despesas_*.xlsx` ou reconstruir a compilacao de pagamentos OSC para 2019-2026. |
| PI | 5 anos: 2022-2026 | 1.796 | Ajustado em 19/05/2026: criada coleta focada via API atual e parser passou a usar `pi_despesas_osc_*.json`. | Saiu do grupo de 1-2 anos, mas ainda segue com cobertura curta; proxima etapa e buscar anos anteriores a 2022. |
| RO | 15 anos: 2005, 2012-2013, 2015-2026 | 70 | Ajustado em 19/05/2026: incorporada API oficial de dados abertos (`transparencia.api.ro.gov.br/api/v1/convenios`) com 6.694 registros e CNPJ; HTML legado mantido como complemento. | Saiu do grupo critico; revisar registros com valor zero e eventuais anos sem execucao OSC. |
| SE | 4 anos: 2023-2026 | 8.704 | Ajustado em 19/05/2026: criado downloader pelo export JSON mensal da API atual de empenhos; 2026 entrou com 1.315 linhas filtradas para OSC. | Ainda critico por nao haver anos anteriores a 2023; proxima etapa e buscar historico pre-2023. |
| AC | 25 anos: 2002-2026 | 1.860.661 | Ajustado em 19/05/2026: criada coleta paginada da fonte oficial `Despesa Geral - Serie Historica` do portal estadual, sem filtro de OSC, consolidando todos os empenhos retornados pelo endpoint `/despesas/listar`. | Saiu do grupo critico; manter acompanhamento de 2026 e tratar 1996-2001 como anos sem registros retornados pelo portal. |

## Baixa Cobertura

| UF | Cobertura atual | Buracos principais |
| --- | ---: | --- |
| AP | 6 anos: 2021-2026 | anos anteriores a 2021 |
| TO | 6 anos: 2020-2025 | anos anteriores a 2020 e 2026 |
| AM | 7 anos: 2019-2025 | anos anteriores a 2019 e 2026 |
| PR | 7 anos: 2012-2017, 2020 | 2018-2019 e 2021-2026 |
| SP | 8 anos: 2019-2026 | anos anteriores a 2019 |
| AL | 9 anos: 2018-2026 | anos anteriores a 2018 |
| RJ | 9 anos: 2017, 2019-2026 | 2018 sem registros filtrados e anos anteriores a 2017 |

## Ordem Recomendada de Execucao

1. Reprocessar onde ja ha bruto local historico com chance alta de ganho rapido: `BA`. `AC` ja foi ampliado para 2002-2026, `PI` para 2022-2026, `SE` para 2023-2026, `RJ` para 2017/2019-2026, `MA` para 2015-2026 e `DF` para 2009-2026.
2. Criar ou completar downloaders para UFs criticas sem bruto historico local; para `SE`, buscar historico anterior a 2023.
3. Subir para baixa cobertura: `AP`, `TO`, `AM`, `PR`, `SP`, `AL`.
4. Depois revisar medias incompletas com buracos internos relevantes: `RR`, `RN`, `PE`, `MT`.
