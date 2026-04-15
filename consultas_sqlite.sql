-- GUIA MESTRE DE CONSULTAS
-- Banco alvo: osc_unificado.sqlite
--
-- Como usar:
-- 1. Rode uma consulta por vez.
-- 2. Nas consultas por estado, troque o valor de `uf_alvo` no bloco `WITH parametros`.
-- 3. A tabela `transferencias` contem o schema principal.
-- 4. A tabela `transferencias_analitica` contem colunas derivadas para analise.
-- 5. Para dinheiro, use `valor_total` como campo monetario principal.
-- 6. A coluna `origem` distingue a trilha de carga, como `convenios`, `orcamento_geral` ou `convenios_federal`.
--
-- O que voce vai encontrar neste arquivo:
-- - estrutura do banco
-- - panorama nacional
-- - consultas reutilizaveis para qualquer UF
-- - consultas de entidades, municipios, anos e qualidade
-- - acesso a historias e auditoria
-- - join completo entre schema e camada analitica


-- ============================================================
-- 1. ESTRUTURA DO BANCO
-- O que voce encontra:
-- lista de tabelas e views disponiveis no SQLite.
-- ============================================================
SELECT name, type
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY type, name;


-- ============================================================
-- 2. TIPOS DA TABELA PRINCIPAL
-- O que voce encontra:
-- schema exato da tabela `transferencias`.
-- ============================================================
PRAGMA table_info(transferencias);


-- ============================================================
-- 3. CONTAGEM DE LINHAS POR TABELA
-- O que voce encontra:
-- volume de registros em cada tabela principal do banco.
-- ============================================================
SELECT 'transferencias' AS tabela, COUNT(*) AS linhas FROM transferencias
UNION ALL
SELECT 'transferencias_analitica' AS tabela, COUNT(*) AS linhas FROM transferencias_analitica
UNION ALL
SELECT 'arquivos_origem' AS tabela, COUNT(*) AS linhas FROM arquivos_origem
UNION ALL
SELECT 'historias' AS tabela, COUNT(*) AS linhas FROM historias
UNION ALL
SELECT 'auditoria_resumo' AS tabela, COUNT(*) AS linhas FROM auditoria_resumo;


-- ============================================================
-- 4. RESUMO NACIONAL POR UF
-- O que voce encontra:
-- ranking geral dos estados com valor total, registros e coberturas.
-- Fonte: view pronta `vw_resumo_uf`.
-- ============================================================
SELECT *
FROM vw_resumo_uf
ORDER BY valor_total DESC;


-- ============================================================
-- 5. TOP 10 UFS POR VALOR TOTAL
-- O que voce encontra:
-- os estados mais pesados financeiramente.
-- ============================================================
SELECT
    uf,
    registros,
    ROUND(valor_total, 2) AS valor_total,
    ROUND(ticket_medio, 2) AS ticket_medio
FROM vw_resumo_uf
ORDER BY valor_total DESC
LIMIT 10;


-- ============================================================
-- 6. TOP 10 UFS POR QUANTIDADE DE REGISTROS
-- O que voce encontra:
-- os estados com maior massa de linhas.
-- ============================================================
SELECT
    uf,
    registros,
    ROUND(valor_total, 2) AS valor_total
FROM vw_resumo_uf
ORDER BY registros DESC
LIMIT 10;


-- ============================================================
-- 7. TOP ENTIDADES DO PAIS
-- O que voce encontra:
-- os maiores beneficiarios considerando todas as UFs.
-- ============================================================
SELECT
    uf,
    nome_osc,
    cnpj,
    registros,
    ROUND(valor_total, 2) AS valor_total
FROM vw_top_entidades
ORDER BY valor_total DESC
LIMIT 30;


-- ============================================================
-- 8. PARAMETRO CENTRAL PARA CONSULTAS POR UF
-- O que voce encontra:
-- troque `BA` pela UF que quiser analisar.
-- Exemplo: 'SP', 'AM', 'MG', 'PR'.
-- ============================================================
WITH parametros AS (
    SELECT 'BA' AS uf_alvo
)
SELECT uf_alvo
FROM parametros;


-- ============================================================
-- 9. RESUMO DE UMA UF ESPECIFICA
-- O que voce encontra:
-- um retrato geral do estado escolhido.
-- ============================================================
WITH parametros AS (
    SELECT 'BA' AS uf_alvo
)
SELECT *
FROM vw_resumo_uf
WHERE uf = (SELECT uf_alvo FROM parametros);


