"""
Comprehensive tests for IAM policy JSON files.

This test suite validates:
- JSON syntax correctness
- IAM policy structure
- Required policy elements
- Security best practices
- GitHub Actions OIDC trust policy
- Permissions scope
"""

import json
from pathlib import Path
import pytest


@pytest.fixture
def github_actions_policy_path():
    """
    Path to the GitHub Actions CI IAM policy file.
    
    Returns:
        Path: Path object pointing to "terraform/iam/github_actions_ci_policy.json".
    """
    return Path("terraform/iam/github_actions_ci_policy.json")


@pytest.fixture
def github_oidc_trust_policy_path():
    """
    Path to the GitHub OIDC trust policy JSON file in the repository.
    
    Returns:
        pathlib.Path: Path to terraform/iam/github_oidc_trust_policy.json
    """
    return Path("terraform/iam/github_oidc_trust_policy.json")


@pytest.fixture
def github_actions_policy(github_actions_policy_path):
    """
    Load and parse the GitHub Actions CI IAM policy JSON from the given path.
    
    Parameters:
        github_actions_policy_path (Path | str): Path to the GitHub Actions CI policy JSON file.
    
    Returns:
        dict: Parsed JSON object representing the policy.
    """
    with open(github_actions_policy_path) as f:
        return json.load(f)


@pytest.fixture
def github_oidc_trust_policy(github_oidc_trust_policy_path):
    """
    Load the GitHub OIDC trust policy JSON file and return it as a Python dictionary.
    
    Parameters:
        github_oidc_trust_policy_path (str | pathlib.Path): Path to the GitHub OIDC trust policy JSON file.
    
    Returns:
        dict: Parsed JSON content of the trust policy.
    """
    with open(github_oidc_trust_policy_path) as f:
        return json.load(f)


class TestPolicyFilesExist:
    """Test policy files exist."""

    def test_github_actions_policy_exists(self, github_actions_policy_path):
        """Verify GitHub Actions policy file exists."""
        assert github_actions_policy_path.exists()

    def test_github_oidc_trust_policy_exists(self, github_oidc_trust_policy_path):
        """Verify GitHub OIDC trust policy exists."""
        assert github_oidc_trust_policy_path.exists()


