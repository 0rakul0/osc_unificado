# Rio Grande do Sul (RS)

## Visao geral

Rio Grande do Sul soma 50.504 registros e R$ 10.334.785.228,41 em valor total. No ranking geral da base, a UF esta em 11o lugar por valor, 5o por quantidade de registros, 24o por ticket medio e 11o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 204.633,00, a mediana e de R$ 14.000,00 e os 5 maiores beneficiarios concentram 37,7% do valor total.

_Fonte local deste bloco: `processada/RS.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, RS aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Rio Grande do Sul cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 2,9%.

_Fonte local deste bloco: `processada/RS.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- 31,4% dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros.

_Fonte local deste bloco: `processada/RS.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `89161475000173` - ASSOC RIOGRANDENSE EMPR ASS TEC EXT RURAL: R$ 1.935.262.685,90 em 31 registros.
2. `88648761001843` - FUND UNIVERSIDADE DE CAXIAS DO SUL: R$ 601.917.339,34 em 24 registros.
3. `92898550000864` - FUND UNIVERSITARIA DE CARDIOLOGIA EM REC JUD: R$ 250.448.410,70 em 13 registros.
4. `87958583000146` - ESTADO DO RGS SECRETARIA DA SEGURANCA PUBLICA: R$ 237.240.394,19 em 125 registros.
5. `88648761000103` - FUND UNIVERSIDADE DE CAXIAS DO SUL: R$ 225.923.604,21 em 100 registros.

_Fonte local deste bloco: `processada/RS.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `TRANSITO, MUNICIPIO, SERVICOS, PRESENTE, SOCIAL, FISCALIZACAO, CONVENIO, COMO, ANIMAL, CARATER, CONTINUADO, ATRAVES`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `ASSOC RIOGRANDENSE EMPR ASS TEC EXT RURAL` - R$ 722.806.251,16 (ano 2011): Cooperacao, integracao e complementacao de esforcos entre o Estado e a EMATER/RS, visando promover o desenvolvimento rural, conjulgando melhoria de renda, qualificacao tecnologica e sustentabilidade social e ambiental, atreves da Assistencia Tecnica e Extensao Rural..
2. `ASSOC RIOGRANDENSE EMPR ASS TEC EXT RURAL` - R$ 704.900.000,00 (ano 2015): Cooperacao, integracao e complementacao de esforcos entre o Estado e a EMATER/RS, visando promover o desenvolvimento rural, conjulgando melhoria de renda, qualificacao tecnologica e sustentabilidade social e ambiental, atreves da Assistencia Tecnica e Extensao Rural..
3. `FUND UNIVERSIDADE DE CAXIAS DO SUL` - R$ 376.608.091,80 (ano 2020): Viabilizar o funcionamento do Hospital Geral de Caxias do Sul..
4. `FUND UNIVERSITARIA DE CARDIOLOGIA EM REC JUD` - R$ 231.836.494,61 (ano 2020): A finalidade do presente Convenio e a uniao de esforcos entre os participes para a realizacao de acoes necessarias para a manutencao do atendimento ambulatorial e adequacoes fisicas e estruturais necessarias a implantacao gradativa da parte hospitalar do HOSPITAL REGIONAL DE SANTA MARIA, com sede na Rua Florianopolis, sem numero, Parque Pinheiro Machado, Vila Rossi, no Municipio de Santa Maria/RS, com escopo de dar continuidade a ESTRUTURACAO, OPERACIONALIZACAO, ADMINISTRACAO E FUNCIONAMENTO do HOSPITAL, com vista a ampliacao da assistencia a saude, atraves do atendimento hospitalar, somente a usuarios do SUS, em conformidade com o Plano de Trabalho aprovado e constante no processo administr.
5. `FUND UNIVERSIDADE DE CAXIAS DO SUL` - R$ 180.438.274,00 (ano 2015): O presente Convenio tem por objeto a uniao de esforcos entre os participes, para viabilizar o funcionamento do Hospital Geral de Caxias do Sul, a fim de manter os servicos prestados ao SUS, de acordo com o Plano de Trabalho constante do expediente no 072750-20.00/15.1, independentemente de transcricao..

O maior registro individual da UF foi para `ASSOC RIOGRANDENSE EMPR ASS TEC EXT RURAL` no valor de R$ 722.806.251,16. O objeto associado foi: Cooperacao, integracao e complementacao de esforcos entre o Estado e a EMATER/RS, visando promover o desenvolvimento rural, conjulgando melhoria de renda, qualificacao tecnologica e sustentabilidade social e ambiental, atreves da Assistencia Tecnica e Extensao Rural..

