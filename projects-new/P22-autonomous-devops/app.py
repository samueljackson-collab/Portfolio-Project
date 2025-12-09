from __future__ import annotations
from datetime import datetime
from pathlib import Path

ARTIFACT = Path("artifacts/self_heal.log")
ARTIFACT.parent.mkdir(exist_ok=True)


def detect_issue() -> str:
    return "pod-crash-loop"


def remediate(issue: str) -> str:
    actions = {
        "pod-crash-loop": "restart deployment",
        "high-latency": "scale out",
    }
    return actions.get(issue, "investigate")


def orchestrate():
    issue = detect_issue()
    action = remediate(issue)
    return [
        f"{datetime.utcnow().isoformat()}Z detected: {issue}",
        f"{datetime.utcnow().isoformat()}Z action: {action}",
        "closed-loop: success",
    ]


def main():
    log = orchestrate()
    ARTIFACT.write_text("\n".join(log))
    print("Autonomous DevOps demo complete. See artifacts/self_heal.log")


if __name__ == "__main__":
    main()
