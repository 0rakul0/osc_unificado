# Ceara (CE)

## Atualizacao de orcamento geral

- Foi criado o parser `processar_orcamento_geral_ce.py` a partir da compilacao dos contratos e do cruzamento com a base de convenios sem fins lucrativos.
- A saida canonica atual esta em `E:\dados\orcamento_geral_processada\CE.parquet`, com 4.802 linhas, 428 CNPJs e serie de 2014 a 2026.
- O `valor_total` usa `Valor pago`, com fallback para `Valor atualizado` quando o pagamento vier vazio.

## Visao geral

Ceara soma 4.802 registros e R$ 13.488.770.700,85 em valor total. No ranking geral da base, a UF esta em 13o lugar por valor, 14o por quantidade de registros, 7o por ticket medio e 4o por concentracao dos 5 maiores beneficiarios.

O perfil dominante da UF e ticket medio e concentracao. O ticket medio e de R$ 2.808.990,15, a mediana e de R$ 26.776,00 e os 5 maiores beneficiarios concentram 75,5% do valor total.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\CE.parquet`; campos e agregacoes usados: `valor_total`, `nome_osc`, `cnpj`, `ano`, agregacoes por UF, ranks e shares dos maiores beneficiarios._

## Leitura narrativa

Comparando com o conjunto nacional, CE aparece entre as UFs lideres por valor em `MT, PB, PA, AL, BA`, por volume em `MT, PB, PA, ES, SE`, por ticket medio em `PE, BA, RR, RJ, AM` e por concentracao em `AC, RR, PE, CE, AM`.

Na pratica, isso indica que Ceara cresce principalmente por ticket medio e concentracao. A participacao da UF no total nacional desta pasta e de 0,2%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\CE.parquet`; campos e agregacoes usados: benchmark nacional entre UFs, com comparacao de `valor_num`, `registros`, `ticket_medio` e `top5_share_pct`._

## Ressalvas da fonte

- 10,3% dos registros desta UF tem `valor_total = 0` no parquet. Isso sugere que a fonte mistura instrumentos sem valor informado ou sem execucao financeira no campo principal, entao leituras de volume devem ser acompanhadas da contagem de registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\CE.parquet`; campos e agregacoes usados: auditoria do bruto da UF, com comparacao entre campos financeiros publicados e o campo `valor_total` mantido no parquet._

## Principais entidades

1. `05268526000170` - INSTITUTO DE SAUDE E GESTAO HOSPITALAR: R$ 7.327.739.452,16 em 20 registros.
2. `03021597000149` - INSTITUTO CENTRO DE ENSINO TECNOLOGICO: R$ 1.120.144.585,80 em 25 registros.
3. `04867567000110` - INSTITUTO AGROPOLOS DO CEARA: R$ 674.559.647,24 em 43 registros.
4. `07325673000160` - LAR ANTONIO DE PADUA: R$ 553.304.499,41 em 85 registros.
5. `19521941000107` - COOPERATIVA DE TRABALHO DOS PROFISSIONAIS DE ENFERMAGEM E DE SAUDE DO NORDESTE DO ESTADO DO CEARA - COOPERNORDESTE / CE: R$ 504.965.505,19 em 101 registros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\CE.parquet`; campos e agregacoes usados: agrupamento por `nome_osc` e `cnpj`, soma de `valor_num` e contagem de registros._

## Gastos e objetivos

Termos mais frequentes nos objetos da UF: `GENEROS, ALIMENTICIOS, OUTROS, LOCACAO, TERCEIRIZACAO, OBRA, SERVICOS, CONSULTORIA, COOPERATIVA, OBRAS, ENGENHARIA, IMOVEIS`.

Registros de maior valor que ajudam a explicar os objetivos do gasto:

