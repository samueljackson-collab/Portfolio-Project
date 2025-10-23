from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any, Dict

import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@db:5432/portfolio")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
API_VERSION = os.getenv("API_VERSION", "0.1.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

    app.state.db_pool = db_pool
    app.state.redis = redis_client

    try:
        yield
    finally:
        await db_pool.close()
        await redis_client.close()


def build_response(status: str, detail: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "status": status,
        "version": API_VERSION,
    }
    if detail:
        payload.update(detail)
    return payload


class Event(BaseModel):
    type: str = Field(default="custom", max_length=120)
    payload: Dict[str, Any] = Field(default_factory=dict)


app = FastAPI(
    title="Portfolio Sample API",
    description="Minimal FastAPI service backing smoke tests and examples.",
    version=API_VERSION,
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health() -> Dict[str, Any]:
    return build_response(
        "healthy",
        {
            "checks": {
                "database": "pass",
                "redis": "pass",
            }
        },
    )


@app.get("/health/db", tags=["health"])
async def health_db() -> Dict[str, Any]:
    try:
        async with app.state.db_pool.acquire() as conn:
            await conn.execute("SELECT 1;")
    except Exception as exc:  # pragma: no cover - surfaced through HTTP response
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}") from exc

    return build_response("healthy", {"checks": {"database": "pass"}})


@app.get("/health/redis", tags=["health"])
async def health_redis() -> Dict[str, Any]:
    try:
        pong = await app.state.redis.ping()
    except Exception as exc:  # pragma: no cover - surfaced through HTTP response
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {exc}") from exc

    if not pong:
        raise HTTPException(status_code=503, detail="Redis ping returned falsy response")

    return build_response("healthy", {"checks": {"redis": "pass"}})


@app.get("/metrics", tags=["telemetry"])
async def metrics() -> Dict[str, Any]:
    """Return simple counters to visualise within examples."""
    counter = int(await app.state.redis.get("example:visits") or 0)
    await app.state.redis.set("example:visits", counter + 1)

    row = await app.state.db_pool.fetchrow(
        "SELECT COUNT(*) AS visit_count FROM example_health_events;"
    )
    visits = row["visit_count"] if row else 0

    return {
        "version": API_VERSION,
        "redis_visits": counter + 1,
        "database_visits": visits,
    }


@app.post("/metrics", tags=["telemetry"], status_code=201)
async def record_event(event: Event) -> Dict[str, Any]:
    """Persist simple event payloads to demonstrate database connectivity."""
    async with app.state.db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO example_health_events (event_type, payload)
            VALUES ($1, $2);
            """,
            event.type,
            event.model_dump(),
        )

    return build_response("recorded", {"event_type": event.type})
