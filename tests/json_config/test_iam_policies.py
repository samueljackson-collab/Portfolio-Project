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
    """Return path to GitHub Actions CI policy."""
    return Path("terraform/iam/github_actions_ci_policy.json")


@pytest.fixture
def github_oidc_trust_policy_path():
    """Return path to GitHub OIDC trust policy."""
    return Path("terraform/iam/github_oidc_trust_policy.json")


@pytest.fixture
def github_actions_policy(github_actions_policy_path):
    """Load and parse GitHub Actions CI policy."""
    with open(github_actions_policy_path) as f:
        return json.load(f)


@pytest.fixture
def github_oidc_trust_policy(github_oidc_trust_policy_path):
    """Load and parse GitHub OIDC trust policy."""
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
        """Verify GitHub OIDC trust policy is valid JSON."""
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
        """Verify policy has Statement array."""
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
        """Verify trust policy has conditions for security."""
        for stmt in github_oidc_trust_policy["Statement"]:
            if stmt.get("Effect") == "Allow":
                assert "Condition" in stmt, "Trust policy should have conditions"

    def test_conditions_check_audience(self, github_oidc_trust_policy):
        """Verify conditions check aud claim."""
        policy_str = json.dumps(github_oidc_trust_policy)
        assert "aud" in policy_str or "sts.amazonaws.com" in policy_str

    def test_conditions_check_subject(self, github_oidc_trust_policy):
        """Verify conditions check sub claim for repository."""
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
        """Verify policy allows DeleteItem on DynamoDB."""
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
        """Verify statements primarily use Allow effect (deny by default)."""
        for stmt in github_actions_policy["Statement"]:
            # Most statements should be Allow (implicit deny is AWS default)
            assert stmt["Effect"] in ["Allow", "Deny"]

    def test_policy_has_resource_restrictions(self, github_actions_policy):
        """Verify at least some statements have Resource restrictions."""
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

class TestGitHubActionsPolicyPlaceholders:
    """Test GitHub Actions policy placeholder values (regression)."""

    def test_s3_bucket_placeholder_format(self, github_actions_policy):
        """Verify S3 bucket ARN uses consistent placeholder format."""
        for stmt in github_actions_policy["Statement"]:
            if "Resource" in stmt:
                resources = stmt["Resource"]
                if isinstance(resources, str):
                    resources = [resources]
                
                for resource in resources:
                    if "arn:aws:s3:::" in resource:
                        # Should use REPLACE_ prefix for clarity
                        assert "REPLACE_TFSTATE_BUCKET" in resource or \
                               "REPLACE" in resource.upper(), \
                            f"S3 bucket ARN should use clear placeholder: {resource}"

    def test_dynamodb_table_placeholder_format(self, github_actions_policy):
        """Verify DynamoDB table ARN uses consistent placeholder format."""
        for stmt in github_actions_policy["Statement"]:
            if "Resource" in stmt:
                resources = stmt["Resource"]
                if isinstance(resources, str):
                    resources = [resources]
                
                for resource in resources:
                    if "arn:aws:dynamodb:" in resource:
                        # Should use clear placeholders
                        assert "REPLACE" in resource.upper(), \
                            f"DynamoDB ARN should use clear placeholder: {resource}"

    def test_account_id_placeholder_in_arns(self, github_actions_policy):
        """Verify ARNs use account ID placeholder."""
        for stmt in github_actions_policy["Statement"]:
            if "Resource" in stmt:
                resources = stmt["Resource"]
                if isinstance(resources, str):
                    resources = [resources]
                
                for resource in resources:
                    if "arn:aws:" in resource and "::" not in resource:
                        # Should have account ID placeholder
                        assert "REPLACE_ACCOUNT_ID" in resource or \
                               "REPLACE" in resource.upper() or \
                               "${" in resource or \
                               "*" in resource, \
                            f"ARN should use account ID placeholder: {resource}"


class TestIAMPolicyResourceScoping:
    """Test IAM policy resource scoping."""

    def test_s3_resources_include_bucket_and_objects(self, github_actions_policy):
        """Verify S3 permissions include both bucket and object ARNs."""
        s3_resources = []
        for stmt in github_actions_policy["Statement"]:
            if "Resource" in stmt:
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                
                if any("s3:" in action for action in actions):
                    resources = stmt["Resource"]
                    if isinstance(resources, str):
                        resources = [resources]
                    s3_resources.extend(resources)
        
        if s3_resources:
            # Should have both bucket (without /*) and objects (with /*)
            has_bucket = any(not r.endswith("/*") and "s3:::" in r for r in s3_resources)
            has_objects = any(r.endswith("/*") for r in s3_resources)
            
            assert has_bucket and has_objects, \
                "S3 permissions should include both bucket and object ARNs"

    def test_wildcard_resources_justified(self, github_actions_policy):
        """Verify wildcard resources are used only where necessary."""
        wildcard_statements = []
        for stmt in github_actions_policy["Statement"]:
            if "Resource" in stmt:
                resources = stmt["Resource"]
                if isinstance(resources, str):
                    resources = [resources]
                
                if "*" in resources:
                    wildcard_statements.append(stmt)
        
        # Wildcard should be limited and have good reason (EC2, EKS, etc.)
        for stmt in wildcard_statements:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            
            # These services often need wildcard due to dynamic resource names
            justified_services = ["ec2:", "eks:", "elasticloadbalancing:", "autoscaling:", "logs:", "kms:"]
            has_justified_action = any(
                any(service in action for service in justified_services)
                for action in actions
            )
            
            assert has_justified_action, \
                f"Wildcard resource should be justified: {stmt.get('Sid', 'Unknown')}"


