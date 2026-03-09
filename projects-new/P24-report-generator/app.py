from __future__ import annotations
from pathlib import Path
from datetime import date

ARTIFACT = Path("artifacts/summary_report.txt")
ARTIFACT.parent.mkdir(exist_ok=True)


def build_report() -> str:
    lines = [
        "Executive Summary",
        "-----------------",
        "This demo shows how a templated report might be generated for stakeholders.",
        f"Date: {date.today().isoformat()}",
        "Key Metrics: uptime=99.9%, cost=$12k",
    ]
    return "\n".join(lines)


def main():
    report = build_report()
    ARTIFACT.write_text(report)
    print("Report generator demo complete. See artifacts/summary_report.txt")


if __name__ == "__main__":
    main()
