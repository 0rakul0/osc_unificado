# Historias por UF

Colecao de narrativas geradas a partir dos arquivos `.parquet` em `processada/`.

## Atualizacao do projeto em 08/04/2026

- `AL`: trilha de orcamento geral ja estava disponivel e segue como ponto de partida do projeto; `E:\dados\orcamento_geral_processada\AL.parquet` tem 144.411 linhas, 35.554 CNPJs e anos de 2018 a 2026.
- `BA`: parser `processar_orcamento_geral_ba.py` criado; `E:\dados\orcamento_geral_processada\BA.parquet` esta fechado com 13.994 linhas e 980 CNPJs, mantendo o recorte amplo decidido depois do cruzamento com convenios.
- `CE`: parser `processar_orcamento_geral_ce.py` criado; `E:\dados\orcamento_geral_processada\CE.parquet` esta fechado com 4.802 linhas e 428 CNPJs, usando `Valor pago` com fallback para `Valor atualizado`.
- `ES`: parser `processar_orcamento_geral_es.py` criado; `E:\dados\orcamento_geral_processada\ES.parquet` esta fechado com 247.128 linhas e 1.844 CNPJs, todos com 14 digitos.
- `PA`: parser `processar_orcamento_geral_pa.py` criado a partir da API oficial de notas de empenho; `E:\dados\orcamento_geral_processada\PA.parquet` esta fechado com 799.354 linhas e 14.454 CNPJs.
- `PB`: downloader `baixar_orcamento_geral_pb_dados_abertos.py` e parser `processar_orcamento_geral_pb.py` criados; `E:\dados\orcamento_geral_processada\PB.parquet` esta fechado com 1.794.815 linhas, 44.848 CNPJs e `valor_total` preenchido em toda a base.
- `MT`: a trilha legada foi substituida pela base oficial rica do portal; `processar_orcamento_geral_mt.py` agora delega para `processar_orcamento_geral_mt_oficial.py`, e `E:\dados\orcamento_geral_processada\MT.parquet` ficou com 14.195.271 linhas e 26.002 CNPJs. O ano de 2022 ficou fora do canone por nao trazer data no layout oficial.
- `PE`: houve investigacao inicial, mas a trilha de orcamento geral ainda nao foi fechada. A base local de despesas nao parece uma extracao estadual completa e precisara de coleta oficial mais rica antes de virar parquet canonico.

- [Acre (AC)](AC.md)
- [Alagoas (AL)](AL.md)
- [Amazonas (AM)](AM.md)
- [Amapa (AP)](AP.md)
- [Bahia (BA)](BA.md)
- [Ceara (CE)](CE.md)
- [Distrito Federal (DF)](DF.md)
- [Espirito Santo (ES)](ES.md)
- [Goias (GO)](GO.md)
- [Maranhao (MA)](MA.md)
- [Minas Gerais (MG)](MG.md)
- [Mato Grosso do Sul (MS)](MS.md)
- [Mato Grosso (MT)](MT.md)
- [Para (PA)](PA.md)
- [Paraiba (PB)](PB.md)
- [Pernambuco (PE)](PE.md)
- [Piaui (PI)](PI.md)
- [Parana (PR)](PR.md)
- [Rio de Janeiro (RJ)](RJ.md)
- [Rio Grande do Norte (RN)](RN.md)
- [Rondonia (RO)](RO.md)
- [Roraima (RR)](RR.md)
- [Rio Grande do Sul (RS)](RS.md)
- [Santa Catarina (SC)](SC.md)
- [Sergipe (SE)](SE.md)
- [Sao Paulo (SP)](SP.md)
- [Tocantins (TO)](TO.md)
