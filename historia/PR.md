# Parana (PR)

## Visao geral

Parana soma 66.042 registros e R$ 50.316.457.171,81 em valor total. No ranking geral da base, a UF esta em 1o lugar por valor, 4o por quantidade de registros, 12o por ticket medio e 26o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e volume de dados. O ticket medio e de R$ 761.885,73, a mediana e de R$ 209.978,50 e os 5 maiores beneficiarios concentram 6,6% do valor total.

_Fonte local deste bloco: `processada/PR.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, PR aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Parana cresce principalmente por volume de dados. A participacao da UF no total nacional desta pasta e de 14,3%.

_Fonte local deste bloco: `processada/PR.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- No bruto do Parana, a tabela relacional de entidade identificava o concedente, e nao o tomador. O parquet atual passou a usar o `tomador` como beneficiario e reteve apenas linhas com CNPJ recuperavel no enriquecimento.

_Fonte local deste bloco: `processada/PR.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `77816510000166` - MUNICIPIO DE FRANCISCO BELTRAO: R$ 917.094.410,61 em 337 registros.
2. `76208867000107` - MUNICIPIO DE CASCAVEL: R$ 652.183.492,49 em 330 registros.
3. `76105543000135` - MUNICIPIO DE SAO JOSE DOS PINHAIS: R$ 621.553.132,99 em 138 registros.
4. `00445188000181` - CONSORCIO INTERMUNICIPAL DE SAUDE DO MEDIO PARANAPANEMA: R$ 569.813.033,43 em 52 registros.
5. `76175884000187` - MUNICIPIO DE PONTA GROSSA: R$ 537.005.300,33 em 223 registros.

_Fonte local deste bloco: `processada/PR.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `PLANO, AQUISICAO, CONVENIO, TRABALHO, CONFORME, DESTE, PROGRAMA, RECURSOS, CONSTITUI, ACOES, DESENVOLVIMENTO, IMPLEMENTACAO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `MUNICIPIO DE FAZENDA RIO GRANDE` - R$ 89.000.000,00 (ano 2025): CONSTRUCAO DE VIADUTOS SOBRE A BR-116.
2. `MUNICIPIO DE FAZENDA RIO GRANDE` - R$ 89.000.000,00 (ano 2025): CONSTRUCAO DE VIADUTOS SOBRE A BR-116.
3. `FUNDACAO DE APOIO AO DESENVOLVIMENTO INSTITUCIONAL, CIENTIFICO E TECNOLOGICO DA UNIVERSIDADE ESTADUAL DE PONTA GROSSA - FAUEPG` - R$ 62.977.938,95 (ano 2025): O presente Convenio visa a realizacao conjunta de atividades de Pesquisa,Desenvolvimento e Inovacao (PD&I) entre os PARTICIPES, em regime de mutuacolaboracao, tendo por objeto a execucao do projeto intitulado Anel de Conectividade paraPesquisa e Inovacao do Parana, protocolo no 24.025.617-7.
4. `FUNDACAO DE APOIO AO DESENVOLVIMENTO INSTITUCIONAL, CIENTIFICO E TECNOLOGICO DA UNIVERSIDADE ESTADUAL DE PONTA GROSSA - FAUEPG` - R$ 62.977.938,95 (ano 2025): O presente Convenio visa a realizacao conjunta de atividades de Pesquisa,Desenvolvimento e Inovacao (PD&I) entre os PARTICIPES, em regime de mutuacolaboracao, tendo por objeto a execucao do projeto intitulado Anel de Conectividade paraPesquisa e Inovacao do Parana, protocolo no 24.025.617-7.
5. `MUNICIPIO DE MARILENA` - R$ 60.725.448,51 (ano 2024): falta EMPENHO  Execucao de servicos de recape asfaltico e em bloco sextavado ligando a Sede do Municipio de Marilena ao Porto Maringa, Distrito Ipanema..

O maior registro individual da UF foi para `MUNICIPIO DE FAZENDA RIO GRANDE` no valor de R$ 89.000.000,00. O objeto associado foi: CONSTRUCAO DE VIADUTOS SOBRE A BR-116.

_Fonte local deste bloco: `processada/PR.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2023` - R$ 8.542.721.077,36 em 4.193 registros.
2. `2022` - R$ 7.050.499.799,23 em 7.593 registros.
3. `2025` - R$ 6.703.156.360,28 em 4.375 registros.

Ultimos anos da serie:

- `2021`: R$ 3.444.059.184,88 em 4.114 registros, variacao n/d.
- `2022`: R$ 7.050.499.799,23 em 7.593 registros, variacao 104,7%.
- `2023`: R$ 8.542.721.077,36 em 4.193 registros, variacao 21,2%.
- `2024`: R$ 6.154.013.954,38 em 5.243 registros, variacao -28,0%.
- `2025`: R$ 6.703.156.360,28 em 4.375 registros, variacao 8,9%.

_Fonte local deste bloco: `processada/PR.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

