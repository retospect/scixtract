from __future__ import annotations

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
_src = _repo_root / "src"
_src_str = str(_src)
if _src_str in sys.path:
    sys.path.remove(_src_str)
sys.path.insert(0, _src_str)


_to_delete = [
    name for name in sys.modules if name == "scixtract" or name.startswith("scixtract.")
]
for name in _to_delete:
    del sys.modules[name]
