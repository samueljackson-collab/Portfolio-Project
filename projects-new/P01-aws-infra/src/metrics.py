"""Prometheus metrics helpers."""

from __future__ import annotations

import time
from typing import Callable, Awaitable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNTER = Counter(
    "aws_infra_requests_total",
    "Total HTTP requests processed by the AWS infra service",
    labelnames=["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "aws_infra_request_latency_seconds",
    "Latency of HTTP requests in seconds",
    labelnames=["endpoint"],
)

AWS_CALL_COUNTER = Counter(
    "aws_infra_aws_calls_total",
    "Number of AWS SDK calls made by the service",
    labelnames=["service", "operation", "status"],
)


def record_request_metrics(method: str, endpoint: str, status_code: int, latency_seconds: float) -> None:
    """Increment counters for request metrics."""

    REQUEST_COUNTER.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency_seconds)


def record_aws_call(service: str, operation: str, success: bool) -> None:
    """Track AWS SDK invocation results."""

    status = "success" if success else "error"
    AWS_CALL_COUNTER.labels(service=service, operation=operation, status=status).inc()


def metrics_endpoint() -> tuple[bytes, str]:
    """Return serialized metrics and content type."""

    payload = generate_latest()
    return payload, CONTENT_TYPE_LATEST


async def metrics_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Collect latency metrics for every HTTP request."""

    start_time = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start_time
    record_request_metrics(request.method, request.url.path, response.status_code, elapsed)
    return response
