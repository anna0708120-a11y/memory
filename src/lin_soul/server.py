"""Authenticated Streamable HTTP MCP application."""

from __future__ import annotations

import os
from typing import Any

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

from .auth import LinSoulTokenVerifier
from .store import MemoryStore

mcp = FastMCP(
    "lin-soul",
    token_verifier=LinSoulTokenVerifier(),
    auth=AuthSettings(
        issuer_url="https://memory-8cvf.onrender.com",
        resource_server_url="https://memory-8cvf.onrender.com/mcp",
    ),
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    streamable_http_path="/mcp",
)


store: MemoryStore | None = None


def _store() -> MemoryStore:
    global store
    if store is None:
        store = MemoryStore()
    return store


@mcp.tool()
def memory_write(key: str, value: str) -> dict[str, Any]:
    """Write or replace one durable Lin Soul memory by key."""
    return _store().write(key, value)


@mcp.tool()
def memory_get(key: str) -> dict[str, Any]:
    """Read one durable Lin Soul memory by key."""
    result = _store().get(key)
    if result is None:
        return {"key": key, "found": False}
    return {"found": True, **result}


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
