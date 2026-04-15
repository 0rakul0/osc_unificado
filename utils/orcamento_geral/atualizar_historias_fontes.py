from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from project_paths import HISTORIA_DIR
from utils.orcamento_geral.historias_fontes import provenance_section
from utils.orcamento_geral.registry import STATE_CAPITALS


PROVENANCE_HEADING = "## Proveniencia das fontes"
CONCLUSION_HEADING = "## Conclusao"


def inject_section(markdown: str, section: str) -> str:
    conclusion_index = markdown.find(CONCLUSION_HEADING)
    if conclusion_index == -1:
        conclusion_index = len(markdown)

    current_index = markdown.find(PROVENANCE_HEADING)
    if current_index != -1 and current_index < conclusion_index:
        prefix = markdown[:current_index].rstrip()
    else:
        prefix = markdown[:conclusion_index].rstrip()

    suffix = markdown[conclusion_index:].lstrip()
    parts = [prefix, section.rstrip()]
    if suffix:
        parts.append(suffix)
    return "\n\n".join(part for part in parts if part)


def main() -> None:
    updated = 0
    for entry in STATE_CAPITALS:
        path = HISTORIA_DIR / f"{entry.uf}.md"
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        enriched = inject_section(original, provenance_section(entry.uf))
        path.write_text(enriched, encoding="utf-8")
        updated += 1
        print(f"Historia atualizada: {path.name}")
    print(f"Total de historias enriquecidas: {updated}")


if __name__ == "__main__":
    main()