class TestJSONSyntax:
    """Test JSON syntax validity."""

    def test_github_actions_policy_valid_json(self, github_actions_policy_path):
        """Verify GitHub Actions policy is valid JSON."""
        try:
            with open(github_actions_policy_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON: {e}")

    def test_github_oidc_trust_policy_valid_json(self, github_oidc_trust_policy_path):
        """
        Check that the GitHub OIDC trust policy file contains valid JSON.
        
        Parameters:
            github_oidc_trust_policy_path (Path): Filesystem path to the GitHub OIDC trust policy JSON file.
        """
        try:
            with open(github_oidc_trust_policy_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON: {e}")


class TestGitHubActionsPolicyStructure:
    """Test GitHub Actions CI policy structure."""

    def test_has_version(self, github_actions_policy):
        """Verify policy has Version field."""
        assert "Version" in github_actions_policy
        assert github_actions_policy["Version"] == "2012-10-17"

    def test_has_statement(self, github_actions_policy):
        """
        Check that the policy contains a non-empty "Statement" list.
        
        Asserts that the top-level "Statement" key exists, is a list, and has at least one element.
        """
        assert "Statement" in github_actions_policy
        assert isinstance(github_actions_policy["Statement"], list)
        assert len(github_actions_policy["Statement"]) > 0

    def test_statements_have_required_fields(self, github_actions_policy):
        """Verify each statement has required fields."""
        for stmt in github_actions_policy["Statement"]:
            assert "Effect" in stmt, "Statement missing Effect"
            assert "Action" in stmt, "Statement missing Action"
            assert stmt["Effect"] in ["Allow", "Deny"]

    def test_statements_have_sid(self, github_actions_policy):
        """Verify statements have Sid for identification."""
        for stmt in github_actions_policy["Statement"]:
            assert "Sid" in stmt, "Statement should have Sid for clarity"

    def test_has_terraform_state_access(self, github_actions_policy):
        """Verify policy grants Terraform state access."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("TerraformState" in sid or "State" in sid for sid in sids)

    def test_has_dynamodb_lock_access(self, github_actions_policy):
        """Verify policy grants DynamoDB lock access."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("DynamoDB" in sid or "Lock" in sid for sid in sids)

    def test_has_ec2_permissions(self, github_actions_policy):
        """Verify policy includes EC2 permissions."""
        all_actions = []
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            all_actions.extend(actions)
        
        assert any("ec2:" in action for action in all_actions)

    def test_has_rds_permissions(self, github_actions_policy):
        """Verify policy includes RDS permissions."""
        all_actions = []
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            all_actions.extend(actions)
        
        assert any("rds:" in action for action in all_actions)


class TestGitHubOIDCTrustPolicyStructure:
    """Test GitHub OIDC trust policy structure."""

    def test_has_version(self, github_oidc_trust_policy):
        """Verify trust policy has Version field."""
        assert "Version" in github_oidc_trust_policy
        assert github_oidc_trust_policy["Version"] == "2012-10-17"

    def test_has_statement(self, github_oidc_trust_policy):
        """Verify trust policy has Statement array."""
        assert "Statement" in github_oidc_trust_policy
        assert isinstance(github_oidc_trust_policy["Statement"], list)

    def test_has_assume_role_action(self, github_oidc_trust_policy):
        """Verify trust policy allows AssumeRoleWithWebIdentity."""
        for stmt in github_oidc_trust_policy["Statement"]:
            if "Action" in stmt:
                assert "sts:AssumeRoleWithWebIdentity" in stmt["Action"]

    def test_has_federated_principal(self, github_oidc_trust_policy):
        """Verify trust policy has Federated principal."""
        for stmt in github_oidc_trust_policy["Statement"]:
            if "Principal" in stmt:
                assert "Federated" in stmt["Principal"]

    def test_references_github_oidc_provider(self, github_oidc_trust_policy):
        """Verify trust policy references GitHub OIDC provider."""
        policy_str = json.dumps(github_oidc_trust_policy)
        assert "token.actions.githubusercontent.com" in policy_str

    def test_has_conditions(self, github_oidc_trust_policy):
        """
        Ensure every statement with Effect "Allow" in the GitHub OIDC trust policy includes a `Condition` block.
        
        Parameters:
            github_oidc_trust_policy (dict): Parsed JSON policy representing the OIDC trust policy.
        """
        for stmt in github_oidc_trust_policy["Statement"]:
            if stmt.get("Effect") == "Allow":
                assert "Condition" in stmt, "Trust policy should have conditions"

    def test_conditions_check_audience(self, github_oidc_trust_policy):
        """
        Ensure the trust policy includes an audience condition.
        
        Asserts that the serialized policy contains either "aud" or "sts.amazonaws.com", indicating an audience check is present.
        """
        policy_str = json.dumps(github_oidc_trust_policy)
        assert "aud" in policy_str or "sts.amazonaws.com" in policy_str

    def test_conditions_check_subject(self, github_oidc_trust_policy):
        """
        Checks that the OIDC trust policy's conditions include a subject claim (`sub`) or a repository identifier (`repo:`).
        
        Parameters:
            github_oidc_trust_policy (dict): Parsed JSON object of the GitHub OIDC trust policy.
        """
        policy_str = json.dumps(github_oidc_trust_policy)
        assert "sub" in policy_str or "repo:" in policy_str


class TestS3StatePermissions:
    """Test S3 state bucket permissions."""

    def test_s3_permissions_include_get_object(self, github_actions_policy):
        """Verify policy allows GetObject on S3."""
        s3_actions = []
        for stmt in github_actions_policy["Statement"]:
            if any("s3:" in str(a) for a in stmt.get("Action", [])):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                s3_actions.extend(actions)
        
        assert any("s3:GetObject" in action for action in s3_actions)

    def test_s3_permissions_include_put_object(self, github_actions_policy):
        """Verify policy allows PutObject on S3."""
        s3_actions = []
        for stmt in github_actions_policy["Statement"]:
            if any("s3:" in str(a) for a in stmt.get("Action", [])):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                s3_actions.extend(actions)
        
        assert any("s3:PutObject" in action for action in s3_actions)

    def test_s3_permissions_include_list_bucket(self, github_actions_policy):
        """Verify policy allows ListBucket on S3."""
        s3_actions = []
        for stmt in github_actions_policy["Statement"]:
            if any("s3:" in str(a) for a in stmt.get("Action", [])):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                s3_actions.extend(actions)
        
        assert any("s3:ListBucket" in action for action in s3_actions)


class TestDynamoDBLockPermissions:
    """Test DynamoDB lock table permissions."""

    def test_dynamodb_permissions_include_get_item(self, github_actions_policy):
        """Verify policy allows GetItem on DynamoDB."""
        dynamodb_actions = []
        for stmt in github_actions_policy["Statement"]:
            if any("dynamodb:" in str(a) for a in stmt.get("Action", [])):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                dynamodb_actions.extend(actions)
        
        assert any("dynamodb:GetItem" in action for action in dynamodb_actions)

    def test_dynamodb_permissions_include_put_item(self, github_actions_policy):
        """Verify policy allows PutItem on DynamoDB."""
        dynamodb_actions = []
        for stmt in github_actions_policy["Statement"]:
            if any("dynamodb:" in str(a) for a in stmt.get("Action", [])):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                dynamodb_actions.extend(actions)
        
        assert any("dynamodb:PutItem" in action for action in dynamodb_actions)

    def test_dynamodb_permissions_include_delete_item(self, github_actions_policy):
        """
        Check that the GitHub Actions IAM policy includes the DynamoDB action `dynamodb:DeleteItem`.
        """
        dynamodb_actions = []
        for stmt in github_actions_policy["Statement"]:
            if any("dynamodb:" in str(a) for a in stmt.get("Action", [])):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                dynamodb_actions.extend(actions)
        
        assert any("dynamodb:DeleteItem" in action for action in dynamodb_actions)


class TestSecurityBestPractices:
    """Test security best practices in policies."""

    def test_statements_use_allow_effect(self, github_actions_policy):
        """
        Assert each statement's `Effect` field is either "Allow" or "Deny".
        
        This verifies that every statement explicitly specifies an effect rather than relying on implicit defaults.
        """
        for stmt in github_actions_policy["Statement"]:
            # Most statements should be Allow (implicit deny is AWS default)
            assert stmt["Effect"] in ["Allow", "Deny"]

    def test_policy_has_resource_restrictions(self, github_actions_policy):
        """
        Check that the policy contains at least one Statement with a Resource field not equal to "*".
        
        This test asserts there is at least one statement that restricts resources (i.e., has a "Resource" key whose value is not "*").
        """
        has_resource_restriction = False
        for stmt in github_actions_policy["Statement"]:
            if "Resource" in stmt and stmt["Resource"] != "*":
                has_resource_restriction = True
                break
        
        # At least state bucket should have specific resource
        assert has_resource_restriction, "Policy should have some resource-specific restrictions"

    def test_trust_policy_uses_string_equals(self, github_oidc_trust_policy):
        """Verify trust policy uses StringEquals for exact matching."""
        policy_str = json.dumps(github_oidc_trust_policy)
        assert "StringEquals" in policy_str, "Trust policy should use StringEquals for security"


class TestPolicyPlaceholders:
    """Test that policies have proper placeholders."""

    def test_github_actions_policy_has_placeholders(self, github_actions_policy_path):
        """Verify GitHub Actions policy has REPLACE_ placeholders."""
        content = github_actions_policy_path.read_text()
        # Should have placeholders for customization
        assert "REPLACE_" in content or "REPLACE" in content.upper()

    def test_oidc_trust_policy_has_placeholders(self, github_oidc_trust_policy_path):
        """Verify OIDC trust policy has placeholders."""
        content = github_oidc_trust_policy_path.read_text()
        # Should have placeholders for account ID
        assert "REPLACE_" in content or "${{" in content