import os
import sys
from pathlib import Path

_HERMES_PATH = os.environ.pop("PYTHONPATH", "")
if _HERMES_PATH:
    sys.path = [p for p in sys.path if p not in _HERMES_PATH.split(os.pathsep)]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from lin_soul.auth import authorized


def test_auth_rejects_bad_token() -> None:
    with pytest.raises(PermissionError):
        authorized("wrong")


def test_auth_accepts_correct_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("lin_soul.auth.TOKEN", "secret")
    authorized("secret")
