"""Evaluate failover readiness from health check snapshots."""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    snapshot = Path("artifacts/healthchecks/healthchecks.json")
    if not snapshot.exists():
        raise SystemExit("Generate health checks first")
    data = json.loads(snapshot.read_text())
    unhealthy = [c for c in data.get("checks", []) if c.get("status") != "healthy"]
    report = {
        "generated_at": data.get("generated_at"),
        "unhealthy_regions": [c.get("region") for c in unhealthy],
        "ready_for_failover": not unhealthy,
    }
    out = Path("artifacts/healthchecks/failover-readiness.json")
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