-- ============================================================
-- 10. TOP ENTIDADES DA UF ESCOLHIDA
-- O que voce encontra:
-- as entidades com maior valor acumulado naquela UF.
-- ============================================================
WITH parametros AS (
    SELECT 'BA' AS uf_alvo
)
SELECT
    uf,
    nome_osc,
    cnpj,
    registros,
    ROUND(valor_total, 2) AS valor_total,
    ROUND(ticket_medio, 2) AS ticket_medio
FROM vw_top_entidades
WHERE uf = (SELECT uf_alvo FROM parametros)
ORDER BY valor_total DESC
LIMIT 20;


-- ============================================================
-- 11. SERIE ANUAL DA UF ESCOLHIDA
-- O que voce encontra:
-- evolucao anual de registros, valor total e ticket medio.
-- ============================================================
WITH parametros AS (
    SELECT 'BA' AS uf_alvo
)
SELECT
    uf,
    ano_num,
    registros,
    ROUND(valor_total, 2) AS valor_total,
    ROUND(ticket_medio, 2) AS ticket_medio
FROM vw_serie_anual
WHERE uf = (SELECT uf_alvo FROM parametros)
ORDER BY ano_num;


-- ============================================================
-- 12. SERIE ANUAL NACIONAL CONSOLIDADA
-- O que voce encontra:
-- a soma do pais por ano, sem separar UF.
-- ============================================================
SELECT
    ano_num,
    SUM(registros) AS registros,
    ROUND(SUM(valor_total), 2) AS valor_total
FROM vw_serie_anual
GROUP BY ano_num
ORDER BY ano_num;


-- ============================================================
-- 13. TOP MUNICIPIOS DA UF ESCOLHIDA
-- O que voce encontra:
-- os municipios com maior valor somado dentro da UF.
-- ============================================================
WITH parametros AS (
    SELECT 'BA' AS uf_alvo
)
SELECT
    t.uf,
    t.municipio,
    COUNT(*) AS registros,
    ROUND(SUM(CAST(t.valor_total AS NUMERIC)), 2) AS valor_total
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE t.uf = (SELECT uf_alvo FROM parametros)
GROUP BY t.uf, t.municipio
ORDER BY valor_total DESC
LIMIT 20;


-- ============================================================
-- 14. MAIORES TRANSFERENCIAS INDIVIDUAIS DO BANCO
-- O que voce encontra:
-- os maiores registros isolados, independentemente da UF.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    t.cnpj,
    ROUND(CAST(t.valor_total AS NUMERIC), 2) AS valor_total,
    t.municipio,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
ORDER BY CAST(t.valor_total AS NUMERIC) DESC
LIMIT 50;


-- ============================================================
-- 15. REGISTROS ACIMA DE 10 MILHOES
-- O que voce encontra:
-- contratos ou transferencias muito grandes, em qualquer UF.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    ROUND(CAST(t.valor_total AS NUMERIC), 2) AS valor_total,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE CAST(t.valor_total AS NUMERIC) >= 10000000
ORDER BY CAST(t.valor_total AS NUMERIC) DESC;


-- ============================================================
-- 16. ALERTAS DE QUALIDADE POR UF
-- O que voce encontra:
-- resumo de zeros, negativos, anos invalidos, sem municipio, sem objeto etc.
-- ============================================================
SELECT *
FROM vw_alertas_qualidade
ORDER BY anos_invalidos DESC, sem_objeto DESC, sem_municipio DESC;


-- ============================================================
-- 17. REGISTROS COM VALOR ZERO
-- O que voce encontra:
-- exemplos de linhas cujo valor foi carregado como zero.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    t.cnpj,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE a.valor_zero = 1
LIMIT 100;


-- ============================================================
-- 18. REGISTROS COM VALOR NEGATIVO
-- O que voce encontra:
-- linhas com valores negativos para revisao.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    t.cnpj,
    ROUND(CAST(t.valor_total AS NUMERIC), 2) AS valor_total,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE a.valor_negativo = 1
ORDER BY CAST(t.valor_total AS NUMERIC) ASC;


-- ============================================================
-- 19. REGISTROS COM ANO INVALIDO
-- O que voce encontra:
-- linhas cujo ano existe, mas foi classificado como invalido.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    t.cnpj,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE a.ano_valido = 0
  AND t.ano IS NOT NULL
LIMIT 100;


