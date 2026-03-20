#!/usr/bin/env python3
"""
generate_report.py — Emulation Plan Report Generator

Reads one or more emulation plan YAML files and generates formatted
reports suitable for inclusion in security documentation and presentations.

Usage:
    python generate_report.py --plan apt29
    python generate_report.py --plan fin7 --output /tmp/fin7_report.txt
    python generate_report.py --all
    python generate_report.py --plan apt29 --format markdown
"""

import argparse
import datetime
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


PLANS_DIR = Path(__file__).parent.parent / "emulation-plans"
PLAN_FILES = {
    "apt29": PLANS_DIR / "apt29-plan.yaml",
    "fin7": PLANS_DIR / "fin7-plan.yaml",
}


def load_plan(plan_name: str) -> dict:
    """Load and parse an emulation plan YAML file."""
    plan_name_lower = plan_name.lower()
    if plan_name_lower not in PLAN_FILES:
        available = ", ".join(PLAN_FILES.keys())
        print(f"ERROR: Plan '{plan_name}' not found. Available: {available}")
        sys.exit(1)

    path = PLAN_FILES[plan_name_lower]
    if not path.exists():
        print(f"ERROR: Plan file not found: {path}")
        sys.exit(1)

    with open(path, "r") as f:
        return yaml.safe_load(f)


def count_techniques(plan: dict) -> int:
    """Count total unique techniques in a plan."""
    technique_ids = set()
    for phase in plan.get("phases", []):
        for tech in phase.get("techniques", []):
            technique_ids.add(tech["id"])
    return len(technique_ids)


def count_tests(plan: dict) -> int:
    """Count total tests in a plan."""
    return sum(len(phase.get("techniques", [])) for phase in plan.get("phases", []))


def get_tactic_summary(plan: dict) -> dict:
    """Return dict of tactic -> {tests, techniques}."""
    summary: dict = {}
    for phase in plan.get("phases", []):
        phase_name = phase["name"]
        techniques = phase.get("techniques", [])
        unique_technique_ids = set(t["id"] for t in techniques)
        summary[phase_name] = {
            "tests": len(techniques),
            "techniques": len(unique_technique_ids),
        }
    return summary


