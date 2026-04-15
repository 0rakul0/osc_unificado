# Santa Catarina (SC)

## Visao geral

Santa Catarina soma 2.380 registros e R$ 1.473.046.529,75 em valor total. No ranking geral da base, a UF esta em 21o lugar por valor, 19o por quantidade de registros, 14o por ticket medio e 22o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e base mais distribuida. O ticket medio e de R$ 618.927,11, a mediana e de R$ 139.998,64 e os 5 maiores beneficiarios concentram 13,1% do valor total.

_Fonte local deste bloco: `processada/SC.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, SC aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Santa Catarina cresce principalmente por base mais distribuida. A participacao da UF no total nacional desta pasta e de 0,4%.

_Fonte local deste bloco: `processada/SC.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `83933192000116` - ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS DE FPOLIS (83.933.192/0001-16): R$ 65.520.239,19 em 17 registros.
2. `83784355000146` - ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS (83.784.355/0001-46): R$ 36.248.056,00 em 13 registros.
3. `03657851000108` - INSTITUTO ESCOLA DO TEATRO BOLSHOI NO BRASIL (03.657.851/0001-08): R$ 33.632.076,18 em 10 registros.
4. `00126152000135` - ASSOCIACAO DOS BOMBEIROS VOLUNTARIOS NO ESTADO DE S.C. (00.126.152/0001-35): R$ 29.904.742,21 em 7 registros.
5. `82656554000106` - ASSOC DE PAIS E AMIGOS DOS EXCEPCIONAIS DE BLUMENAU (82.656.554/0001-06): R$ 27.447.067,85 em 14 registros.

