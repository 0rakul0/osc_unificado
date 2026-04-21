# Recife - Colunas Candidatas

Pasta analisada: `E:\dados\bases_convenios_capitais\Recife`

Resumo consolidado das colunas mais prováveis para mapear despesas do Recife.

## Resumo Geral

- `ano`: ano, Ano, ano_movimentacao, empenho_ano
- `mes`: mês, Mês, mes_movimentacao, mes
- `valor_total`: Empenhado, Liquidado, Pago, Liquidação, Pagamento, valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: CPF/CNPJ, credor_codigo
- `nome_osc`: Nome do Credor, orgao_nome, credor_nome
- `objeto`: Código do programa, Descrição do programa, Descrição da ação, Código de Programa, Programa, modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: Código da categoria, Descrição da categoria, Código de Tipo de Licitação, Tipo de Licitação, Código da Modalidade do Empenho, Código de Modalidade, Modalidade, categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome, Categoria da despesa, Código da modalidade, cod_categoria, desc_categoria, cod_grupo_despesa, desc_grupo_despesa, cod_modalidade, desc_modalidade
- `data_inicio`: Data do Empenho, Data de Pagamento
- `data_fim`: (nenhuma)

## recife_despesa-contabil-2025.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 19

### Colunas candidatas por campo

