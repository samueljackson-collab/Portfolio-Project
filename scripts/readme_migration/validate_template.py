#!/usr/bin/env python3
"""Validate README files against the portfolio README migration template."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_HEADING_PATTERNS: dict[str, str] = {
    "overview": r"overview",
    "scope_status": r"scope\s*&\s*status",
    "architecture": r"architecture",
    "setup_runbook": r"setup\s*&\s*runbook",
    "testing": r"testing",
    "risk": r"risk",
    "delivery": r"delivery\s*&\s*observability",
    "roadmap": r"roadmap",
    "evidence_index": r"evidence\s+index",
    "documentation_freshness": r"documentation\s+freshness",
}

TABLE_REQUIRED_SECTIONS: dict[str, str] = {
    "scope_status": "scope_status",
    "testing": "testing",
    "risk": "risk",
    "roadmap": "roadmap",
    "documentation_freshness": "documentation_freshness",
}


@dataclass
class Heading:
    level: int
    title: str
    start: int
    end: int


def run_git_command(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def discover_readmes(mode: str, base_ref: str) -> list[Path]:
    if mode == "full":
        return sorted(
            path
            for path in REPO_ROOT.rglob("README.md")
            if ".git" not in path.parts and "node_modules" not in path.parts
        )

    diff_output = run_git_command(
        ["diff", "--name-only", "--diff-filter=AMR", f"{base_ref}...HEAD"]
    )
    if not diff_output:
        return []

    return sorted(
        REPO_ROOT / rel_path
        for rel_path in diff_output.splitlines()
        if rel_path.endswith("README.md")
    )


def extract_headings(lines: list[str]) -> list[Heading]:
    headings: list[Heading] = []
    for idx, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        headings.append(Heading(level=len(match.group(1)), title=match.group(2), start=idx, end=len(lines)))

    for current, nxt in zip(headings, headings[1:]):
        current.end = nxt.start

    return headings


def find_heading(headings: Iterable[Heading], pattern: str) -> Heading | None:
    regex = re.compile(pattern, flags=re.IGNORECASE)
    for heading in headings:
        if regex.search(heading.title):
            return heading
    return None


def has_non_empty_table(section_lines: list[str]) -> bool:
    i = 0
    while i < len(section_lines):
        line = section_lines[i].strip()
        if not (line.startswith("|") and line.endswith("|")):
            i += 1
            continue

        block = []
        while i < len(section_lines):
            candidate = section_lines[i].strip()
            if candidate.startswith("|") and candidate.endswith("|"):
                block.append(candidate)
                i += 1
            else:
                break

        if len(block) < 3:
            continue

        separator = block[1].replace(" ", "")
        if not re.fullmatch(r"\|:?-{3,}:?(\|:?-{3,}:?)+\|", separator):
            continue

        data_rows = [row for row in block[2:] if re.sub(r"[|\s]", "", row)]
        if data_rows:
            return True

    return False


def validate_readme(path: Path) -> dict[str, object]:
    content = path.read_bytes().decode("utf-8", errors="replace")
    lines = content.splitlines()
    headings = extract_headings(lines)

    errors: list[str] = []

    for check_name, pattern in REQUIRED_HEADING_PATTERNS.items():
        if find_heading(headings, pattern) is None:
            errors.append(f"missing_required_heading:{check_name}")

    if re.search(r"status\s*(key|legend)", content, flags=re.IGNORECASE) is None:
        errors.append("missing_status_legend")

    architecture_heading = find_heading(headings, REQUIRED_HEADING_PATTERNS["architecture"])
    delivery_heading = find_heading(headings, REQUIRED_HEADING_PATTERNS["delivery"])

    if architecture_heading:
        architecture_content = "\n".join(lines[architecture_heading.start:architecture_heading.end])
        if "```mermaid" not in architecture_content:
            errors.append("missing_architecture_mermaid")
    if delivery_heading:
        delivery_content = "\n".join(lines[delivery_heading.start:delivery_heading.end])
        if "```mermaid" not in delivery_content:
            errors.append("missing_delivery_mermaid")

    for table_name, section_key in TABLE_REQUIRED_SECTIONS.items():
        section_heading = find_heading(headings, REQUIRED_HEADING_PATTERNS[section_key])
        if section_heading is None:
            continue
        section_lines = lines[section_heading.start:section_heading.end]
        if not has_non_empty_table(section_lines):
            errors.append(f"missing_non_empty_table:{table_name}")

    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "compliant": not errors,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["changed", "full"], default="changed")
    parser.add_argument(
        "--base-ref",
        default="origin/main",
        help="Git base ref for changed mode (default: origin/main)",
    )
    args = parser.parse_args()

    try:
        readmes = discover_readmes(mode=args.mode, base_ref=args.base_ref)
    except subprocess.CalledProcessError as exc:
        print(f"Failed to discover README files: {exc.stderr}", file=sys.stderr)
        return 2

    results = [validate_readme(path) for path in readmes]
    non_compliant = [item for item in results if not item["compliant"]]

    report = {
        "mode": args.mode,
        "base_ref": args.base_ref if args.mode == "changed" else None,
        "checked_files": len(results),
        "non_compliant_files": len(non_compliant),
        "files": results,
    }

    print(json.dumps(report, indent=2))
    print()

    if not results:
        print("README template validation summary: no README files matched the selected scope.")
    elif not non_compliant:
        print("README template validation summary: all checked README files are compliant.")
    else:
        print("README template validation summary: non-compliant README files detected:")
        for item in non_compliant:
            errors = ", ".join(item["errors"])
            print(f"- {item['path']}: {errors}")

    return 1 if non_compliant else 0


if __name__ == "__main__":
    sys.exit(main())
