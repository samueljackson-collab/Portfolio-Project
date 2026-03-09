from __future__ import annotations
from pathlib import Path
import json

ARTIFACT = Path("artifacts/alert_summary.json")
ARTIFACT.parent.mkdir(exist_ok=True)


def evaluate_thresholds(metrics: dict[str, float]) -> dict:
    alerts = []
    if metrics.get("cpu", 0) > 80:
        alerts.append("cpu_high")
    if metrics.get("error_rate", 0) > 0.05:
        alerts.append("error_rate_high")
    return {"alerts": alerts, "total_alerts": len(alerts)}


def main():
    snapshot = {"cpu": 87.2, "error_rate": 0.02, "latency_ms": 210}
    summary = evaluate_thresholds(snapshot)
    ARTIFACT.write_text(json.dumps(summary, indent=2))
    print("Advanced monitoring demo complete. See artifacts/alert_summary.json")


if __name__ == "__main__":
    main()
