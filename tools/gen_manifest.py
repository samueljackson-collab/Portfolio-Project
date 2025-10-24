#!/usr/bin/env python3
"""Generate a manifest describing the repository contents."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".terraform", ".mypy_cache", ".pytest_cache"}


def collect_file_info(root: Path) -> Dict[str, int]:
    """Return a counter of file extensions under the root directory."""
    counter: Counter[str] = Counter()
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in IGNORED_DIRS:
                continue
        elif path.is_file():
            ext = path.suffix or "<no-ext>"
            counter[ext] += 1
    return dict(counter)


def list_services(root: Path) -> List[str]:
    services = []
    for directory in ["backend", "frontend", "infra", "monitoring", "e2e-tests"]:
        if (root / directory).exists():
            services.append(directory)
    return services


def build_manifest(root: Path) -> Dict[str, object]:
    return {
        "root": str(root),
        "total_files": sum(1 for _ in root.rglob("*") if _.is_file()),
        "extension_breakdown": collect_file_info(root),
        "services": list_services(root),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="File to write manifest JSON")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    manifest = build_manifest(root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest written to {args.output}")


if __name__ == "__main__":
    main()
