"""Consume synthetic roaming events and emit metrics stub."""
from __future__ import annotations

import json
from pathlib import Path


class MetricsSink:
    def __init__(self) -> None:
        self.success = 0
        self.failures = 0
        self.latencies = []

    def record(self, event: dict) -> None:
        if event.get("result") == "SUCCESS":
            self.success += 1
        else:
            self.failures += 1
        if "latency_ms" in event:
            self.latencies.append(event["latency_ms"])

    def summary(self) -> dict:
        latencies = self.latencies or [0]
        return {
            "success": self.success,
            "failures": self.failures,
            "latency_avg_ms": sum(latencies) / len(latencies),
        }


def main() -> None:
    events_file = Path("artifacts/events/sample-events.json")
    if not events_file.exists():
        raise SystemExit("No events found; run producer first")
    events = json.loads(events_file.read_text())
    sink = MetricsSink()
    for event in events:
        sink.record(event)
    summary_path = Path("artifacts/metrics/summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(sink.summary(), indent=2))
    print(summary_path.read_text())


if __name__ == "__main__":
    main()
