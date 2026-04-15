# Bahia (BA)

## Atualizacao de orcamento geral

- Foi criado o parser `processar_orcamento_geral_ba.py` para consolidar pagamentos e cruzar recebedores com a trilha local de convenios.
- A saida canonica atual esta em `E:\dados\orcamento_geral_processada\BA.parquet`, com 13.994 linhas, 980 CNPJs e serie de 2022 a 2026.
- A versao final da Bahia manteve o recorte amplo decidido na revisao, inclusive com casos de heuristica baixa.

## Visao geral

Bahia soma 13.994 registros e R$ 67.783.417.595,00 em valor total. No ranking geral da base, a UF esta em 5o lugar por valor, 12o por quantidade de registros, 2o por ticket medio e 11o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e ticket medio. O ticket medio e de R$ 4.843.748,58, a mediana e de R$ 80.292,00 e os 5 maiores beneficiarios concentram 47,0% do valor total.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\BA.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, BA aparece entre as UFs lideres por valor em `MT, PB, PA, AL, BA`, por volume em `MT, PB, PA, ES, SE`, por ticket medio em `PE, BA, RR, RJ, AM` e por concentracao em `AC, RR, PE, CE, AM`.

Na pratica, isso indica que Bahia cresce principalmente por ticket medio. A participacao da UF no total nacional desta pasta e de 1,2%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\BA.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `00394460005887` - Secretaria Da Receita Federal Do Brasil: R$ 17.418.562.026,00 em 3.168 registros.
2. `15194004000125` - Fundacao Jose Silveira: R$ 6.280.177.000,00 em 101 registros.
3. `15178551000117` - Associacao Obras Sociais Irma Dulce: R$ 2.963.649.678,00 em 14 registros.
4. `14485841000140` - Universidade Do Estado Da Bahia: R$ 2.677.911.011,00 em 33 registros.
5. `11858570000133` - Instituto De Gestao E Humanizacao Igh: R$ 2.490.959.140,00 em 16 registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\BA.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `2019, CONFORME, TERMO, CONSTANTE, EMPRESA, RECONHECIMENTO, DEBITO, CORRESPONDENTE, RECOLHIMENTO, ENCARGOS, INSS, EMITIDA`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `Secretaria Da Receita Federal Do Brasil` - R$ 3.196.118.796,00 (ano 2026): Recolhimento de encargos do INSS correspondente a No 388/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.0008301-56. | Recolhimento de encargos do INSS correspondente a No 401/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.00010277-05. | Recolhimento de encargos do INSS correspondente NF No 471, emitida pela empresa ELLU TERCEIRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI:0115391.2019.0016422-51. | Recolhimento de encargos do INSS correspondente a NF No 505/2019, emitida pela empresa ELLU TERCEIRIZ.
2. `Secretaria Da Receita Federal Do Brasil` - R$ 2.174.543.972,00 (ano 2022): Recolhimento de encargos do INSS correspondente a No 388/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.0008301-56. | Recolhimento de encargos do INSS correspondente a No 401/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.00010277-05. | Recolhimento de encargos do INSS correspondente NF No 471, emitida pela empresa ELLU TERCEIRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI:0115391.2019.0016422-51. | Recolhimento de encargos do INSS correspondente a NF No 505/2019, emitida pela empresa ELLU TERCEIRIZ.
3. `Agencia De Fomento Do Estado Da Bahia S/a` - R$ 1.876.477.072,00 (ano 2022): servicos de cooperacao tecnica.
4. `Secretaria Da Receita Federal Do Brasil` - R$ 1.397.221.635,00 (ano 2022): Recolhimento de encargos do INSS correspondente a No 388/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.0008301-56. | Recolhimento de encargos do INSS correspondente a No 401/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.00010277-05. | Recolhimento de encargos do INSS correspondente NF No 471, emitida pela empresa ELLU TERCEIRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI:0115391.2019.0016422-51. | Recolhimento de encargos do INSS correspondente a NF No 505/2019, emitida pela empresa ELLU TERCEIRIZ.
5. `Secretaria Da Receita Federal Do Brasil` - R$ 1.353.990.460,00 (ano 2026): Recolhimento de encargos do INSS correspondente a No 388/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.0008301-56. | Recolhimento de encargos do INSS correspondente a No 401/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.00010277-05. | Recolhimento de encargos do INSS correspondente NF No 471, emitida pela empresa ELLU TERCEIRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI:0115391.2019.0016422-51. | Recolhimento de encargos do INSS correspondente a NF No 505/2019, emitida pela empresa ELLU TERCEIRIZ.

