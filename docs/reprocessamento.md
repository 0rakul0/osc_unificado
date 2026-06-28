# Reprocessamento e reproducao

Este documento resume o caminho minimo para recriar o projeto em outra maquina com foco em curadoria e auditoria.

## 1. Configurar caminhos de dados

O projeto aceita caminhos locais padrao ou sobrescritos por variaveis de ambiente:

- `OSC_BASES_CONVENIOS_DIR`
- `OSC_BASES_ORCAMENTO_GERAL_DIR`
- `OSC_BASES_ORCAMENTO_GERAL_CAPITAIS_DIR`
- `OSC_BASES_CONVENIOS_CAPITAIS_DIR`
- `OSC_PROCESSADA_DIR`
- `OSC_ORCAMENTO_GERAL_PROCESSADA_DIR`
- `OSC_CAPITAIS_PROCESSADA_DIR`
- `OSC_SQLITE_PATH`

Se nada for configurado, os defaults sao resolvidos por [config.py](/D:/github/osc_unificado/config.py).

## 2. Rodar os processamentos principais

Antes de reprocessar convenios estaduais, vale conferir o inventario de fontes em [fontes_convenios_estaduais.md](/D:/github/osc_unificado/docs/fontes_convenios_estaduais.md).

Processamento completo:

```powershell
python D:\github\osc_unificado\unificador.py
```

Apenas convenios:

```powershell
python D:\github\osc_unificado\utils\convenios\processar_convenios.py
```

Apenas orcamento geral estadual:

```powershell
python D:\github\osc_unificado\utils\orcamento_geral\processar_estados.py --scope despesa
```

Apenas capitais:

```powershell
python D:\github\osc_unificado\utils\capitais\processar_capitais.py
```

## 3. Evidencias geradas

Depois de cada execucao em lote, verificar:

- `logs/`: mostra o detalhe operacional por pipeline, UF ou capital.
- `outputs/manifests/`: registra parametros, inicio, fim, duracao e status.
- `outputs/relatorios/`: concentra relatorios de apoio e checagens.

## 4. Analise anual por origem

Para recriar os agregados anuais e os boxplots HTML usando os dados do SQLite:

```powershell
python D:\github\osc_unificado\scripts\gerar_analise_origens_anuais.py
```

Saidas esperadas:

- `outputs/analise_origens_anuais/agregados_uf_ano/`
- `outputs/analise_origens_anuais/tabelas/`
- `outputs/analise_origens_anuais/graficos/`

## 5. Checklist de curadoria

- Conferir se os dados brutos estao nas pastas corretas antes de reprocessar.
- Validar se os manifestos JSON foram gerados para cada lote.
- Revisar outliers e ruídos antes de usar graficos para inferencia substantiva.
- Registrar em `docs/` qualquer excecao nova de parser, filtro ou regra de negocio.
