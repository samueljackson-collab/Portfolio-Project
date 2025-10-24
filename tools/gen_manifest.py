#!/usr/bin/env python3
"""Generate repository manifest with file counts and line statistics."""
from __future__ import annotations

import json
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".terraform"}


def should_skip(path: pathlib.Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def main() -> None:
    counts: Counter[str] = Counter()
    total_lines = 0

    for file_path in ROOT.rglob("*"):
        if file_path.is_dir():
            continue
        if should_skip(file_path):
            continue
        suffix = file_path.suffix or "<no_ext>"
        counts[suffix] += 1
        try:
            total_lines += sum(1 for _ in file_path.open("r", encoding="utf-8", errors="ignore"))
        except OSError:
            continue

    manifest = {
        "total_files": sum(counts.values()),
        "total_lines": total_lines,
        "files_by_extension": dict(counts),
    }

    output_path = ROOT / "data" / "master_repo_manifest_v1.4.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written to {output_path}")


if __name__ == "__main__":
    main()