-- ============================================================
-- 20. REGISTROS SEM MUNICIPIO
-- O que voce encontra:
-- linhas sem municipio preenchido.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    ROUND(CAST(t.valor_total AS NUMERIC), 2) AS valor_total,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE a.tem_municipio = 0
LIMIT 100;


-- ============================================================
-- 21. REGISTROS SEM OBJETO
-- O que voce encontra:
-- linhas sem descricao de objeto, uteis para auditoria.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    ROUND(CAST(t.valor_total AS NUMERIC), 2) AS valor_total,
    t.modalidade
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE a.tem_objeto = 0
LIMIT 100;


-- ============================================================
-- 22. DUPLICADOS APARENTES
-- O que voce encontra:
-- linhas potencialmente repetidas no criterio do ETL.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    t.cnpj,
    ROUND(CAST(t.valor_total AS NUMERIC), 2) AS valor_total,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE a.duplicado_aparente = 1
LIMIT 100;


-- ============================================================
-- 23. COBERTURA DE DADOS POR UF
-- O que voce encontra:
-- porcentagem de cobertura de CNPJ, municipio, objeto e modalidade.
-- ============================================================
SELECT
    uf,
    ROUND(cobertura_cnpj_pct, 2) AS cobertura_cnpj_pct,
    ROUND(cobertura_municipio_pct, 2) AS cobertura_municipio_pct,
    ROUND(cobertura_objeto_pct, 2) AS cobertura_objeto_pct,
    ROUND(cobertura_modalidade_pct, 2) AS cobertura_modalidade_pct
FROM vw_resumo_uf
ORDER BY cobertura_objeto_pct ASC, cobertura_municipio_pct ASC;


-- ============================================================
-- 24. LISTA DE HISTORIAS DISPONIVEIS
-- O que voce encontra:
-- quais UFs tem narrativa salva na tabela `historias`.
-- ============================================================
SELECT uf, titulo
FROM historias
ORDER BY uf;


-- ============================================================
-- 25. LER A HISTORIA DE UMA UF
-- O que voce encontra:
-- o markdown integral da narrativa do estado escolhido.
-- ============================================================
WITH parametros AS (
    SELECT 'BA' AS uf_alvo
)
SELECT uf, titulo, markdown
FROM historias
WHERE uf = (SELECT uf_alvo FROM parametros);


-- ============================================================
-- 26. AUDITORIA RESUMIDA POR UF
-- O que voce encontra:
-- a aba Resumo da auditoria convertida para tabela SQL.
-- ============================================================
SELECT *
FROM auditoria_resumo
ORDER BY uf;


-- ============================================================
-- 27. JOIN COMPLETO ENTRE SCHEMA E ANALITICA
-- O que voce encontra:
-- uma amostra completa juntando os campos principais e os derivados.
-- Use essa consulta quando quiser montar analises mais customizadas.
-- ============================================================
SELECT
    t.uf,
    t.ano,
    t.valor_total,
    t.cnpj,
    t.nome_osc,
    t.mes,
    t.cod_municipio,
    t.municipio,
    t.objeto,
    t.modalidade,
    t.data_inicio,
    t.data_fim,
    a.ano_num,
    a.mes_num,
    a.tem_cnpj_valido,
    a.tem_municipio,
    a.tem_objeto,
    a.tem_modalidade,
    a.valor_zero,
    a.valor_negativo,
    a.ano_valido,
    a.mes_valido,
    a.entidade_base,
    a.municipio_base,
    a.modalidade_base,
    a.ano_mes,
    a.duplicado_aparente
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
LIMIT 100;


-- ============================================================
-- 28. MODELO PARA FILTRAR QUALQUER UF E QUALQUER ANO
-- O que voce encontra:
-- uma consulta-base que pode ser adaptada para estudos especificos.
-- ============================================================
WITH parametros AS (
    SELECT 'BA' AS uf_alvo, 2022 AS ano_alvo
)
SELECT
    t.uf,
    t.ano,
    t.nome_osc,
    ROUND(CAST(t.valor_total AS NUMERIC), 2) AS valor_total,
    t.municipio,
    t.objeto
FROM transferencias t
JOIN transferencias_analitica a
    ON a.transferencia_id = t.rowid
WHERE t.uf = (SELECT uf_alvo FROM parametros)
  AND t.ano = (SELECT ano_alvo FROM parametros)
ORDER BY CAST(t.valor_total AS NUMERIC) DESC
LIMIT 50;


