from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (ROOT, SRC):
    as_str = str(path)
    if as_str not in sys.path:
        sys.path.insert(0, as_str)