_Fonte local deste bloco: `processada/SC.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Nao ha objetos suficientes para aprofundar os objetivos do gasto.
O maior registro individual da UF foi para `ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS DE FPOLIS (83.933.192/0001-16)` no valor de R$ 23.966.374,76. O objeto associado foi: .

_Fonte local deste bloco: `processada/SC.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2024` - R$ 647.161.126,28 em 614 registros.
2. `2020` - R$ 305.434.702,10 em 224 registros.
3. `2022` - R$ 217.663.470,25 em 443 registros.

Ultimos anos da serie:

- `2021`: R$ 116.158.050,10 em 460 registros, variacao n/d.
- `2022`: R$ 217.663.470,25 em 443 registros, variacao 87,4%.
- `2023`: R$ 50.055.845,56 em 119 registros, variacao -77,0%.
- `2024`: R$ 647.161.126,28 em 614 registros, variacao 1192,9%.
- `2025`: R$ 88.294.057,90 em 397 registros, variacao -86,4%.

_Fonte local deste bloco: `processada/SC.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `FLORIANOPOLIS` - R$ 137.413.977,50 em 162 registros.
2. `JOINVILLE` - R$ 113.369.496,31 em 114 registros.
3. `CRICIUMA` - R$ 52.258.870,17 em 87 registros.
4. `JARAGUA DO SUL` - R$ 52.012.848,39 em 42 registros.
5. `CHAPECO` - R$ 42.749.930,71 em 67 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 100,0%, objeto em 0,0% e modalidade em 100,0%. Ha 0 registros negativos e 65 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/SC.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/SC.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS DE FPOLIS (83.933.192/0001-16)` (83933192000116): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/83933192000116) - situacao ATIVA; municipio/UF FLORIANOPOLIS/SC; porte DEMAIS; atividade principal Atividades de associacoes de defesa de direitos sociais.
- `ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS (83.784.355/0001-46)` (83784355000146): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/83784355000146) - situacao ATIVA; municipio/UF JARAGUA DO SUL/SC; porte DEMAIS; atividade principal Atividades de associacoes de defesa de direitos sociais.
- `INSTITUTO ESCOLA DO TEATRO BOLSHOI NO BRASIL (03.657.851/0001-08)` (03657851000108): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/03657851000108) - situacao ATIVA; municipio/UF JOINVILLE/SC; porte DEMAIS; atividade principal Educacao profissional de nivel tecnico.
- `ASSOCIACAO DOS BOMBEIROS VOLUNTARIOS NO ESTADO DE S.C. (00.126.152/0001-35)` (00126152000135): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/00126152000135) - situacao ATIVA; municipio/UF JOINVILLE/SC; porte DEMAIS; atividade principal Atividades de associacoes de defesa de direitos sociais.
- `ASSOC DE PAIS E AMIGOS DOS EXCEPCIONAIS DE BLUMENAU (82.656.554/0001-06)` (82656554000106): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/82656554000106) - situacao ATIVA; municipio/UF BLUMENAU/SC; porte DEMAIS; atividade principal Atividades de associacoes de defesa de direitos sociais.

### Investigacao complementar

- [ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS DE FPOLIS (83.933.192/0001-16) - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=83933192000116+ASSOCIACAO+DE+PAIS+E+AMIGOS+DOS+EXCEPCIONAIS+DE+FPOLIS+%2883.933.192%2F0001-16%29+Santa+Catarina+convenio+contrato+gestao)
- [ASSOCIACAO DE PAIS E AMIGOS DOS EXCEPCIONAIS (83.784.355/0001-46) - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=83784355000146+ASSOCIACAO+DE+PAIS+E+AMIGOS+DOS+EXCEPCIONAIS+%2883.784.355%2F0001-46%29+Santa+Catarina+convenio+contrato+gestao)
- [INSTITUTO ESCOLA DO TEATRO BOLSHOI NO BRASIL (03.657.851/0001-08) - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=03657851000108+INSTITUTO+ESCOLA+DO+TEATRO+BOLSHOI+NO+BRASIL+%2803.657.851%2F0001-08%29+Santa+Catarina+convenio+contrato+gestao)
- [ASSOCIACAO DOS BOMBEIROS VOLUNTARIOS NO ESTADO DE S.C. (00.126.152/0001-35) - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=00126152000135+ASSOCIACAO+DOS+BOMBEIROS+VOLUNTARIOS+NO+ESTADO+DE+S.C.+%2800.126.152%2F0001-35%29+Santa+Catarina+convenio+contrato+gestao)
- [ASSOC DE PAIS E AMIGOS DOS EXCEPCIONAIS DE BLUMENAU (82.656.554/0001-06) - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=82656554000106+ASSOC+DE+PAIS+E+AMIGOS+DOS+EXCEPCIONAIS+DE+BLUMENAU+%2882.656.554%2F0001-06%29+Santa+Catarina+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\SC.parquet` (5372 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\SC`.
- Exemplos de arquivos brutos estaduais: `sc_transferencias.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_sc.py`, `utils/orcamento_geral/baixar_orcamento_geral_sc.py`.
- Fontes oficiais registradas para o estado: [consultas.sctransferencias.cge.sc.gov.br/](https://consultas.sctransferencias.cge.sc.gov.br/), [sctransf-api.prod.okd4.ciasc.sc.gov.br/csv/transferencias](https://sctransf-api.prod.okd4.ciasc.sc.gov.br/csv/transferencias).

### Capital (Florianopolis)

- Parquet da capital consolidado: `E:\dados\capitais_processada\SC_FLORIANOPOLIS.parquet` (25 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Florianopolis`.
- Exemplos de arquivos brutos da capital: `florianopolis_convenios_enriquecido.json`, `florianopolis_convenios_lista.json`, `florianopolis_convenios_resumo.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_florianopolis.py`.
- Fontes oficiais registradas para a capital: [transparencia.e-publica.net/epublica-portal/#/florianopolis/portal/despesa/convenioRepassadoTable?entidade=2002](https://transparencia.e-publica.net/epublica-portal/#/florianopolis/portal/despesa/convenioRepassadoTable?entidade=2002).

## Conclusao

Santa Catarina deve ser lido como uma UF puxada por base mais distribuida. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
