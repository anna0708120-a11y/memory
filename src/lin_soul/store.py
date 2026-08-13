"""Persistent PostgreSQL key/value storage for Lin Soul memories."""

from __future__ import annotations

import os
from typing import Any

import psycopg
from psycopg.rows import dict_row


SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    memory_key TEXT PRIMARY KEY,
    memory_value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""


class MemoryStore:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL must be set")
        self._ensure_schema()

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def _ensure_schema(self) -> None:
        with self._connect() as db:
            db.execute(SCHEMA)

    def write(self, key: str, value: str) -> dict[str, Any]:
        if not key or not value:
            raise ValueError("key and value are required")
        with self._connect() as db:
            db.execute(
                """INSERT INTO memories(memory_key, memory_value)
                   VALUES (%s, %s)
                   ON CONFLICT(memory_key) DO UPDATE SET
                     memory_value=EXCLUDED.memory_value,
                     updated_at=NOW()""",
                (key, value),
            )
        return {"key": key, "value": value}

    def get(self, key: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT memory_key, memory_value, updated_at FROM memories WHERE memory_key = %s",
                (key,),
            ).fetchone()
        if row is None:
            return None
        return {"key": row["memory_key"], "value": row["memory_value"], "updated_at": row["updated_at"]}