Municipios com maior valor acumulado no recorte:

1. `LONDRINA` - R$ 1.621.570.878,27 em 628 registros.
2. `CASCAVEL` - R$ 1.369.200.245,91 em 999 registros.
3. `CURITIBA` - R$ 1.349.853.362,60 em 790 registros.
4. `PONTA GROSSA` - R$ 1.275.075.599,35 em 2.482 registros.
5. `MARINGA` - R$ 1.233.319.234,61 em 4.889 registros.

Cobertura observada: CNPJ valido em 100,0%, municipio em 99,9%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 64.014 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/PR.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/PR.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `MUNICIPIO DE FRANCISCO BELTRAO` (77816510000166): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/77816510000166) - situacao ATIVA; municipio/UF FRANCISCO BELTRAO/PR; porte DEMAIS; atividade principal Administracao publica em geral.
- `MUNICIPIO DE CASCAVEL` (76208867000107): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/76208867000107) - situacao ATIVA; municipio/UF CASCAVEL/PR; porte DEMAIS; atividade principal Administracao publica em geral.
- `MUNICIPIO DE SAO JOSE DOS PINHAIS` (76105543000135): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/76105543000135) - situacao ATIVA; municipio/UF SAO JOSE DOS PINHAIS/PR; porte DEMAIS; atividade principal Administracao publica em geral.
- `CONSORCIO INTERMUNICIPAL DE SAUDE DO MEDIO PARANAPANEMA` (00445188000181): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/00445188000181) - situacao ATIVA; municipio/UF LONDRINA/PR; porte DEMAIS; atividade principal Outras atividades de atencao a saude humana nao especificadas anteriormente.
- `MUNICIPIO DE PONTA GROSSA` (76175884000187): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/76175884000187) - situacao ATIVA; municipio/UF PONTA GROSSA/PR; porte DEMAIS; atividade principal Administracao publica em geral.

### Investigacao complementar

- [MUNICIPIO DE FRANCISCO BELTRAO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=77816510000166+MUNICIPIO+DE+FRANCISCO+BELTRAO+Parana+convenio+contrato+gestao)
- [MUNICIPIO DE CASCAVEL - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=76208867000107+MUNICIPIO+DE+CASCAVEL+Parana+convenio+contrato+gestao)
- [MUNICIPIO DE SAO JOSE DOS PINHAIS - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=76105543000135+MUNICIPIO+DE+SAO+JOSE+DOS+PINHAIS+Parana+convenio+contrato+gestao)
- [CONSORCIO INTERMUNICIPAL DE SAUDE DO MEDIO PARANAPANEMA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=00445188000181+CONSORCIO+INTERMUNICIPAL+DE+SAUDE+DO+MEDIO+PARANAPANEMA+Parana+convenio+contrato+gestao)
- [MUNICIPIO DE PONTA GROSSA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=76175884000187+MUNICIPIO+DE+PONTA+GROSSA+Parana+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\PR.parquet` (60572 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\PR`.
- Exemplos de arquivos brutos estaduais: `DESPESA_PAGAMENTO-2009.zip`, `DESPESA_PAGAMENTO-2010.zip`, `DESPESA_PAGAMENTO-2011.zip`, `DESPESA_PAGAMENTO-2012.zip`, `DESPESA_PAGAMENTO-2013.zip`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_pr.py`.
- Observacao de trilha: Serie derivada dos zips historicos preservados em `bases_orcamento_geral/PR`.

### Capital (Curitiba)

- Parquet da capital consolidado: `E:\dados\capitais_processada\PR_CURITIBA.parquet` (360 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Curitiba`.
- Exemplos de arquivos brutos da capital: `curitiba_convenios.csv`, `curitiba_convenios.html`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_curitiba.py`.
- Fontes oficiais registradas para a capital: [www.transparencia.curitiba.pr.gov.br/conteudo/convenios.aspx](https://www.transparencia.curitiba.pr.gov.br/conteudo/convenios.aspx).

## Conclusao

Parana deve ser lido como uma UF puxada por volume de dados. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
