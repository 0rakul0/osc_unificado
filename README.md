# OSC Unificado

Projeto para consolidar bases estaduais de convenios, transferencias e despesas em arquivos `.parquet` padronizados por UF.

O objetivo e transformar fontes heterogeneas em um schema unico, permitindo auditoria, comparacao e enriquecimento posterior.

## Estrutura

- [bases_convenios](D:/github/osc_unificado/bases_convenios): arquivos brutos de convenios por UF e fontes auxiliares.
- `bases_convenios_capitais/`: pasta reservada para convenios das capitais, separada da trilha estadual.
- `bases_orcamento_geral/`: pasta criada no workspace para a trilha estadual de orcamento geral.
- `bases_orcamento_geral_capitais/`: pasta reservada para a trilha de orcamento geral das capitais.
- `capitais_processada/`: saida consolidada das capitais em `.parquet`, separada das trilhas estaduais.
  Os arquivos seguem o padrao `UF_NOMECAPITAL.parquet`, por exemplo `MT_CUIABA.parquet` e `AC_RIO_BRANCO.parquet`.
- [processada](D:/github/osc_unificado/processada): saida consolidada em `.parquet`, um arquivo por UF.
- [governo_federal](D:/github/osc_unificado/governo_federal): parquets por UF derivados da base federal, no mesmo schema consolidado.
- [utils](D:/github/osc_unificado/utils): parsers por UF, componentes comuns e subpastas por trilha.
- [utils/convenios](D:/github/osc_unificado/utils/convenios): scripts da trilha principal de convenios, incluindo consolidacao, enriquecimento federal, separacao federal e auditoria.
- [utils/orcamento_geral](D:/github/osc_unificado/utils/orcamento_geral): scripts da trilha de orcamento geral, organizados por UF.
- [utils/convenios/unificador.py](D:/github/osc_unificado/utils/convenios/unificador.py): script principal de consolidacao.
- [utils/convenios/enriquecer_processada_governo.py](D:/github/osc_unificado/utils/convenios/enriquecer_processada_governo.py): enriquecimento dos parquets com a base federal.
- [utils/convenios/separar_governo_federal.py](D:/github/osc_unificado/utils/convenios/separar_governo_federal.py): separa a base federal em um parquet por UF.
- [utils/convenios/auditar_processada.py](D:/github/osc_unificado/utils/convenios/auditar_processada.py): gera a planilha de auditoria.
- [utils/convenios/baixar_convenios_go_dadosabertos.py](D:/github/osc_unificado/utils/convenios/baixar_convenios_go_dadosabertos.py): baixa os datasets de convenios de GO no portal Dados Abertos Goias e organiza os arquivos em `bases_convenios/GO/`.
- [auditoria_processada.xlsx](D:/github/osc_unificado/auditoria_processada.xlsx): relatorio gerado a partir da pasta `processada`.
- [config.py](D:/github/osc_unificado/config.py): fonte central das configuracoes principais do projeto, incluindo caminhos, variaveis de ambiente e nomes de tabelas/views do SQLite.
- [etl_parquets_sqlite.py](D:/github/osc_unificado/etl_parquets_sqlite.py): carrega os parquets consolidados em um banco SQLite para analise, incluindo `processada/` e `capitais_processada/` automaticamente quando existirem.
- [visualizar_processados.py](D:/github/osc_unificado/visualizar_processados.py): app Streamlit para inspecionar os arquivos processados, inclusive sob `E:/dados`, listar os parquets da pasta escolhida e abrir uma amostra de ate 50 linhas com colunas e tipos.
- [project_paths.py](D:/github/osc_unificado/project_paths.py): centraliza os caminhos padrao do projeto e permite sobrescrever por variaveis de ambiente.

## Schema final

Todos os parquets seguem este schema:

- `uf`
- `origem`
- `ano`
- `valor_total`
- `cnpj`
- `nome_osc`
- `mes`
- `cod_municipio`
- `municipio`
- `objeto`
- `modalidade`
- `data_inicio`
- `data_fim`

Regras gerais atualmente aplicadas:

- `valor_total` e obrigatorio para todas as UFs.
- `origem` identifica de qual trilha o registro veio. A carga estadual usa `convenios` e a base federal do governo usa `convenios_federal`.
- `valor_total` e normalizado para texto numerico consistente, aceitando tanto `1234.56` quanto `1234,56` nas fontes.
- no parquet final, `valor_total` e gravado como decimal exato com 2 casas, evitando erro de ponto flutuante.
- na consolidacao bruta, `cnpj` e obrigatorio apenas para `RJ`.
- a base final enriquecida mantem apenas registros com `cnpj` valido no campo `cnpj` (14 caracteres apos a limpeza).
- `ano` e `mes` sao normalizados para texto inteiro quando vierem como `2022.0`, `5.0` etc.
- `cnpj` passa por limpeza padrao, preservando CPF/CNPJ mascarado quando ele ja vem assim na fonte.

