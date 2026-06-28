# Colunas de valor por UF no `orcamento_geral`

Este arquivo documenta qual coluna cada parser estadual usa para preencher `valor_total` no parquet canônico de `orcamento_geral`.

Regra geral atual: quando a fonte traz `liquidado`, a prioridade deve ser `liquidado -> total/empenhado/original -> pago`. Quando a fonte não traz `liquidado`, o parser usa a melhor coluna financeira disponível na origem.

| UF | Parser | Tipo de fonte / ramo | Ordem atual para `valor_total` | Observação |
| --- | --- | --- | --- | --- |
| AC | `processar_orcamento_geral_ac.py` | Convênios | `valorprevisto -> valorliberadoconvenio` | Sem `liquidado`. |
| AC | `processar_orcamento_geral_ac.py` | Despesa geral | `totalempenho -> valorempenhado` | Sem `liquidado`. |
| AL | `processar_orcamento_geral_al.py` | Despesa geral | `valor_pago` | Usa pago direto. |
| AM | `processar_orcamento_geral_am.py` | Convênios | `Valor do Repasse (R$)` | Sem `liquidado`. |
| AM | `processar_orcamento_geral_am.py` | Despesa geral | `VALOR PAGO` | Usa pago direto. |
| AP | `processar_orcamento_geral_ap.py` | Convênios | `Valor Total -> Valor do Fomento -> Valor do Convênio` | Sem `liquidado`. |
| AP | `processar_orcamento_geral_ap.py` | Despesa geral | `VAL_LIQUIDADO / VALOR_LIQUIDO / Valor Liquidado -> VAL_EMPENHADO / VALOR_EMPENHADO / Valor Empenhado -> VAL_PAGO / VALOR_PAGO / Valor Pago` | Ajustado para priorizar liquidado. |
| BA | `processar_orcamento_geral_ba.py` | Planilha de despesa geral | `VAL_LIQUIDADO_TOTAL -> VAL_EMPENHADO_TOTAL -> VAL_PAGO` | Ajustado para priorizar liquidado. |
| BA | `processar_orcamento_geral_ba.py` | CSV consolidado | `valor_total` | Valor já vem consolidado. |
| BA | `processar_orcamento_geral_ba.py` | Detalhamento de pagamento | `Valor do Pagamento` | Usa pago direto. |
| BA | `processar_orcamento_geral_ba.py` | DataFrame geral normalizado | `VAL_LIQUIDADO_TOTAL -> VAL_EMPENHADO_TOTAL -> VAL_PAGO` | Mesmo critério do ramo de planilha. |
| CE | `processar_orcamento_geral_ce.py` | Consolidado | `valor_total -> valor_atualizado` | Sem `liquidado`. |
| DF | `processar_orcamento_geral_df.py` | Despesa geral | `valorNlBruto -> valorObFinal -> valorNeFinal -> VALOR FINAL -> VALOR INICIAL -> valorPagoExercicio` | Ajustado para priorizar liquidado/bruto antes de pago. |
| ES | `processar_orcamento_geral_es.py` | Consolidado | `valor_total` | Valor já vem consolidado. |
| GO | `processar_orcamento_geral_go.py` | Despesa geral | `Valor Pagamento` | Usa pagamento direto. |
| MA | `processar_orcamento_geral_ma.py` | Despesa filtrada por fase | `valor` | O parser filtra `fase == PAGAMENTO`. |
| MA | `processar_orcamento_geral_ma.py` | Base alternativa | `valor_pago` | Usa pago direto. |
| MG | `processar_orcamento_geral_mg.py` | Despesa geral | `vr_liquidado -> vr_empenhado -> vr_pago` | Ajustado para priorizar liquidado. |
| MS | `processar_orcamento_geral_ms.py` | Resumo anual por credor | `Liquidado -> Empenhado -> Pago` | Ajustado para priorizar liquidado. |
| MT | `processar_orcamento_geral_mt.py` | Despesa geral | `VLLIQUIDADO -> VLDESPESA ou VLPAGO -> VLEMPENHADO` | `VLDESPESA` é usado quando há fase de pagamento; sem fase, cai em `VLPAGO`. |
| PA | `processar_orcamento_geral_pa.py` | Despesa geral | `vlr_pago` | Usa pago direto. |
| PB | `processar_orcamento_geral_pb.py` | Despesa geral | `VALOR_EMPENHO` | Sem `liquidado`. |
| PE | `processar_orcamento_geral_pe.py` | Planilha / linha posicional | `row[8]` | Convém nomear a coluna de origem em próxima limpeza. |
| PI | `processar_orcamento_geral_pi.py` | Despesa geral | `temp_pago_saldo` | Usa saldo/pagamento da fonte. |
| PR | `processar_orcamento_geral_pr.py` | Despesa oficial | `valor_pagamento` | Usa pagamento direto. |
| PR | `processar_orcamento_geral_pr.py` | Documentador | `PAGO -> Valor` | Não há `liquidado` nesse ramo. |
| RJ | `processar_orcamento_geral_rj.py` | Despesa geral | `Valor Liquidado -> Valor Empenhado -> Valor Pago` | Ajustado para priorizar liquidado. |
| RN | `processar_orcamento_geral_rn.py` | Convênios / parcerias | `ValorTotal` | Sem `liquidado`. |
| RO | `processar_orcamento_geral_ro.py` | Convênios | `valor_total_previsto` | Sem `liquidado`. |
| RO | `processar_orcamento_geral_ro.py` | Outra base de convênios | `valorInicial` | Sem `liquidado`. |
| RO | `processar_orcamento_geral_ro.py` | Despesa geral | `valorPago -> valorEmpenhado` | Usa pago antes de empenhado; não há `liquidado`. |
| RR | `processar_orcamento_geral_rr.py` | JSON de despesa | `totalLiquidado -> valorEmpenho -> totalPago` | Ajustado para priorizar liquidado. |
| RR | `processar_orcamento_geral_rr.py` | Base legada | `Valor Global -> Valor Repasse` | Sem `liquidado`. |
| RS | `processar_orcamento_geral_rs.py` | Despesa geral | `Valor` | Coluna única na origem. |
| SC | `processar_orcamento_geral_sc.py` | Transferências | `Valor Repassado -> Valor da Transferência` | Sem `liquidado`. |
| SE | `processar_orcamento_geral_se.py` | Planilha de empenhos | `vlTotalLiquidadoEmpenho -> vlOriginalEmpenho -> vlSolicEmpenho -> vlTotalPagoEmpenho` | Ajustado para priorizar liquidado. |
| SE | `processar_orcamento_geral_se.py` | API | `valorExecutado -> valorOriginal` | Sem coluna explícita de liquidado. |
| SP | `processar_orcamento_geral_sp.py` | Portal de parcerias | `valor_total` | Valor já vem consolidado. |
| SP | `processar_orcamento_geral_sp.py` | Despesa webservice | `ValorLiquidado -> ValorEmpenhado -> ValorPago` | Ajustado para priorizar liquidado. |
| TO | `processar_orcamento_geral_to.py` | Convênios | `Valor do Convênio` | Sem `liquidado`. |

