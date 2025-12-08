import argparse
import json
from statistics import mean


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--expect", choices=["primary", "secondary", "either"], default="secondary")
    args = parser.parse_args()

    with open(args.report, encoding="utf-8") as fh:
        events = json.load(fh)

    regions = [e["region"] for e in events]
    switched = regions.count(regions[0]) != len(regions)
    if not events:
        print("No events found in report.")
        return

    avg_latency = mean([e["latency_ms"] for e in events])

    print(f"Switch observed: {switched}")
    print(f"Average latency: {avg_latency:.2f} ms")


if __name__ == "__main__":
    main()
