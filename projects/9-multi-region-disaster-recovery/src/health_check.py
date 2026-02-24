"""Health check for Multi-Region Disaster Recovery project."""
from __future__ import annotations

import json
import datetime
from pathlib import Path


def run_health_check() -> dict:
    """Verify core DR assets exist."""
    base_dir = Path(__file__).resolve().parents[1]
    required_paths = [
        base_dir / "README.md",
        base_dir / "terraform" / "main.tf",
        base_dir / "scripts",
        base_dir / "runbooks",
    ]
    missing = [str(path.relative_to(base_dir)) for path in required_paths if not path.exists()]
    status = "ok" if not missing else "failed"
    return {"status": status, "missing": missing}


def check_health() -> dict:
    """Return structured health status with project metadata and timestamp."""
    base_result = run_health_check()
    return {
        "status": base_result["status"],
        "project": "9-multi-region-disaster-recovery",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "missing": base_result.get("missing", []),
    }


def main() -> int:
    """CLI entrypoint for container health checks."""
    result = check_health()
    print(json.dumps(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