- `ano`: ano
- `mes`: mês
- `valor_total`: Empenhado, Liquidado, Pago
- `cnpj`: (nenhuma)
- `nome_osc`: (nenhuma)
- `objeto`: Código do programa, Descrição do programa, Descrição da ação
- `modalidade`: Código da categoria, Descrição da categoria
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano`: 2025
- `mês`: 1,0
- `Código do programa`: 2161, 1315, 2160
- `Descrição do programa`: GESTÃO ADMINISTRATIVA DOS ÓRGÃOS, ENTIDADES E FUNDOS MUNICIPAIS, APOIO À INOVAÇÃO E DIFUSÃO DO CONHECIMENTO CIENTÍFICO E TECNOLÓGICO, GESTÃO DAS POLÍTICAS MUNICIPAIS
- `Descrição da ação`: APOIO ADMINISTRATIVO ÀS AÇÕES DA UNIDADE ORÇAMENTÁRIA, DESENVOLVIMENTO DE INSTRUMENTOS DE APOIO À INOVAÇÃO E À DIFUSÃO DO CONHECIMENTO CIENTÍFICO E TECNOLÓGICO, COORDENAÇÃO, SUPERVISÃO E EXECUÇÃO DAS POLÍTICAS DE CIÊNCIA, TECNOLOGIA E INOVAÇÃO
- `Código da categoria`: 3, 4
- `Descrição da categoria`: DESPESAS CORRENTES, DESPESAS DE CAPITAL
- `Empenhado`: 0,0, 279508,9, 289771,26
- `Liquidado`: 0,0, 279508,9
- `Pago`: 0,0, 252799,45, 9464,87

### Todas as colunas

`ano`, `mês`, `Código do órgão`, `Descrição do órgão`, `Código da função`, `Descrição da função`, `Código da sub-função`, `Descrição da sub-função`, `Código do programa`, `Descrição do programa`, `Código da ação`, `Descrição da ação`, `Código da categoria`, `Descrição da categoria`, `Dotação inicial`, `Dotação atualizada`, `Empenhado`, `Liquidado`, `Pago`

## recife_despesa-funcional-programatica-2024.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 17

### Colunas candidatas por campo

- `ano`: Ano
- `mes`: Mês
- `valor_total`: Empenhado, Liquidado, Pago
- `cnpj`: (nenhuma)
- `nome_osc`: (nenhuma)
- `objeto`: Código de Programa, Programa
- `modalidade`: (nenhuma)
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `Ano`: 2024
- `Mês`: 0
- `Código de Programa`: 1206, 2161, 1323
- `Programa`: ORGANIZAÇÃO EFICAZ DO ENSINO E DA APRENDIZAGEM, GESTÃO ADMINISTRATIVA DOS ÓRGÃOS, ENTIDADES E FUNDOS MUNICIPAIS, MANUTENÇÃO URBANA
- `Empenhado`: 0.0
- `Liquidado`: 0.0
- `Pago`: 0.0

### Todas as colunas

`Ano`, `Mês`, `Código da Função`, `Função`, `Código de Sub-função`, `Sub-função`, `Código de Programa`, `Programa`, `Código da Ação`, `Ação`, `Código da Fonte`, `Fonte`, `Dotação Inicial`, `Dotação Atualizada`, `Empenhado`, `Liquidado`, `Pago`

## recife_despesa-funcional-programatica-2025.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 17

### Colunas candidatas por campo

- `ano`: Ano
- `mes`: Mês
- `valor_total`: Empenhado, Liquidado, Pago
- `cnpj`: (nenhuma)
- `nome_osc`: (nenhuma)
- `objeto`: Código de Programa, Programa
- `modalidade`: (nenhuma)
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `Ano`: 2025
- `Mês`: 1
- `Código de Programa`: 1323, 1216, 2160
- `Programa`: MANUTENÇÃO URBANA, FORTALECIMENTO E QUALIFICAÇÃO DA ATENÇÃO BÁSICA EM SAÚDE, GESTÃO DAS POLÍTICAS MUNICIPAIS
- `Empenhado`: 0.0, 233200.39, 760767.77
- `Liquidado`: 0.0, 233200.39, 284126.65
- `Pago`: 0.0, 215509.91

### Todas as colunas

`Ano`, `Mês`, `Código da Função`, `Função`, `Código de Sub-função`, `Sub-função`, `Código de Programa`, `Programa`, `Código da Ação`, `Ação`, `Código da Fonte`, `Fonte`, `Dotação Inicial`, `Dotação Atualizada`, `Empenhado`, `Liquidado`, `Pago`

## recife_despesa-por-credor-empenho-2024.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 26

### Colunas candidatas por campo

- `ano`: Ano
- `mes`: Mês
- `valor_total`: Empenhado, Liquidação, Pagamento
- `cnpj`: CPF/CNPJ
- `nome_osc`: Nome do Credor
- `objeto`: (nenhuma)
- `modalidade`: Código de Tipo de Licitação, Tipo de Licitação, Código da Modalidade do Empenho, Código de Modalidade, Modalidade
- `data_inicio`: Data do Empenho, Data de Pagamento
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `Ano`: 2024
- `Mês`: 1
- `CPF/CNPJ`: 66455593000199, 35173456000138, 08362490000188
- `Nome do Credor`: HOMEOFFICE MOVEIS LTDA ME, MF SUL COMERCIO DE MOVEIS CORPORATIVOS E ESCOLARES LTDA, ADSERV EMPREENDIMENTOS E SERVICOS DE MAO DE OBRA LTDA
- `Código de Tipo de Licitação`: 12
- `Tipo de Licitação`: Registro de Preço
- `Código da Modalidade do Empenho`: 1, 2
- `Código de Modalidade`: 90
- `Modalidade`: APLICAÇÕES DIRETAS
- `Data do Empenho`: 2024/01/31 00:00:00.000, 2024/01/29 00:00:00.000
- `Data de Pagamento`: {}, {2024-02-15,2024-03-07}, {2024-03-12,2024-03-13,2024-04-02,2024-05-21,2024-07-01,2024-07-19,2024-09-02,2024-09-09,2024-10-29,2024-11-27,2024-12-13,2025-01-12}
- `Empenhado`: 0.0, 168413.09, 241219.8
- `Liquidação`: 0.0, 168413.09, 241219.8
- `Pagamento`: 0.0, 168413.09, 241219.8

### Todas as colunas

`Ano`, `Mês`, `Código da Unidade`, `Unidade`, `CPF/CNPJ`, `Nome do Credor`, `Código de Tipo de Licitação`, `Tipo de Licitação`, `Data do Empenho`, `Data de Pagamento`, `Código da Modalidade do Empenho`, `Modadlidade do Empenho`, `Poder`, `Código do Órgão`, `Órgão`, `Grupo de Despesa`, `Código de Modalidade`, `Modalidade`, `Empenhado`, `Liquidação`, `Pagamento`, `Anulação Empenho`, `Anulação Liquidação`, `Anulação Pagamento`, `Dotação Inicial`, `Dotação Atualizada`

## recife_despesa-por-credor-empenho-2025.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 26

### Colunas candidatas por campo

- `ano`: Ano
- `mes`: Mês
- `valor_total`: Empenhado, Liquidação, Pagamento
- `cnpj`: CPF/CNPJ
- `nome_osc`: Nome do Credor
- `objeto`: (nenhuma)
- `modalidade`: Código de Tipo de Licitação, Tipo de Licitação, Código da Modalidade do Empenho, Código de Modalidade, Modalidade
- `data_inicio`: Data do Empenho, Data de Pagamento
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `Ano`: 2025
- `Mês`: 1
- `CPF/CNPJ`: 52090345420, 11431327000134, 08362490000188
- `Nome do Credor`: EDNA MARTINS ALVES DE SOUZA, PERNAMBUCO TRIBUNAL DE JUSTIÇA, ADSERV EMPREENDIMENTOS E SERVICOS DE MAO DE OBRA LTDA
- `Código de Tipo de Licitação`: 9, 16, 12
- `Tipo de Licitação`: Outros / Não Aplicável, Dispensado, Registro de Preço
- `Código da Modalidade do Empenho`: 1, 2
- `Código de Modalidade`: 50, 90
- `Modalidade`: TRANSFERÊNCIAS À INSTITUIÇÕES PRIVADAS SEM FINS LUCRATIVOS, APLICAÇÕES DIRETAS
- `Data do Empenho`: 2025/01/23 00:00:00.000, 2025/01/28 00:00:00.000, 2025/01/27 00:00:00.000
- `Data de Pagamento`: {2025-01-24}, {2025-01-30}, {2025-02-05,2025-03-18,2025-04-16,2025-05-06,2025-06-06,2025-07-02,2025-08-19,2025-09-03,2025-10-08,2025-11-18}
- `Empenhado`: 500.0, 1869000.0, 268835.66
- `Liquidação`: 500.0, 1869000.0, 268835.66
- `Pagamento`: 500.0, 1869000.0, 268835.66

### Todas as colunas

`Ano`, `Mês`, `Código da Unidade`, `Unidade`, `CPF/CNPJ`, `Nome do Credor`, `Código de Tipo de Licitação`, `Tipo de Licitação`, `Data do Empenho`, `Data de Pagamento`, `Código da Modalidade do Empenho`, `Modadlidade do Empenho`, `Poder`, `Código do Órgão`, `Órgão`, `Grupo de Despesa`, `Código de Modalidade`, `Modalidade`, `Empenhado`, `Liquidação`, `Pagamento`, `Anulação Empenho`, `Anulação Liquidação`, `Anulação Pagamento`, `Dotação Inicial`, `Dotação Atualizada`

## recife_despesas-orcamentarias-2002.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2022
- `empenho_ano`: 2022
- `mes_movimentacao`: 4, 8, 10
- `orgao_nome`: GABINETE DO CENTRO DO RECIFE
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: COORDENAÇÃO, SUPERVISÃO E EXECUÇÃO DAS POLÍTICAS DO GABINETE DO CENTRO DO RECIFE
- `credor_codigo`: 0
- `valor_empenhado`: 14393,12, 15167,24, 15156,00
- `valor_liquidado`: 14393,12, 15167,24, 15156,00
- `valor_pago`: 14393,12, 15167,24, 15156,00

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2003.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2003
- `empenho_ano`: 2003
- `mes_movimentacao`: 1, 2, 7
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: SALÁRIO-FAMÍLIA, VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: SALÁRIO-FAMÍLIA - ATIVO PESSOAL CIVIL, VENCIMENTOS E SALÁRIOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2150
- `programa_nome`: FORTALECIMENTO DO ASSESSORAMENTO GOVERNAMENTAL
- `acao_nome`: ASSESSORAMENTO AO PREFEITO E AO VICE-PREFEITO
- `credor_codigo`: 0
- `valor_empenhado`: 338, 377, 383.5
- `valor_liquidado`: 338, 377, 383.5
- `valor_pago`: 338, 377, 383.5

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2004.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2004
- `empenho_ano`: 2004
- `mes_movimentacao`: 4, 6, 8
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: SALÁRIO-FAMÍLIA, VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: SALÁRIO-FAMÍLIA - ATIVO PESSOAL CIVIL, ADICIONAL DE PERICULOSIDADE, INSALUBRIDADE E ATIVIDADES PENOSAS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2124
- `programa_nome`: GESTÃO ADMINISTRATIVA DA GOVERNADORIA MUNICIPAL
- `acao_nome`: APOIO ADMINISTRATIVO ÀS AÇÕES DA GOVERNADORIA MUNICIPAL
- `credor_codigo`: 0
- `valor_empenhado`: 19.5, 52, 46.48
- `valor_liquidado`: 19.5, 52, 46.48
- `valor_pago`: 19.5, 52, 46.48

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2005.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2005
- `empenho_ano`: 2005
- `mes_movimentacao`: 11, 4, 6
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES, GRATIFICAÇÃO POR EXERCÍCIO DE CARGOS TÉCNICOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2124
- `programa_nome`: GESTÃO ADMINISTRATIVA DA GOVERNADORIA MUNICIPAL
- `acao_nome`: APOIO ADMINISTRATIVO ÀS AÇÕES DA GOVERNADORIA MUNICIPAL
- `credor_codigo`: 0
- `valor_empenhado`: 2244.32, 1249.33, 813.21
- `valor_liquidado`: 2244.32, 1249.33, 813.21
- `valor_pago`: 2244.32, 1249.33, 813.21

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2006.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2006
- `empenho_ano`: 2006
- `mes_movimentacao`: 2, 3, 4
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: SALÁRIO-FAMÍLIA, VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: SALÁRIO-FAMÍLIA - ATIVO PESSOAL CIVIL, VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 44.97, 26246.74, 25504.3
- `valor_liquidado`: 44.97, 26246.74, 25504.3
- `valor_pago`: 44.97, 26246.74, 25504.3

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2007.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2007
- `empenho_ano`: 2007
- `mes_movimentacao`: 3, 7, 9
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES, ADICIONAL DE PERICULOSIDADE, INSALUBRIDADE E ATIVIDADES PENOSAS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 30572.94, 63458.31, 32784.81
- `valor_liquidado`: 30572.94, 63458.31, 32784.81
- `valor_pago`: 30572.94, 63458.31, 32784.81

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2008.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2008
- `empenho_ano`: 2008
- `mes_movimentacao`: 6, 8, 9
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: INCORPORAÇÕES, ADICIONAL DE PERICULOSIDADE, INSALUBRIDADE E ATIVIDADES PENOSAS, GRATIFICAÇÃO POR EXERCÍCIO DE CARGOS TÉCNICOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 7063.65, 3576.35, 35643.41
- `valor_liquidado`: 7063.65, 3576.35, 35643.41
- `valor_pago`: 7063.65, 3576.35, 35643.41

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2009.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2009
- `empenho_ano`: 2009
- `mes_movimentacao`: 2, 6, 7
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 38991.38, 38127.96, 42133.95
- `valor_liquidado`: 38991.38, 38127.96, 42133.95
- `valor_pago`: 38991.38, 38127.96, 42133.95

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2010.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2010
- `empenho_ano`: 2010
- `mes_movimentacao`: 5, 4, 6
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: INCORPORAÇÕES, GRATIFICAÇÃO DE CARGOS COMISSIONADOS E FUNÇÕES GRATIFICADAS, GRATIFICAÇÃO DE TEMPO DE SERVIÇO
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: PLANEJAMENTO DA AÇÃO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 337.03, 69589.05, 73195.65
- `valor_liquidado`: 337.03, 69589.05, 73195.65
- `valor_pago`: 337.03, 69589.05, 73195.65

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2011.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2011
- `empenho_ano`: 2011
- `mes_movimentacao`: 1, 3, 4
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: PLANEJAMENTO DA AÇÃO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 1415.86, 352.74
- `valor_liquidado`: 1415.86, 352.74
- `valor_pago`: 1415.86, 352.74

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2012.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2012
- `empenho_ano`: 2012
- `mes_movimentacao`: 10, 11, 12
- `orgao_nome`: GOVERNADORIA MUNICIPAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES, GRATIFICAÇÃO DE CARGOS COMISSIONADOS E FUNÇÕES GRATIFICADAS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: PLANEJAMENTO DA AÇÃO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 2900.24, 393.81, 83822.17
- `valor_liquidado`: 2900.24, 393.81, 83822.17
- `valor_pago`: 2900.24, 393.81, 83822.17

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2013.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2013
- `empenho_ano`: 2013
- `mes_movimentacao`: 1, 4, 8
- `orgao_nome`: GABINETE DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL, OUTRAS DESPESAS VARIÁVEIS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, OUTRAS DESPESAS VARIÁVEIS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: PLANEJAMENTO DA AÇÃO GOVERNAMENTAL, ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 2900.24, 5664, 415558.96
- `valor_liquidado`: 2900.24, 5664, 415558.96
- `valor_pago`: 2900.24, 5664, 415558.96

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2014.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2014
- `empenho_ano`: 2014
- `mes_movimentacao`: 1, 9, 2
- `orgao_nome`: GABINETE DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 437705.34, -1570.29, 377953.43
- `valor_liquidado`: 437705.34, -1570.29, 377953.43
- `valor_pago`: 437705.34, -1570.29, 377953.43

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2015.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2015
- `empenho_ano`: 2015
- `mes_movimentacao`: 5, 10, 11
- `orgao_nome`: GABINETE DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: CONTRATAÇÃO POR TEMPO DETERMINADO, VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 404712.83, 204075.41, -23930.64
- `valor_liquidado`: 404712.83, 204075.41, -23930.64
- `valor_pago`: 404712.83, 204075.41, -23930.64

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2016.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2016
- `empenho_ano`: 2016
- `mes_movimentacao`: 2, 3, 5
- `orgao_nome`: GABINETE DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: CONTRATAÇÃO POR TEMPO DETERMINADO, VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 203743,33, 199860,59, 190589,62
- `valor_liquidado`: 203743,33, 199860,59, 190589,62
- `valor_pago`: 203743,33, 199860,59, 190589,62

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2017.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2017
- `empenho_ano`: 2017
- `mes_movimentacao`: 3, 4, 7
- `orgao_nome`: GABINETE DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 160613,59, 159933,78, 77521,68
- `valor_liquidado`: 160613,59, 159933,78, 77521,68
- `valor_pago`: 160613,59, 159933,78, 77521,68

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2018.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2018
- `empenho_ano`: 2018
- `mes_movimentacao`: 1, 8, 11
- `orgao_nome`: GABINETE DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: INCORPORAÇÕES, ADICIONAL DE PERICULOSIDADE, INSALUBRIDADE E ATIVIDADES PENOSAS, GRATIFICAÇÃO POR EXERCÍCIO DE CARGOS TÉCNICOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 2693,13, 1877,05, 12678,32
- `valor_liquidado`: 2693,13, 1877,05, 12678,32
- `valor_pago`: 2693,13, 1877,05, 12678,32

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2019.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2019
- `empenho_ano`: 2019
- `mes_movimentacao`: 4, 2, 7
- `orgao_nome`: ASSESSORIA ESPECIAL DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES, GRATIFICAÇÃO POR EXERCÍCIO DE CARGOS TÉCNICOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 4560,91, 604,50, 3480,46
- `valor_liquidado`: 4560,91, 604,50, 3480,46
- `valor_pago`: 4560,91, 604,50, 3480,46

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2020.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2020
- `empenho_ano`: 2020
- `mes_movimentacao`: 1, 6, 8
- `orgao_nome`: ASSESSORIA ESPECIAL DO PREFEITO
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 4560,91, 4788,95, 604,50
- `valor_liquidado`: 4560,91, 4788,95, 604,50
- `valor_pago`: 4560,91, 4788,95, 604,50

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2021.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2021
- `empenho_ano`: 2021
- `mes_movimentacao`: 7, 9, 8
- `orgao_nome`: ASSESSORIA ESPECIAL E REPRESENTAÇÃO INSTITUCIONAL
- `credor_nome`: CREDOR NÃO INFORMADO
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 1
- `grupo_despesa_nome`: PESSOAL E ENCARGOS SOCIAIS
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: VENCIMENTOS E VANTAGENS FIXAS - PESSOAL CIVIL
- `subelemento_nome`: VENCIMENTOS E SALÁRIOS, INCORPORAÇÕES, GRATIFICAÇÃO POR EXERCÍCIO DE CARGOS TÉCNICOS
- `empenho_modalidade_nome`: SEM TIPO INFORMADO
- `empenho_modalidade_codigo`: 0
- `modalidade_licitacao_codigo`: 0
- `modalidade_licitacao_nome`: NÃO INFORMADA
- `programa_codigo`: 2160
- `programa_nome`: GESTÃO DAS POLÍTICAS MUNICIPAIS
- `acao_nome`: ASSESSORAMENTO GOVERNAMENTAL
- `credor_codigo`: 0
- `valor_empenhado`: 6706,09, 9655,35, 604,50
- `valor_liquidado`: 6706,09, 9655,35, 604,50
- `valor_pago`: 6706,09, 9655,35, 604,50

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2022.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2022
- `empenho_ano`: 2022
- `mes_movimentacao`: 1
- `orgao_nome`: SECRETARIA DE EDUCAÇÃO
- `credor_nome`: JOSE FERNANDES DE OLIVEIRA, RONILDES LOUREIRO BASTOS NAPOLES DE CARVALHO, MARIA DO CARMO PEREIRA DA SILVA
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 3
- `grupo_despesa_nome`: OUTRAS DESPESAS CORRENTES
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: OUTROS SERVIÇOS DE TERCEIROS - PESSOA FÍSICA
- `subelemento_nome`: LOCAÇÃO DE IMÓVEIS
- `empenho_modalidade_nome`: ORDINARIO, GLOBAL
- `empenho_modalidade_codigo`: 1, 3
- `modalidade_licitacao_codigo`: 16
- `modalidade_licitacao_nome`: DISPENSADO
- `programa_codigo`: 1249
- `programa_nome`: AMPLIAÇÃO E GESTÃO DA REDE DE ENSINO FUNDAMENTAL
- `acao_nome`: UNIVERSALIZAÇÃO E QUALIFICAÇÃO DO ENSINO FUNDAMENTAL
- `credor_codigo`: 0500046, 0500057, 0500059
- `valor_empenhado`: 5352,99, 44000,00, 568,69
- `valor_liquidado`: 0,00
- `valor_pago`: 0,00

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orcamentarias-2023.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 39

### Colunas candidatas por campo

- `ano`: ano_movimentacao, empenho_ano
- `mes`: mes_movimentacao
- `valor_total`: valor_empenhado, valor_liquidado, valor_pago
- `cnpj`: credor_codigo
- `nome_osc`: orgao_nome, credor_nome
- `objeto`: modalidade_aplicacao_nome, subelemento_nome, programa_codigo, programa_nome, acao_nome, modalidade_licitacao_nome
- `modalidade`: categoria_economica_codigo, categoria_economica_nome, grupo_despesa_codigo, grupo_despesa_nome, modalidade_aplicacao_codigo, modalidade_aplicacao_nome, elemento_nome, subelemento_nome, empenho_modalidade_nome, empenho_modalidade_codigo, modalidade_licitacao_codigo, modalidade_licitacao_nome
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano_movimentacao`: 2023
- `empenho_ano`: 2023
- `mes_movimentacao`: 5, 9, 2
- `orgao_nome`: SECRETARIA DE FINANÇAS - ADMINISTRAÇÃO SUPERVISIONADA
- `credor_nome`: GEOD PROJETOS CONSULTORIA E TREINAMENTO EM GEOPROCESSAMENTO PLANEJAMENTO URBANO LTDA ME, SOLL SERVICOS OBRAS E LOCACOES LTDA
- `categoria_economica_codigo`: 3
- `categoria_economica_nome`: DESPESAS CORRENTES
- `grupo_despesa_codigo`: 3
- `grupo_despesa_nome`: OUTRAS DESPESAS CORRENTES
- `modalidade_aplicacao_codigo`: 90
- `modalidade_aplicacao_nome`: APLICAÇÕES DIRETAS
- `elemento_nome`: SERVIÇOS DE CONSULTORIA, LOCAÇÃO DE MÃO-DE-OBRA
- `subelemento_nome`: ASSESSORIA E CONSULTORIA TÉCNICA - PESSOA JURÍDICA, SERVIÇOS DE CONDUTORES DE VEÍCULOS
- `empenho_modalidade_nome`: GLOBAL
- `empenho_modalidade_codigo`: 3
- `modalidade_licitacao_codigo`: 24, 36
- `modalidade_licitacao_nome`: DISPENSADO, PREGAO - REG. PRECO
- `programa_codigo`: 2122
- `programa_nome`: GESTÃO PÚBLICA DE EXCELÊNCIA
- `acao_nome`: DESENVOLVIMENTO E APERFEIÇOAMENTO DA ADMINISTRAÇÃO TRIBUTÁRIA
- `credor_codigo`: 04301727, 06000040
- `valor_empenhado`: 16229,00, 0,00, 50071,08
- `valor_liquidado`: 0,00, 16229,00
- `valor_pago`: 0,00, 16229,00