_Fonte local deste bloco: `processada/RS.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2015` - R$ 953.062.421,11 em 1.757 registros.
2. `2020` - R$ 883.363.813,88 em 2.301 registros.
3. `2011` - R$ 864.554.363,09 em 1.984 registros.

Ultimos anos da serie:

- `2021`: R$ 786.637.435,36 em 2.562 registros, variacao n/d.
- `2022`: R$ 793.722.941,63 em 3.516 registros, variacao 0,9%.
- `2023`: R$ 671.414.839,00 em 3.164 registros, variacao -15,4%.
- `2024`: R$ 773.165.003,07 em 2.462 registros, variacao 15,2%.
- `2025`: R$ 489.797.578,87 em 1.810 registros, variacao -36,7%.

_Fonte local deste bloco: `processada/RS.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `PORTO ALEGRE` - R$ 3.336.529.288,00 em 2.501 registros.
2. `CAXIAS DO SUL` - R$ 907.282.809,05 em 510 registros.
3. `SANTA MARIA` - R$ 341.561.944,42 em 386 registros.
4. `PASSO FUNDO` - R$ 244.542.322,85 em 332 registros.
5. `ALVORADA` - R$ 182.541.784,79 em 120 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 100,0%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 71 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/RS.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/RS.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `ASSOC RIOGRANDENSE EMPR ASS TEC EXT RURAL` (89161475000173): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/89161475000173) - situacao ATIVA; municipio/UF PORTO ALEGRE/RS; porte DEMAIS; atividade principal Atividades de associacoes de defesa de direitos sociais.
- `FUND UNIVERSIDADE DE CAXIAS DO SUL` (88648761001843): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/88648761001843) - situacao ATIVA; municipio/UF CAXIAS DO SUL/RS; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `FUND UNIVERSITARIA DE CARDIOLOGIA EM REC JUD` (92898550000864): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/92898550000864) - situacao ATIVA; municipio/UF SANTA MARIA/RS; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `ESTADO DO RGS SECRETARIA DA SEGURANCA PUBLICA` (87958583000146): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/87958583000146) - situacao ATIVA; municipio/UF PORTO ALEGRE/RS; porte DEMAIS; atividade principal Administracao publica em geral.
- `FUND UNIVERSIDADE DE CAXIAS DO SUL` (88648761000103): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/88648761000103) - situacao ATIVA; municipio/UF CAXIAS DO SUL/RS; porte DEMAIS; atividade principal Educacao superior - graduacao.

### Investigacao complementar

- [ASSOC RIOGRANDENSE EMPR ASS TEC EXT RURAL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=89161475000173+ASSOC+RIOGRANDENSE+EMPR+ASS+TEC+EXT+RURAL+Rio+Grande+do+Sul+convenio+contrato+gestao)
- [FUND UNIVERSIDADE DE CAXIAS DO SUL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=88648761001843+FUND+UNIVERSIDADE+DE+CAXIAS+DO+SUL+Rio+Grande+do+Sul+convenio+contrato+gestao)
- [FUND UNIVERSITARIA DE CARDIOLOGIA EM REC JUD - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=92898550000864+FUND+UNIVERSITARIA+DE+CARDIOLOGIA+EM+REC+JUD+Rio+Grande+do+Sul+convenio+contrato+gestao)
- [ESTADO DO RGS SECRETARIA DA SEGURANCA PUBLICA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=87958583000146+ESTADO+DO+RGS+SECRETARIA+DA+SEGURANCA+PUBLICA+Rio+Grande+do+Sul+convenio+contrato+gestao)
- [FUND UNIVERSIDADE DE CAXIAS DO SUL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=88648761000103+FUND+UNIVERSIDADE+DE+CAXIAS+DO+SUL+Rio+Grande+do+Sul+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\RS.parquet` (614285 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\RS`.
- Exemplos de arquivos brutos estaduais: `Despesas do Estado-2014.zip`, `Despesas do Estado-2015.zip`, `Despesas do Estado-2016.zip`, `Despesas do Estado-2017.zip`, `Despesas do Estado-2018.zip`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_rs.py`.
- Observacao de trilha: Serie derivada dos zips historicos preservados em `bases_orcamento_geral/RS`.

### Capital (Porto Alegre)

- Parquet da capital consolidado: `E:\dados\capitais_processada\RS_PORTO_ALEGRE.parquet` (388 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Porto Alegre`.
- Exemplos de arquivos brutos da capital: `portoalegre_convenios.csv`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_porto_alegre.py`.
- Fontes oficiais registradas para a capital: [cnc.procempa.com.br/cnc/servlet/cnc.procempa.com.br.wwconvenios_portal](https://cnc.procempa.com.br/cnc/servlet/cnc.procempa.com.br.wwconvenios_portal).

## Conclusao

Rio Grande do Sul deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
