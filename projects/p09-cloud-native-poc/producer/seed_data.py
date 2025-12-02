"""Seed initial data and tasks for the POC."""
from __future__ import annotations

import json
from pathlib import Path

items = [
    {"name": "sensor-A", "status": "active"},
    {"name": "sensor-B", "status": "provisioning"},
]

def main() -> None:
    out_dir = Path("artifacts")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "seed-items.json").write_text(json.dumps(items, indent=2))
    print("Seeded items to artifacts/seed-items.json")


if __name__ == "__main__":
    main()
