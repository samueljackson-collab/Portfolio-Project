import argparse
import json
from pathlib import Path


def summarize(report_path: str):
    with open(report_path, encoding="utf-8") as fh:
        data = json.load(fh)
    stats = {
        "executions": len(data.get("run", {}).get("executions", [])),
        "failures": data.get("run", {}).get("failures", []),
    }
    stats["pass_rate"] = 1 - (len(stats["failures"]) / max(stats["executions"], 1))
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="out/newman-summary.json")
    args = parser.parse_args()

    Path("out").mkdir(exist_ok=True)
    stats = summarize(args.input)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)
    print(f"Pass rate: {stats['pass_rate']:.2%}")


if __name__ == "__main__":
    main()
