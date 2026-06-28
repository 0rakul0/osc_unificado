from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import cli_default, ORCAMENTO_GERAL_PROCESSADA_DIR
from utils.core.audit_runs import build_run_file_path, ensure_dir, utc_now_iso, write_json
from utils.orcamento_geral.paths import add_scope_argument


def available_ufs() -> list[str]:
    parsers_dir = Path(__file__).resolve().parent / "parsers"
    ufs: list[str] = []
    for path in sorted(parsers_dir.glob("processar_orcamento_geral_*.py")):
        suffix = path.stem.removeprefix("processar_orcamento_geral_").upper()
        if len(suffix) == 2:
            ufs.append(suffix)
    return ufs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa os processadores estaduais de orcamento_geral em lote ou por UF."
    )
    add_scope_argument(parser)
    parser.add_argument(
        "--ufs",
        nargs="*",
        help="Lista opcional de UFs para processar. Se omitido, executa todas as UFs disponiveis.",
    )
    parser.add_argument(
        "--output-dir",
        default=cli_default(ORCAMENTO_GERAL_PROCESSADA_DIR),
        help="Pasta de saida comum para os parquets da trilha estadual.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continua processando as proximas UFs mesmo se alguma falhar.",
    )
    parser.add_argument(
        "--logs-dir",
        default=str(ROOT_DIR / "logs" / "orcamento_geral"),
        help="Pasta para logs por UF.",
    )
    parser.add_argument(
        "--manifest-dir",
        default=str(ROOT_DIR / "outputs" / "manifests" / "orcamento_geral"),
        help="Pasta para manifestos JSON do lote.",
    )
    return parser.parse_args()


def selected_ufs(raw_ufs: list[str] | None) -> list[str]:
    all_ufs = available_ufs()
    if not raw_ufs:
        return all_ufs

    normalized = []
    unknown = []
    allowed = set(all_ufs)
    for item in raw_ufs:
        uf = item.strip().upper()
        if not uf:
            continue
        if uf in allowed:
            normalized.append(uf)
        else:
            unknown.append(uf)
    if unknown:
        raise ValueError(f"UFs sem processador estadual: {', '.join(sorted(set(unknown)))}")
    return normalized


def script_path_for_uf(uf: str) -> Path:
    return Path(__file__).resolve().parent / "parsers" / f"processar_orcamento_geral_{uf.lower()}.py"


def run_state_processor(uf: str, scope: str, output_dir: str) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(script_path_for_uf(uf)),
        "--scope",
        scope,
        "--output-dir",
        output_dir,
    ]
    return subprocess.run(command, text=True, capture_output=True, check=False)


def main() -> None:
    args = parse_args()
    ufs = selected_ufs(args.ufs)
    failures: list[str] = []
    run_started = datetime.now(timezone.utc)
    logs_dir = ensure_dir(Path(args.logs_dir))
    manifest_dir = ensure_dir(Path(args.manifest_dir))
    manifest_steps: list[dict[str, object]] = []

    print(f"Escopo: {args.scope}")
    print(f"Saida comum: {args.output_dir}")

    for uf in ufs:
        print(f"\n[{uf}] Executando processador estadual...")
        started = datetime.now(timezone.utc)
        result = run_state_processor(uf, args.scope, args.output_dir)
        finished = datetime.now(timezone.utc)
        log_path = logs_dir / f"{uf}_{args.scope}.log"
        log_content = (result.stdout or "").strip()
        err_content = (result.stderr or "").strip()
        with log_path.open("w", encoding="utf-8", errors="replace") as handle:
            if log_content:
                handle.write(log_content + "\n")
            if err_content:
                handle.write(err_content + "\n")
        if log_content:
            print(log_content)
        manifest_steps.append(
            {
                "uf": uf,
                "scope": args.scope,
                "log_path": str(log_path),
                "started_at": started.replace(microsecond=0).isoformat(),
                "finished_at": finished.replace(microsecond=0).isoformat(),
                "duration_seconds": round((finished - started).total_seconds(), 3),
                "returncode": result.returncode,
                "status": "ok" if result.returncode == 0 else "failed",
            }
        )
        if result.returncode == 0:
            print(f"[{uf}] OK")
            continue

        failures.append(uf)
        print(f"[{uf}] FALHOU")
        if result.stderr:
            print(result.stderr.strip())
        if not args.continue_on_error:
            break

    if failures:
        manifest_path = build_run_file_path(manifest_dir, f"processar_estados_{args.scope}")
        write_json(
            manifest_path,
            {
                "runner": "utils/orcamento_geral/processar_estados.py",
                "scope": args.scope,
                "output_dir": args.output_dir,
                "ufs": ufs,
                "started_at": run_started.replace(microsecond=0).isoformat(),
                "finished_at": utc_now_iso(),
                "failures": failures,
                "steps": manifest_steps,
            },
        )
        raise SystemExit(f"Falha em: {', '.join(failures)}")

    manifest_path = build_run_file_path(manifest_dir, f"processar_estados_{args.scope}")
    write_json(
        manifest_path,
        {
            "runner": "utils/orcamento_geral/processar_estados.py",
            "scope": args.scope,
            "output_dir": args.output_dir,
            "ufs": ufs,
            "started_at": run_started.replace(microsecond=0).isoformat(),
            "finished_at": utc_now_iso(),
            "failures": [],
            "steps": manifest_steps,
        },
    )
    print(f"\nProcessamento concluido para {len(ufs)} UF(s).")


if __name__ == "__main__":
    main()
