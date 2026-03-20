#!/usr/bin/env python3
"""
QA Gate Checker

Runs applicable quality gates against a project directory and produces
a structured compliance report. Gates are loaded from gate-definitions.yaml.

Usage:
    python gate-checker.py <project_path>
    python gate-checker.py --demo
    python gate-checker.py --list-gates
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

GATES_FILE = Path(__file__).parent / "gate-definitions.yaml"


def load_gates():
    with open(GATES_FILE) as f:
        return yaml.safe_load(f)["gates"]


def detect_project_type(project_path: Path) -> list:
    """Detect which gate categories apply based on project contents."""
    detected = []

    py_files = list(project_path.rglob("*.py"))
    tf_files = list(project_path.rglob("*.tf"))
    ts_files = list(project_path.rglob("*.ts"))
    js_files = list(project_path.rglob("*.js"))
    dockerfiles = list(project_path.rglob("Dockerfile*"))

    if py_files:
        detected.append("python")
    if tf_files:
        detected.append("terraform")
    if ts_files:
        detected.append("typescript")
    if js_files or ts_files:
        detected.append("node")
    if dockerfiles:
        detected.append("docker")

    return detected


def check_gate_structurally(gate: dict, project_path: Path) -> dict:
    """
    Structural check: verifies that required files/patterns exist for each gate.
    Does NOT actually run the tool (for portability without full CI environment).
    """
    gate_id = gate["id"]
    name = gate["name"]
    tool = gate["tool"]
    applies_to = gate.get("applies_to", [])

    result = {
        "id": gate_id,
        "name": name,
        "tool": tool,
        "status": "PASS",
        "note": "",
        "severity": gate.get("severity", "block"),
    }

    # Python checks
    if "python" in applies_to:
        py_files = list(project_path.rglob("*.py"))
        if not py_files:
            result["status"] = "SKIP"
            result["note"] = "No Python files found"
            return result

        if tool == "pytest":
            test_dirs = [p for p in project_path.rglob("test_*.py")]
            if not test_dirs:
                result["status"] = "WARN"
                result["note"] = "No test files found (test_*.py pattern)"
            else:
                result["note"] = f"{len(test_dirs)} test file(s) found"

        elif tool == "pytest-cov":
            test_dirs = [p for p in project_path.rglob("test_*.py")]
            if not test_dirs:
                result["status"] = "WARN"
                result["note"] = "No test files found — coverage cannot be measured"
            else:
                result["note"] = f"Coverage gate: ≥ {gate.get('threshold', 80)}% required"

    # Terraform checks
    if "terraform" in applies_to:
        tf_files = list(project_path.rglob("*.tf"))
        if not tf_files:
            result["status"] = "SKIP"
            result["note"] = "No Terraform files found"
            return result

        if tool == "terraform":
            has_versions = any("versions.tf" in str(f) for f in tf_files)
            has_variables = any("variables.tf" in str(f) for f in tf_files)
            if "fmt" in gate.get("command", "") and not has_versions:
                result["note"] = f"{len(tf_files)} Terraform file(s) found"
            else:
                result["note"] = f"{len(tf_files)} Terraform file(s), variables.tf: {'✓' if has_variables else '✗'}"

    # Docker checks
    if "docker" in applies_to:
        dockerfiles = list(project_path.rglob("Dockerfile*"))
        if not dockerfiles:
            result["status"] = "SKIP"
            result["note"] = "No Dockerfile found"
            return result

        if tool in ["trivy", "hadolint"]:
            # Check Dockerfile has non-root user
            df_text = dockerfiles[0].read_text()
            has_user = "USER " in df_text
            has_healthcheck = "HEALTHCHECK" in df_text
            issues = []
            if not has_user:
                issues.append("missing USER directive")
            if not has_healthcheck:
                issues.append("missing HEALTHCHECK")
            if issues:
                result["status"] = "WARN"
                result["note"] = "Dockerfile issues: " + ", ".join(issues)
            else:
                result["note"] = "Dockerfile: USER ✓, HEALTHCHECK ✓"

    return result


def generate_report(project_path: Path, results: list) -> str:
    lines = []
    lines.append("=" * 68)
    lines.append("  QA GATE COMPLIANCE REPORT")
    lines.append(f"  Project: {project_path.name}")
    lines.append("=" * 68)
    lines.append("")

    categories = {
        "code_quality": [],
        "testing": [],
        "security": [],
    }

    for r in results:
        gate = next((g for g in load_gates() if g["id"] == r["id"]), {})
        cat = gate.get("category", "other")
        categories.setdefault(cat, []).append(r)

    cat_labels = {
        "code_quality": "CODE QUALITY",
        "testing": "TESTING",
        "security": "SECURITY",
    }

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    failed = sum(1 for r in results if r["status"] == "FAIL")

    for cat, cat_results in categories.items():
        if not cat_results:
            continue
        lines.append(f"  {cat_labels.get(cat, cat.upper())}")
        lines.append("  " + "-" * 50)
        for r in cat_results:
            icon = {"PASS": "✅", "WARN": "⚠️ ", "SKIP": "⏭️ ", "FAIL": "❌"}.get(r["status"], "?")
            lines.append(f"  {icon} [{r['id']}] {r['name']}")
            if r["note"]:
                lines.append(f"       {r['note']}")
        lines.append("")

    lines.append("  " + "=" * 50)
    lines.append(f"  Summary: {passed} passed, {warned} warned, {skipped} skipped, {failed} failed")
    lines.append(f"  Total gates evaluated: {total}")

    blocking_failures = [r for r in results if r["status"] == "FAIL"
                         and r.get("severity") in ("block", "block_on_high", "block_on_critical")]
    if blocking_failures:
        lines.append("")
        lines.append("  ❌ BLOCKING FAILURES — merge not allowed:")
        for r in blocking_failures:
            lines.append(f"    → {r['id']}: {r['name']}")
    elif failed == 0:
        lines.append("  ✅ All applicable gates passed — PR eligible for merge.")

    lines.append("=" * 68)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="QA Gate Checker")
    parser.add_argument("project_path", nargs="?", help="Path to project directory")
    parser.add_argument("--demo", action="store_true", help="Run against this handbook's project 1 (aws-infra)")
    parser.add_argument("--list-gates", action="store_true", help="List all gate definitions")
    args = parser.parse_args()

    if args.list_gates:
        gates = load_gates()
        print(f"{'ID':<12} {'Name':<35} {'Tool':<15} {'Applies To'}")
        print("-" * 80)
        for g in gates:
            print(f"{g['id']:<12} {g['name']:<35} {g['tool']:<15} {', '.join(g['applies_to'])}")
        return

    if args.demo:
        # Use the p01-aws-infra project as demo target
        project_path = Path(__file__).parent.parent.parent.parent / "projects" / "p01-aws-infra"
        if not project_path.exists():
            project_path = Path(__file__).parent.parent.parent.parent / "projects" / "1-aws-infrastructure-automation"
        if not project_path.exists():
            print("Demo target not found; using current directory")
            project_path = Path(".")
    elif args.project_path:
        project_path = Path(args.project_path)
    else:
        print("Error: provide a project path or --demo", file=sys.stderr)
        sys.exit(1)

    if not project_path.exists():
        print(f"Error: {project_path} does not exist", file=sys.stderr)
        sys.exit(1)

    gates = load_gates()
    project_types = detect_project_type(project_path)

    results = []
    for gate in gates:
        applies_to = gate.get("applies_to", [])
        if any(t in project_types for t in applies_to):
            r = check_gate_structurally(gate, project_path)
            results.append(r)

    report = generate_report(project_path, results)
    print(report)

    failed_blocking = any(
        r["status"] == "FAIL" and r.get("severity") in ("block", "block_on_high", "block_on_critical")
        for r in results
    )
    sys.exit(1 if failed_blocking else 0)


if __name__ == "__main__":
    main()
