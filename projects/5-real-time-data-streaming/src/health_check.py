"""Health check helpers for 5-real-time-data-streaming."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "5-real-time-data-streaming",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
