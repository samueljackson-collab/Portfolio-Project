"""Health check helpers for 2-database-migration."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "2-database-migration",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
