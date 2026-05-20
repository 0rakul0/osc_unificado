from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


ALL_UFS = [
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
]


@dataclass(frozen=True)
class Downloader:
    uf: str
    script: str
    note: str = ""
    supports_overwrite: bool = False


DOWNLOADERS: dict[str, Downloader] = {
    "AC": Downloader("AC", "utils/orcamento_geral/baixar_orcamento_geral_ac.py"),
    "AL": Downloader("AL", "utils/orcamento_geral/baixar_orcamento_geral_al.py"),
    "AM": Downloader("AM", "utils/orcamento_geral/baixar_orcamento_geral_am.py"),
    "AP": Downloader("AP", "utils/orcamento_geral/baixar_orcamento_geral_ap.py", supports_overwrite=True),
    "DF": Downloader("DF", "utils/orcamento_geral/baixar_orcamento_geral_df.py"),
    "MA": Downloader("MA", "utils/orcamento_geral/baixar_orcamento_geral_ma.py"),
    "PI": Downloader("PI", "utils/orcamento_geral/baixar_orcamento_geral_pi.py"),
    "PR": Downloader("PR", "utils/orcamento_geral/baixar_orcamento_geral_pr.py", supports_overwrite=True),
    "RJ": Downloader("RJ", "utils/orcamento_geral/baixar_orcamento_geral_rj.py"),
    "RN": Downloader("RN", "utils/orcamento_geral/baixar_orcamento_geral_rn.py"),
    "RO": Downloader("RO", "utils/orcamento_geral/baixar_orcamento_geral_ro.py"),
    "RR": Downloader("RR", "utils/orcamento_geral/baixar_orcamento_geral_rr.py"),
    "SC": Downloader("SC", "utils/orcamento_geral/baixar_orcamento_geral_sc.py"),
    "SE": Downloader("SE", "utils/orcamento_geral/baixar_orcamento_geral_se.py"),
    "SP": Downloader(
        "SP",
        "utils/orcamento_geral/baixar_orcamento_geral_sp_despesas.py",
        note="usa o webservice de despesas gerais, nao o portal de parcerias",
        supports_overwrite=True,
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa em lote os downloaders disponiveis de orcamento geral estadual."
    )
    parser.add_argument(
        "--ufs",
        nargs="*",
        help="UFs a baixar. Se omitido, tenta todas as UFs com downloader disponivel.",
    )
    parser.add_argument(
        "--skip-ufs",
        nargs="*",
        default=[],
        help="UFs a pular no lote.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rebaixa arquivos existentes nos downloaders que suportam --overwrite.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra os comandos sem executar.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Para no primeiro erro. Por padrao, continua nas proximas UFs.",
    )
    parser.add_argument(
        "--process-after",
        action="store_true",
        help="Depois dos downloads bem-sucedidos, executa processar_estados.py para essas UFs.",
    )
    parser.add_argument(
        "--report",
        default="relatorio_download_orcamento_geral.csv",
        help="CSV de status do lote.",
    )
    parser.add_argument(
        "--logs-dir",
        default="logs/download_orcamento_geral",
        help="Pasta para logs stdout/stderr por UF.",
    )
    return parser.parse_args()


def normalize_ufs(raw_ufs: list[str] | None) -> list[str]:
    if not raw_ufs:
        return sorted(DOWNLOADERS)
    selected: list[str] = []
    for raw in raw_ufs:
        uf = raw.strip().upper()
        if uf and uf not in selected:
            selected.append(uf)
    return selected


def command_for(downloader: Downloader, overwrite: bool) -> list[str]:
    command = [sys.executable, str(ROOT_DIR / downloader.script)]
    if overwrite and downloader.supports_overwrite:
        command.append("--overwrite")
    return command


def run_command(command: list[str], log_path: Path, dry_run: bool) -> tuple[int | None, float]:
    started = datetime.now()
    if dry_run:
        return None, 0.0

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", errors="replace") as log_file:
        process = subprocess.run(
            command,
            cwd=ROOT_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    elapsed = (datetime.now() - started).total_seconds()
    return process.returncode, elapsed


def write_report(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "uf",
        "status",
        "returncode",
        "seconds",
        "command",
        "log",
        "note",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_successful_ufs(ufs: list[str], report_rows: list[dict[str, object]], logs_dir: Path, dry_run: bool) -> None:
    if not ufs:
        return
    command = [
        sys.executable,
        str(ROOT_DIR / "utils/orcamento_geral/processar_estados.py"),
        "--ufs",
        *ufs,
        "--continue-on-error",
    ]
    log_path = logs_dir / "processar_estados.log"
    print(f"[processar] {' '.join(command)}")
    returncode, seconds = run_command(command, log_path, dry_run)
    status = "dry-run" if dry_run else ("ok" if returncode == 0 else "erro")
    report_rows.append(
        {
            "uf": "PROCESSAR",
            "status": status,
            "returncode": "" if returncode is None else returncode,
            "seconds": f"{seconds:.1f}",
            "command": " ".join(command),
            "log": str(log_path),
            "note": ",".join(ufs),
        }
    )


def main() -> None:
    args = parse_args()
    selected = normalize_ufs(args.ufs)
    skip = {uf.strip().upper() for uf in args.skip_ufs}
    selected = [uf for uf in selected if uf not in skip]

    logs_dir = Path(args.logs_dir)
    report_rows: list[dict[str, object]] = []
    successful_ufs: list[str] = []

    missing = [uf for uf in selected if uf not in DOWNLOADERS]
    runnable = [uf for uf in selected if uf in DOWNLOADERS]

    for uf in missing:
        report_rows.append(
            {
                "uf": uf,
                "status": "sem_downloader",
                "returncode": "",
                "seconds": "0.0",
                "command": "",
                "log": "",
                "note": "ha parser ou bruto local/manual, mas nao ha downloader em utils/orcamento_geral/downloads",
            }
        )
        print(f"[{uf}] sem downloader disponivel")

    for uf in runnable:
        downloader = DOWNLOADERS[uf]
        command = command_for(downloader, args.overwrite)
        log_path = logs_dir / f"{uf}.log"
        print(f"[{uf}] {' '.join(command)}")
        returncode, seconds = run_command(command, log_path, args.dry_run)
        status = "dry-run" if args.dry_run else ("ok" if returncode == 0 else "erro")
        if status == "ok":
            successful_ufs.append(uf)
        report_rows.append(
            {
                "uf": uf,
                "status": status,
                "returncode": "" if returncode is None else returncode,
                "seconds": f"{seconds:.1f}",
                "command": " ".join(command),
                "log": str(log_path),
                "note": downloader.note,
            }
        )
        if status == "erro" and args.stop_on_error:
            break

    if args.process_after:
        process_successful_ufs(successful_ufs, report_rows, logs_dir, args.dry_run)

    report_path = Path(args.report)
    write_report(report_path, report_rows)
    print(f"Relatorio: {report_path}")

    if missing:
        print("Sem downloader:", ", ".join(missing))
    if args.dry_run:
        print("Dry run concluido.")


if __name__ == "__main__":
    main()
