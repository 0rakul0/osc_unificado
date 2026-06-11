@echo off
setlocal

cd /d "%~dp0"

set "PY=.venv\Scripts\python.exe"
set "SYS_PY=python"
set "ORC_DIR=E:\dados\orcamento_geral_processada"

if not exist "%PY%" (
  echo ERRO: nao encontrei %PY%.
  exit /b 1
)

echo.
echo [1/8] Processando convenios estaduais...
"%PY%" utils\convenios\processar_convenios.py --force
if errorlevel 1 exit /b %errorlevel%

echo.
echo [2/8] Processando orcamento geral estadual em lote...
"%PY%" utils\orcamento_geral\processar_estados.py --continue-on-error

echo.
echo [3/8] Reprocessando excecoes da trilha estadual...
"%PY%" utils\orcamento_geral\parsers\processar_orcamento_geral_am.py
if errorlevel 1 exit /b %errorlevel%
"%PY%" utils\orcamento_geral\parsers\processar_orcamento_geral_to.py
if errorlevel 1 exit /b %errorlevel%

echo.
echo [4/8] Reprocessando parsers estaduais que dependem de pacotes fora da venv...
%SYS_PY% utils\orcamento_geral\parsers\processar_orcamento_geral_ap.py
%SYS_PY% utils\orcamento_geral\parsers\processar_orcamento_geral_rj.py
%SYS_PY% utils\orcamento_geral\parsers\processar_orcamento_geral_sp.py
%SYS_PY% utils\orcamento_geral\parsers\processar_orcamento_geral_mt.py

echo.
echo [5/8] Processando capitais...
"%PY%" utils\capitais\processar_capitais.py
if errorlevel 1 exit /b %errorlevel%
"%PY%" utils\capitais\processar_recife_despesas_lookup_local.py
if errorlevel 1 exit /b %errorlevel%
"%PY%" utils\capitais\processar_despesas_capitais_extras.py
if errorlevel 1 exit /b %errorlevel%
"%PY%" utils\capitais\consolidar_capitais_nome_padrao.py
if errorlevel 1 exit /b %errorlevel%

echo.
echo [6/8] Normalizando marcadores de origem...
"%PY%" utils\normalizar_origens_processadas.py
if errorlevel 1 exit /b %errorlevel%

echo.
echo [7/8] Removendo SQLite anterior...
if exist E:\dados\sqlite\osc_unificado.sqlite del /f /q E:\dados\sqlite\osc_unificado.sqlite
if exist E:\dados\sqlite\osc_unificado.sqlite-journal del /f /q E:\dados\sqlite\osc_unificado.sqlite-journal

echo.
echo [8/8] Carregando SQLite com convenios, capitais e orcamento geral estadual...
"%PY%" etl_parquets_sqlite.py --extra-processed-dir "%ORC_DIR%"
if errorlevel 1 exit /b %errorlevel%

echo.
echo OK: processamento completo e banco atualizado.
endlocal
