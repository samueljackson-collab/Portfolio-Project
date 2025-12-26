"""Health check helpers for 9-multi-region-disaster-recovery."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "9-multi-region-disaster-recovery",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
