import argparse
import json
import random
import time
from pathlib import Path


def simulate(primary: str, secondary: str, fail_after: int):
    events = []
    for second in range(0, fail_after + 60, 10):
        region = primary if second < fail_after else secondary
        events.append({"timestamp": second, "region": region, "latency_ms": random.randint(40, 120)})
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", default="us-east-1")
    parser.add_argument("--secondary", default="us-west-2")
    parser.add_argument("--fail-after", type=int, default=30)
    parser.add_argument("--output", default="out/failover.json")
    args = parser.parse_args()

    Path("out").mkdir(exist_ok=True)
    events = simulate(args.primary, args.secondary, args.fail_after)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(events, fh, indent=2)
    print(f"Simulated failover after {args.fail_after}s; wrote {len(events)} events to {args.output}")


if __name__ == "__main__":
    main()
