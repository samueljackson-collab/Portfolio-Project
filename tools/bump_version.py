#!/usr/bin/env python3
"""Bump semantic versions across repository files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Tuple

VERSION_PATTERN = re.compile(r"(\d+)\.(\d+)\.(\d+)")
TARGET_FILES = [
    Path("package.json"),
    Path("CHANGELOG.md"),
    Path("README.md"),
]


def parse_version(version: str) -> Tuple[int, int, int]:
    major, minor, patch = VERSION_PATTERN.fullmatch(version).groups()
    return int(major), int(minor), int(patch)


def bump(major: int, minor: int, patch: int, release: str) -> Tuple[int, int, int]:
    if release == "major":
        return major + 1, 0, 0
    if release == "minor":
        return major, minor + 1, 0
    if release == "patch":
        return major, minor, patch + 1
    raise ValueError("Release must be major, minor, or patch")


def update_file(path: Path, old: str, new: str) -> None:
    if not path.exists():
        return
    content = path.read_text()
    content = content.replace(old, new)
    path.write_text(content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release", choices=["major", "minor", "patch"], help="Type of release bump")
    parser.add_argument("current", help="Current semantic version (e.g., 1.4.0)")
    args = parser.parse_args()

    current_version = args.current
    match = VERSION_PATTERN.fullmatch(current_version)
    if not match:
        raise ValueError("Current version must be in the form X.Y.Z")

    new_version_tuple = bump(*parse_version(current_version), release=args.release)
    new_version = ".".join(str(part) for part in new_version_tuple)

    for file_path in TARGET_FILES:
        update_file(file_path, current_version, new_version)

    print(f"Version bumped from {current_version} to {new_version}")


if __name__ == "__main__":
    main()
