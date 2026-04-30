"""Async SQLite storage backend using aiosqlite."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    model TEXT,
    provider TEXT,
    tokens_in INTEGER,
    tokens_out INTEGER,
    latency_ms REAL,
    cost_usd REAL,
    cache_hit BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS response_cache (
    request_hash TEXT PRIMARY KEY,
    response_data BLOB NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id TEXT NOT NULL,
    error_type TEXT,
    timestamp TEXT NOT NULL
);
"""


class Storage:
    """Async SQLite storage for HCC telemetry, caching, and provider health."""

    def __init__(self, db_path: str = "~/.fcc/hcc.db") -> None:
        self._db_path = Path(db_path).expanduser()
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self._db_path))
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(_SCHEMA)
        await self._db.commit()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("Storage not initialized — call init() first")
        return self._db

    # ------------------------------------------------------------------
    # Request logging
    # ------------------------------------------------------------------

    async def log_request(
        self,
        timestamp: str,
        model: str | None,
        provider: str | None,
        tokens_in: int | None,
        tokens_out: int | None,
        latency_ms: float | None,
        cost_usd: float | None,
        cache_hit: bool = False,
    ) -> None:
        await self._conn().execute(
            """INSERT INTO requests
               (timestamp, model, provider, tokens_in, tokens_out, latency_ms, cost_usd, cache_hit)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (timestamp, model, provider, tokens_in, tokens_out, latency_ms, cost_usd, cache_hit),
        )
        await self._conn().commit()

    async def get_cost_summary(self, period: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        if period == "session":
            where = ""
            params: tuple[Any, ...] = ()
        elif period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            where = "WHERE timestamp >= ?"
            params = (start,)
        elif period == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            where = "WHERE timestamp >= ?"
            params = (start,)
        else:
            raise ValueError(f"Unknown period: {period!r} (expected session/daily/monthly)")

        row = await self._fetchone(
            f"""SELECT
                    COUNT(*) AS total_requests,
                    COALESCE(SUM(tokens_in), 0) AS total_tokens_in,
                    COALESCE(SUM(tokens_out), 0) AS total_tokens_out,
                    COALESCE(SUM(cost_usd), 0.0) AS total_cost_usd,
                    COALESCE(AVG(latency_ms), 0.0) AS avg_latency_ms
                FROM requests {where}""",
            params,
        )
        if row is None:
            return {
                "period": period,
                "total_requests": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
            }
        return {
            "period": period,
            "total_requests": row["total_requests"],
            "total_tokens_in": row["total_tokens_in"],
            "total_tokens_out": row["total_tokens_out"],
            "total_cost_usd": row["total_cost_usd"],
            "avg_latency_ms": row["avg_latency_ms"],
        }

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------

    async def get_cache_stats(self) -> dict[str, int]:
        row = await self._fetchone(
            """SELECT
                   SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) AS hits,
                   SUM(CASE WHEN NOT cache_hit THEN 1 ELSE 0 END) AS misses
               FROM requests""",
            (),
        )
        if row is None:
            return {"hits": 0, "misses": 0}
        return {"hits": row["hits"] or 0, "misses": row["misses"] or 0}

    async def store_cached_response(
        self,
        request_hash: str,
        response_data: Any,
        ttl_seconds: int,
    ) -> None:
        now = datetime.now(timezone.utc)
        created = now.isoformat()
        from datetime import timedelta

        expires = (now + timedelta(seconds=ttl_seconds)).isoformat()
        blob = json.dumps(response_data).encode("utf-8")
        await self._conn().execute(
            """INSERT OR REPLACE INTO response_cache
               (request_hash, response_data, created_at, expires_at)
               VALUES (?, ?, ?, ?)""",
            (request_hash, blob, created, expires),
        )
        await self._conn().commit()

    async def get_cached_response(self, request_hash: str) -> Any | None:
        row = await self._fetchone(
            "SELECT response_data, expires_at FROM response_cache WHERE request_hash = ?",
            (request_hash,),
        )
        if row is None:
            return None
        expires = datetime.fromisoformat(row["expires_at"])
        if datetime.now(timezone.utc) > expires:
            await self._conn().execute(
                "DELETE FROM response_cache WHERE request_hash = ?",
                (request_hash,),
            )
            await self._conn().commit()
            return None
        return json.loads(row["response_data"])

    async def clear_cache(self) -> int:
        cursor = await self._conn().execute("DELETE FROM response_cache")
        await self._conn().commit()
        return cursor.rowcount

    async def evict_expired_cache(self) -> int:
        now = datetime.now(timezone.utc).isoformat()
        cursor = await self._conn().execute(
            "DELETE FROM response_cache WHERE expires_at < ?", (now,)
        )
        await self._conn().commit()
        return cursor.rowcount

    async def enforce_cache_max_entries(self, max_entries: int) -> int:
        row = await self._fetchone(
            "SELECT COUNT(*) AS cnt FROM response_cache", ()
        )
        count = row["cnt"] if row else 0
        if count <= max_entries:
            return 0
        excess = count - max_entries
        cursor = await self._conn().execute(
            """DELETE FROM response_cache WHERE request_hash IN (
                   SELECT request_hash FROM response_cache
                   ORDER BY created_at ASC LIMIT ?
               )""",
            (excess,),
        )
        await self._conn().commit()
        return cursor.rowcount

    async def get_cache_entry_count(self) -> int:
        row = await self._fetchone(
            "SELECT COUNT(*) AS cnt FROM response_cache", ()
        )
        return row["cnt"] if row else 0

    # ------------------------------------------------------------------
    # Provider health
    # ------------------------------------------------------------------

    async def log_provider_error(
        self,
        provider_id: str,
        error_type: str | None,
        timestamp: str,
    ) -> None:
        await self._conn().execute(
            "INSERT INTO provider_errors (provider_id, error_type, timestamp) VALUES (?, ?, ?)",
            (provider_id, error_type, timestamp),
        )
        await self._conn().commit()

    async def get_provider_health(self, provider_id: str) -> dict[str, Any]:
        row = await self._fetchone(
            """SELECT COUNT(*) AS error_count,
                      MAX(timestamp) AS last_error
               FROM provider_errors
               WHERE provider_id = ?""",
            (provider_id,),
        )
        if row is None or row["error_count"] == 0:
            return {"provider_id": provider_id, "error_count": 0, "last_error": None}
        return {
            "provider_id": provider_id,
            "error_count": row["error_count"],
            "last_error": row["last_error"],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _fetchone(
        self, sql: str, params: tuple[Any, ...]
    ) -> aiosqlite.Row | None:
        cursor = await self._conn().execute(sql, params)
        return await cursor.fetchone()
