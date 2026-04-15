# Tocantins (TO)

## Visao geral

Tocantins soma 2.570 registros e R$ 984.194.205,75 em valor total. No ranking geral da base, a UF esta em 22o lugar por valor, 18o por quantidade de registros, 17o por ticket medio e 21o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e base mais distribuida. O ticket medio e de R$ 382.954,94, a mediana e de R$ 199.940,89 e os 5 maiores beneficiarios concentram 16,5% do valor total.

_Fonte local deste bloco: `processada/TO.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, TO aparece entre as UFs lideres por valor em `PR, SP, PB, MS, SE`, por volume em `SE, PB, MG, PR, RS`, por ticket medio em `PE, RR, RJ, AM, AC` e por concentracao em `AC, RR, CE, PE, AM`.

Na pratica, isso indica que Tocantins cresce principalmente por base mais distribuida. A participacao da UF no total nacional desta pasta e de 0,3%.

_Fonte local deste bloco: `processada/TO.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Principais entidades

1. `23453830000170` - INSTITUTO NACIONAL DE DESENVOLVIMENTO SOCIAL E HUMANO - INDSH: R$ 72.950.215,39 em 2 registros.
2. `25092230000159` - FEDERACAO DA AGRICULTURA E PECUARIA DO ESTADO DO TOCANTINS/FAET: R$ 41.533.214,75 em 107 registros.
3. `18311315000115` - INSTITUTO CULTURAL SABER E ARTE: R$ 20.648.711,38 em 122 registros.
4. `10436545000107` - INSTITUTO MUSICAL ARTISTICO TOCANTINENSE  MAT: R$ 14.152.529,00 em 72 registros.
5. `06343763000111` - FUNDACAO DE APOIO CIENTIFICO E TECNOLOGICO DO TOCANTINS - FAPTO: R$ 12.616.555,93 em 69 registros.

_Fonte local deste bloco: `processada/TO.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `REALIZACAO, MUNICIPIO, TOCANTINS, AQUISICAO, PRAIA, APOIAR, ANIVERSARIO, TEMPORADA, CONTRATACAO, SHOW, CONSTRUCAO, 2023`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `INSTITUTO NACIONAL DE DESENVOLVIMENTO SOCIAL E HUMANO - INDSH` - R$ 72.000.000,00 (ano 2025): GERENCIAMENTO, OPERACIONALIZACAO E EXECUCAO DAS ACOES DO CETEA COMPREENDENDO ATIVIDADES DE SAUDE AO QUE SE REFERE AOS DECRETOS E NORMAS VIGENTES DA REDE DE CUIDADOS A PESSOA COM DEFCIENCIA.
2. `FEDERACAO DA AGRICULTURA E PECUARIA DO ESTADO DO TOCANTINS/FAET` - R$ 6.406.550,00 (ano 2024): CONTRATACAO DE ESTRUTURA PARA APOIO A REALIZACAO DAS EXPOSICOES AGROPECUARIAS DO ESTADO DO TOCANTINS.
3. `FEDERACAO DA AGRICULTURA E PECUARIA DO ESTADO DO TOCANTINS/FAET` - R$ 4.664.753,75 (ano 2025): EXPOSICOES AGROPECUARIAS DO TOCANTINS 2025.
4. `INSTITUTO IDESP` - R$ 4.150.790,00 (ano 2024): ATENDIMENTO DE PACIENTES NOS MUNICIPIOS INDICADOS PELOS PARLAMENTARES A FIM DE EXECUCAO DE CONSULTAS OFTALMOLOGICAS E ENCAMINHAMENTO DE PACIENTES PARA REALIZACAO DE CIRURGIAS DE FACOEMULSIFICACAO COM IMPLANTE DE LENTE DOBRAVEL (CATARATA) E TRATAMENTO CIRURGICO DE PTERIGIO, CONFORME PLANO DE TRABALHO DESCRITO NESTE PROJETO..
5. `SERVICO NACIONAL DE APRENDIZAGEM INDUSTRIAL DO ESTADO DO TOCANTINS` - R$ 4.123.210,00 (ano 2025): TOCANTINS + PROFISSIONALIZACAO.

O maior registro individual da UF foi para `INSTITUTO NACIONAL DE DESENVOLVIMENTO SOCIAL E HUMANO - INDSH` no valor de R$ 72.000.000,00. O objeto associado foi: GERENCIAMENTO, OPERACIONALIZACAO E EXECUCAO DAS ACOES DO CETEA COMPREENDENDO ATIVIDADES DE SAUDE AO QUE SE REFERE AOS DECRETOS E NORMAS VIGENTES DA REDE DE CUIDADOS A PESSOA COM DEFCIENCIA.

_Fonte local deste bloco: `processada/TO.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2025` - R$ 248.386.694,03 em 487 registros.
2. `2022` - R$ 222.448.471,25 em 571 registros.
3. `2021` - R$ 211.588.701,70 em 426 registros.

Ultimos anos da serie:

- `2021`: R$ 211.588.701,70 em 426 registros, variacao n/d.
- `2022`: R$ 222.448.471,25 em 571 registros, variacao 5,1%.
- `2023`: R$ 120.224.601,89 em 511 registros, variacao -46,0%.
- `2024`: R$ 159.242.331,33 em 484 registros, variacao 32,5%.
- `2025`: R$ 248.386.694,03 em 487 registros, variacao 56,0%.

_Fonte local deste bloco: `processada/TO.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 7 registros marcados como duplicado aparente.