## UFs já ajustadas para priorizar `liquidado`

- AP
- BA
- DF
- MG
- MS
- MT
- RJ
- RR
- SE
- SP

## UFs sem coluna de `liquidado` mapeada no parser atual

- AC
- AL
- AM
- CE
- ES
- GO
- MA
- PA
- PB
- PE
- PI
- PR
- RN
- RO
- RS
- SC
- TO

## Convenios

Regra geral atual: quando a fonte de `convenios` expoe `liquidado`, a prioridade deve ser `liquidado -> total/original/solicitado -> pago`. Quando a fonte nao expoe `liquidado`, o parser preserva o melhor total publicado na origem.

| UF | Parser | Tipo de fonte / ramo | Ordem atual para `valor_total` | Observacao |
| --- | --- | --- | --- | --- |
| AC | `utils/convenios/parsers/AC.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| AL | `utils/convenios/parsers/AL.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| AM | `utils/convenios/parsers/AM.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| AP | `utils/convenios/parsers/AP.py` | Convenios | `Valor Total` | Sem `liquidado`. |
| BA | `utils/convenios/parsers/BA.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| CE | `utils/convenios/parsers/CE.py` | Convenios | `Valor empenhado final` | Sem `liquidado`. |
| DF | `utils/convenios/parsers/DF.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| ES | `utils/convenios/parsers/ES.py` | Execucao orcamentaria de convenios | `ValorLiquidado -> ValorPago` | Ajustado para priorizar liquidado. |
| GO | `utils/convenios/parsers/GO.py` | Convenios | `VALOR_TOTAL` | Valor consolidado da origem. |
| MA | `utils/convenios/parsers/MA.py` | Convenios | `Valor Total Previsto` ou `Valor Total do Instrumento` | Sem `liquidado`. |
| MG | `utils/convenios/parsers/MG.py` | Convenios | `vr_total_atual` | Valor consolidado da origem. |
| MS | `utils/convenios/parsers/MS.py` | Convenios | `valorConvenio` | Sem `liquidado`. |
| MT | `utils/convenios/parsers/MT.py` | Convenios | `valor_total` da base padronizada | Sem ajuste recente. |
| PA | `utils/convenios/parsers/PA.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| PB | `utils/convenios/parsers/PB.py` | Convenios | `Valor Total` | Sem `liquidado`. |
| PE | `utils/convenios/parsers/PE.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| PI | `utils/convenios/parsers/PI.py` | Convenios | `Valor Concedente` ou `valor_total` | Sem `liquidado`. |
| PR | `utils/convenios/parsers/PR.py` | Convenios | `total_repasses` | Sem `liquidado`. |
| RJ | `utils/convenios/parsers/RJ.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| RN | `utils/convenios/parsers/RN.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| RO | `utils/convenios/parsers/RO.py` | Convenios | `Valor Global R$` | Sem `liquidado`. |
| RR | `utils/convenios/parsers/RR.py` | Convenios | `Valor Global` | Sem `liquidado`. |
| RS | `utils/convenios/parsers/RS.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| SC | `utils/convenios/parsers/SC.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| SE | `utils/convenios/parsers/SE.py` | Empenhos ligados a convenios | `vlTotalLiquidadoEmpenho -> vlOriginalEmpenho -> vlSolicEmpenho -> vlTotalPagoEmpenho` | Ajustado para priorizar liquidado. |
| SP | `utils/convenios/parsers/SP.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |
| TO | `utils/convenios/parsers/TO.py` | Convenios | valor mapeado pela coluna padrao da fonte | Sem ajuste recente. |

