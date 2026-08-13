import os
import sys
from pathlib import Path

_HERMES_PATH = os.environ.pop("PYTHONPATH", "")
if _HERMES_PATH:
    sys.path = [p for p in sys.path if p not in _HERMES_PATH.split(os.pathsep)]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

os.environ.setdefault("LIN_SOUL_AUTH_TOKEN", "test-token")

from lin_soul.auth import LinSoulTokenVerifier


@pytest.mark.anyio
async def test_verifier_rejects_bad_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIN_SOUL_AUTH_TOKEN", "secret")
    assert await LinSoulTokenVerifier().verify_token("wrong") is None


@pytest.mark.anyio
async def test_verifier_accepts_correct_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIN_SOUL_AUTH_TOKEN", "secret")
    token = await LinSoulTokenVerifier().verify_token("secret")
    assert token is not None
    assert token.client_id == "lin-soul-client"
    assert token.scopes == []