1. `INSTITUTO DE SAUDE E GESTAO HOSPITALAR` - R$ 1.284.375.775,36 (ano 2020): Outros.
2. `INSTITUTO DE SAUDE E GESTAO HOSPITALAR` - R$ 895.424.303,35 (ano 2020): Outros.
3. `INSTITUTO DE SAUDE E GESTAO HOSPITALAR` - R$ 772.241.961,26 (ano 2020): Outros.
4. `INSTITUTO DE SAUDE E GESTAO HOSPITALAR` - R$ 747.957.848,66 (ano 2020): Outros.
5. `INSTITUTO DE SAUDE E GESTAO HOSPITALAR` - R$ 722.355.726,01 (ano 2020): Outros.

O maior registro individual da UF foi para `INSTITUTO DE SAUDE E GESTAO HOSPITALAR` no valor de R$ 1.284.375.775,36. O objeto associado foi: Outros.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\CE.parquet`; campos e agregacoes usados: campos `objeto`, `valor_total`, `ano`; selecao dos maiores registros por `valor_num`._

## Evolucao temporal

Anos de maior volume:

1. `2020` - R$ 5.601.319.497,09 em 484 registros.
2. `2024` - R$ 2.262.188.946,25 em 1.075 registros.
3. `2022` - R$ 1.536.666.228,92 em 644 registros.

Ultimos anos da serie:

- `2022`: R$ 1.536.666.228,92 em 644 registros, variacao 84,0%.
- `2023`: R$ 708.408.566,07 em 761 registros, variacao -53,9%.
- `2024`: R$ 2.262.188.946,25 em 1.075 registros, variacao 219,3%.
- `2025`: R$ 838.433.519,39 em 820 registros, variacao -62,9%.
- `2026`: R$ 0,00 em 11 registros, variacao -100,0%.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\CE.parquet`; campos e agregacoes usados: agregacao anual por `ano_num`, soma de `valor_num`, contagem de registros e variacao percentual._

## Territorio e cobertura

A base desta UF nao traz cobertura territorial suficiente para destacar municipios com seguranca.

Cobertura observada: CNPJ valido em 100,0%, municipio em 0,0%, objeto em 100,0% e modalidade em 100,0%. Ha 0 registros negativos e 231 registros marcados como duplicado aparente.

_Fonte local deste bloco: `E:\dados\orcamento_geral_processada\CE.parquet`; campos e agregacoes usados: campos `municipio`, `cod_municipio`, `objeto`, `modalidade`, `cnpj`, `duplicado_aparente`, `valor_negativo`._

## Fontes extras

### Dados locais

- Arquivo principal desta historia: `E:\dados\orcamento_geral_processada\CE.parquet`.
- Todas as afirmacoes sobre gasto, volume, anos, concentracao, objetivos e municipios foram derivadas desse parquet.

### Fontes externas verificadas por entidade

