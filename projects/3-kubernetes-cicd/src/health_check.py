"""Health check helpers for 3-kubernetes-cicd."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "3-kubernetes-cicd",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
