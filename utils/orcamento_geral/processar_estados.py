from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import cli_default, ORCAMENTO_GERAL_PROCESSADA_DIR
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

    print(f"Escopo: {args.scope}")
    print(f"Saida comum: {args.output_dir}")

    for uf in ufs:
        print(f"\n[{uf}] Executando processador estadual...")
        result = run_state_processor(uf, args.scope, args.output_dir)
        if result.stdout:
            print(result.stdout.strip())
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
        raise SystemExit(f"Falha em: {', '.join(failures)}")

    print(f"\nProcessamento concluido para {len(ufs)} UF(s).")


if __name__ == "__main__":
    main()
