"""Health check helpers for 25-portfolio-website."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "25-portfolio-website",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
