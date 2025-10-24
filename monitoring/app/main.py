"""Metrics exporter."""
from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

app = FastAPI(title="Portfolio Metrics", version="1.0.0")
registry = CollectorRegistry()
request_counter = Counter("request_count", "Number of backend requests", registry=registry)
request_latency = Histogram(
    "request_duration_seconds",
    "Backend request latency",
    registry=registry,
)
active_users = Gauge("active_users", "Number of authenticated users", registry=registry)


@app.get("/metrics")
async def metrics() -> Response:
    data = generate_latest(registry)
    return Response(content=data, media_type="text/plain; version=0.0.4")


@app.post("/ingest")
async def ingest(event: dict[str, float]) -> dict[str, str]:
    request_counter.inc(event.get("requests", 1))
    if "latency" in event:
        request_latency.observe(event["latency"])
    if "active_users" in event:
        active_users.set(event["active_users"])
    return {"status": "ok"}
