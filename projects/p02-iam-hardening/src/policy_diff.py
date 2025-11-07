#!/usr/bin/env python3
"""
IAM Policy Diff Tool.

Compare two IAM policy documents and highlight permission changes.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Set


def load_policy(path: Path) -> Dict:
    """Load IAM policy from JSON file."""
    with open(path) as f:
        return json.load(f)


def extract_permissions(policy: Dict) -> Set[str]:
    """Extract all actions from policy statements."""
    permissions = set()
    for statement in policy.get("Statement", []):
        effect = statement.get("Effect", "Deny")
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        for action in actions:
            permissions.add(f"{effect}:{action}")
    return permissions


def diff_policies(old_policy: Dict, new_policy: Dict) -> Dict[str, Set[str]]:
    """Compare two policies and return added/removed permissions."""
    old_perms = extract_permissions(old_policy)
    new_perms = extract_permissions(new_policy)

    return {
        "added": new_perms - old_perms,
        "removed": old_perms - new_perms,
        "unchanged": old_perms & new_perms,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: policy_diff.py <old-policy.json> <new-policy.json>")
        sys.exit(1)

    old_path = Path(sys.argv[1])
    new_path = Path(sys.argv[2])

    if not old_path.exists() or not new_path.exists():
        print("Error: Policy files not found")
        sys.exit(1)

    old_policy = load_policy(old_path)
    new_policy = load_policy(new_path)

    diff = diff_policies(old_policy, new_policy)

    print(f"\n{'='*60}")
    print(f"Policy Diff: {old_path.name} → {new_path.name}")
    print(f"{'='*60}\n")

    if diff["added"]:
        print("➕ ADDED PERMISSIONS:")
        for perm in sorted(diff["added"]):
            print(f"   + {perm}")
        print()

    if diff["removed"]:
        print("➖ REMOVED PERMISSIONS:")
        for perm in sorted(diff["removed"]):
            print(f"   - {perm}")
        print()

    if not diff["added"] and not diff["removed"]:
        print("✓ No changes detected")
    else:
        print(f"Summary: +{len(diff['added'])} added, -{len(diff['removed'])} removed")

    print()


if __name__ == "__main__":
    main()
