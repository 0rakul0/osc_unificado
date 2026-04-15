# Para (PA)

## Atualizacao de orcamento geral

- Foi criado o parser `processar_orcamento_geral_pa.py` usando a trilha oficial de notas de empenho do Para e a resolucao complementar de CNPJ por nome via API de detalhe.
- A saida canonica atual esta em `E:\dados\orcamento_geral_processada\PA.parquet`, com 799.354 linhas, 14.454 CNPJs e serie de 2016 a 2026.
- O fechamento do PA respeitou a regra de manter apenas CNPJ valido no parquet final.

## Visao geral

Para soma 799.354 registros e R$ 123.554.519.126,31 em valor total. No ranking geral da base, a UF esta em 3o lugar por valor, 3o por quantidade de registros, 25o por ticket medio e 21o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 154.567,96, a mediana e de R$ 3.743,18 e os 5 maiores beneficiarios concentram 20,3% do valor total.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PA.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, PA aparece entre as UFs lideres por valor em `MT, PB, PA, AL, BA`, por volume em `MT, PB, PA, ES, SE`, por ticket medio em `PE, BA, RR, RJ, AM` e por concentracao em `AC, RR, PE, CE, AM`.

Na pratica, isso indica que Para cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 2,2%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PA.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- 12,1% dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PA.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `05873910000100` - INSTITUTO DE GESTAO PREVIDENCIARIA DO PARA: R$ 16.189.452.606,83 em 19.677 registros.
2. `01227588000183` - CAIXA ECONOMICA FEDERAL: R$ 2.927.751.488,72 em 16.208 registros.
3. `05056031000188` - IASEP-INST.DE ASSISTENCIA SERV.PUBLICOS PARA: R$ 2.373.058.820,90 em 608 registros.
4. `84154608000160` - HOSPITAL PORTO DIAS LTDA: R$ 1.813.827.751,04 em 378 registros.
5. `04945341000190` - COMPANHIA DE SANEAMENTO DO PARA-COSANPA: R$ 1.802.862.486,92 em 3.755 registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PA.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `SESPA, SEAP, SEDUC, IASEP, FHCGV, CASA, FASEPA, SEFA, FEAS, UEPA, FUND, HEMOPA`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `INSTITUTO DE GESTAO PREVIDENCIARIA DO PARA` - R$ 340.458.223,05 (ano 2020): SEPLAD.
2. `INSTITUTO DE GESTAO PREVIDENCIARIA DO PARA` - R$ 188.495.283,95 (ano 2017): SEAD.
3. `INSTITUTO SOCIAL MAIS SAUDE` - R$ 187.068.036,08 (ano 2025): SESPA.
4. `HOSPITAL PORTO DIAS LTDA` - R$ 159.839.229,08 (ano 2020): IASEP.
5. `HOSPITAL PORTO DIAS LTDA` - R$ 143.825.975,21 (ano 2022): IASEP.

O maior registro individual da UF foi para `INSTITUTO DE GESTAO PREVIDENCIARIA DO PARA` no valor de R$ 340.458.223,05. O objeto associado foi: SEPLAD.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PA.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2025` - R$ 21.810.105.421,82 em 139.560 registros.
2. `2024` - R$ 18.578.715.887,95 em 130.853 registros.
3. `2023` - R$ 16.784.980.255,65 em 136.498 registros.

Ultimos anos da serie:

- `2022`: R$ 14.972.433.719,98 em 61.565 registros, variacao 24,1%.
- `2023`: R$ 16.784.980.255,65 em 136.498 registros, variacao 12,1%.
- `2024`: R$ 18.578.715.887,95 em 130.853 registros, variacao 10,7%.
- `2025`: R$ 21.810.105.421,82 em 139.560 registros, variacao 17,4%.
- `2026`: R$ 1.105.331.924,88 em 10.866 registros, variacao -94,9%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PA.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 100,0% e modalidade em 0,0%. Ha 0 registros negativos e 193.068 registros marcados como duplicado aparente.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\PA.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `E:\dados\orcamento_geral_processada\PA.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `INSTITUTO DE GESTAO PREVIDENCIARIA DO PARA` (05873910000100): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/05873910000100) - situacao ATIVA; municipio/UF BELEM/PA; porte DEMAIS; atividade principal Seguridade social obrigatoria.
- `CAIXA ECONOMICA FEDERAL` (01227588000183): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01227588000183) - situacao SUSPENSA; municipio/UF BRASILIA/DF; porte DEMAIS; atividade principal Administracao publica em geral.
- `IASEP-INST.DE ASSISTENCIA SERV.PUBLICOS PARA` (05056031000188): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/05056031000188) - situacao ATIVA; municipio/UF BELEM/PA; porte DEMAIS; atividade principal Planos de saude.
- `HOSPITAL PORTO DIAS LTDA` (84154608000160): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/84154608000160) - situacao ATIVA; municipio/UF BELEM/PA; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `COMPANHIA DE SANEAMENTO DO PARA-COSANPA` (04945341000190): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/04945341000190) - situacao ATIVA; municipio/UF BELEM/PA; porte DEMAIS; atividade principal Captacao, tratamento e distribuicao de agua.

### Investigacao complementar

- [INSTITUTO DE GESTAO PREVIDENCIARIA DO PARA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=05873910000100+INSTITUTO+DE+GESTAO+PREVIDENCIARIA+DO+PARA+Para+convenio+contrato+gestao)
- [CAIXA ECONOMICA FEDERAL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01227588000183+CAIXA+ECONOMICA+FEDERAL+Para+convenio+contrato+gestao)
- [IASEP-INST.DE ASSISTENCIA SERV.PUBLICOS PARA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=05056031000188+IASEP-INST.DE+ASSISTENCIA+SERV.PUBLICOS+PARA+Para+convenio+contrato+gestao)
- [HOSPITAL PORTO DIAS LTDA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=84154608000160+HOSPITAL+PORTO+DIAS+LTDA+Para+convenio+contrato+gestao)
- [COMPANHIA DE SANEAMENTO DO PARA-COSANPA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=04945341000190+COMPANHIA+DE+SANEAMENTO+DO+PARA-COSANPA+Para+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\PA.parquet` (799354 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\PA`.
- Exemplos de arquivos brutos estaduais: `2016.csv`, `2017.csv`, `2018.csv`, `2019.csv`, `2020.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_pa.py`.
- Fontes oficiais registradas para o estado: [api-notas-empenho.sistemas.pa.gov.br/notas-empenho/detalhe](https://api-notas-empenho.sistemas.pa.gov.br/notas-empenho/detalhe).
- Observacao de trilha: Serie complementada com CSVs locais preservados em `bases_orcamento_geral/PA`.

### Capital (Belem)

- Parquet da capital consolidado: `E:\dados\capitais_processada\PA_BELEM.parquet` (2 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Belem`.
- Exemplos de arquivos brutos da capital: `belem_convenios_consulta_todos_2000_2026.html`, `belem_convenios_export.bin`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`.
- Fontes oficiais registradas para a capital: [transparencia.belem.pa.gov.br/giig/portais/portaldatransparencia/Despesas/wfrmConsultaConveniosSemLayout.aspx](https://transparencia.belem.pa.gov.br/giig/portais/portaldatransparencia/Despesas/wfrmConsultaConveniosSemLayout.aspx).

## Conclusao

Para deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
