"""Collect a small metrics snapshot from the API."""
from __future__ import annotations

import json
import requests

API_URL = "http://localhost:8000/metrics"

def main() -> None:
    resp = requests.get(API_URL, timeout=5)
    resp.raise_for_status()
    metrics_snapshot = {"bytes": len(resp.text), "status": resp.status_code}
    with open("artifacts/metrics-snapshot.json", "w", encoding="utf-8") as f:
        json.dump(metrics_snapshot, f, indent=2)
    print(json.dumps(metrics_snapshot, indent=2))


if __name__ == "__main__":
    main()
