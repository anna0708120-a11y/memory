"""Authenticated Streamable HTTP MCP application."""

from __future__ import annotations

import os
from typing import Any

from mcp.server.mcpserver import MCPServer

from .auth import authorized
from .store import MemoryStore

mcp = MCPServer("lin-soul")


store: MemoryStore | None = None


def _store() -> MemoryStore:
    global store
    if store is None:
        store = MemoryStore()
    return store


def _authorized(token: str | None) -> None:
    authorized(token)


@mcp.tool()
def memory_write(key: str, value: str, auth_token: str) -> dict[str, Any]:
    """Write or replace one durable Lin Soul memory by key."""
    _authorized(auth_token)
    return _store().write(key, value)


@mcp.tool()
def memory_get(key: str, auth_token: str) -> dict[str, Any]:
    """Read one durable Lin Soul memory by key."""
    _authorized(auth_token)
    result = _store().get(key)
    if result is None:
        return {"key": key, "found": False}
    return {"found": True, **result}


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
