# Priorizacao - Orcamento Geral Estadual

Base analisada: `E:\dados\orcamento_geral_processada`

Escopo deste relatorio: somente despesas/orcamento geral dos estados. Nao inclui `capitais_processada` nem a trilha estadual de `convenios`. Totais atualizados em 20/05/2026. Regra atual do campo `cnpj`: preservar o CNPJ numerico de 14 digitos informado pela fonte, mesmo quando falhar no checksum; falhas de digito verificador entram como alerta de qualidade, nao como criterio de exclusao.

## Criterio

- Criticos: 1 a 5 anos cobertos no parquet canonico de `orcamento_geral`.
- Baixa cobertura: 6 a 9 anos cobertos.
- Media incompleta: 10 a 17 anos cobertos, ou com buracos internos relevantes/pouca densidade.
- Melhor cobertura: acima de 20 anos cobertos.

## Criticos

| UF | Cobertura atual | Linhas | Situacao observada | Proxima acao |
| --- | ---: | ---: | --- | --- |
| DF | 18 anos: 2009-2026 | 36.678 | Ajustado em 19/05/2026: criado downloader oficial dos ZIPs anuais do portal de dados abertos do DF e parser passou a ler os empenhos historicos. | Saiu do grupo critico; manter acompanhamento mensal para 2026. |
| MA | 12 anos: 2015-2026 | 1.823 | Ajustado em 19/05/2026: criada coleta particionada no portal legado por ano e termo de busca, com 2015-2025 agregados por fornecedor; 2026 segue pelo CSV detalhado local. | Saiu do grupo critico; se necessario, aprofundar detalhe mensal/por orgao dos fornecedores historicos. |
| RJ | 10 anos: 2017-2026 | 49.668 | Ajustado em 19/05/2026: parser refeito com `polars` para ler o ZIP oficial completo do TFE/Fazenda RJ (`despesa.zip`) como despesa geral. | Manter atualizacao do ZIP oficial e revisar densidade, pois a contagem atual ficou baixa para uma serie completa de despesas. |
| BA | 2 anos: 2022, 2026 | 46.241 | Ajustado em 20/05/2026: parser passou a preferir os CSVs de pagamentos detalhados (`pagamentos_painel_*_detalhamento.csv`), que trazem `CPF/CNPJ`. | Buscar historico detalhado de pagamentos para anos alem de 2022 e 2026. |
| RR | 1 ano: 2023 | 353 | Ajustado em 20/05/2026: rebaixada a API oficial de despesa detalhada do portal estadual; parser passou a tratar a base como despesa geral. Testes FIPLAN encontraram relatorios de 2020-2022, mas sem CNPJ do credor. | Para ampliar anos, precisa fonte que exponha CPF/CNPJ do credor ou credencial para o servico `Credor`; sem isso, os anos FIPLAN continuam sem entrar no parquet. |
| PI | 5 anos: 2022-2026 | 297.470 | Ajustado em 19/05/2026: downloader passou a coletar todas as paginas da API de despesas por ano (`pi_despesas_gerais_*.json`). | Buscar disponibilidade anterior a 2022. |
| SE | 4 anos: 2023-2026 | 186.820 | Ajustado em 19/05/2026: parser passou a consolidar todos os empenhos dos XLSX locais e do export JSON de 2026. | Buscar historico anterior a 2023. |
| AC | 25 anos: 2002-2026 | 933.732 | Ajustado em 19/05/2026: criada coleta paginada da fonte oficial `Despesa Geral - Serie Historica`; em 20/05/2026, CNPJs de 14 digitos com checksum invalido passaram a ser preservados como informados pela fonte. | Manter acompanhamento de 2026 e tratar 1996-2001 como anos sem registros retornados pelo portal. |

## Baixa Cobertura

| UF | Cobertura atual | Buracos principais |
| --- | ---: | --- |
| TO | 6 anos: 2020-2025 | anos anteriores a 2020 e 2026 |
| AP | 7 anos: 2015, 2019-2024 | 2016-2018 e 2025-2026 |
| RO | 7 anos: 2020-2026 | anos anteriores a 2020; CNPJ vem por match conservador de nome contra `governo_federal/RO.parquet` |

Resolvido em 20/05/2026: `AL` saiu da baixa cobertura apos coleta oficial de 2010-2017 e reprocessamento da serie 2010-2026.

Resolvido em 20/05/2026: `PR` saiu da baixa cobertura apos coleta do documentador oficial da SEFA/PR para pagamentos por credor de 2018, 2019, 2021, 2022 e 2023. O parquet foi reprocessado com 4.231.324 linhas e cobertura de 2012-2023.

## Media Incompleta

| UF | Cobertura atual | Linhas | Situacao observada | Proxima acao |
| --- | ---: | ---: | --- | --- |
| RN | 16 anos: 2000-2002, 2006-2007, 2009-2011, 2019-2026 | 422 | Serie longa, mas com densidade muito baixa e buracos internos. | Revisar fonte/parsing antes de usar analiticamente. |
| PE | 15 anos: 2011-2023, 2025-2026 | 661 | Serie longa, mas com densidade muito baixa e falta 2024. | Revisar filtro/parsing e procurar fonte transacional mais densa. |
| PR | 12 anos: 2012-2023 | 4.231.324 | Ampliado em 20/05/2026 com o documentador oficial de despesas de 2018-2023. | Proxima busca: 2024-2026 na pagina nova de gastos publicos; 2010-2011 existem como ZIP local, mas ainda nao geram linhas canonicas suficientes apos normalizacao. |
| MT | 16 anos: 2010-2021, 2023-2026 | 13.598.069 | Boa densidade, mas falta 2022. | Buscar layout/fonte de 2022 com data da despesa. |
| AL | 17 anos: 2010-2026 | 161.978 | Ampliado em 20/05/2026 com coleta da API oficial de despesas de AL para 2010-2017 e consolidação com 2018-2026. | Manter acompanhamento; se necessario, revisar se o limite/filtro anual captura todos os registros por ano. |
| AM | 17 anos: 2010-2026 | 55.560 | Ajustado em 20/05/2026: criado downloader do CSV anual de pagamentos por credor do portal legado da SEFAZ-AM. | Fonte atual e consolidada por credor/ano; buscar fonte transacional detalhada se a analise exigir empenho/pagamento individual. |
| SP | 17 anos: 2010-2026 | 3.823.266 | Ajustado em 20/05/2026: criado downloader do Web Service oficial da Fazenda/SP (`ConsultarDespesas`) e parser passou a preferir os CSVs anuais de despesas gerais. | Serie oficial disponivel a partir de 2010; manter atualizacao incremental de 2026. |

## Ordem Recomendada de Execucao

1. Foco imediato em baixa cobertura: `TO`, `AP`, `RO`. `AL` saiu da fila apos ampliacao para 2010-2026; `PR` saiu apos ampliacao para 2012-2023.
2. Em seguida, revisar pouca densidade/buracos internos: `RN`, `PE`, `MT`, `RJ`.
3. Manter criticos em paralelo quando houver fonte nova: `RR`, `BA`, `SE`, `PI`.
4. Para `AC`, `ES`, `PB`, `PR` e `SP`, manter no relatorio de qualidade os CNPJs de 14 digitos com checksum invalido preservados da fonte.