-- ============================================================
-- 29. COBERTURA DE UFS POR ORIGEM E ANO
-- O que voce encontra:
-- para cada `origem` (marcador de carga), quantas UFs aparecem em cada ano.
-- ============================================================
WITH base AS (
    SELECT origem, ano, uf
    FROM transferencias
    WHERE origem IS NOT NULL
      AND ano IS NOT NULL
      AND uf IS NOT NULL
    GROUP BY origem, ano, uf
),
ufs_por_origem AS (
    SELECT
        origem,
        COUNT(DISTINCT uf) AS total_ufs_origem
    FROM base
    GROUP BY origem
),
cobertura AS (
    SELECT
        origem,
        ano,
        COUNT(DISTINCT uf) AS ufs_no_ano
    FROM base
    GROUP BY origem, ano
)
SELECT
    c.origem,
    c.ano,
    c.ufs_no_ano,
    u.total_ufs_origem,
    ROUND(c.ufs_no_ano * 100.0 / u.total_ufs_origem, 2) AS cobertura_ufs_pct
FROM cobertura c
JOIN ufs_por_origem u
    ON u.origem = c.origem
ORDER BY c.origem, c.ano;


-- ============================================================
-- 30. ANOS QUE APARECEM EM TODAS AS UFS DISPONIVEIS DA ORIGEM
-- O que voce encontra:
-- a intersecao de anos por `origem`, considerando apenas as UFs
-- que aquela origem realmente possui no banco.
-- ============================================================
WITH base AS (
    SELECT origem, ano, uf
    FROM transferencias
    WHERE origem IS NOT NULL
      AND ano IS NOT NULL
      AND uf IS NOT NULL
    GROUP BY origem, ano, uf
),
ufs_por_origem AS (
    SELECT
        origem,
        COUNT(DISTINCT uf) AS total_ufs_origem
    FROM base
    GROUP BY origem
),
cobertura AS (
    SELECT
        origem,
        ano,
        COUNT(DISTINCT uf) AS ufs_no_ano
    FROM base
    GROUP BY origem, ano
)
SELECT
    c.origem,
    c.ano,
    c.ufs_no_ano AS ufs_cobertas,
    u.total_ufs_origem
FROM cobertura c
JOIN ufs_por_origem u
    ON u.origem = c.origem
WHERE c.ufs_no_ano = u.total_ufs_origem
ORDER BY c.origem, c.ano;


-- ============================================================
-- 31. ANOS QUE APARECEM EM TODAS AS 27 UFS DO BANCO
-- O que voce encontra:
-- anos em que a origem cobre todas as UFs presentes no universo nacional
-- carregado no SQLite.
-- ============================================================
WITH base AS (
    SELECT origem, ano, uf
    FROM transferencias
    WHERE origem IS NOT NULL
      AND ano IS NOT NULL
      AND uf IS NOT NULL
    GROUP BY origem, ano, uf
),
universo_nacional AS (
    SELECT COUNT(DISTINCT uf) AS total_ufs_brasil
    FROM transferencias
    WHERE uf IS NOT NULL
),
cobertura AS (
    SELECT
        origem,
        ano,
        COUNT(DISTINCT uf) AS ufs_no_ano
    FROM base
    GROUP BY origem, ano
)
SELECT
    c.origem,
    c.ano,
    c.ufs_no_ano
FROM cobertura c
CROSS JOIN universo_nacional u
WHERE c.ufs_no_ano = u.total_ufs_brasil
ORDER BY c.origem, c.ano;


-- ============================================================
-- 32. DIAGNOSTICO DE UFS FALTANTES EM UM ANO DE UMA ORIGEM
-- O que voce encontra:
-- informa quais UFs ainda faltam para fechar a cobertura de uma origem
-- em um ano especifico, usando como referencia as UFs existentes
-- naquela propria origem.
-- ============================================================
WITH parametros AS (
    SELECT 'orcamento_geral' AS origem_alvo, 2024 AS ano_alvo
),
universo AS (
    SELECT DISTINCT uf
    FROM transferencias
    WHERE origem = (SELECT origem_alvo FROM parametros)
),
presentes AS (
    SELECT DISTINCT uf
    FROM transferencias
    WHERE origem = (SELECT origem_alvo FROM parametros)
      AND ano = (SELECT ano_alvo FROM parametros)
)
SELECT
    u.uf AS uf_faltante
FROM universo u
LEFT JOIN presentes p
    ON p.uf = u.uf
WHERE p.uf IS NULL
ORDER BY u.uf;
