import os
import sys
from pathlib import Path

_HERMES_PATH = os.environ.pop("PYTHONPATH", "")
if _HERMES_PATH:
    sys.path = [p for p in sys.path if p not in _HERMES_PATH.split(os.pathsep)]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from lin_soul.store import MemoryStore


def test_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError):
        MemoryStore(None)
