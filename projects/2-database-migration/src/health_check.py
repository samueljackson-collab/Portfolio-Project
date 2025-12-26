"""Health check for Database Migration Platform."""
from __future__ import annotations

import json
from pathlib import Path


def run_health_check() -> dict:
    """Verify essential migration assets exist."""
    base_dir = Path(__file__).resolve().parents[1]
    required_paths = [
        base_dir / "README.md",
        base_dir / "requirements.txt",
        base_dir / "src" / "migration_orchestrator.py",
        base_dir / "config",
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
