"""Health check helpers for 1-aws-infrastructure-automation."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "1-aws-infrastructure-automation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
