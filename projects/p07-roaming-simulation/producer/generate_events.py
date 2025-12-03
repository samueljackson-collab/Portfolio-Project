"""Generate synthetic roaming events for simulations."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from random import choice, randint

MCC_MNC_POOL = ["310-410", "208-01", "262-01", "724-02"]
RESULTS = ["SUCCESS", "ROAMING_DENIED", "AUTH_FAILED"]


def generate_event() -> dict:
    visited = choice(MCC_MNC_POOL)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "imsi": f"00101{randint(10**9, 10**10-1)}",
        "msisdn": f"1555{randint(10**6, 10**7-1)}",
        "visited_mcc_mnc": visited,
        "result": choice(RESULTS if visited != "724-02" else ["ROAMING_DENIED"]),
        "latency_ms": randint(80, 450),
    }


def main() -> None:
    out_dir = Path("artifacts/events")
    out_dir.mkdir(parents=True, exist_ok=True)
    payloads = [generate_event() for _ in range(20)]
    out = out_dir / "sample-events.json"
    out.write_text(json.dumps(payloads, indent=2))
    print(f"Wrote {len(payloads)} events to {out}")


if __name__ == "__main__":
    main()
