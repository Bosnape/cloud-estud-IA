import sys
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(raiz))
sys.path.insert(0, str(raiz / "app"))
