# Estrutura auditavel do projeto

Este repositorio passa a seguir uma separacao simples entre codigo versionado, dados gerados e evidencias de execucao.

## Pastas principais

- `utils/`: parsers, consolidadores e rotinas principais por trilha (`convenios`, `orcamento_geral`, `capitais`).
- `scripts/`: scripts auxiliares de auditoria, analise e geracao de graficos.
- `historia/`: textos e artefatos editoriais versionados.
- `docs/`: documentacao operacional para reprocessamento, auditoria e curadoria.
- `outputs/`: tudo que for gerado pelo pipeline e nao deve ser versionado.
- `logs/`: logs de execucao locais, tambem fora do versionamento.

## Convencoes para saidas

- `outputs/relatorios/`: CSVs e MDs de relatorio gerados pelos utilitarios.
- `outputs/manifests/`: manifestos JSON com parametros, tempos e status das execucoes.
- `outputs/analise_origens_anuais/`: agregados anuais, tabelas intermediarias e graficos HTML da analise por origem.
- `logs/pipelines/`: logs do `unificador.py`.
- `logs/convenios/`: um log por UF no processamento de convenios.
- `logs/orcamento_geral/`: um log por UF no processamento estadual.
- `logs/capitais/`: um log por capital.

## Regras praticas

- Codigo fonte nao deve gravar relatorios na raiz do repositorio.
- Toda execucao em lote deve gerar manifesto JSON em `outputs/manifests/`.
- Toda execucao longa deve gerar log em `logs/`.
- Dados brutos baixados novamente devem entrar nas pastas configuradas em `config.py` ou pelas variaveis `OSC_*`.
- Arquivos temporarios, parquet e sqlite continuam fora do Git.
