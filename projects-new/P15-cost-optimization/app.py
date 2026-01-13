from __future__ import annotations
import json
from pathlib import Path

ARTIFACT = Path("artifacts/cost_report.json")
ARTIFACT.parent.mkdir(exist_ok=True)


def calculate_savings(current_month: float, rightsized: float, spot: float) -> dict:
    return {
        "current_spend": current_month,
        "rightsized_spend": current_month - rightsized,
        "spot_savings": spot,
        "net_savings": rightsized + spot,
    }


def main():
    savings = calculate_savings(current_month=12000.0, rightsized=1800.0, spot=950.0)
    ARTIFACT.write_text(json.dumps(savings, indent=2))
    print("Cost optimization demo complete. See artifacts/cost_report.json")


if __name__ == "__main__":
    main()