### Todas as colunas

`ano_movimentacao`, `mes_movimentacao`, `orgao_codigo`, `orgao_nome`, `unidade_codigo`, `unidade_nome`, `categoria_economica_codigo`, `categoria_economica_nome`, `grupo_despesa_codigo`, `grupo_despesa_nome`, `modalidade_aplicacao_codigo`, `modalidade_aplicacao_nome`, `elemento_codigo`, `elemento_nome`, `subelemento_codigo`, `subelemento_nome`, `funcao_codigo`, `funcao_nome`, `subfuncao_codigo`, `subfuncao_nome`, `programa_codigo`, `programa_nome`, `acao_codigo`, `acao_nome`, `fonte_recurso_codigo`, `fonte_recurso_nome`, `empenho_ano`, `empenho_modalidade_nome`, `empenho_modalidade_codigo`, `empenho_numero`, `subempenho`, `indicador_subempenho`, `credor_codigo`, `credor_nome`, `modalidade_licitacao_codigo`, `modalidade_licitacao_nome`, `valor_empenhado`, `valor_liquidado`, `valor_pago`

## recife_despesas-orgao-2024.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 18

### Colunas candidatas por campo

- `ano`: Ano
- `mes`: Mês
- `valor_total`: Empenhado, Liquidado, Pago
- `cnpj`: (nenhuma)
- `nome_osc`: (nenhuma)
- `objeto`: (nenhuma)
- `modalidade`: Categoria da despesa, Código da modalidade, Modalidade
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `Ano`: 2024
- `Mês`: 3, 10, 6
- `Categoria da despesa`: DESPESAS DE CAPITAL, DESPESAS CORRENTES
- `Código da modalidade`: 90
- `Modalidade`: APLICAÇÕES DIRETAS
- `Empenhado`: 1344259.44, 24179785.07, 1332336.09
- `Liquidado`: 1344259.44, 5992476.31, 1332336.09
- `Pago`: 1164367.95, 5867744.2, 1511200.19

