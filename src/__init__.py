"""Top-level package for the MonkAI marketing suite prototypes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

try:  # Optional dependency; falls back to a no-op stub when missing.
    from fastapi import FastAPI
except Exception:  # pragma: no cover - fallback path for minimal envs
    FastAPI = None  # type: ignore

    class _FastAPIStub:
        def include_router(self, router: Any) -> None:  # noqa: D401 - simple stub
            """Compatibility shim when FastAPI isn't installed."""

        def get(self, *_args: Any, **_kwargs: Any):  # pragma: no cover - stub only
            def decorator(func):
                return func

            return decorator

    app: Any = _FastAPIStub()
else:
    app = FastAPI(title="MonkAI Enterprise Toolkit", version="0.1.0")

try:
    from .order_tracking import order_router
except Exception:  # pragma: no cover - defensive import guard
    order_router = None

if FastAPI is not None and order_router is not None:
    app.include_router(order_router)


async def health_check() -> Dict[str, Any]:
    """Return health metadata for the composite toolkit."""

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "modules": {
            "content_seo": "available",
            "video_production": "available",
            "advertising": "available",
            "order_tracking": "available" if order_router is not None else "degraded",
        },
    }


if FastAPI is not None:

    @app.get("/api/health")
    async def _health_endpoint() -> Dict[str, Any]:
        return await health_check()


__all__ = ["app", "health_check", "order_router"]
