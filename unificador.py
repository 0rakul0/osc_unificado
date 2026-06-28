from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.core.audit_runs import build_run_file_path, ensure_dir, utc_now_iso, write_json

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
    parser.add_argument(
        "--logs-dir",
        default=str(ROOT_DIR / "logs" / "pipelines"),
        help="Pasta para logs das pipelines executadas pelo unificador.",
    )
    parser.add_argument(
        "--manifest-dir",
        default=str(ROOT_DIR / "outputs" / "manifests" / "pipelines"),
        help="Pasta para manifestos JSON de execucao do unificador.",
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
    run_started = datetime.now(timezone.utc)
    logs_dir = ensure_dir(Path(args.logs_dir))
    manifest_dir = ensure_dir(Path(args.manifest_dir))
    manifest_rows: list[dict[str, object]] = []

    print(f"Ordem de execucao: {', '.join(pipelines)}")
    for pipeline in pipelines:
        script_path = PIPELINE_SCRIPTS[pipeline]
        print(f"\n[{pipeline}] Executando {script_path.name}...")
        command = [sys.executable, str(script_path)]
        log_path = logs_dir / f"{pipeline}.log"
        started = datetime.now(timezone.utc)
        with log_path.open("w", encoding="utf-8", errors="replace") as handle:
            result = subprocess.run(command, check=False, stdout=handle, stderr=subprocess.STDOUT, text=True)
        finished = datetime.now(timezone.utc)
        manifest_rows.append(
            {
                "pipeline": pipeline,
                "script": str(script_path),
                "command": command,
                "log_path": str(log_path),
                "started_at": started.replace(microsecond=0).isoformat(),
                "finished_at": finished.replace(microsecond=0).isoformat(),
                "duration_seconds": round((finished - started).total_seconds(), 3),
                "returncode": result.returncode,
                "status": "ok" if result.returncode == 0 else "failed",
            }
        )
        if result.returncode == 0:
            print(f"[{pipeline}] OK")
            continue

        failures.append(pipeline)
        print(f"[{pipeline}] FALHOU (codigo {result.returncode})")
        if not args.continue_on_error:
            break

    if failures:
        manifest_path = build_run_file_path(manifest_dir, "unificador")
        write_json(
            manifest_path,
            {
                "runner": "unificador.py",
                "started_at": run_started.replace(microsecond=0).isoformat(),
                "finished_at": utc_now_iso(),
                "pipelines": pipelines,
                "continue_on_error": args.continue_on_error,
                "failures": failures,
                "steps": manifest_rows,
            },
        )
        raise SystemExit(f"Falha em: {', '.join(failures)}")

    manifest_path = build_run_file_path(manifest_dir, "unificador")
    write_json(
        manifest_path,
        {
            "runner": "unificador.py",
            "started_at": run_started.replace(microsecond=0).isoformat(),
            "finished_at": utc_now_iso(),
            "pipelines": pipelines,
            "continue_on_error": args.continue_on_error,
            "failures": [],
            "steps": manifest_rows,
        },
    )
    print("\nFluxo completo concluido com sucesso.")


if __name__ == "__main__":
    main()
