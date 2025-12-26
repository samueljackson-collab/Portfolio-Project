"""Health check helpers for 24-report-generator."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "24-report-generator",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
