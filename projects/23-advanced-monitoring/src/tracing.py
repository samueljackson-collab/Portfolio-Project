"""Distributed tracing integration for observability stack."""
from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Generator, List, Optional
import uuid

LOGGER = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    LOGGER.warning("OpenTelemetry not available, using fallback tracing")


@dataclass
class SpanContext:
    """Represents a span in a distributed trace."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    service_name: str = ""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    status: str = "OK"
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)

    def add_tag(self, key: str, value: Any) -> None:
        self.tags[key] = value

    def add_log(self, message: str, **kwargs) -> None:
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            **kwargs,
        })

    def finish(self, status: str = "OK") -> None:
        self.end_time = datetime.utcnow()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.status = status


class TracingConfig:
    """Configuration for distributed tracing."""

    def __init__(
        self,
        service_name: str = "portfolio-service",
        otlp_endpoint: Optional[str] = None,
        sample_rate: float = 1.0,
        enabled: bool = True,
    ):
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint or os.environ.get(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
        )
        self.sample_rate = sample_rate
        self.enabled = enabled


class OTelTracer:
    """OpenTelemetry-based tracer."""

    def __init__(self, config: TracingConfig):
        self.config = config
        self._tracer = None

        if OTEL_AVAILABLE and config.enabled:
            self._initialize_otel()

    def _initialize_otel(self) -> None:
        """Initialize OpenTelemetry tracing."""
        resource = Resource.create({
            "service.name": self.config.service_name,
            "service.version": os.environ.get("SERVICE_VERSION", "1.0.0"),
        })

        provider = TracerProvider(resource=resource)

        otlp_exporter = OTLPSpanExporter(
            endpoint=self.config.otlp_endpoint,
            insecure=True,
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        trace.set_tracer_provider(provider)
        self._tracer = trace.get_tracer(self.config.service_name)

        LOGGER.info(f"OpenTelemetry initialized with endpoint: {self.config.otlp_endpoint}")

    @contextmanager
    def start_span(
        self,
        operation_name: str,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Generator[Any, None, None]:
        """Start a new span."""
        if self._tracer:
            with self._tracer.start_as_current_span(operation_name) as span:
                if tags:
                    for key, value in tags.items():
                        span.set_attribute(key, str(value))
                yield span
        else:
            # Fallback span context
            ctx = SpanContext(
                trace_id=uuid.uuid4().hex,
                span_id=uuid.uuid4().hex[:16],
                operation_name=operation_name,
                service_name=self.config.service_name,
            )
            if tags:
                ctx.tags.update(tags)
            yield ctx
            ctx.finish()

    def trace_function(
        self,
        operation_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        """Decorator to trace a function."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                span_name = operation_name or func.__name__
                with self.start_span(span_name, tags):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


class FallbackTracer:
    """Fallback tracer when OpenTelemetry is not available."""

    def __init__(self, config: TracingConfig):
        self.config = config
        self._spans: List[SpanContext] = []
        self._current_span: Optional[SpanContext] = None

    @contextmanager
    def start_span(
        self,
        operation_name: str,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Generator[SpanContext, None, None]:
        """Start a new span."""
        parent_id = self._current_span.span_id if self._current_span else None

        span = SpanContext(
            trace_id=self._current_span.trace_id if self._current_span else uuid.uuid4().hex,
            span_id=uuid.uuid4().hex[:16],
            parent_span_id=parent_id,
            operation_name=operation_name,
            service_name=self.config.service_name,
        )

        if tags:
            span.tags.update(tags)

        previous_span = self._current_span
        self._current_span = span

        try:
            yield span
            span.finish("OK")
        except Exception as e:
            span.finish("ERROR")
            span.add_log(f"Error: {e}", level="error")
            raise
        finally:
            self._current_span = previous_span
            self._spans.append(span)

    def trace_function(
        self,
        operation_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        """Decorator to trace a function."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                span_name = operation_name or func.__name__
                with self.start_span(span_name, tags):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_recent_spans(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent spans for debugging."""
        return [
            {
                "trace_id": s.trace_id,
                "span_id": s.span_id,
                "parent_span_id": s.parent_span_id,
                "operation": s.operation_name,
                "duration_ms": s.duration_ms,
                "status": s.status,
                "tags": s.tags,
            }
            for s in self._spans[-limit:]
        ]


def create_tracer(config: Optional[TracingConfig] = None) -> Any:
    """Factory to create appropriate tracer."""
    config = config or TracingConfig()

    if OTEL_AVAILABLE and config.enabled:
        return OTelTracer(config)
    return FallbackTracer(config)


# Context propagation utilities
class TracePropagator:
    """Handles trace context propagation across services."""

    def __init__(self):
        self._propagator = TraceContextTextMapPropagator() if OTEL_AVAILABLE else None

    def inject(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Inject trace context into headers."""
        if self._propagator:
            self._propagator.inject(headers)
        else:
            # Fallback: Use simple header-based propagation
            if "X-Trace-ID" not in headers:
                headers["X-Trace-ID"] = uuid.uuid4().hex
        return headers

    def extract(self, headers: Dict[str, str]) -> Optional[str]:
        """Extract trace context from headers."""
        if self._propagator:
            ctx = self._propagator.extract(headers)
            return str(ctx) if ctx else None
        return headers.get("X-Trace-ID")


# Middleware for web frameworks
class TracingMiddleware:
    """ASGI middleware for automatic request tracing."""

    def __init__(self, app, tracer: Any):
        self.app = app
        self.tracer = tracer

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "/")
        method = scope.get("method", "UNKNOWN")

        with self.tracer.start_span(
            f"{method} {path}",
            tags={
                "http.method": method,
                "http.path": path,
                "http.scheme": scope.get("scheme", "http"),
            },
        ):
            await self.app(scope, receive, send)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config = TracingConfig(service_name="test-service")
    tracer = create_tracer(config)

    @tracer.trace_function(tags={"component": "test"})
    def example_operation():
        time.sleep(0.1)
        return "completed"

    with tracer.start_span("main-operation") as span:
        span.add_tag("test", "value")
        result = example_operation()
        print(f"Result: {result}")
