# Goias (GO)

## Visao geral

Goias soma 1.676 registros e R$ 374.908.527,86 em valor total. No ranking geral da base, a UF esta em 24o lugar por valor, 20o por quantidade de registros, 23o por ticket medio e 7o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e concentracao. O ticket medio e de R$ 223.692,44, a mediana e de R$ 0,00 e os 5 maiores beneficiarios concentram 49,4% do valor total.

_Fonte local deste bloco: `processada/GO.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, GO aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Goias cresce principalmente por concentracao. A participacao da UF no total nacional desta pasta e de 0,1%.

_Fonte local deste bloco: `processada/GO.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- Na fonte bruta de Goias, o campo `VALOR_TOTAL` fica zerado na maior parte dos registros ate 2016. O parquet manteve esse mesmo campo para preservar aderencia ao dado publicado, entao os totais financeiros de 2008 a 2016 devem ser lidos como subestimados pela propria fonte.
- Nos arquivos brutos do `GO`, os campos com melhor cobertura financeira sao `VALOR_PLANO_TOTAL` e `VALOR_CONCEDENTE`, mas eles nao foram promovidos a `valor_total` para evitar trocar a definicao oficial que ja vinha sendo trabalhada no projeto.
- 82,2% dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros.

_Fonte local deste bloco: `processada/GO.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `01285170000122` - COMPANHIA DE DESENVOLVIMENTO ECONOMICO DE GOIAS: R$ 122.074.582,04 em 14 registros.
2. `01181585000156` - PIRES DO RIO: R$ 19.268.991,80 em 2 registros.
3. `01219807000182` - URUACU: R$ 17.464.808,40 em 4 registros.
4. `01165729000180` - JATAI: R$ 15.203.449,62 em 6 registros.
5. `01169416000109` - LUZIANIA: R$ 11.310.932,62 em 1 registros.

_Fonte local deste bloco: `processada/GO.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `UNIDADES, HABITACIONAIS, REFORMA, CONSTRUCAO, ASFALTICA, AQUISICAO, MASSA, FORNECIMENTO, PAVIMENTACAO, PRACA, TIPO, PUBLICO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `COMPANHIA DE DESENVOLVIMENTO ECONOMICO DE GOIAS` - R$ 80.236.559,25 (ano 2018): Execucao de Obras de Infraestrutura de Pavimentacao e Obras de Arte na GO 108: Guarani/Terra Ronca.
2. `PIRES DO RIO` - R$ 19.268.991,80 (ano 2018): Recuperacao e Conservacao de Pavimentacao Asfaltica de Pires do Rio.
3. `LUZIANIA` - R$ 11.310.932,62 (ano 2017): PAVIMENTACAO ASFALTICA NOS BAIRROS DE LUZIANIA.
4. `JATAI` - R$ 10.830.051,84 (ano 2017): RECAPEAMENTO COM CBUQ - CONCRETO BETUMINOSO USINADO A QUENTE E LAMA ASFALTICA GROSSA.
5. `COMPANHIA DE DESENVOLVIMENTO ECONOMICO DE GOIAS` - R$ 10.269.734,26 (ano 2018): Reconstrucao e Recapeamento de Vias Urbanas do Municipio de Minacu, neste Estado.

O maior registro individual da UF foi para `COMPANHIA DE DESENVOLVIMENTO ECONOMICO DE GOIAS` no valor de R$ 80.236.559,25. O objeto associado foi: Execucao de Obras de Infraestrutura de Pavimentacao e Obras de Arte na GO 108: Guarani/Terra Ronca.

_Fonte local deste bloco: `processada/GO.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2018` - R$ 211.516.000,82 em 233 registros.
2. `2017` - R$ 163.392.527,04 em 93 registros.
3. `2010` - R$ 0,00 em 1 registros.

Ultimos anos da serie:

- `2014`: R$ 0,00 em 646 registros, variacao n/d.
- `2015`: R$ 0,00 em 83 registros, variacao n/d.
- `2016`: R$ 0,00 em 184 registros, variacao n/d.
- `2017`: R$ 163.392.527,04 em 93 registros, variacao inf%.
- `2018`: R$ 211.516.000,82 em 233 registros, variacao 29,5%.

_Fonte local deste bloco: `processada/GO.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 99,9% e modalidade em 100,0%. Ha 0 registros negativos e 209 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/GO.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/GO.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `COMPANHIA DE DESENVOLVIMENTO ECONOMICO DE GOIAS` (01285170000122): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01285170000122) - status da consulta 429.
- `PIRES DO RIO` (01181585000156): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01181585000156) - status da consulta 429.
- `URUACU` (01219807000182): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01219807000182) - status da consulta 429.
- `JATAI` (01165729000180): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01165729000180) - status da consulta 429.
- `LUZIANIA` (01169416000109): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/01169416000109) - status da consulta 429.

### Investigacao complementar

- [COMPANHIA DE DESENVOLVIMENTO ECONOMICO DE GOIAS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01285170000122+COMPANHIA+DE+DESENVOLVIMENTO+ECONOMICO+DE+GOIAS+Goias+convenio+contrato+gestao)
- [PIRES DO RIO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01181585000156+PIRES+DO+RIO+Goias+convenio+contrato+gestao)
- [URUACU - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01219807000182+URUACU+Goias+convenio+contrato+gestao)
- [JATAI - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01165729000180+JATAI+Goias+convenio+contrato+gestao)
- [LUZIANIA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=01169416000109+LUZIANIA+Goias+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\GO.parquet` (16371 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\GO`.
- Exemplos de arquivos brutos estaduais: `Documento sem título.docx`, `GO_dados_gerais_2003_2026.xlsx`, `transparencia_eof_gastos_gov_transf_vol.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_go.py`.
- Observacao de trilha: Serie consolidada a partir de planilha historica local preservada em `bases_convenios/GO`.

### Capital (Goiania)

- Parquet da capital consolidado: `E:\dados\capitais_processada\GO_GOIANIA.parquet` (1048 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Goiania`.
- Exemplos de arquivos brutos da capital: `goiania_convenios_2016.csv`, `goiania_convenios_2017.csv`, `goiania_convenios_2018.csv`, `goiania_convenios_2019.csv`, `goiania_convenios_2020.csv`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_goiania.py`.
- Fontes oficiais registradas para a capital: [www10.goiania.go.gov.br/transweb/Portal_DespesasTransferencias.aspx](https://www10.goiania.go.gov.br/transweb/Portal_DespesasTransferencias.aspx).

## Conclusao

Goias deve ser lido como uma UF puxada por concentracao. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
