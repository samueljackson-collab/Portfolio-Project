"""Test security policies."""

import pytest
import json
from pathlib import Path


def test_jwt_policy_exists():
    """Test JWT policy file exists."""
    policy_file = Path(__file__).parent.parent / "policies" / "jwt_policy.json"
    assert policy_file.exists()


def test_jwt_policy_valid():
    """Test JWT policy is valid JSON."""
    policy_file = Path(__file__).parent.parent / "policies" / "jwt_policy.json"
    with open(policy_file) as f:
        policy = json.load(f)
    assert "version" in policy
    assert "statement" in policy
