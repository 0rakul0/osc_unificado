from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.orcamento_geral.parsers.processar_orcamento_geral_rn import main

if __name__ == "__main__":
    main()
