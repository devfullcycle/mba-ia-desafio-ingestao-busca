from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

as_str = str(ROOT)
if as_str not in sys.path:
    sys.path.insert(0, as_str)
