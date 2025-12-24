from __future__ import annotations
from pathlib import Path
import json

ARTIFACT = Path("artifacts/compliance_report.json")
ARTIFACT.parent.mkdir(exist_ok=True)

CHECKS = {
    "cis-1.1": True,
    "cis-1.2": False,
    "guardduty": True,
}


def run_checks() -> dict:
    failed = [k for k, v in CHECKS.items() if not v]
    return {"passed": len(CHECKS) - len(failed), "failed": failed}


def main():
    results = run_checks()
    ARTIFACT.write_text(json.dumps(results, indent=2))
    print("Security automation demo complete. See artifacts/compliance_report.json")


if __name__ == "__main__":
    main()