## Como o pipeline funciona

O fluxo recomendado e este:

1. Consolidar as bases brutas em parquet por UF.
2. Enriquecer os parquets com a base federal de convenios, quando houver match confiavel.
3. Gerar a auditoria final para revisar cobertura, anos, CNPJ e colunas vazias.

## Caminhos em outro disco

O projeto agora aceita mover pastas grandes para outro disco usando variaveis de ambiente, sem depender do workspace atual.

Variaveis suportadas:

- `OSC_BASES_CONVENIOS_DIR`
- `OSC_BASES_CONVENIOS_CAPITAIS_DIR`
- `OSC_BASES_ORCAMENTO_GERAL_DIR`
- `OSC_BASES_ORCAMENTO_GERAL_CAPITAIS_DIR`
- `OSC_CAPITAIS_PROCESSADA_DIR`
- `OSC_PROCESSADA_DIR`
- `OSC_GOVERNO_FEDERAL_DIR`
- `OSC_HISTORIA_DIR`
- `OSC_AUDITORIA_XLSX_PATH`
- `OSC_SQLITE_PATH`

Exemplo em PowerShell:

```powershell
$env:OSC_BASES_ORCAMENTO_GERAL_DIR = "E:\\dados\\bases_orcamento_geral"
$env:OSC_SQLITE_PATH = "E:\\dados\\sqlite\\osc_unificado.sqlite"
python etl_parquets_sqlite.py --processed-dir D:\\github\\osc_unificado\\processada --extra-processed-dir D:\\github\\osc_unificado\\governo_federal
```

Observacoes:

- o SQLite pode ser gravado em outro disco; o script cria a pasta pai automaticamente quando necessario
- a carga do SQLite inclui `capitais_processada/` por padrao quando a pasta existir no caminho configurado; `--extra-processed-dir` continua servindo para fontes adicionais, como `governo_federal/`
- as trilhas `bases_orcamento_geral/` e `bases_orcamento_geral_capitais/` ficam separadas para evitar mistura entre arquivos estaduais e das capitais
- a pasta `bases_convenios_capitais/` segue a mesma logica, isolando os downloads e brutos municipais da trilha estadual

## Convencao de escopo

Ao baixar ou guardar arquivos brutos, o projeto agora separa explicitamente:

- `estado`: usar `bases_convenios/` e `bases_orcamento_geral/`
- `capital`: usar `bases_convenios_capitais/` e `bases_orcamento_geral_capitais/`

Saidas processadas:

- capitais devem ir para `capitais_processada/`
- trilhas estaduais continuam em `processada/` ou `orcamento_geral_processada/`, conforme a fonte

Na trilha de orcamento geral, os scripts preparados para download/processamento aceitam `--scope estado` ou `--scope capital`.

Quando a saida for de capital, o parquet gerado passa a usar o nome da capital no arquivo, por exemplo `MT_CUIABA.parquet`.

## Regra operacional

Fluxo padrao daqui para frente:

1. Fechar a busca de despesas do orcamento geral no estado.
2. Verificar se ha sinal de OSC no bruto ou no parquet dessa trilha.
3. Assim que a etapa estadual fechar, procurar os convenios da capital correspondente.
4. Processar a capital separadamente em `capitais_processada/`.
5. Repetir o ciclo para a proxima UF.

Para acompanhar isso sem depender de controle manual, use:

```powershell
python utils/orcamento_geral/gerar_tracker_estado_capital_osc.py
```

O tracker gerado resume o status de estado e capital, incluindo um sinal heuristico de OSC.

## Workflow dos scripts

### 1. Consolidacao inicial

Script: [utils/convenios/unificador.py](D:/github/osc_unificado/utils/convenios/unificador.py)

Le os arquivos em `bases_convenios/`, aplica o parser da UF correspondente e grava um `.parquet` em `processada/`.

Comando basico:

```powershell
python utils/convenios/unificador.py --force
```

Comandos uteis:

```powershell
python utils/convenios/unificador.py --ufs RJ DF PA --force
python utils/convenios/unificador.py --skip-ufs RJ PA
python utils/convenios/unificador.py --preview-rows 1000 --ufs AP
```

O que ele faz:

- identifica os arquivos de entrada por UF
- escolhe o parser em `utils/<UF>.py`
- renomeia colunas para o schema padrao
- deriva `ano` e `mes` a partir de datas quando necessario
- preenche `origem = convenios` para a carga estadual, salvo quando um parser informar outro valor
- filtra linhas sem `valor_total`
- grava `valor_total` como decimal exato no parquet
- grava um parquet final por UF

