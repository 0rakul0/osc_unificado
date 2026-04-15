from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.capitais.registry import CAPITAL_CONFIGS
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
    configs = selected_configs(args.capitais)
    if not configs:
        raise ValueError("Nenhuma capital correspondente foi encontrada no filtro informado.")

    summaries: list[str] = []
    for config in configs:
        paths = find_source_files(base_dir, config)
        if not paths:
            print(f"Sem arquivos para {config.municipio} ({config.uf}).")
            continue
        output_path, source_rows, parquet_rows = write_capital_parquet(config, paths, output_dir, args.batch_size)
        summaries.append(
            f"{config.municipio} ({config.uf}) -> {output_path.name}: origem={source_rows}, parquet={parquet_rows}"
        )
        print(summaries[-1])

    if summaries:
        print("Capitais processadas:")
        for line in summaries:
            print(f"- {line}")


if __name__ == "__main__":
    main()
