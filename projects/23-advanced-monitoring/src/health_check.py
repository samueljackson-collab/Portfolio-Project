"""Health check helpers for 23-advanced-monitoring."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "23-advanced-monitoring",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
