import argparse
import json
import os
import random
import time
from pathlib import Path

PROFILES = {
    "urban": {"latency_ms": (40, 120), "loss_pct": (0.1, 0.5)},
    "rural": {"latency_ms": (80, 200), "loss_pct": (0.5, 1.5)},
    "cross_border": {"latency_ms": (120, 280), "loss_pct": (1.0, 3.0)},
}


def generate_event(profile: str, seq: int) -> dict:
    cfg = PROFILES[profile]
    latency = round(random.uniform(*cfg["latency_ms"]), 2)
    loss = round(random.uniform(*cfg["loss_pct"]), 2)
    return {
        "event_id": f"evt-{seq}",
        "timestamp": time.time(),
        "imsi": f"00101{random.randint(100000000, 999999999)}",
        "home_plmn": "001-01",
        "visited_plmn": random.choice(["208-01", "234-15", "302-220"]),
        "latency_ms": latency,
        "loss_pct": loss,
        "policy_action": "allow" if loss < 2 else "throttle",
    }


def main():
    parser = argparse.ArgumentParser(description="Generate roaming events")
    parser.add_argument("--profile", choices=PROFILES.keys(), default="urban")
    parser.add_argument("--events", type=int, default=50)
    parser.add_argument("--output", default="out/events.jsonl")
    args = parser.parse_args()

    Path(os.path.dirname(args.output) or ".").mkdir(parents=True, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as fh:
        for seq in range(1, args.events + 1):
            evt = generate_event(args.profile, seq)
            fh.write(json.dumps(evt) + "\n")
    print(f"Wrote {args.events} {args.profile} events to {args.output}")


if __name__ == "__main__":
    main()
