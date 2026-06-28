from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.capitais.registry import CAPITAL_CONFIGS
from utils.core.audit_runs import build_run_file_path, ensure_dir, utc_now_iso, write_json
from utils.capitais.shared import parse_args, find_source_files, write_capital_parquet, CapitalConfig


def selected_configs(capitais: list[str] | None) -> list[CapitalConfig]:
    if not capitais:
        return CAPITAL_CONFIGS

    selected = {item.strip().lower() for item in capitais if item.strip()}
    resolved: list[CapitalConfig] = []
    for config in CAPITAL_CONFIGS:
        aliases = {
            config.key,
            config.uf.lower(),
            config.municipio.lower(),
            config.folder.lower(),
            config.municipio.lower().replace(" ", ""),
        }
        if aliases & selected:
            resolved.append(config)
    return resolved


def main() -> None:
    args = parse_args()
    base_dir = Path(args.base_dir)
    output_dir = Path(args.output_dir)
    logs_dir = ensure_dir(ROOT_DIR / "logs" / "capitais")
    manifest_dir = ensure_dir(ROOT_DIR / "outputs" / "manifests" / "capitais")
    run_started = datetime.now(timezone.utc)
    configs = selected_configs(args.capitais)
    if not configs:
        raise ValueError("Nenhuma capital correspondente foi encontrada no filtro informado.")

    summaries: list[str] = []
    steps: list[dict[str, object]] = []
    for config in configs:
        started = datetime.now(timezone.utc)
        paths = find_source_files(base_dir, config)
        if not paths:
            print(f"Sem arquivos para {config.municipio} ({config.uf}).")
            steps.append(
                {
                    "capital": config.key,
                    "uf": config.uf,
                    "municipio": config.municipio,
                    "status": "missing_sources",
                    "source_files": [],
                    "started_at": started.replace(microsecond=0).isoformat(),
                    "finished_at": utc_now_iso(),
                }
            )
            continue
        log_path = logs_dir / f"{config.uf}_{config.key}.log"
        try:
            output_path, source_rows, parquet_rows = write_capital_parquet(config, paths, output_dir, args.batch_size)
            log_path.write_text(
                "\n".join(
                    [
                        f"capital={config.key}",
                        f"uf={config.uf}",
                        f"municipio={config.municipio}",
                        f"source_files={len(paths)}",
                        *[str(path) for path in paths],
                        f"source_rows={source_rows}",
                        f"parquet_rows={parquet_rows}",
                        f"output={output_path}",
                    ]
                ),
                encoding="utf-8",
            )
            steps.append(
                {
                    "capital": config.key,
                    "uf": config.uf,
                    "municipio": config.municipio,
                    "status": "ok",
                    "source_files": [str(path) for path in paths],
                    "source_rows": source_rows,
                    "parquet_rows": parquet_rows,
                    "output_path": str(output_path),
                    "log_path": str(log_path),
                    "started_at": started.replace(microsecond=0).isoformat(),
                    "finished_at": utc_now_iso(),
                }
            )
        except Exception as exc:
            log_path.write_text(
                "\n".join(
                    [
                        f"capital={config.key}",
                        f"uf={config.uf}",
                        f"municipio={config.municipio}",
                        f"erro={type(exc).__name__}: {exc}",
                    ]
                ),
                encoding="utf-8",
            )
            steps.append(
                {
                    "capital": config.key,
                    "uf": config.uf,
                    "municipio": config.municipio,
                    "status": "failed",
                    "source_files": [str(path) for path in paths],
                    "log_path": str(log_path),
                    "error": f"{type(exc).__name__}: {exc}",
                    "started_at": started.replace(microsecond=0).isoformat(),
                    "finished_at": utc_now_iso(),
                }
            )
            raise
        summaries.append(
            f"{config.municipio} ({config.uf}) -> {output_path.name}: origem={source_rows}, parquet={parquet_rows}"
        )
        print(summaries[-1])

    if summaries:
        print("Capitais processadas:")
        for line in summaries:
            print(f"- {line}")
    manifest_path = build_run_file_path(manifest_dir, "processar_capitais")
    write_json(
        manifest_path,
        {
            "runner": "utils/capitais/processar_capitais.py",
            "base_dir": str(base_dir),
            "output_dir": str(output_dir),
            "batch_size": args.batch_size,
            "capitais": [config.key for config in configs],
            "started_at": run_started.replace(microsecond=0).isoformat(),
            "finished_at": utc_now_iso(),
            "steps": steps,
        },
    )


if __name__ == "__main__":
    main()