- [Consulta oficial de CNPJ (gov.br)](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas)
- [Comprovante de inscricao e situacao cadastral (Receita)](https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp)
- [Convenios e transferencias federais (gov.br / Transferegov)](https://www.gov.br/planejamento/pt-br/acesso-a-informacao/convenios-e-transparencias)

- `INSTITUTO DE SAUDE E GESTAO HOSPITALAR` (05268526000170): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/05268526000170) - situacao ATIVA; municipio/UF FORTALEZA/CE; porte DEMAIS; atividade principal Atividades de apoio a gestao de saude.
- `INSTITUTO CENTRO DE ENSINO TECNOLOGICO` (03021597000149): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/03021597000149) - situacao ATIVA; municipio/UF FORTALEZA/CE; porte DEMAIS; atividade principal Educacao profissional de nivel tecnologico.
- `INSTITUTO AGROPOLOS DO CEARA` (04867567000110): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/04867567000110) - situacao ATIVA; municipio/UF FORTALEZA/CE; porte DEMAIS; atividade principal Atividades associativas nao especificadas anteriormente.
- `LAR ANTONIO DE PADUA` (07325673000160): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/07325673000160) - situacao ATIVA; municipio/UF FORTALEZA/CE; porte DEMAIS; atividade principal Educacao infantil - creche.
- `COOPERATIVA DE TRABALHO DOS PROFISSIONAIS DE ENFERMAGEM E DE SAUDE DO NORDESTE DO ESTADO DO CEARA - COOPERNORDESTE / CE` (19521941000107): [fonte externa verificada](https://brasilapi.com.br/api/cnpj/v1/19521941000107) - situacao ATIVA; municipio/UF FORTALEZA/CE; porte DEMAIS; atividade principal Atividades de enfermagem.

### Investigacao complementar

- [INSTITUTO DE SAUDE E GESTAO HOSPITALAR - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=05268526000170+INSTITUTO+DE+SAUDE+E+GESTAO+HOSPITALAR+Ceara+convenio+contrato+gestao)
- [INSTITUTO CENTRO DE ENSINO TECNOLOGICO - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=03021597000149+INSTITUTO+CENTRO+DE+ENSINO+TECNOLOGICO+Ceara+convenio+contrato+gestao)
- [INSTITUTO AGROPOLOS DO CEARA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=04867567000110+INSTITUTO+AGROPOLOS+DO+CEARA+Ceara+convenio+contrato+gestao)
- [LAR ANTONIO DE PADUA - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=07325673000160+LAR+ANTONIO+DE+PADUA+Ceara+convenio+contrato+gestao)
- [COOPERATIVA DE TRABALHO DOS PROFISSIONAIS DE ENFERMAGEM E DE SAUDE DO NORDESTE DO ESTADO DO CEARA - COOPERNORDESTE / CE - busca complementar por CNPJ/nome/UF](https://www.google.com/search?q=19521941000107+COOPERATIVA+DE+TRABALHO+DOS+PROFISSIONAIS+DE+ENFERMAGEM+E+DE+SAUDE+DO+NORDESTE+DO+ESTADO+DO+CEARA+-+COOPERNORDESTE+%2F+CE+Ceara+convenio+contrato+gestao)

## Proveniencia das fontes

### Estado

- Parquet estadual consolidado: `E:\dados\orcamento_geral_processada\CE.parquet` (4802 linhas).
- Pasta bruta usada no pipeline estadual: `E:\dados\bases_orcamento_geral\CE`.
- Exemplos de arquivos brutos estaduais: `contrator.zip`, `contratos_osc_alta_confianca_cruzadas.csv`, `contratos_osc_alta_mais_nao_encontradas.csv`, `contratos_osc_candidatas_cruzadas.csv`, `contratos_osc_candidatas_nao_encontradas_em_sem_fins.csv`.
- Scripts associados ao estado: `utils/orcamento_geral/processar_orcamento_geral_ce.py`.
- Observacao de trilha: Serie montada a partir de arquivos locais legados preservados em `bases_convenios/CE`.

### Capital (Fortaleza)

- Parquet da capital consolidado: `E:\dados\capitais_processada\CE_FORTALEZA.parquet` (82 linhas).
- Pasta bruta usada no pipeline da capital: `E:\dados\bases_convenios_capitais\Fortaleza`.
- Exemplos de arquivos brutos da capital: `fortaleza_convenios_2024.html`, `fortaleza_convenios_2025.html`, `fortaleza_convenios_2026.html`, `fortaleza_detalhe_40352.html`.
- Scripts associados a capital: `utils/orcamento_geral/processar_orcamento_geral_capitais.py`.
- Fontes oficiais registradas para a capital: [transparencia.fortaleza.ce.gov.br/index.php/convenio](https://transparencia.fortaleza.ce.gov.br/index.php/convenio).

## Conclusao

Ceara deve ser lido como uma UF puxada por ticket medio e concentracao. Se o objetivo for auditar volume financeiro, os principais focos sao as entidades lideres e os anos de pico. Se o objetivo for comparar com outras UFs, os melhores eixos sao quantidade de registros, ticket medio, concentracao e cobertura dos campos territoriais.
