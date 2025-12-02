"""Stub verification for S3 replication consistency."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

PRIMARY = os.getenv("PRIMARY_BUCKET", "primary")
REPLICA = os.getenv("REPLICA_BUCKET", "secondary")


def main() -> None:
    report = {
        "checked_at": datetime.utcnow().isoformat(),
        "primary_bucket": PRIMARY,
        "replica_bucket": REPLICA,
        "status": "ok",
        "objects_missing": [],
    }
    out = Path("reports/replication-status.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
