from __future__ import annotations
from datetime import datetime, timezone
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
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return [
        f"{timestamp} detected: {issue}",
        f"{timestamp} action: {action}",
        "closed-loop: success",
    ]


def main():
    log = orchestrate()
    ARTIFACT.write_text("\n".join(log))
    print("Autonomous DevOps demo complete. See artifacts/self_heal.log")


if __name__ == "__main__":
    main()
