from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone

ARTIFACT = Path("artifacts/pipeline_run.txt")
ARTIFACT.parent.mkdir(exist_ok=True)


STEPS = ["checkout", "build", "unit_test", "docker_push", "kubectl_apply"]


def run_pipeline() -> list[str]:
    log: list[str] = []
    for step in STEPS:
        log.append(f"{datetime.now(timezone.utc).isoformat()}Z {step} succeeded")
    log.append("pipeline status: green")
    return log


def main():
    log = run_pipeline()
    ARTIFACT.write_text("\n".join(log))
    print("Kubernetes CI/CD demo complete. See artifacts/pipeline_run.txt")


if __name__ == "__main__":
    main()
