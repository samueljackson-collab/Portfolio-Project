from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime, timezone

ARTIFACT = Path("artifacts/telemetry_bundle.json")
ARTIFACT.parent.mkdir(exist_ok=True)


def collect_telemetry() -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "metrics": {"latency_ms": 42, "throughput_rps": 128},
        "logs": ["service started", "handled request", "exported metrics"],
        "traces": ["trace-abc123"],
    }


def main():
    bundle = collect_telemetry()
    ARTIFACT.write_text(json.dumps(bundle, indent=2))
    print("Observability demo complete. See artifacts/telemetry_bundle.json")


if __name__ == "__main__":
    main()
