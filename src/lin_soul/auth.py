"""Authentication helpers independent of the MCP SDK."""

from __future__ import annotations

import os
import secrets

TOKEN = os.environ.get("LIN_SOUL_AUTH_TOKEN")
if not TOKEN:
    raise RuntimeError("LIN_SOUL_AUTH_TOKEN must be set")


def authorized(token: str | None) -> None:
    if token is None or TOKEN is None or not secrets.compare_digest(token, TOKEN):
        raise PermissionError("unauthorized")