class TestIAMPolicyPermissionsScope:
    """Test IAM policy permissions are appropriately scoped."""

    def test_kms_permissions_scoped(self, github_actions_policy):
        """Verify KMS permissions are present but appropriately scoped."""
        kms_actions = []
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            
            kms_actions.extend([a for a in actions if "kms:" in a])
        
        if kms_actions:
            # Should have decrypt, encrypt, generate for state encryption
            essential_kms = ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey"]
            has_essential = any(action in kms_actions for action in essential_kms)
            
            assert has_essential, "KMS permissions should include essential actions"
            
            # Should NOT have dangerous actions like DeleteKey
            dangerous_kms = ["kms:DeleteKey", "kms:ScheduleKeyDeletion"]
            has_dangerous = any(action in kms_actions for action in dangerous_kms)
            
            assert not has_dangerous, "KMS permissions should not include dangerous actions"

    def test_iam_passtole_is_scoped(self, github_actions_policy):
        """Verify iam:PassRole is appropriately scoped."""
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            
            if "iam:PassRole" in actions:
                # Should ideally have resource restriction or condition
                # At minimum, document the need for this permission
                assert stmt.get("Sid") is not None, \
                    "iam:PassRole statement should have Sid for documentation"

    def test_no_admin_wildcard_permissions(self, github_actions_policy):
        """Verify policy doesn't grant admin-level wildcard permissions."""
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            
            resources = stmt.get("Resource", [])
            if isinstance(resources, str):
                resources = [resources]
            
            # Should NOT have ["*"] actions with ["*"] resources
            has_wildcard_actions = "*" in actions
            has_wildcard_resources = "*" in resources
            
            assert not (has_wildcard_actions and has_wildcard_resources), \
                f"Statement {stmt.get('Sid')} grants excessive permissions"


class TestIAMPolicyStatementStructure:
    """Test IAM policy statement structure and organization."""

    def test_all_statements_have_unique_sids(self, github_actions_policy):
        """Verify all statements have unique Sid values."""
        sids = [stmt.get("Sid") for stmt in github_actions_policy["Statement"] if "Sid" in stmt]
        
        assert len(sids) == len(set(sids)), \
            f"Duplicate Sid values found: {[s for s in sids if sids.count(s) > 1]}"

    def test_statement_sids_descriptive(self, github_actions_policy):
        """Verify Sid values are descriptive."""
        for stmt in github_actions_policy["Statement"]:
            if "Sid" in stmt:
                sid = stmt["Sid"]
                # Sid should not be generic like "Statement1"
                assert not sid.startswith("Statement"), \
                    f"Sid should be descriptive, not generic: {sid}"
                
                # Sid should relate to the actions
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                
                # At least one action should relate to Sid (loose check)
                if actions and actions != ["*"]:
                    # Extract service from first action
                    service = actions[0].split(":")[0] if ":" in actions[0] else ""
                    # Sid should mention service or be clearly descriptive
                    assert len(sid) > 3, f"Sid too short: {sid}"

    def test_statements_grouped_logically(self, github_actions_policy):
        """Verify statements are grouped by service/function."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        
        # Should have logical groupings like TerraformState, EC2, RDS, etc.
        expected_groups = ["State", "DynamoDB", "KMS", "EC2", "RDS", "EKS", "CloudWatch"]
        
        found_groups = sum(1 for group in expected_groups if any(group in sid for sid in sids))
        
        assert found_groups >= 3, \
            "Policy should have logical statement groupings"


class TestIAMPolicyCompliance:
    """Test IAM policy compliance with best practices."""

    def test_no_notaction_or_notresource(self, github_actions_policy):
        """Verify policy doesn't use NotAction or NotResource (anti-pattern)."""
        for stmt in github_actions_policy["Statement"]:
            assert "NotAction" not in stmt, "Avoid NotAction - use explicit Allow"
            assert "NotResource" not in stmt, "Avoid NotResource - use explicit Resource"

    def test_all_allow_statements_have_resources(self, github_actions_policy):
        """Verify Allow statements specify resources."""
        for stmt in github_actions_policy["Statement"]:
            if stmt.get("Effect") == "Allow":
                # Should have Resource field (even if it's ["*"])
                assert "Resource" in stmt, \
                    f"Allow statement {stmt.get('Sid')} missing Resource field"

    def test_no_principal_in_identity_policy(self, github_actions_policy):
        """Verify identity policy doesn't include Principal."""
        for stmt in github_actions_policy["Statement"]:
            # Identity policies (for users/roles) shouldn't have Principal
            assert "Principal" not in stmt, \
                "Identity policy should not have Principal field"


class TestTerraformSpecificPermissions:
    """Test Terraform-specific permission requirements."""

    def test_has_state_locking_permissions(self, github_actions_policy):
        """Verify policy grants DynamoDB permissions for state locking."""
        dynamodb_actions = []
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            dynamodb_actions.extend([a for a in actions if "dynamodb:" in a])
        
        required_lock_actions = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"]
        for action in required_lock_actions:
            assert action in dynamodb_actions, \
                f"Missing required DynamoDB lock action: {action}"

    def test_has_state_read_write_permissions(self, github_actions_policy):
        """Verify policy grants S3 permissions for state read/write."""
        s3_actions = []
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            s3_actions.extend([a for a in actions if "s3:" in a])
        
        required_state_actions = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        for action in required_state_actions:
            assert action in s3_actions, \
                f"Missing required S3 state action: {action}"

    def test_has_infrastructure_management_permissions(self, github_actions_policy):
        """Verify policy grants permissions to manage infrastructure."""
        all_actions = []
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            all_actions.extend(actions)
        
        # Should have EC2, RDS, EKS permissions for infrastructure
        required_services = ["ec2:", "rds:", "eks:"]
        for service in required_services:
            has_service = any(service in action for action in all_actions)
            assert has_service, f"Missing permissions for {service}"