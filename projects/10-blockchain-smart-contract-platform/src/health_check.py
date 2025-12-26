"""Health check helpers for 10-blockchain-smart-contract-platform."""
from __future__ import annotations

from datetime import datetime, timezone


def check_health() -> dict[str, str]:
    """Return a minimal health check payload."""
    return {
        "status": "ok",
        "project": "10-blockchain-smart-contract-platform",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