O maior registro individual da UF foi para `Secretaria Da Receita Federal Do Brasil` no valor de R$ 3.196.118.796,00. O objeto associado foi: Recolhimento de encargos do INSS correspondente a No 388/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.0008301-56. | Recolhimento de encargos do INSS correspondente a No 401/2019, emitida
pela empresa ELLU TERCEiRIZACAO, conforme Termo de Reconhecimento de Debito constante no processo SEI: 0115391.2019.00010277-05. | Recolhimento de encargos do INSS correspondente NF No 471, emitida pela empresa ELLU TERCEIRIZACA.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\BA.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2022` - R$ 43.130.633.017,00 em 8.440 registros.
2. `2026` - R$ 24.652.784.578,00 em 5.554 registros.

Ultimos anos da serie:

- `2022`: R$ 43.130.633.017,00 em 8.440 registros, variacao n/d.
- `2026`: R$ 24.652.784.578,00 em 5.554 registros, variacao -42,8%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\BA.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `SALVADOR` - R$ 21.189.190.560,00 em 4.444 registros.
2. `BRASILIA` - R$ 17.960.029.456,00 em 3.209 registros.
3. `Nao informado` - R$ 16.059.384.439,00 em 559 registros.
4. `RUY BARBOSA` - R$ 909.853.442,00 em 40 registros.
5. `FEIRA DE SANTANA` - R$ 894.166.132,00 em 305 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 96,0%, objeto em 96,0% e modalidade em 96,0%. Ha 0 registros negativos e 3.053 registros marcados como duplicado aparente.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\BA.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `E:\dados\orcamento_geral_processada\BA.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `Secretaria Da Receita Federal Do Brasil` (00394460005887): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/00394460005887) - situacao ATIVA; municipio/UF BRASILIA/DF; porte DEMAIS; atividade principal Administracao publica em geral.
- `Fundacao Jose Silveira` (15194004000125): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/15194004000125) - situacao ATIVA; municipio/UF SALVADOR/BA; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `Associacao Obras Sociais Irma Dulce` (15178551000117): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/15178551000117) - situacao ATIVA; municipio/UF SALVADOR/BA; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `Universidade Do Estado Da Bahia` (14485841000140): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/14485841000140) - situacao ATIVA; municipio/UF SALVADOR/BA; porte DEMAIS; atividade principal Educacao superior - graduacao.
- `Instituto De Gestao E Humanizacao Igh` (11858570000133): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/11858570000133) - situacao ATIVA; municipio/UF SALVADOR/BA; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.

### Investigacao complementar

- [Secretaria Da Receita Federal Do Brasil - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=00394460005887+Secretaria+Da+Receita+Federal+Do+Brasil+Bahia+convenio+contrato+gestao)
- [Fundacao Jose Silveira - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=15194004000125+Fundacao+Jose+Silveira+Bahia+convenio+contrato+gestao)
- [Associacao Obras Sociais Irma Dulce - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=15178551000117+Associacao+Obras+Sociais+Irma+Dulce+Bahia+convenio+contrato+gestao)
- [Universidade Do Estado Da Bahia - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=14485841000140+Universidade+Do+Estado+Da+Bahia+Bahia+convenio+contrato+gestao)
- [Instituto De Gestao E Humanizacao Igh - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=11858570000133+Instituto+De+Gestao+E+Humanizacao+Igh+Bahia+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\BA.parquet` (13994 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\BA`.
- Exemplos de arquivos brutos estaduais: `despesas.xlsx`, `despesas_2019.xlsx`, `despesas_2020.xlsx`, `despesas_2021.xlsx`, `despesas_2022.xlsx`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_ba.py`.
- Observacao de trilha: Serie montada a partir de arquivos locais legados preservados em `bases_convenios/BA`.

### Capital (Salvador)

- Parquet da capital consolidado: `E:\dados\capitais_processada\BA_SALVADOR.parquet` (1454031 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Salvador`.
- Exemplos de arquivos brutos da capital: `salvador_2015.json`, `salvador_2016.json`, `salvador_2017.json`, `salvador_2018.json`, `salvador_2019.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`.
- Observacao de trilha: Capital consolidada a partir de base legada local preservada em `bases_convenios_capitais/Salvador`.

## Conclusao

Bahia deve ser lido como uma UF puxada por ticket medio. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
