from __future__ import annotations

import random
from datetime import datetime

from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.responses import PlainTextResponse

app = FastAPI(title="Portfolio Monitoring Exporter")

# Core Prometheus metrics describing request load, latency, and the synthetic active user count.
REQUEST_COUNT = Counter("portfolio_requests_total", "Total requests processed", ["endpoint"])
REQUEST_DURATION = Histogram("portfolio_request_duration_seconds", "Request duration", buckets=(0.1, 0.3, 0.5, 1, 2))
ACTIVE_USERS = Gauge("portfolio_active_users", "Number of active users")


@app.on_event("startup")
async def startup_event() -> None:
    ACTIVE_USERS.set(5)


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    REQUEST_COUNT.labels(endpoint="metrics").inc()
    REQUEST_DURATION.observe(random.uniform(0.05, 0.2))
    ACTIVE_USERS.set(random.randint(3, 10))
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type="text/plain; version=0.0.4")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
