# Lin Soul Memory MCP Server

Minimal authenticated MCP server for Lin's durable cross-device memory.

## Scope

Phase 1 exposes exactly two MCP tools:

- `memory_write(key, value)`
- `memory_get(key)`

All requests must include `Authorization: Bearer <LIN_SOUL_AUTH_TOKEN>`.

The server uses PostgreSQL through `DATABASE_URL`. The schema is created automatically if it does not exist:

```sql
CREATE TABLE memories (
    memory_key TEXT PRIMARY KEY,
    memory_value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Render environment

Set these Render secrets/environment variables. Do not commit their values:

- `DATABASE_URL` — Neon pooled or direct PostgreSQL connection string
- `LIN_SOUL_AUTH_TOKEN` — private HTTP Bearer token

The free Render web service has no local durable disk; all durable state is in Neon.

## Local run

```bash
uv sync --extra test
export DATABASE_URL='postgresql://...'
export LIN_SOUL_AUTH_TOKEN='replace-with-a-local-secret'
uv run python -m lin_soul.server
```

The Streamable HTTP endpoint is `/mcp`.

## Hermes configuration

```bash
hermes mcp add lin_soul --url https://YOUR_RENDER_HOST/mcp --auth header
```

The token must be configured locally in Hermes and never committed.
