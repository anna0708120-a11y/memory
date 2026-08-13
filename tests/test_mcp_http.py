import json
import os
import sys
from pathlib import Path

_HERMES_PATH = os.environ.pop("PYTHONPATH", "")
if _HERMES_PATH:
    sys.path = [p for p in sys.path if p not in _HERMES_PATH.split(os.pathsep)]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

os.environ.setdefault("LIN_SOUL_AUTH_TOKEN", "test-token")

from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

import lin_soul.server as server

mcp = server.mcp


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    app = mcp.streamable_http_app()
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            yield client


def initialize_request() -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    }


def response_message(response: Any) -> dict[str, Any]:
    if response.headers["content-type"].startswith("text/event-stream"):
        payload = next(line[6:] for line in response.text.splitlines() if line.startswith("data: "))
        return json.loads(payload)
    return response.json()


@pytest.mark.anyio
async def test_mcp_rejects_missing_or_bad_bearer_token(client: AsyncClient) -> None:
    for headers in ({}, {"Authorization": "Bearer wrong-token"}):
        response = await client.post("/mcp", json=initialize_request(), headers=headers)
        assert response.status_code == 401
        assert response.headers["www-authenticate"].startswith("Bearer ")


@pytest.mark.anyio
async def test_initialize_and_tools_list_accept_valid_bearer_token(client: AsyncClient) -> None:
    headers = {
        "Authorization": "Bearer test-token",
        "Accept": "application/json, text/event-stream",
    }
    initialized = await client.post("/mcp", json=initialize_request(), headers=headers)

    assert initialized.status_code == 200
    session_id = initialized.headers["mcp-session-id"]
    assert response_message(initialized)["result"]["serverInfo"]["name"] == "lin-soul"

    tools = await client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        headers={**headers, "mcp-session-id": session_id},
    )

    assert tools.status_code == 200
    schemas = {tool["name"]: tool["inputSchema"] for tool in response_message(tools)["result"]["tools"]}
    assert set(schemas) == {"memory_get", "memory_write"}
    assert set(schemas["memory_write"]["properties"]) == {"key", "value"}
    assert set(schemas["memory_get"]["properties"]) == {"key"}


@pytest.mark.anyio
async def test_memory_get_tool_call_preserves_not_found_response(client: AsyncClient) -> None:
    headers = {
        "Authorization": "Bearer test-token",
        "Accept": "application/json, text/event-stream",
    }
    initialized = await client.post("/mcp", json=initialize_request(), headers=headers)
    session_id = initialized.headers["mcp-session-id"]

    server.store = type("FakeStore", (), {"get": lambda _, key: None})()
    try:
        result = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "memory_get", "arguments": {"key": "missing-key"}},
            },
            headers={**headers, "mcp-session-id": session_id},
        )
    finally:
        server.store = None

    assert result.status_code == 200
    assert response_message(result)["result"]["structuredContent"] == {"key": "missing-key", "found": False}


@pytest.mark.anyio
async def test_memory_write_tool_call_preserves_store_response(client: AsyncClient) -> None:
    headers = {
        "Authorization": "Bearer test-token",
        "Accept": "application/json, text/event-stream",
    }
    initialized = await client.post("/mcp", json=initialize_request(), headers=headers)
    session_id = initialized.headers["mcp-session-id"]

    server.store = type(
        "FakeStore",
        (),
        {"write": lambda _, key, value: {"key": key, "value": value, "updated": True}},
    )()
    try:
        result = await client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "memory_write", "arguments": {"key": "k", "value": "v"}},
            },
            headers={**headers, "mcp-session-id": session_id},
        )
    finally:
        server.store = None

    assert result.status_code == 200
    assert response_message(result)["result"]["structuredContent"] == {
        "key": "k",
        "value": "v",
        "updated": True,
    }