_Fonte local deste bloco: `processada/TO.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `processada/TO.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `INSTITUTO NACIONAL DE DESENVOLVIMENTO SOCIAL E HUMANO - INDSH` (23453830000170): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/23453830000170) - situacao ATIVA; municipio/UF PEDRO LEOPOLDO/MG; porte DEMAIS; atividade principal Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgencias.
- `FEDERACAO DA AGRICULTURA E PECUARIA DO ESTADO DO TOCANTINS/FAET` (25092230000159): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/25092230000159) - situacao ATIVA; municipio/UF PALMAS/TO; porte DEMAIS; atividade principal Seguridade social obrigatoria.
- `INSTITUTO CULTURAL SABER E ARTE` (18311315000115): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/18311315000115) - situacao ATIVA; municipio/UF PORTO NACIONAL/TO; porte DEMAIS; atividade principal Atividades de organizacoes associativas ligadas a cultura e a arte.
- `INSTITUTO MUSICAL ARTISTICO TOCANTINENSE  MAT` (10436545000107): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/10436545000107) - situacao ATIVA; municipio/UF ARAGUAINA/TO; porte DEMAIS; atividade principal Atividades associativas nao especificadas anteriormente.
- `FUNDACAO DE APOIO CIENTIFICO E TECNOLOGICO DO TOCANTINS - FAPTO` (06343763000111): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/06343763000111) - situacao ATIVA; municipio/UF PALMAS/TO; porte DEMAIS; atividade principal Outras atividades de ensino nao especificadas anteriormente.

### Investigacao complementar

- [INSTITUTO NACIONAL DE DESENVOLVIMENTO SOCIAL E HUMANO - INDSH - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=23453830000170+INSTITUTO+NACIONAL+DE+DESENVOLVIMENTO+SOCIAL+E+HUMANO+-+INDSH+Tocantins+convenio+contrato+gestao)
- [FEDERACAO DA AGRICULTURA E PECUARIA DO ESTADO DO TOCANTINS/FAET - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=25092230000159+FEDERACAO+DA+AGRICULTURA+E+PECUARIA+DO+ESTADO+DO+TOCANTINS%2FFAET+Tocantins+convenio+contrato+gestao)
- [INSTITUTO CULTURAL SABER E ARTE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=18311315000115+INSTITUTO+CULTURAL+SABER+E+ARTE+Tocantins+convenio+contrato+gestao)
- [INSTITUTO MUSICAL ARTISTICO TOCANTINENSE  MAT - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=10436545000107+INSTITUTO+MUSICAL+ARTISTICO+TOCANTINENSE++MAT+Tocantins+convenio+contrato+gestao)
- [FUNDACAO DE APOIO CIENTIFICO E TECNOLOGICO DO TOCANTINS - FAPTO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=06343763000111+FUNDACAO+DE+APOIO+CIENTIFICO+E+TECNOLOGICO+DO+TOCANTINS+-+FAPTO+Tocantins+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\TO.parquet` (791 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\TO`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_to.py`.
- Observacao de trilha: Serie consolidada a partir da planilha legada `bases_convenios/TO/convenios_completo.xlsx`.

### Capital (Palmas)

- Parquet da capital consolidado: `E:\dados\capitais_processada\TO_PALMAS.parquet` (4 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Palmas`.
- Exemplos de arquivos brutos da capital: `palmas_contratos_brutos.json`, `palmas_convenios_osc.json`, `palmas_convenios_resumo.json`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`, `utils/orcamento_geral/baixar_convenios_capital_palmas.py`.
- Fontes oficiais registradas para a capital: [prodata.palmas.to.gov.br/sig/app.html#/transparencia/contratos/](https://prodata.palmas.to.gov.br/sig/app.html#/transparencia/contratos/), [prodata.palmas.to.gov.br/sig/rest/transparenciaContratosController/getContratos](https://prodata.palmas.to.gov.br/sig/rest/transparenciaContratosController/getContratos).

## Conclusao

Tocantins deve ser lido como uma UF puxada por base mais distribuida. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
