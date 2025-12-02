"""Rotate and scrub audit logs for P07."""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from datetime import datetime, timedelta
from pathlib import Path


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def rotate_logs(log_dir: Path, days: int, delete: bool = False) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=days)
    archived = []
    for path in sorted(log_dir.glob("*.log")):
        if datetime.utcfromtimestamp(path.stat().st_mtime) < cutoff:
            archived.append(path)
    metadata = {"rotated": [], "generated_at": datetime.utcnow().isoformat()}
    if archived:
        archive_path = log_dir.parent / "artifacts" / "rotation" / f"audit-archive-{datetime.utcnow().date()}.tar.gz"
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive_path, "w:gz") as tar:
            for item in archived:
                tar.add(item, arcname=item.name)
                metadata["rotated"].append({"file": item.name, "sha256": hash_file(item)})
                if delete:
                    item.unlink()
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path("logs/audit"))
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--delete", action="store_true")
    args = parser.parse_args()

    meta = rotate_logs(args.path, args.days, args.delete)
    manifest = args.path.parent / "artifacts" / "rotation" / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
