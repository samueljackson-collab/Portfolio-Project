#!/usr/bin/env python3
"""
AWS Landing Zone SCP Validation Script.

Reads all JSON files in terraform/scp/policies/, validates that each:
  - Is valid JSON
  - Has the required top-level 'Version' field
  - Has the required top-level 'Statement' array
  - Each Statement entry has 'Effect', 'Action', and 'Resource' fields

Prints a detailed validation report and exits with code 0 if all checks pass,
or code 1 if any check fails.

Usage:
    python3 scripts/validate_scps.py
    python3 scripts/validate_scps.py --policies-dir path/to/policies
"""

import json
import os
import sys
import argparse
from typing import Any


def find_policies_dir() -> str:
    """Locate the SCP policies directory relative to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    return os.path.join(project_root, "terraform", "scp", "policies")


def load_policy_files(policies_dir: str) -> list[tuple[str, str]]:
    """Return list of (filename, full_path) for all JSON files in the directory."""
    if not os.path.isdir(policies_dir):
        print(f"[ERROR] Policies directory not found: {policies_dir}", file=sys.stderr)
        sys.exit(1)

    files = [
        (f, os.path.join(policies_dir, f))
        for f in sorted(os.listdir(policies_dir))
        if f.endswith(".json")
    ]
    return files


def validate_policy(filename: str, filepath: str) -> tuple[list[str], list[str]]:
    """
    Validate a single SCP JSON file.

    Returns:
        (passes, failures) — two lists of result message strings
    """
    passes = []
    failures = []

    def ok(msg: str) -> None:
        passes.append(f"[PASS] {filename} - {msg}")

    def fail(msg: str) -> None:
        failures.append(f"[FAIL] {filename} - {msg}")

    # Check 1: valid JSON
    try:
        with open(filepath, "r") as fh:
            policy: dict[str, Any] = json.load(fh)
        ok("Valid JSON")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {exc}")
        return passes, failures
    except OSError as exc:
        fail(f"Cannot read file: {exc}")
        return passes, failures

    # Check 2: Version field
    version = policy.get("Version")
    if version:
        ok(f"Has Version field: {version}")
    else:
        fail("Missing required 'Version' field")

    # Check 3: Statement array
    statements = policy.get("Statement")
    if not isinstance(statements, list):
        fail("Missing or invalid 'Statement' field (must be an array)")
        return passes, failures

    statement_count = len(statements)
    ok(f"Has {statement_count} Statement(s)")

    # Check 4: each Statement has Effect, Action, Resource
    for idx, stmt in enumerate(statements):
        if not isinstance(stmt, dict):
            fail(f"Statement[{idx}] is not an object")
            continue

        effect = stmt.get("Effect")
        action = stmt.get("Action") or stmt.get("NotAction")
        resource = stmt.get("Resource")

        if not effect:
            fail(f"Statement[{idx}]: Missing 'Effect' field")
        if action is None:
            fail(f"Statement[{idx}]: Missing 'Action' or 'NotAction' field")
        if resource is None:
            fail(f"Statement[{idx}]: Missing 'Resource' field")

        if effect and action is not None and resource is not None:
            action_list = action if isinstance(action, list) else [action]
            action_count = len(action_list)
            ok(f"Statement[{idx}]: Effect={effect}, Actions={action_count}, Resource={resource}")

    return passes, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AWS SCP JSON policy files")
    parser.add_argument(
        "--policies-dir",
        default=None,
        help="Path to the directory containing SCP JSON files",
    )
    args = parser.parse_args()

    policies_dir = args.policies_dir or find_policies_dir()
    policy_files = load_policy_files(policies_dir)

    print("=== AWS Landing Zone SCP Validation ===")
    print(f"Validating {len(policy_files)} SCP policy files...")
    print()

    all_passes: list[str] = []
    all_failures: list[str] = []

    for filename, filepath in policy_files:
        passes, failures = validate_policy(filename, filepath)
        all_passes.extend(passes)
        all_failures.extend(failures)

    # Print all results
    for line in all_passes:
        print(line)
    for line in all_failures:
        print(line)

    total_checks = len(all_passes) + len(all_failures)
    passed_count = len(all_passes)
    failed_count = len(all_failures)

    print()
    print("==========================================")

    if failed_count == 0:
        print(f"{total_checks}/{total_checks} checks passed. All SCPs are valid.")
        return 0
    else:
        print(f"{passed_count}/{total_checks} checks passed. {failed_count} check(s) FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
