#!/usr/bin/env python3
"""
Playbook Validator

Validates that all 8 IT Playbook phases are present and contain
required sections. Outputs a validation report.

Usage:
    python playbook_validator.py [--playbook-dir DIR]
"""

import argparse
import os
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
PLAYBOOK_DIR = BASE / "playbook"

REQUIRED_PHASES = {
    "01-project-intake.md": {
        "sections": ["Purpose", "Intake", "Checklist"],
        "description": "Project Intake"
    },
    "02-design-architecture.md": {
        "sections": ["Purpose", "Design", "Architecture"],
        "description": "Design & Architecture"
    },
    "03-development.md": {
        "sections": ["Purpose", "Development", "Standards"],
        "description": "Development"
    },
    "04-testing-qa.md": {
        "sections": ["Purpose", "Testing", "QA"],
        "description": "Testing & QA"
    },
    "05-deployment-release.md": {
        "sections": ["Purpose", "Deployment", "Checklist"],
        "description": "Deployment & Release"
    },
    "06-operations-monitoring.md": {
        "sections": ["Purpose", "Monitoring", "SLO"],
        "description": "Operations & Monitoring"
    },
    "07-maintenance.md": {
        "sections": ["Purpose", "Patch", "Capacity"],
        "description": "Maintenance & Support"
    },
    "08-decommission.md": {
        "sections": ["Purpose", "Checklist", "Decommission"],
        "description": "Decommission"
    },
}

EXAMPLES_REQUIRED = [
    "sample-project-charter.md",
    "sample-adr-001.md",
]


def check_file(path: Path, required_keywords: list) -> tuple:
    """Returns (passed: bool, missing: list). Keyword matching is case-insensitive."""
    if not path.exists():
        return False, [f"FILE MISSING: {path.name}"]
    text = path.read_text().lower()
    missing = [kw for kw in required_keywords if kw.lower() not in text]
    return len(missing) == 0, missing


def run_validation(playbook_dir: Path) -> dict:
    results = {
        "phases": {},
        "examples": {},
        "total_checks": 0,
        "passed_checks": 0,
        "failed_checks": 0,
        "issues": []
    }

    # Check phases
    for filename, spec in REQUIRED_PHASES.items():
        path = playbook_dir / filename
        passed, missing = check_file(path, spec["sections"])
        results["phases"][filename] = {
            "description": spec["description"],
            "passed": passed,
            "missing": missing
        }
        results["total_checks"] += 1
        if passed:
            results["passed_checks"] += 1
        else:
            results["failed_checks"] += 1
            results["issues"].extend([f"{filename}: missing keyword '{m}'" for m in missing])

    # Check examples
    examples_dir = playbook_dir.parent / "examples"
    for filename in EXAMPLES_REQUIRED:
        path = examples_dir / filename
        exists = path.exists()
        results["examples"][filename] = {"passed": exists}
        results["total_checks"] += 1
        if exists:
            results["passed_checks"] += 1
        else:
            results["failed_checks"] += 1
            results["issues"].append(f"examples/{filename}: FILE MISSING")

    return results


def format_report(results: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("  IT PLAYBOOK VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    lines.append("  PHASE VALIDATION")
    lines.append("  " + "-" * 40)
    for filename, r in results["phases"].items():
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        lines.append(f"  {status}  {r['description']:30s}  {filename}")
        if not r["passed"]:
            for m in r["missing"]:
                lines.append(f"         → missing: {m}")

    lines.append("")
    lines.append("  EXAMPLES VALIDATION")
    lines.append("  " + "-" * 40)
    for filename, r in results["examples"].items():
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        lines.append(f"  {status}  {filename}")

    lines.append("")
    lines.append("  " + "=" * 40)
    t = results["total_checks"]
    p = results["passed_checks"]
    f = results["failed_checks"]
    lines.append(f"  Results: {p}/{t} checks passed, {f} failed")

    if results["issues"]:
        lines.append("")
        lines.append("  ISSUES:")
        for issue in results["issues"]:
            lines.append(f"    → {issue}")
    else:
        lines.append("  All checks passed! Playbook is complete.")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="IT Playbook Validator")
    parser.add_argument("--playbook-dir", default=str(PLAYBOOK_DIR),
                        help="Path to playbook/ directory")
    args = parser.parse_args()

    playbook_dir = Path(args.playbook_dir)
    results = run_validation(playbook_dir)
    report = format_report(results)
    print(report)

    sys.exit(0 if results["failed_checks"] == 0 else 1)


if __name__ == "__main__":
    main()
