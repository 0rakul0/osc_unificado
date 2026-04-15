from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parent

PIPELINE_SCRIPTS = {
    "convenios": ROOT_DIR / "utils" / "convenios" / "processar_convenios.py",
    "orcamento_geral": ROOT_DIR / "utils" / "orcamento_geral" / "processar_estados.py",
    "capitais": ROOT_DIR / "utils" / "capitais" / "processar_capitais.py",
    "sqlite": ROOT_DIR / "etl_parquets_sqlite.py",
}

PIPELINE_ALIASES = {
    "convenio": "convenios",
    "orcamento": "orcamento_geral",
    "orcamento-geral": "orcamento_geral",
    "capital": "capitais",
    "etl": "sqlite",
    "banco": "sqlite",
}
DEFAULT_PIPELINE_ORDER = ["convenios", "orcamento_geral", "capitais", "sqlite"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa o fluxo completo do projeto, encadeando as trilhas principais."
    )
    parser.add_argument(
        "--only",
        nargs="*",
        help="Executa apenas as pipelines informadas. Padrao: roda tudo na ordem completa.",
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        default=[],
        help="Pipelines a pular explicitamente.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continua para a proxima etapa mesmo se alguma pipeline falhar.",
    )
    return parser.parse_args()


def normalize_pipeline(value: str) -> str:
    key = value.strip().lower()
    return PIPELINE_ALIASES.get(key, key)


def normalize_pipeline_list(values: list[str] | None) -> list[str]:
    if not values:
        return DEFAULT_PIPELINE_ORDER.copy()

    normalized: list[str] = []
    for value in values:
        pipeline = normalize_pipeline(value)
        if pipeline not in PIPELINE_SCRIPTS:
            allowed = ", ".join(sorted(PIPELINE_SCRIPTS))
            raise SystemExit(f"Pipeline invalida: {value!r}. Use uma destas: {allowed}.")
        if pipeline not in normalized:
            normalized.append(pipeline)
    return normalized


def main() -> None:
    args = parse_args()
    selected = normalize_pipeline_list(args.only)
    skipped = set(normalize_pipeline_list(args.skip)) if args.skip else set()
    pipelines = [pipeline for pipeline in selected if pipeline not in skipped]

    if not pipelines:
        raise SystemExit("Nenhuma pipeline restante para executar.")

    failures: list[str] = []

    print(f"Ordem de execucao: {', '.join(pipelines)}")
    for pipeline in pipelines:
        script_path = PIPELINE_SCRIPTS[pipeline]
        print(f"\n[{pipeline}] Executando {script_path.name}...")
        result = subprocess.run([sys.executable, str(script_path)], check=False)
        if result.returncode == 0:
            print(f"[{pipeline}] OK")
            continue

        failures.append(pipeline)
        print(f"[{pipeline}] FALHOU (codigo {result.returncode})")
        if not args.continue_on_error:
            break

    if failures:
        raise SystemExit(f"Falha em: {', '.join(failures)}")

    print("\nFluxo completo concluido com sucesso.")


if __name__ == "__main__":
    main()
