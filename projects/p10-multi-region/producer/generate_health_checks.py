"""Generate synthetic Route 53 health check documents."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

checks = [
    {"region": "us-east-1", "endpoint": "https://primary.example.com/healthz", "status": "healthy"},
    {"region": "us-west-2", "endpoint": "https://secondary.example.com/healthz", "status": "healthy"},
]

def main() -> None:
    out_dir = Path("artifacts/healthchecks")
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": datetime.utcnow().isoformat(), "checks": checks}
    (out_dir / "healthchecks.json").write_text(json.dumps(payload, indent=2))
    print("Wrote health check snapshot")


if __name__ == "__main__":
    main()
