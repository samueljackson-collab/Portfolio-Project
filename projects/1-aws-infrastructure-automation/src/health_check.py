"""Health check for AWS Infrastructure Automation project."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def check_health() -> dict:
    """Return standardized health check payload for testing."""
    return {
        "status": "ok",
        "project": "1-aws-infrastructure-automation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def run_health_check() -> dict:
    """Run basic readiness checks for key project assets."""
    base_dir = Path(__file__).resolve().parents[1]
    required_paths = [
        base_dir / "README.md",
        base_dir / "terraform" / "main.tf",
        base_dir / "terraform" / "variables.tf",
        base_dir / "scripts" / "deploy-terraform.sh",
    ]

    missing = [str(path.relative_to(base_dir)) for path in required_paths if not path.exists()]
    status = "ok" if not missing else "failed"

    return {"status": status, "missing": missing}


def main() -> int:
    """CLI entrypoint for container health checks."""
    result = run_health_check()
    print(json.dumps(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