def generate_text_report(plan: dict, mode: str = "DRY-RUN") -> str:
    """Generate a plain-text formatted emulation report."""
    now = datetime.datetime.utcnow()
    lines = []

    phases = plan.get("phases", [])
    total_tests = count_tests(plan)
    total_techniques = count_techniques(plan)
    tactic_summary = get_tactic_summary(plan)

    # Header
    lines.append("=" * 70)
    lines.append("=== Adversary Emulation Report ===")
    lines.append("=" * 70)
    lines.append(f"Plan:     {plan['name']} v{plan.get('version', '1.0')}")
    lines.append(f"Executed: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append(f"Mode:     {mode} (no commands executed)")
    lines.append(f"Analyst:  {plan.get('author', 'Unknown')}")
    lines.append(f"Plan ID:  {plan.get('id', 'Unknown')}")
    lines.append("")

    # Executive Summary
    lines.append("=" * 70)
    lines.append("=== Executive Summary ===")
    lines.append("=" * 70)
    lines.append(f"Phases:     {len(phases)}")
    lines.append(f"Techniques: {total_techniques}")
    lines.append(f"Tests:      {total_tests}")
    lines.append(f"Coverage:   {total_techniques} MITRE ATT&CK techniques across {len(phases)} tactics")
    lines.append("")
    lines.append(f"Description:")
    description = plan.get("description", "").strip()
    for para in description.split("\n"):
        lines.append(f"  {para.strip()}")
    lines.append("")

    # MITRE Groups
    groups = plan.get("mitre_groups", [])
    if groups:
        lines.append(f"MITRE Groups: {', '.join(groups)}")
    tags = plan.get("tags", [])
    if tags:
        lines.append(f"Tags: {', '.join(tags)}")
    lines.append("")

    # Per-phase detail
    lines.append("=" * 70)
    lines.append("=== Detailed Phase Report ===")
    lines.append("=" * 70)

    for phase in phases:
        techniques = phase.get("techniques", [])
        lines.append("")
        lines.append(f"=== {phase['name']} ===")
        lines.append(f"Phase ID:    {phase['id']}")
        lines.append(f"Tests:       {len(techniques)}")
        lines.append(f"Description: {phase.get('description', '').strip()[:120]}...")
        lines.append("")

        for tech in techniques:
            safe_label = "SAFE" if tech.get("safe") else "UNSAFE"
            lines.append(f"  [{safe_label}] [{tech['id']}] {tech['name']}")
            lines.append(f"    Test ID:   {tech['test_id']} — {tech['test_name']}")
            lines.append(f"    Tactic:    {tech.get('tactic', 'unknown')}")
            lines.append(f"    Command:   {tech.get('command', 'N/A')}")
            lines.append(f"    Detection: {tech.get('expected_detection', 'N/A')}")
            lines.append(f"    Rule:      {tech.get('detection_rule', 'N/A')}")
            lines.append(f"    Status:    WOULD_EXECUTE (dry-run)")
            cleanup = tech.get("cleanup", "N/A")
            lines.append(f"    Cleanup:   {cleanup}")
            refs = tech.get("references", [])
            if refs:
                lines.append(f"    Reference: {refs[0]}")
            lines.append("")

    # Coverage Summary
    lines.append("=" * 70)
    lines.append("=== Coverage Summary ===")
    lines.append("=" * 70)
    lines.append(f"{'Tactic':<30} {'Tests':>6} {'Techniques':>12}")
    lines.append("-" * 50)
    total_t = 0
    total_tech = 0
    for tactic, stats in tactic_summary.items():
        lines.append(f"  {tactic:<28} {stats['tests']:>6} {stats['techniques']:>12}")
        total_t += stats["tests"]
        total_tech += stats["techniques"]
    lines.append("-" * 50)
    lines.append(f"  {'TOTAL':<28} {total_t:>6} {total_tech:>12}")
    lines.append("")

    # Detection Engineering Recommendations
    lines.append("=" * 70)
    lines.append("=== Detection Engineering Recommendations ===")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Based on this emulation plan, the following detection capabilities")
    lines.append("should be validated or developed:")
    lines.append("")

    all_rules = set()
    for phase in phases:
        for tech in phase.get("techniques", []):
            rule = tech.get("detection_rule", "")
            if rule:
                all_rules.add(rule)

    for rule in sorted(all_rules):
        lines.append(f"  - {rule}")

    lines.append("")
    lines.append("Integration Notes:")
    lines.append("  - Import Sigma rules into your SIEM (Splunk, Elastic, QRadar)")
    lines.append("  - Validate EDR telemetry covers all techniques in this plan")
    lines.append("  - Run detection-as-code pipeline to regression-test detections")
    lines.append("  - Cross-reference with Project 35 (Detection Rules) for coverage")
    lines.append("")

    lines.append("=" * 70)
    lines.append(f"Report generated: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_markdown_report(plan: dict) -> str:
    """Generate a Markdown formatted emulation report."""
    now = datetime.datetime.utcnow()
    phases = plan.get("phases", [])
    total_tests = count_tests(plan)
    total_techniques = count_techniques(plan)
    tactic_summary = get_tactic_summary(plan)

    lines = []
    lines.append(f"# Adversary Emulation Report: {plan['name']}")
    lines.append("")
    lines.append(f"**Version:** {plan.get('version', '1.0')}  ")
    lines.append(f"**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')} UTC  ")
    lines.append(f"**Analyst:** {plan.get('author', 'Unknown')}  ")
    lines.append(f"**Plan ID:** {plan.get('id', 'Unknown')}  ")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Phases | {len(phases)} |")
    lines.append(f"| Unique Techniques | {total_techniques} |")
    lines.append(f"| Total Tests | {total_tests} |")
    lines.append(f"| MITRE Groups | {', '.join(plan.get('mitre_groups', []))} |")
    lines.append("")

    lines.append("## Coverage by Tactic")
    lines.append("")
    lines.append("| Tactic | Tests | Techniques |")
    lines.append("|--------|-------|------------|")
    for tactic, stats in tactic_summary.items():
        lines.append(f"| {tactic} | {stats['tests']} | {stats['techniques']} |")
    lines.append("")

    lines.append("## Phase Details")
    lines.append("")

    for phase in phases:
        techniques = phase.get("techniques", [])
        lines.append(f"### {phase['name']}")
        lines.append("")
        lines.append(f"**Phase ID:** `{phase['id']}` | **Tests:** {len(techniques)}")
        lines.append("")
        lines.append("| Test ID | Technique | MITRE ID | Safe | Detection Rule |")
        lines.append("|---------|-----------|----------|------|----------------|")
        for tech in techniques:
            safe_marker = "Yes" if tech.get("safe") else "No"
            rule = tech.get("detection_rule", "N/A").replace("sigma/", "")
            lines.append(
                f"| {tech['test_id']} | {tech['name']} | "
                f"`{tech['id']}` | {safe_marker} | `{rule}` |"
            )
        lines.append("")

    lines.append("---")
    lines.append(f"*Report generated {now.strftime('%Y-%m-%d %H:%M:%S')} UTC*")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emulation Plan Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_report.py --plan apt29
  python generate_report.py --plan fin7 --output /tmp/fin7_report.txt
  python generate_report.py --all
  python generate_report.py --plan apt29 --format markdown
        """,
    )
    parser.add_argument("--plan", help="Plan name (apt29, fin7)")
    parser.add_argument("--all", action="store_true", help="Generate reports for all plans")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument(
        "--format",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if not args.plan and not args.all:
        parser.print_help()
        sys.exit(1)

    plan_names = list(PLAN_FILES.keys()) if args.all else [args.plan]

    all_output = []

    for plan_name in plan_names:
        plan = load_plan(plan_name)

        if args.format == "markdown":
            report = generate_markdown_report(plan)
        else:
            report = generate_text_report(plan)

        all_output.append(report)

    combined = "\n\n".join(all_output)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(combined)
        print(f"Report written to: {output_path}")
    else:
        print(combined)


if __name__ == "__main__":
    main()
