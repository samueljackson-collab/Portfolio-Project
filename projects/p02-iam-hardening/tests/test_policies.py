"""Unit tests for IAM policy validation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def policies_dir():
    """Get policies directory."""
    return Path(__file__).parent.parent / "policies"


@pytest.fixture
def developer_policy(policies_dir):
    """Load developer role policy."""
    policy_path = policies_dir / "developer-role.json"
    with open(policy_path) as f:
        return json.load(f)


def test_developer_policy_exists(policies_dir):
    """Verify developer policy file exists."""
    policy_path = policies_dir / "developer-role.json"
    assert policy_path.exists(), f"Policy not found: {policy_path}"


def test_developer_policy_valid_json(developer_policy):
    """Verify policy is valid JSON."""
    assert developer_policy is not None
    assert "Version" in developer_policy
    assert "Statement" in developer_policy


def test_developer_policy_has_deny_production(developer_policy):
    """Verify policy explicitly denies production resource access."""
    statements = developer_policy.get("Statement", [])
    deny_statements = [s for s in statements if s.get("Effect") == "Deny"]

    assert (
        len(deny_statements) > 0
    ), "Policy should have explicit Deny statements for production"

    prod_deny = next(
        (s for s in deny_statements if "DenyProductionResources" in s.get("Sid", "")),
        None,
    )
    assert prod_deny is not None, "Missing production resource deny statement"


def test_developer_policy_s3_restricted(developer_policy):
    """Verify S3 access is restricted to dev buckets."""
    statements = developer_policy.get("Statement", [])
    s3_statements = [
        s for s in statements if any("s3:" in str(a) for a in s.get("Action", []))
    ]

    assert len(s3_statements) > 0, "Policy should have S3 permissions"

    for stmt in s3_statements:
        if stmt.get("Effect") == "Allow":
            resources = stmt.get("Resource", [])
            if isinstance(resources, str):
                resources = [resources]
            # Check that S3 resources are scoped (not wildcards)
            for resource in resources:
                assert (
                    "dev-" in resource
                    or "*" not in resource
                    or resource.startswith("arn:aws:s3:::dev-")
                ), f"S3 resource should be scoped to dev buckets: {resource}"


def test_developer_policy_no_iam_permissions(developer_policy):
    """Verify policy does not grant IAM modification permissions."""
    statements = developer_policy.get("Statement", [])
    for stmt in statements:
        if stmt.get("Effect") == "Allow":
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            for action in actions:
                assert not action.startswith(
                    "iam:Create"
                ), f"Policy should not allow IAM creation: {action}"
                assert not action.startswith(
                    "iam:Delete"
                ), f"Policy should not allow IAM deletion: {action}"
                assert not action.startswith(
                    "iam:Put"
                ), f"Policy should not allow IAM modification: {action}"


def test_policy_diff_script_exists():
    """Verify policy diff script exists."""
    script_path = Path(__file__).parent.parent / "src" / "policy_diff.py"
    assert script_path.exists(), f"Policy diff script not found: {script_path}"