### Todas as colunas

`Ano`, `Mês`, `Poder`, `Código órgão`, `Órgão setorial`, `Código da unidade`, `Unidade gestora`, `Código da despesa`, `Categoria da despesa`, `Código do grupo de despesa`, `Grupo de despesa`, `Código da modalidade`, `Modalidade`, `Dotação atualizada`, `Dotação inicial`, `Empenhado`, `Liquidado`, `Pago`

## recife_despesas-orgao-2025.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 18

### Colunas candidatas por campo

- `ano`: Ano
- `mes`: Mês
- `valor_total`: Empenhado, Liquidado, Pago
- `cnpj`: (nenhuma)
- `nome_osc`: (nenhuma)
- `objeto`: (nenhuma)
- `modalidade`: Categoria da despesa, Código da modalidade, Modalidade
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `Ano`: 2025
- `Mês`: 8, 12, 7
- `Categoria da despesa`: DESPESAS CORRENTES, DESPESAS DE CAPITAL
- `Código da modalidade`: 90, 50
- `Modalidade`: APLICAÇÕES DIRETAS, TRANSFERÊNCIAS À INSTITUIÇÕES PRIVADAS SEM FINS LUCRATIVOS
- `Empenhado`: 305580.96, 0.0, 500.0
- `Liquidado`: 305580.96, 39709.6, 500.0
- `Pago`: 299225.18, 38989.9, 500.0

