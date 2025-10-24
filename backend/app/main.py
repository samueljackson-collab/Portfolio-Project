"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, make_asgi_app

from .config import get_settings
from .routers import api_router

settings = get_settings()
app = FastAPI(title="Portfolio Backend", version="1.0.0")
metrics_app = make_asgi_app()
request_counter = Counter("request_count", "Number of API requests", namespace=settings.prometheus_namespace)
request_latency = Histogram(
    "request_duration_seconds",
    "API request latency",
    namespace=settings.prometheus_namespace,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def record_metrics(request: Request, call_next) -> Response:  # type: ignore[override]
    request_counter.inc()
    with request_latency.time():
        response = await call_next(request)
    return response


app.include_router(api_router)
app.mount("/metrics", metrics_app)
