import argparse
import json
from collections import Counter
from pathlib import Path


def consume(file_path: str):
    stats = Counter()
    with open(file_path, encoding="utf-8") as fh:
        for line in fh:
            evt = json.loads(line)
            stats["events"] += 1
            stats[f"action_{evt['policy_action']}"] += 1
            if evt.get("loss_pct", 0) > 2:
                stats["high_loss"] += 1
    return stats


def main():
    parser = argparse.ArgumentParser(description="Consume roaming events")
    parser.add_argument("--ingest-file", required=True)
    parser.add_argument("--metrics-port", type=int, default=9200)
    args = parser.parse_args()

    stats = consume(args.ingest_file)
    Path("out").mkdir(exist_ok=True)
    with open("out/kpis.json", "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    print(f"Processed {stats['events']} events; results stored in out/kpis.json")
    print(f"Expose metrics via port {args.metrics_port} in real deployment")


if __name__ == "__main__":
    main()