### UFs de convenios ja ajustadas para priorizar `liquidado`

- ES
- SE

## Capitais

Regra geral atual: quando a fonte de `capitais` expoe `liquidado`, a prioridade deve ser `liquidado -> total/empenhado -> pago`. Quando a fonte nao expoe `liquidado`, o parser usa o melhor total disponivel na origem.

| Capital | UF | Parser / arquivo | Tipo de fonte / ramo | Ordem atual para `valor_total` | Observacao |
| --- | --- | --- | --- | --- | --- |
| Rio Branco | AC | `utils/capitais/shared.py` | Despesa | `liquidado_rs -> empenhado_rs -> pago_rs` | Ajustado para priorizar liquidado. |
| Maceio | AL | `utils/capitais/shared.py` | Despesa | `valor_liquidado -> valor_empenhado -> valor_pago` | Ajustado para priorizar liquidado. |
| Macapa | AP | `utils/capitais/shared.py` | Despesa | `valor` | Sem `liquidado`. |
| Manaus | AM | `utils/capitais/shared.py` | Despesa | `EmpTotalLiquidado -> EmpValorEmpenho -> EmpTotalPago` | Ajustado para priorizar liquidado. |
| Salvador | BA | `utils/capitais/shared.py` | Despesa | `Valor Liquidado` | Ja usava liquidado direto. |
| Fortaleza | CE | `utils/capitais/shared.py` | Despesa / convenio | `TOTAL NO PERIODO` ou `Valor do Convenio` | Sem `liquidado` nesses ramos. |
| Brasilia | DF | `utils/capitais/shared.py` | Convenios | `VALOR PAGO -> VALOR TOTAL` | Sem coluna explicita de `liquidado` nesse ramo. |
| Vitoria | ES | `utils/capitais/shared.py` | Convenios | `ValorContratado -> ValorOriginal -> ValorAditivo` | Sem `liquidado`. |
| Goiania | GO | `utils/capitais/processar_despesas_capitais_extras.py` | Despesa extra | `VlLiquidado -> VlEmpenhado -> VlPago` | Ajustado para priorizar liquidado. |
| Sao Luis | MA | `utils/capitais/shared.py` | Convenios | `valor_pactuado -> valor_contrapartida` | Sem `liquidado`. |
| Belo Horizonte | MG | `utils/capitais/shared.py` | Despesa / convenio | `valor_bruto_op / vl_npd / vl_empenhado` | Nao houve ajuste; nao ha campo explicito de liquidado nesses ramos. |
| Cuiaba | MT | `utils/capitais/processar_despesas_capitais_extras.py` | Despesa extra | `DespesaLiquidacao -> DespesaEmpenho -> DespesaPagamento` | Ajustado para priorizar liquidado. |
| Campo Grande | MS | `utils/capitais/shared.py` | Convenios | `valor_total -> valor_concedente` | Sem `liquidado`. |
| Belem | PA | `utils/capitais/shared.py` | Convenios / despesa | `Valor Atualizado do Instrumento -> Valor Instrumento` ou `valor_lista -> valor_previsto_total -> valor_repasse` | Sem `liquidado`. |
| Joao Pessoa | PB | `utils/capitais/shared.py` | Convenios | `valor_mes -> valor_total_ano` | Sem `liquidado`. |
| Recife | PE | `utils/capitais/processar_recife_despesas_lookup_local.py` | Despesa historica | `valor_liquidado -> valor_empenhado -> valor_pago` | Ajustado para priorizar liquidado. |
| Recife | PE | `utils/capitais/processar_recife_despesas_lookup_local.py` | Despesa recente | `Liquidação -> Empenhado -> Pagamento` | Ajustado para priorizar liquidado. |
| Curitiba | PR | `utils/capitais/processar_despesas_capitais_extras.py` | Despesa extra | `VL_LIQUIDADO -> VL_PAGO` | Ajustado para priorizar liquidado. |
| Rio de Janeiro | RJ | `utils/capitais/shared.py` | Despesa | `total_liquidado -> total_empenhado -> total_pago` | Ajustado para priorizar liquidado. |
| Natal | RN | `utils/capitais/shared.py` | Convenios | `valor_total` | Valor consolidado da origem. |
| Porto Alegre | RS | `utils/capitais/processar_despesas_capitais_extras.py` | Despesa extra | `Despesa_Paga` | Sem `liquidado` nesse script. |
| Porto Velho | RO | `utils/capitais/shared.py` | Convenios | `valor_total -> valor_executado` | Sem `liquidado`. |
| Boa Vista | RR | `utils/capitais/shared.py` | Despesa | `LIQUIDADO -> EMPENHADO -> PAGO` | Ajustado para priorizar liquidado. |
| Aracaju | SE | `utils/capitais/processar_despesas_capitais_extras.py` | Despesa extra | `Liquidado -> Empenhado -> Pago` | Ajustado para priorizar liquidado. |
| Florianopolis | SC | `utils/capitais/shared.py` | Convenios | `valorTotal -> valorPagoTotal -> valorEmpenhadoTotal` | Sem coluna explicita de `liquidado` nesse ramo. |
| Florianopolis | SC | `utils/capitais/shared.py` | Despesa | `valor_liquidado -> valor_total -> valor_empenhado -> valor_pago` | Ajustado para priorizar liquidado. |
| Sao Paulo | SP | `utils/capitais/shared.py` | Convenios | `Valor Mensal Total (R$)` | Sem `liquidado`. |
| Teresina | PI | `utils/capitais/shared.py` | Convenios | `Valor total -> Valor liberado` | Sem `liquidado`. |
| Teresina | PI | `utils/capitais/shared.py` | Despesa | `valor_pago -> valor_empenho` | Sem `liquidado` nesse ramo. |
| Palmas | TO | `utils/capitais/shared.py` | Despesa | `valor_liquidado -> valor_total -> valor_empenhado -> valor_pago` | Ajustado para priorizar liquidado. |

### Capitais ja ajustadas para priorizar `liquidado`

- Rio Branco
- Maceio
- Manaus
- Goiania
- Cuiaba
- Recife
- Curitiba
- Rio de Janeiro
- Boa Vista
- Aracaju
- Florianopolis
- Palmas
