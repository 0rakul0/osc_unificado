# Fontes prioritarias para estado e capital

Levantamento inicial feito em 2026-04-10 para as 8 UFs que ainda estavam sem base util local na trilha de orcamento geral.

Observacao importante:

- Ja existe uma planilha de apoio em `E:\dados\bases_convenios_capitais\dados_coleta_por_capital.xlsx` com links de capitais que ja vinham sendo mapeados.
- No diretorio `E:\dados\bases_convenios_capitais` tambem ja havia pastas por nome de cidade, como `Rio Branco`, `Manaus` e `MACAPA`. Essas estruturas foram preservadas.

Legenda de status:

- `confirmado`: portal oficial respondeu e pode entrar na fila de coleta
- `confirmado com ressalva`: portal oficial existe, mas ainda precisamos identificar o melhor endpoint/export
- `validar manualmente`: ha indicio oficial suficiente, mas a URL final de extração ainda precisa ser fechada antes do download em lote

## Acre (AC) / Rio Branco

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Portal da Transparencia do Estado do Acre](https://www.transparencia.ac.gov.br/) | [Portal de Dados Abertos do Acre](https://dados.ac.gov.br/) | confirmado com ressalva | O portal de transparencia e o catalogo de dados abertos estao ativos; falta fechar qual dataset/export cobre melhor despesas por credor e convenios. |
| Capital | [Portal da Transparencia de Rio Branco](https://portalcgm.riobranco.ac.gov.br/portal/) | [Portal da Transparencia de Rio Branco](https://portalcgm.riobranco.ac.gov.br/portal/) | confirmado com ressalva | A capital ja tem portal proprio ativo; convem localizar o menu/export de convenios e transferencias. |

## Amapa (AP) / Macapa

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Transparencia-GEA](https://www.transparencia.ap.gov.br/) | [Transparencia-GEA](https://www.transparencia.ap.gov.br/) | confirmado com ressalva | O portal estadual esta ativo; precisamos testar os filtros/exportacoes de despesa e convenios. |
| Capital | [Portal da Transparencia da Prefeitura de Macapa](https://macapa.ap.gov.br/portaldatransparencia/) | [Portal da Transparencia da Prefeitura de Macapa](https://macapa.ap.gov.br/portaldatransparencia/) | confirmado com ressalva | O portal municipal responde bem e deve servir para despesa e convenios. |

## Amazonas (AM) / Manaus

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Portal da Transparencia do Governo do Estado do Amazonas](https://www.transparencia.am.gov.br/) | [Portal da Transparencia do Governo do Estado do Amazonas](https://www.transparencia.am.gov.br/) | confirmado com ressalva | O portal estadual esta ativo; ainda falta fechar a melhor rota/export para despesas por favorecido e convenios. |
| Capital | [Portal da Transparencia de Manaus](https://transparencia.manaus.am.gov.br/transparencia/) | `https://convenios.manaus.am.gov.br/` | validar manualmente | O portal de transparencia da capital esta confirmado. Um portal especifico de convenios aparece citado em documentacao oficial, mas o dominio nao resolveu no teste de hoje. |

## Rio Grande do Norte (RN) / Natal

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Portal da Transparencia do Rio Grande do Norte](http://www.transparencia.rn.gov.br/) | [Portal da Transparencia do Rio Grande do Norte](http://www.transparencia.rn.gov.br/) | confirmado com ressalva | O portal respondeu em `http`; a variante `https` apresentou erro de conexao no teste de hoje. |
| Capital | [Natal Transparente](https://www2.natal.rn.gov.br/transparencia/) | [Natal Transparente](https://www2.natal.rn.gov.br/transparencia/) | confirmado com ressalva | Portal municipal ativo; falta localizar a melhor exportacao para convenios e despesas pagas por credor. |

## Roraima (RR) / Boa Vista

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Portal da Transparencia do Estado de Roraima](https://transparencia.rr.gov.br/) | [Portal da Transparencia do Estado de Roraima](https://transparencia.rr.gov.br/) | confirmado com ressalva | O portal estadual esta ativo e entra na fila de coleta. |
| Capital | [Portal da Transparencia de Boa Vista](https://transparencia.boavista.rr.gov.br/) | [Portal da Transparencia de Boa Vista](https://transparencia.boavista.rr.gov.br/) | confirmado com ressalva | O portal municipal esta ativo; falta testar a navegacao por credor e transferencias/convenios. |

## Santa Catarina (SC) / Florianopolis

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Portal da Transparencia do Poder Executivo de Santa Catarina](https://transparencia.sc.gov.br/) | [SC Transferencias](https://www.cge.sc.gov.br/sctransferencias/) | confirmado | O estado ja tem uma separacao natural: despesas no portal de transparencia e transferencias voluntarias em portal proprio. |
| Capital | [Prefeitura de Florianopolis](https://www.pmf.sc.gov.br/) | [Prefeitura de Florianopolis](https://www.pmf.sc.gov.br/) | validar manualmente | Documentos oficiais da PMF citam portal da transparencia e listagens Betha com categorias de despesa e convenios, mas a URL final do modulo nao ficou estavel no teste automatizado. |

Evidencias complementares para a capital:

- [Plano de Acao Florianopolis Sustentavel](https://strapi.redeplanejamento.pmf.sc.gov.br/uploads/2022_10_06_15_00_24_Florianopolis_Sustentavel_81306b7117.pdf)
- [Betha Sistemas - listagem referenciando despesas e convenios](https://cms.pmf.sc.gov.br/admin/uploads/1581012522.pdf)

## Sao Paulo (SP) / Sao Paulo

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Portal da Transparencia do Estado de Sao Paulo](https://www.transparencia.sp.gov.br/) | [Portal da Transparencia do Estado de Sao Paulo](https://www.transparencia.sp.gov.br/) | confirmado com ressalva | O portal estadual esta ativo; precisamos definir a melhor extração de despesas por favorecido e convenios/termos. |
| Capital | [Portal da Transparencia da Prefeitura de Sao Paulo](https://transparencia.prefeitura.sp.gov.br/) | [Dados Abertos da Prefeitura de Sao Paulo](http://dados.prefeitura.sp.gov.br/pt_PT/) | confirmado | A capital tem portal de transparencia e catalogo de dados abertos; entra como um dos casos mais promissores para baixar em lote. |

## Tocantins (TO) / Palmas

| Escopo | Orcamento geral | Convenios | Status | Observacoes |
| --- | --- | --- | --- | --- |
| Estado | [Portal da Transparencia do Tocantins](https://transparencia.to.gov.br/) | [Portal da Transparencia do Tocantins](https://transparencia.to.gov.br/) | confirmado com ressalva | O portal estadual respondeu, mas ainda precisamos mapear a melhor rota de exportacao. |
| Capital | [Prefeitura de Palmas](https://www.palmas.to.gov.br/) | `http://portaldatransparencia.palmas.to.gov.br/` | validar manualmente | O dominio historico do portal de transparencia da capital apareceu em referencias externas e redireciona para a stack `prodata`, mas nao respondeu bem no teste automatizado de hoje. |

## Ordem pratica sugerida

1. SP capital
2. SC estado
3. RR estado
4. RN estado
5. AC estado
6. AP capital
7. AM estado
8. TO estado

Essa ordem prioriza portais que ja responderam bem e, em pelo menos parte dos casos, tem sinal claro de exportacao estruturada ou catalogo de dados.
