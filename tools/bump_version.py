#!/usr/bin/env python3
"""Semantic version bumper."""
from __future__ import annotations

import argparse
import pathlib
import re
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
PACKAGE_JSON = ROOT / "package.json"

VERSION_PATTERN = re.compile(r"\[([0-9]+\.[0-9]+\.[0-9]+)\]")


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def bump(self, part: str) -> "Version":
        if part == "major":
            return Version(self.major + 1, 0, 0)
        if part == "minor":
            return Version(self.major, self.minor + 1, 0)
        if part == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError(f"Unknown part: {part}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def parse_current_version() -> Version:
    text = CHANGELOG.read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(text)
    if not match:
        raise RuntimeError("Unable to determine current version from CHANGELOG")
    major, minor, patch = map(int, match.group(1).split("."))
    return Version(major, minor, patch)


def update_package_json(new_version: Version) -> None:
    text = PACKAGE_JSON.read_text(encoding="utf-8")
    updated = re.sub(r'"version": "[0-9]+\.[0-9]+\.[0-9]+"', f'"version": "{new_version}"', text, count=1)
    PACKAGE_JSON.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("part", choices=["major", "minor", "patch"], help="Version part to bump")
    args = parser.parse_args()

    current = parse_current_version()
    new_version = current.bump(args.part)
    update_package_json(new_version)
    print(f"Bumped version from {current} to {new_version}")


if __name__ == "__main__":
    main()