## Dashboard Streamlit

O dashboard analitico agora esta organizado em paginas nativas do Streamlit, mantendo os mesmos filtros globais, cores e componentes visuais do app original.

Comando para abrir:

```powershell
streamlit run dashboard_parquets.py
```

Para inspecionar rapidamente os parquets processados em qualquer pasta configurada:

```powershell
streamlit run visualizar_processados.py
```

O visualizador aceita apontar direto para `E:\dados` e pode buscar `.parquet` tambem nas subpastas. Ele exibe no painel o caminho atual do SQLite configurado.

Paginas disponiveis no menu lateral:

- `Inicio`
- `Panorama`
- `Territorio`
- `Entidades`
- `Auditoria`
- `Historias`

### 2. Enriquecimento com base federal

Script: [utils/convenios/enriquecer_processada_governo.py](D:/github/osc_unificado/utils/convenios/enriquecer_processada_governo.py)

Usa a base federal [bases_convenios/governo/20260227_Convenios.csv](D:/github/osc_unificado/bases_convenios/governo/20260227_Convenios.csv) para:

- preencher campos faltantes nos parquets existentes
- complementar registros ja consolidados a partir das bases brutas estaduais

Por padrao, esse enriquecimento nao anexa novas linhas federais ao parquet estadual. Para isso, use `--append-new-rows`.

Campos enriquecidos:

- `cnpj`
- `nome_osc`
- `cod_municipio`
- `municipio`
- `objeto`
- `modalidade`
- `data_inicio`
- `data_fim`
- `ano`
- `mes`

Regras de match:

- primeiro por `cnpj`
- depois por `nome_osc` normalizado
- o preenchimento so acontece quando o valor de origem e univoco para aquela chave
- quando `--append-new-rows` e usado, linhas que so existem na base federal podem ser anexadas ao parquet da UF com `origem = convenios_federal`

### 2.1. Separacao da base federal em parquets por UF

Script: [utils/convenios/separar_governo_federal.py](D:/github/osc_unificado/utils/convenios/separar_governo_federal.py)

Gera a pasta `governo_federal/` com um `.parquet` por UF, preservando o schema final e marcando `origem = convenios_federal`.

Comando basico:

```powershell
python utils/convenios/separar_governo_federal.py
```

Comando basico:

```powershell
python utils/convenios/enriquecer_processada_governo.py
```

Comandos uteis:

```powershell
python utils/convenios/enriquecer_processada_governo.py --ufs AC DF PA
python utils/convenios/enriquecer_processada_governo.py --processed-dir processada --base-dir bases_convenios
```

### 3. Auditoria

Script: [utils/convenios/auditar_processada.py](D:/github/osc_unificado/utils/convenios/auditar_processada.py)

Gera a planilha [auditoria_processada.xlsx](D:/github/osc_unificado/auditoria_processada.xlsx) com:

- uma aba por estado, no formato `Estado - UF`
- contagem de linhas por `ano`
- quantidade de linhas com `cnpj`
- quantidade de `cnpj` unicos
- quantidade de linhas sem `ano`
- quantidade de `valor_total` zerado
- exemplos de `nome_osc` sem `cnpj`
- colunas sem nenhum dado
- arquivos brutos usados
- mapeamento entre coluna bruta e campo do schema

Comando:

```powershell
python utils/convenios/auditar_processada.py
```

### 4. ETL para SQLite

Script: [etl_parquets_sqlite.py](D:/github/osc_unificado/etl_parquets_sqlite.py)

Gera um banco SQLite a partir da pasta `processada`, com:

- tabela `transferencias` exatamente no schema final consolidado
- tabela `transferencias_analitica` com colunas derivadas para analise e qualidade
- tabela `arquivos_origem` com metadados dos parquets
- tabela `historias` com os markdowns por UF, quando a pasta `historia` existir
- tabela `auditoria_resumo` com a aba `Resumo` da auditoria, quando a planilha existir
- views prontas para consulta:
  - `vw_resumo_uf`
  - `vw_top_entidades`
  - `vw_serie_anual`
  - `vw_alertas_qualidade`

Colunas derivadas importantes em `transferencias_analitica`:

- `ano_num`
- `mes_num`
- `data_inicio_iso`
- `data_fim_iso`
- `duracao_dias`
- `tem_cnpj_valido`
- `tem_municipio`
- `tem_objeto`
- `tem_modalidade`
- `valor_zero`
- `valor_negativo`
- `ano_valido`
- `mes_valido`
- `entidade_base`
- `municipio_base`
- `modalidade_base`
- `ano_mes`
- `duplicado_aparente`