### Todas as colunas

`Ano`, `Mês`, `Poder`, `Código órgão`, `Órgão setorial`, `Código da unidade`, `Unidade gestora`, `Código da despesa`, `Categoria da despesa`, `Código do grupo de despesa`, `Grupo de despesa`, `Código da modalidade`, `Modalidade`, `Dotação atualizada`, `Dotação inicial`, `Empenhado`, `Liquidado`, `Pago`

## recife_despesas-totais-2024.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 19

### Colunas candidatas por campo

- `ano`: ano
- `mes`: mes
- `valor_total`: Empenhado, Liquidação, Pagamento
- `cnpj`: (nenhuma)
- `nome_osc`: (nenhuma)
- `objeto`: (nenhuma)
- `modalidade`: cod_categoria, desc_categoria, cod_grupo_despesa, desc_grupo_despesa, cod_modalidade, desc_modalidade
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano`: 2024
- `mes`: 1
- `cod_categoria`: 3
- `desc_categoria`: DESPESAS CORRENTES
- `cod_grupo_despesa`: 1
- `desc_grupo_despesa`: PESSOAL E ENCARGOS SOCIAIS
- `cod_modalidade`: 90
- `desc_modalidade`: APLICAÇÕES DIRETAS
- `Empenhado`: 7716070.9
- `Liquidação`: 0.0
- `Pagamento`: 0.0

### Todas as colunas

`ano`, `mes`, `cod_categoria`, `desc_categoria`, `cod_grupo_despesa`, `desc_grupo_despesa`, `cod_modalidade`, `desc_modalidade`, `cod_elemento`, `desc_elemento`, `cod_sub_elemento`, `desc_sub_elemento`, `cod_fonte`, `desc_fonte`, `Empenhado`, `Liquidação`, `Pagamento`, `dotacao_inicial`, `dotacao_atualizada`

## recife_despesas-totais-2025.csv

- Tipo: CSV
- Encoding: `utf-8-sig`
- Separador: `;`
- Total de colunas: 19

### Colunas candidatas por campo

- `ano`: ano
- `mes`: mes
- `valor_total`: Empenhado, Liquidação, Pagamento
- `cnpj`: (nenhuma)
- `nome_osc`: (nenhuma)
- `objeto`: (nenhuma)
- `modalidade`: cod_categoria, desc_categoria, cod_grupo_despesa, desc_grupo_despesa, cod_modalidade, desc_modalidade
- `data_inicio`: (nenhuma)
- `data_fim`: (nenhuma)

### Amostras das colunas candidatas

- `ano`: 2025
- `mes`: 1
- `cod_categoria`: 3
- `desc_categoria`: DESPESAS CORRENTES
- `cod_grupo_despesa`: 1
- `desc_grupo_despesa`: PESSOAL E ENCARGOS SOCIAIS
- `cod_modalidade`: 90
- `desc_modalidade`: APLICAÇÕES DIRETAS
- `Empenhado`: 26781363.64
- `Liquidação`: 26781363.64
- `Pagamento`: 14561382.2

### Todas as colunas

`ano`, `mes`, `cod_categoria`, `desc_categoria`, `cod_grupo_despesa`, `desc_grupo_despesa`, `cod_modalidade`, `desc_modalidade`, `cod_elemento`, `desc_elemento`, `cod_sub_elemento`, `desc_sub_elemento`, `cod_fonte`, `desc_fonte`, `Empenhado`, `Liquidação`, `Pagamento`, `dotacao_inicial`, `dotacao_atualizada`
