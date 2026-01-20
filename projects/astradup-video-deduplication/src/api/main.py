"""FastAPI service for AstraDup."""

from __future__ import annotations

import time

from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

app = FastAPI(
    title="AstraDup API",
    version="1.0.0",
    description="Health and telemetry endpoints for AstraDup services.",
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    """Record basic request metrics for Prometheus."""
    start_time = time.monotonic()
    response = await call_next(request)
    duration = time.monotonic() - start_time

    route = request.scope.get("route")
    path_template = route.path if route else request.url.path

    REQUEST_LATENCY.labels(request.method, path_template).observe(duration)
    REQUEST_COUNT.labels(
        request.method,
        path_template,
        str(response.status_code),
    ).inc()
    return response


@app.get("/health")
def health_check() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
