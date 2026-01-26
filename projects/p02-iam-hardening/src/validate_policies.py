#!/usr/bin/env python3
"""
IAM Policy Validation Script

Validates IAM policies for security best practices and compliance.
Detects wildcard actions, overly permissive resources, missing conditions, etc.
"""

import json
import sys
import os
from typing import List, Dict, Tuple
from pathlib import Path


class PolicyValidator:
    """Validates IAM policies against security best practices."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []

    def validate_policy_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate a policy JSON file.

        Args:
            file_path: Path to policy JSON file

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        try:
            with open(file_path, "r") as f:
                policy = json.load(f)

            return self.validate_policy(policy, file_path)
        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in {file_path}: {e}")
            return False, self.issues
        except Exception as e:
            self.issues.append(f"Error reading {file_path}: {e}")
            return False, self.issues

    def validate_policy(
        self, policy: Dict, source: str = "policy"
    ) -> Tuple[bool, List[str]]:
        """
        Validate a policy dictionary.

        Args:
            policy: IAM policy dictionary
            source: Source identifier for error messages

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        self.issues = []
        self.warnings = []
        self.info = []

        # Check policy structure
        if "Version" not in policy:
            self.issues.append(f"{source}: Missing 'Version' field")
        elif policy["Version"] != "2012-10-17":
            self.warnings.append(f"{source}: Using non-standard policy version")

        if "Statement" not in policy:
            self.issues.append(f"{source}: Missing 'Statement' field")
            return False, self.issues

        # Validate each statement
        for i, statement in enumerate(policy["Statement"]):
            self._validate_statement(statement, i, source)

        is_valid = len(self.issues) == 0
        all_messages = self.issues + self.warnings + self.info

        return is_valid, all_messages

    def _validate_statement(self, statement: Dict, index: int, source: str):
        """Validate individual policy statement."""
        prefix = f"{source}:Statement[{index}]"

        # Check required fields
        if "Effect" not in statement:
            self.issues.append(f"{prefix}: Missing 'Effect' field")
            return

        if statement["Effect"] not in ["Allow", "Deny"]:
            self.issues.append(f"{prefix}: Invalid Effect value")

        if "Action" not in statement and "NotAction" not in statement:
            self.issues.append(f"{prefix}: Missing 'Action' or 'NotAction'")

        if "Resource" not in statement and "NotResource" not in statement:
            self.issues.append(f"{prefix}: Missing 'Resource' or 'NotResource'")

        # Check for wildcard issues
        self._check_wildcards(statement, prefix)

        # Check for missing conditions on sensitive actions
        self._check_conditions(statement, prefix)

        # Check for overly permissive combinations
        self._check_permissive_combinations(statement, prefix)

    def _check_wildcards(self, statement: Dict, prefix: str):
        """Check for wildcard usage in actions and resources."""
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]

        resources = statement.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]

        # Check for full wildcard actions
        if "*" in actions:
            if statement.get("Effect") == "Allow":
                self.issues.append(
                    f"{prefix}: Uses wildcard '*' action with Allow effect. "
                    "This grants all permissions!"
                )
            else:
                self.info.append(
                    f"{prefix}: Uses Deny with wildcard (acceptable pattern)"
                )

        # Check for service wildcards
        for action in actions:
            if ":*" in action and statement.get("Effect") == "Allow":
                service = action.split(":")[0]
                self.warnings.append(
                    f"{prefix}: Uses wildcard for all {service} actions. "
                    "Consider limiting to specific actions."
                )

        # Check for wildcard resources
        if "*" in resources and statement.get("Effect") == "Allow":
            # Check if there are conditions that limit the wildcard
            if "Condition" not in statement:
                self.warnings.append(
                    f"{prefix}: Uses wildcard '*' resource without conditions. "
                    "Consider adding resource ARN constraints."
                )

    def _check_conditions(self, statement: Dict, prefix: str):
        """Check for missing conditions on sensitive actions."""
        sensitive_actions = [
            "s3:DeleteBucket",
            "s3:DeleteObject",
            "iam:DeleteUser",
            "iam:DeleteRole",
            "rds:DeleteDBInstance",
            "ec2:TerminateInstances",
        ]

        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]

        has_sensitive = any(
            any(sensitive in action for sensitive in sensitive_actions)
            for action in actions
        )

        if has_sensitive and statement.get("Effect") == "Allow":
            if "Condition" not in statement:
                self.warnings.append(
                    f"{prefix}: Allows destructive actions without conditions. "
                    "Consider adding MFA or IP restrictions."
                )

    def _check_permissive_combinations(self, statement: Dict, prefix: str):
        """Check for overly permissive combinations."""
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]

        resources = statement.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]

        # Check for admin-level permissions
        admin_actions = ["iam:*", "sts:AssumeRole", "*:*"]
        has_admin = any(action in actions for action in admin_actions)

        if has_admin and "*" in resources and statement.get("Effect") == "Allow":
            self.issues.append(
                f"{prefix}: Combines administrative actions with wildcard resources. "
                "This effectively grants full admin access!"
            )

        # Check for PassRole without restrictions
        if "iam:PassRole" in actions and statement.get("Effect") == "Allow":
            if "Condition" not in statement:
                self.warnings.append(
                    f"{prefix}: Allows iam:PassRole without conditions. "
                    "Add conditions to limit which roles can be passed."
                )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate IAM policies for security best practices"
    )
    parser.add_argument("policy_files", nargs="+", help="Policy JSON files to validate")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )

    args = parser.parse_args()

    validator = PolicyValidator()
    all_valid = True
    total_issues = 0
    total_warnings = 0

    for policy_file in args.policy_files:
        if not os.path.exists(policy_file):
            print(f"ERROR: File not found: {policy_file}")
            all_valid = False
            continue

        print(f"\nValidating: {policy_file}")
        print("=" * 60)

        is_valid, messages = validator.validate_policy_file(policy_file)

        # Count issues and warnings
        issues = [m for m in messages if m.startswith(os.path.basename(policy_file))]
        issue_count = len(
            [m for m in messages if "ERROR" in m or m in validator.issues]
        )
        warning_count = len([m for m in messages if m in validator.warnings])

        for message in messages:
            if message in validator.issues:
                print(f"  ❌ ERROR: {message}")
            elif message in validator.warnings:
                print(f"  ⚠️  WARNING: {message}")
            else:
                print(f"  ℹ️  INFO: {message}")

        total_issues += issue_count
        total_warnings += warning_count

        if not is_valid:
            all_valid = False
            print(f"\n  ❌ FAILED: {policy_file}")
        elif args.strict and warning_count > 0:
            all_valid = False
            print(f"\n  ❌ FAILED (strict mode): {policy_file}")
        else:
            print(f"\n  ✅ PASSED: {policy_file}")

    print("\n" + "=" * 60)
    print(f"Summary: {len(args.policy_files)} files validated")
    print(f"  Issues: {total_issues}")
    print(f"  Warnings: {total_warnings}")

    if all_valid:
        print("\n✅ All policies passed validation")
        sys.exit(0)
    else:
        print("\n❌ Some policies failed validation")
        sys.exit(1)


if __name__ == "__main__":
    main()
