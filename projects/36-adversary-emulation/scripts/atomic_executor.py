#!/usr/bin/env python3
"""
atomic_executor.py — Adversary Emulation Atomic Test Executor

Loads emulation plan YAML files and executes or previews atomic tests
for detection validation. Designed for defensive security use only.

Usage:
    python atomic_executor.py --plan apt29 --dry-run
    python atomic_executor.py --plan fin7 --safe
    python atomic_executor.py --list-plans
    python atomic_executor.py --plan apt29 --phase phase-1 --dry-run

All commands in SAFE mode are pre-vetted as harmless:
  - Write to /tmp only
  - Read publicly accessible files (/etc/passwd, /etc/hosts, /etc/os-release)
  - Read environment variables
  - No network connections
  - No privilege escalation attempts
"""

import argparse
import datetime
import os
import subprocess
import sys
import time
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

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_plan(plan_name: str) -> dict:
    """Load and parse an emulation plan YAML file."""
    plan_name_lower = plan_name.lower()
    if plan_name_lower not in PLAN_FILES:
        available = ", ".join(PLAN_FILES.keys())
        print(f"{RED}ERROR: Plan '{plan_name}' not found. Available plans: {available}{RESET}")
        sys.exit(1)

    plan_path = PLAN_FILES[plan_name_lower]
    if not plan_path.exists():
        print(f"{RED}ERROR: Plan file not found: {plan_path}{RESET}")
        sys.exit(1)

    with open(plan_path, "r") as f:
        plan = yaml.safe_load(f)

    return plan


def list_plans() -> None:
    """List all available emulation plans."""
    print(f"\n{BOLD}=== Available Emulation Plans ==={RESET}\n")
    for name, path in PLAN_FILES.items():
        if path.exists():
            with open(path, "r") as f:
                plan = yaml.safe_load(f)
            technique_count = sum(
                len(phase.get("techniques", []))
                for phase in plan.get("phases", [])
            )
            print(f"  {CYAN}{name}{RESET}")
            print(f"    Name:       {plan.get('name', 'Unknown')}")
            print(f"    Version:    {plan.get('version', 'Unknown')}")
            print(f"    Phases:     {len(plan.get('phases', []))}")
            print(f"    Techniques: {technique_count}")
            print(f"    Author:     {plan.get('author', 'Unknown')}")
            print(f"    Date:       {plan.get('date', 'Unknown')}")
            print()
        else:
            print(f"  {RED}{name}{RESET} — file not found: {path}")


def list_phases(plan: dict) -> None:
    """List all phases and their test cases."""
    print(f"\n{BOLD}=== Plan: {plan['name']} ==={RESET}")
    print(f"Version: {plan.get('version', 'Unknown')} | Author: {plan.get('author', 'Unknown')}\n")

    for phase in plan.get("phases", []):
        techniques = phase.get("techniques", [])
        print(f"{BOLD}[{phase['id']}] {phase['name']}{RESET}")
        print(f"  {phase.get('description', '').strip()[:100]}...")
        print(f"  Tests: {len(techniques)}")
        for tech in techniques:
            safe_marker = f"{GREEN}SAFE{RESET}" if tech.get("safe") else f"{RED}UNSAFE{RESET}"
            print(f"    [{safe_marker}] {tech['test_id']} — {tech['name']} ({tech['id']})")
        print()


def run_cleanup(command: str) -> None:
    """Run cleanup command silently."""
    try:
        subprocess.run(command, shell=True, capture_output=True, timeout=10)
    except Exception:
        pass


def execute_test(tech: dict, dry_run: bool, safe_only: bool, verbose: bool) -> dict:
    """Execute a single atomic test. Returns result dict."""
    result = {
        "test_id": tech["test_id"],
        "technique_id": tech["id"],
        "technique_name": tech["name"],
        "tactic": tech.get("tactic", "unknown"),
        "safe": tech.get("safe", False),
        "status": None,
        "output": None,
        "error": None,
        "start_time": datetime.datetime.utcnow().isoformat(),
        "duration_ms": 0,
    }

    is_safe = tech.get("safe", False)

    if safe_only and not is_safe:
        result["status"] = "SKIPPED_UNSAFE"
        return result

    command = tech.get("command", "")
    cleanup = tech.get("cleanup", "")

    if dry_run:
        result["status"] = "WOULD_EXECUTE"
        return result

    # Execute the test
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        result["duration_ms"] = elapsed_ms

        if proc.returncode == 0:
            result["status"] = "PASSED"
            result["output"] = proc.stdout.strip()[:500] if proc.stdout else ""
        else:
            result["status"] = "FAILED"
            result["error"] = proc.stderr.strip()[:500] if proc.stderr else f"exit code {proc.returncode}"

    except subprocess.TimeoutExpired:
        result["status"] = "TIMEOUT"
        result["error"] = "Command timed out after 30 seconds"
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

    # Run cleanup
    if cleanup:
        run_cleanup(cleanup)

    return result


def format_result_line(result: dict) -> str:
    """Format a single result for display."""
    status = result["status"]
    status_colors = {
        "PASSED": GREEN,
        "FAILED": RED,
        "WOULD_EXECUTE": YELLOW,
        "SKIPPED_UNSAFE": CYAN,
        "TIMEOUT": RED,
        "ERROR": RED,
    }
    color = status_colors.get(status, RESET)
    return (
        f"  [{color}{status}{RESET}] "
        f"{result['test_id']} — "
        f"{result['technique_id']} {result['technique_name']}"
    )


