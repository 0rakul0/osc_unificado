# Pernambuco (PE)

## Atualizacao de orcamento geral

- Pernambuco foi investigado na trilha de orcamento geral, mas ainda nao foi fechado como parquet canonico.
- A base local em `E:\dados\bases_orcamento_geral\PE\dados_gerais` nao parece uma extracao estadual completa: o recorte encontrado era muito pequeno para representar a serie de despesas do estado.
- Por isso o trabalho recente ficou apenas na triagem tecnica do PE, enquanto o fluxo operacional seguiu para MT. O proximo passo de PE depende de baixar uma fonte oficial mais rica antes de consolidar `valor_total`, `data` e `cnpj` com seguranca.

## Visao geral

Pernambuco soma 65 registros e R$ 5.589.738.467,31 em valor total. No ranking geral da base, a UF esta em 14o lugar por valor, 26o por quantidade de registros, 1o por ticket medio e 4o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e ticket medio e concentracao. O ticket medio e de R$ 85.995.976,42, a mediana e de R$ 29.024.223,00 e os 5 maiores beneficiarios concentram 77,5% do valor total.

_Fonte local deste bloco: `processada/PE.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, PE aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Pernambuco cresce principalmente por ticket medio e concentracao. A participacao da UF no total nacional desta pasta e de 1,6%.

_Fonte local deste bloco: `processada/PE.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `09039744000860` - FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR: R$ 655.633.181,10 em 1 registros.
2. `10988301000633` - INSTITUTO DE MEDICINA INTEGRAL PROFESSOR FERNANDO FIGUEIRA - IMIP: R$ 515.783.454,99 em 1 registros.
3. `09039744000780` - FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR: R$ 514.719.729,60 em 1 registros.
4. `09039744000275` - FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR: R$ 514.187.381,68 em 1 registros.
5. `09767633000447` - FUNDACAO MANOEL DA SILVA ALMEIDA: R$ 269.864.207,13 em 1 registros.

_Fonte local deste bloco: `processada/PE.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `SERVICOS, EXECUCAO, ACOES, OPERACIONALIZACAO, SAUDE, PRESTACAO, PERNAMBUCO, HOSPITAL, PROGRAMA, UPAE, UNIVERSITARIOS, GESTAO`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR` - R$ 655.633.181,10 (ano 2010): OPERACIONALIZACAO E EXECUCAO DAS ACOES E SERVICOS DE SAUDE DO HOSPITAL DOM HELDER.
2. `INSTITUTO DE MEDICINA INTEGRAL PROFESSOR FERNANDO FIGUEIRA - IMIP` - R$ 515.783.454,99 (ano 2011): OPERACIONALIZACAO E EXECUCAO DAS ACOES E SERVICOSDE SAUDE DO HOSPITAL METROPOLITANO OESTE PELOPIDAS SILVEIRA.
3. `FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR` - R$ 514.719.729,60 (ano 2010): OPERACIONALIZACAO E EXECUCAO DAS ACOES E SERVICOS DE SAUDE DO HOSPITAL DOM MALAN.
4. `FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR` - R$ 514.187.381,68 (ano 2009): OPERACIONALIZACAO E EXECUCAO DAS ACOES E SERVICOS DE SAUDE DO HOSPITAL MIGUEL ARRAES.
5. `FUNDACAO MANOEL DA SILVA ALMEIDA` - R$ 269.864.207,13 (ano 2011): OPERACIONALIZACAO E EXECUCAO DAS ACOES E SERVICOS DE SAUDE DO HOSPITAL SILVO MAGALHAES.

O maior registro individual da UF foi para `FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR` no valor de R$ 655.633.181,10. O objeto associado foi: OPERACIONALIZACAO E EXECUCAO DAS ACOES E SERVICOS DE SAUDE DO HOSPITAL DOM HELDER.

_Fonte local deste bloco: `processada/PE.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2010` - R$ 2.072.394.588,92 em 11 registros.
2. `2011` - R$ 1.197.225.975,43 em 7 registros.
3. `2009` - R$ 836.326.266,50 em 4 registros.

Ultimos anos da serie:

- `2013`: R$ 336.347.658,31 em 5 registros, variacao n/d.
- `2014`: R$ 458.746.776,07 em 13 registros, variacao 36,4%.
- `2015`: R$ 118.276.256,46 em 7 registros, variacao -74,2%.
- `2016`: R$ 200.270.987,76 em 7 registros, variacao 69,3%.
- `2017`: R$ 5.979.046,02 em 2 registros, variacao -97,0%.

_Fonte local deste bloco: `processada/PE.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 0 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/PE.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/PE.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR` (09039744000860): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/09039744000860) - status da consulta 429.
- `INSTITUTO DE MEDICINA INTEGRAL PROFESSOR FERNANDO FIGUEIRA - IMIP` (10988301000633): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/10988301000633) - status da consulta 429.
- `FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR` (09039744000780): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/09039744000780) - status da consulta 429.
- `FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR` (09039744000275): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/09039744000275) - status da consulta 429.
- `FUNDACAO MANOEL DA SILVA ALMEIDA` (09767633000447): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/09767633000447) - status da consulta 429.

### Investigacao complementar

- [FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=09039744000860+FUNDACAO+PROFESSOR+MARTINIANO+FERNANDES++IMIP+HOSPITALAR+Pernambuco+convenio+contrato+gestao)
- [INSTITUTO DE MEDICINA INTEGRAL PROFESSOR FERNANDO FIGUEIRA - IMIP - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=10988301000633+INSTITUTO+DE+MEDICINA+INTEGRAL+PROFESSOR+FERNANDO+FIGUEIRA+-+IMIP+Pernambuco+convenio+contrato+gestao)
- [FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=09039744000780+FUNDACAO+PROFESSOR+MARTINIANO+FERNANDES++IMIP+HOSPITALAR+Pernambuco+convenio+contrato+gestao)
- [FUNDACAO PROFESSOR MARTINIANO FERNANDES  IMIP HOSPITALAR - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=09039744000275+FUNDACAO+PROFESSOR+MARTINIANO+FERNANDES++IMIP+HOSPITALAR+Pernambuco+convenio+contrato+gestao)
- [FUNDACAO MANOEL DA SILVA ALMEIDA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=09767633000447+FUNDACAO+MANOEL+DA+SILVA+ALMEIDA+Pernambuco+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\PE.parquet` (661 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\PE`.
- Exemplos de arquivos brutos estaduais: `Documento sem título.docx`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_pe.py`.
- Observacao de trilha: Serie montada a partir do acervo local preservado em `bases_orcamento_geral/PE`.

### Capital (Recife)

- Parquet da capital consolidado: `E:\dados\capitais_processada\PE_RECIFE.parquet` (4 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Recife`.
- Exemplos de arquivos brutos da capital: `recife_aditivos_contratos_gestao_2023.csv`, `recife_contratos_gestao_2023.csv`, `recife_manifest.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_recife.py`.
- Fontes oficiais registradas para a capital: [dados.recife.pe.gov.br/](https://dados.recife.pe.gov.br/), [dados.recife.pe.gov.br/tr/dataset/contratos-de-gestao](https://dados.recife.pe.gov.br/tr/dataset/contratos-de-gestao).

## Conclusao

Pernambuco deve ser lido como uma UF puxada por ticket medio e concentracao. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