Observacao sobre dinheiro no SQLite:

- `transferencias.valor_total` e gravado como `MONEY`
- consultas analiticas somam `valor_total` diretamente com `CAST(valor_total AS NUMERIC)` quando necessario

Comando basico:

```powershell
python etl_parquets_sqlite.py
```

Comandos uteis:

```powershell
python etl_parquets_sqlite.py --output osc_analise.sqlite
python etl_parquets_sqlite.py --processed-dir processada --history-dir historia --audit-xlsx auditoria_processada.xlsx
```

## Parsers por UF

Cada UF possui um parser em [utils](D:/github/osc_unificado/utils). Existem dois tipos principais:

- parsers genericos, baseados em [utils/common.py](D:/github/osc_unificado/utils/common.py)
- parsers customizados, quando a UF exige limpeza ou leitura especial

Exemplos de tratamento customizado:

- [utils/AP.py](D:/github/osc_unificado/utils/AP.py): remove CNPJ colado no final de `nome_osc`.
- [utils/BA.py](D:/github/osc_unificado/utils/BA.py): mantem `data_inicio` e `data_fim` vazios.
- [utils/DF.py](D:/github/osc_unificado/utils/DF.py): completa `codigoCredor` com zeros a esquerda e faz fallback de `objeto`.
- [utils/PA.py](D:/github/osc_unificado/utils/PA.py): leitura tolerante dos CSVs do PA.
- [utils/RJ.py](D:/github/osc_unificado/utils/RJ.py): trata XLSX e CSVs com regras diferentes, inclusive extracao de datas em texto.
- [utils/gov_convenios.py](D:/github/osc_unificado/utils/gov_convenios.py): parser da base federal de convenios.

Os mapeamentos de colunas por UF ficam em [utils/config.py](D:/github/osc_unificado/utils/config.py).

## Regras de entrada atualmente configuradas

Em [utils/convenios/unificador.py](D:/github/osc_unificado/utils/convenios/unificador.py), algumas UFs usam arquivos exclusivos ou fontes especificas:

- `AC`: usa apenas `convenios_ac.csv`
- `DF`: usa apenas `dados_credor_convenios_DF.xlsx`
- `PA`: inclui `*.csv`
- `RJ`: inclui os CSVs de transferencias e o arquivo principal em XLSX
- `GO`: inclui tambem `convenios_2008_2018.zip`
- `RN`: usa a base estadual `tranferencias.xlsx`
- `SE`: usa as planilhas estaduais `empenhos_*.xlsx`

Para GO, a fonte oficial usada para atualizar convenios esta em:

- [Dados Abertos Goias - busca por convenios](https://dadosabertos.go.gov.br/dataset/?q=convenios)

Script recomendado para baixar os arquivos:

```powershell
python utils/convenios/baixar_convenios_go_dadosabertos.py
```

O download organiza os recursos em `E:\dados\bases_convenios\GO\dadosabertos_goias_convenios\` e tambem sincroniza `convenios_2008_2018.zip` na raiz de `bases_convenios/GO/` para compatibilidade com o parser atual.

Regra do pipeline:

- a consolidacao inicial usa apenas arquivos brutos estaduais em `bases_convenios/<UF>/`
- a base federal em `bases_convenios/governo/` e usada somente no script de enriquecimento

## Fluxo recomendado de uso

Quando entrar uma base nova ou um ajuste de parser:

1. editar o parser ou o mapeamento da UF
2. reprocessar a UF afetada com `utils/convenios/unificador.py`
3. se fizer sentido, rodar `utils/convenios/enriquecer_processada_governo.py` para complementar dados
4. rodar `utils/convenios/auditar_processada.py`
5. revisar a aba do estado e a aba `Resumo` na auditoria

Exemplo pratico:

```powershell
python utils/convenios/unificador.py --ufs DF --force
python utils/convenios/enriquecer_processada_governo.py --ufs DF
python utils/convenios/auditar_processada.py
```

## Dependencias

O projeto usa principalmente:

- `pandas`
- `pyarrow`
- `openpyxl`

Se precisar instalar manualmente:

```powershell
pip install pandas pyarrow openpyxl
```

## Observacoes

- O projeto foi ajustado ao longo da construcao, entao as bases estaduais seguem heterogeneas e a base federal entra apenas como apoio no enriquecimento.
- A auditoria e a melhor forma de validar rapidamente se um parser ficou coerente.
- Quando houver mais de uma fonte para a mesma UF, vale sempre conferir se o enriquecimento nao ampliou demais a cobertura por match de nome.
