"""
Unit tests for IAM policy validation.
"""

import json
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.validate_policies import PolicyValidator


class TestPolicyValidator:
    """Test IAM policy validation logic."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return PolicyValidator()

    def test_valid_basic_policy(self, validator):
        """Test validation of a basic valid policy."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::my-bucket/*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        assert is_valid is True
        assert len([m for m in messages if m in validator.issues]) == 0

    def test_missing_version(self, validator):
        """Test detection of missing Version field."""
        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        assert is_valid is False
        assert any("Missing 'Version'" in m for m in messages)

    def test_wildcard_action_detection(self, validator):
        """Test detection of wildcard actions."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        assert is_valid is False
        assert any("wildcard '*' action" in m.lower() for m in messages)

    def test_wildcard_resource_without_condition(self, validator):
        """Test detection of wildcard resources without conditions."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        # Should generate warning about wildcard resource
        assert any("wildcard '*' resource" in m.lower() for m in messages)

    def test_sensitive_actions_without_conditions(self, validator):
        """Test detection of sensitive actions without conditions."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:DeleteBucket",
                    "Resource": "arn:aws:s3:::my-bucket"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        # Should generate warning about destructive actions without conditions
        assert any("destructive" in m.lower() or "condition" in m.lower() for m in messages)

    def test_admin_permissions_detection(self, validator):
        """Test detection of admin-level permissions."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iam:*",
                    "Resource": "*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        assert is_valid is False
        assert any("admin" in m.lower() or "wildcard" in m.lower() for m in messages)

    def test_passrole_without_condition(self, validator):
        """Test detection of PassRole without restrictions."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iam:PassRole",
                    "Resource": "*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        # Should warn about PassRole without conditions
        assert any("passrole" in m.lower() for m in messages)

    def test_deny_statement_allowed(self, validator):
        """Test that Deny statements with wildcards are acceptable."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": "*",
                    "Resource": "*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        # Deny with wildcards should be acceptable (least-privilege pattern)
        assert any("acceptable" in m.lower() for m in messages)

    def test_service_wildcard_warning(self, validator):
        """Test warning for service-level wildcards."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": "arn:aws:s3:::my-bucket/*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        # Should warn about service wildcard
        assert any("wildcard for all" in m.lower() for m in messages)

    def test_multiple_statements(self, validator):
        """Test validation of policy with multiple statements."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::my-bucket/*"
                },
                {
                    "Effect": "Deny",
                    "Action": "s3:DeleteBucket",
                    "Resource": "*"
                }
            ]
        }

        is_valid, messages = validator.validate_policy(policy, "test-policy")
        assert is_valid is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