def print_execution_report(
    plan: dict,
    results: list,
    mode: str,
    phase_filter: Optional[str],
    start_time: datetime.datetime,
) -> None:
    """Print the full execution report."""
    end_time = datetime.datetime.utcnow()
    duration = (end_time - start_time).total_seconds()

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    would_execute = sum(1 for r in results if r["status"] == "WOULD_EXECUTE")
    skipped = sum(1 for r in results if r["status"] == "SKIPPED_UNSAFE")
    errors = sum(1 for r in results if r["status"] in ("TIMEOUT", "ERROR"))

    print()
    print("=" * 70)
    print(f"{BOLD}=== Adversary Emulation Execution Report ==={RESET}")
    print("=" * 70)
    print(f"Plan:     {plan['name']} v{plan.get('version', '?')}")
    print(f"Executed: {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Mode:     {mode}")
    print(f"Analyst:  {plan.get('author', 'Unknown')}")
    if phase_filter:
        print(f"Filter:   Phase = {phase_filter}")
    print()

    print(f"{BOLD}=== Results Summary ==={RESET}")
    print(f"Total Tests:    {total}")
    if mode == "DRY-RUN":
        print(f"Would Execute:  {would_execute}")
    else:
        print(f"Passed:         {GREEN}{passed}{RESET}")
        print(f"Failed:         {RED}{failed}{RESET}")
        print(f"Skipped:        {CYAN}{skipped}{RESET}")
        print(f"Errors:         {RED}{errors}{RESET}")
    print(f"Duration:       {duration:.2f}s")
    print()

    # Per-phase breakdown
    results_by_id = {r["test_id"]: r for r in results}

    for phase in plan.get("phases", []):
        if phase_filter and phase["id"] != phase_filter:
            continue

        phase_techniques = phase.get("techniques", [])
        phase_results = [
            results_by_id[t["test_id"]]
            for t in phase_techniques
            if t["test_id"] in results_by_id
        ]

        if not phase_results:
            continue

        print(f"{BOLD}--- {phase['name']} ---{RESET}")
        for result in phase_results:
            print(format_result_line(result))
            if result.get("error"):
                print(f"    Error: {result['error']}")
        print()

    print("=" * 70)
    print(f"{BOLD}=== Coverage by Tactic ==={RESET}")
    print(f"{'Tactic':<30} {'Tests':>6} {'Pass':>6} {'Fail':>6}")
    print("-" * 50)

    tactic_stats: dict = {}
    for r in results:
        tactic = r.get("tactic", "unknown").replace("-", " ").title()
        if tactic not in tactic_stats:
            tactic_stats[tactic] = {"total": 0, "pass": 0, "fail": 0}
        tactic_stats[tactic]["total"] += 1
        if r["status"] in ("PASSED", "WOULD_EXECUTE"):
            tactic_stats[tactic]["pass"] += 1
        elif r["status"] in ("FAILED", "ERROR", "TIMEOUT"):
            tactic_stats[tactic]["fail"] += 1

    for tactic, stats in sorted(tactic_stats.items()):
        print(f"  {tactic:<28} {stats['total']:>6} {stats['pass']:>6} {stats['fail']:>6}")

    print("-" * 50)
    print(f"  {'TOTAL':<28} {total:>6} {passed + would_execute:>6} {failed:>6}")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adversary Emulation Atomic Test Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python atomic_executor.py --list-plans
  python atomic_executor.py --plan apt29 --dry-run
  python atomic_executor.py --plan fin7 --safe
  python atomic_executor.py --plan apt29 --phase phase-1 --dry-run
  python atomic_executor.py --plan apt29 --list-phases
        """,
    )
    parser.add_argument(
        "--plan",
        help="Emulation plan to execute (apt29, fin7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would execute without running commands",
    )
    parser.add_argument(
        "--safe",
        action="store_true",
        help="Execute only pre-vetted safe tests (file writes to /tmp, env reads)",
    )
    parser.add_argument(
        "--phase",
        help="Execute only a specific phase (e.g., phase-1)",
    )
    parser.add_argument(
        "--list-plans",
        action="store_true",
        help="List all available emulation plans",
    )
    parser.add_argument(
        "--list-phases",
        action="store_true",
        help="List all phases and test cases for a plan",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including command output",
    )

    args = parser.parse_args()

    if args.list_plans:
        list_plans()
        return

    if not args.plan:
        parser.print_help()
        print(f"\n{YELLOW}Hint: Use --list-plans to see available plans{RESET}")
        sys.exit(1)

    plan = load_plan(args.plan)

    if args.list_phases:
        list_phases(plan)
        return

    if not args.dry_run and not args.safe:
        print(
            f"{YELLOW}WARNING: No execution mode specified.\n"
            f"  Use --dry-run to preview without executing.\n"
            f"  Use --safe to execute only pre-vetted safe tests.\n"
            f"  Defaulting to --dry-run.{RESET}\n"
        )
        args.dry_run = True

    mode = "DRY-RUN" if args.dry_run else "SAFE-EXECUTE"

    print(f"\n{BOLD}Adversary Emulation Atomic Executor{RESET}")
    print(f"Plan: {plan['name']} | Mode: {mode}")
    print("-" * 60)

    start_time = datetime.datetime.utcnow()
    results = []

    for phase in plan.get("phases", []):
        if args.phase and phase["id"] != args.phase:
            continue

        print(f"\n{CYAN}[Phase] {phase['id']}: {phase['name']}{RESET}")

        for tech in phase.get("techniques", []):
            result = execute_test(
                tech,
                dry_run=args.dry_run,
                safe_only=args.safe,
                verbose=args.verbose,
            )
            results.append(result)
            print(format_result_line(result))

            if args.verbose and result.get("output"):
                print(f"    Output: {result['output'][:200]}")

    print_execution_report(plan, results, mode, args.phase, start_time)


if __name__ == "__main__":
    main()
