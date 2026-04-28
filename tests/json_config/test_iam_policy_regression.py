"""
Regression tests for IAM policy changes.

This test suite validates:
- IAM policy simplifications didn't remove critical permissions
- Policy structure integrity
- Security best practices maintained
- Required permissions for CI/CD pipeline
"""

import json
from pathlib import Path
import pytest


@pytest.fixture
def github_actions_policy_path():
    """Return path to GitHub Actions CI policy."""
    return Path("terraform/iam/github_actions_ci_policy.json")


@pytest.fixture
def github_actions_policy(github_actions_policy_path):
    """Load and parse GitHub Actions CI policy."""
    if not github_actions_policy_path.exists():
        pytest.skip(f"Policy file not found: {github_actions_policy_path}")
    with open(github_actions_policy_path) as f:
        return json.load(f)


class TestIAMPolicyRegression:
    """Test IAM policy changes and regressions."""

    def test_policy_maintains_terraform_state_access(self, github_actions_policy):
        """Verify policy still allows S3 access for Terraform state."""
        statements = github_actions_policy.get("Statement", [])
        
        s3_statements = [s for s in statements if any('s3:' in a for a in s.get('Action', []))]
        
        assert len(s3_statements) > 0, \
            "Policy should include S3 permissions for Terraform state"
        
        # Check for required S3 actions
        required_s3_actions = ['s3:GetObject', 's3:PutObject', 's3:ListBucket']
        
        all_s3_actions = []
        for stmt in s3_statements:
            actions = stmt.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            all_s3_actions.extend([a for a in actions if a.startswith('s3:')])
        
        for required_action in required_s3_actions:
            assert any(required_action in action or action == 's3:*' 
                      for action in all_s3_actions), \
                f"Policy missing required S3 action: {required_action}"

    def test_policy_maintains_dynamodb_lock_access(self, github_actions_policy):
        """Verify policy still allows DynamoDB access for state locking."""
        statements = github_actions_policy.get("Statement", [])
        
        dynamodb_statements = [s for s in statements 
                              if any('dynamodb:' in a for a in s.get('Action', []))]
        
        assert len(dynamodb_statements) > 0, \
            "Policy should include DynamoDB permissions for state locking"
        
        # Check for required DynamoDB actions
        required_dynamodb_actions = ['dynamodb:GetItem', 'dynamodb:PutItem', 
                                     'dynamodb:DeleteItem']
        
        all_dynamodb_actions = []
        for stmt in dynamodb_statements:
            actions = stmt.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            all_dynamodb_actions.extend([a for a in actions if a.startswith('dynamodb:')])
        
        for required_action in required_dynamodb_actions:
            assert any(required_action in action or action == 'dynamodb:*'
                      for action in all_dynamodb_actions), \
                f"Policy missing required DynamoDB action: {required_action}"

    def test_policy_has_infrastructure_management_permissions(self, github_actions_policy):
        """Verify policy includes permissions for infrastructure management."""
        statements = github_actions_policy.get("Statement", [])
        
        # Should have EC2, RDS, or EKS permissions (depending on what's being deployed)
        service_prefixes = ['ec2:', 'rds:', 'eks:']
        
        found_services = []
        for stmt in statements:
            actions = stmt.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            
            for prefix in service_prefixes:
                if any(prefix in action for action in actions):
                    found_services.append(prefix.rstrip(':'))
        
        assert len(found_services) > 0, \
            f"Policy should include infrastructure permissions. Expected one of: {service_prefixes}"

    def test_policy_structure_valid(self, github_actions_policy):
        """Verify IAM policy has valid structure."""
        assert "Version" in github_actions_policy, "Policy must have Version"
        assert github_actions_policy["Version"] == "2012-10-17", \
            "Policy Version should be 2012-10-17"
        
        assert "Statement" in github_actions_policy, "Policy must have Statement"
        assert isinstance(github_actions_policy["Statement"], list), \
            "Statement must be a list"
        assert len(github_actions_policy["Statement"]) > 0, \
            "Statement list cannot be empty"

    def test_all_statements_have_required_fields(self, github_actions_policy):
        """Verify each statement has required fields."""
        statements = github_actions_policy.get("Statement", [])
        
        for i, stmt in enumerate(statements):
            assert "Effect" in stmt, f"Statement {i} missing Effect field"
            assert stmt["Effect"] in ["Allow", "Deny"], \
                f"Statement {i} has invalid Effect: {stmt['Effect']}"
            
            assert "Action" in stmt, f"Statement {i} missing Action field"
            assert "Resource" in stmt, f"Statement {i} missing Resource field"

    def test_policy_uses_least_privilege_principle(self, github_actions_policy):
        """Verify policy follows least privilege principle."""
        statements = github_actions_policy.get("Statement", [])
        
        # Check for overly broad permissions
        for i, stmt in enumerate(statements):
            actions = stmt.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            
            resources = stmt.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]
            
            # Flag wildcard permissions with wildcard resources
            wildcard_actions = [a for a in actions if a == '*' or a.endswith(':*')]
            wildcard_resources = [r for r in resources if r == '*']
            
            if wildcard_actions and wildcard_resources:
                pytest.warning(
                    f"Statement {i} (Sid: {stmt.get('Sid', 'unknown')}) uses "
                    f"wildcard permissions {wildcard_actions} with wildcard resource '*'. "
                    f"Consider narrowing scope for better security."
                )

    def test_policy_has_descriptive_sids(self, github_actions_policy):
        """Verify statements have descriptive Sid values."""
        statements = github_actions_policy.get("Statement", [])
        
        for i, stmt in enumerate(statements):
            assert "Sid" in stmt, \
                f"Statement {i} should have Sid for clarity"
            
            sid = stmt["Sid"]
            assert len(sid) > 3, \
                f"Statement {i} Sid too short: '{sid}'. Use descriptive names."
            
            # Sid should be alphanumeric
            assert sid.replace('_', '').replace('-', '').isalnum(), \
                f"Statement {i} Sid contains invalid characters: '{sid}'"

    def test_critical_permissions_not_over_simplified(self, github_actions_policy):
        """Verify simplification didn't remove critical granular permissions."""
        statements = github_actions_policy.get("Statement", [])
        
        all_actions = []
        for stmt in statements:
            actions = stmt.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            all_actions.extend(actions)
        
        # If we have wildcard permissions, warn about potential over-simplification
        wildcard_count = sum(1 for a in all_actions if a.endswith(':*') or a == '*')
        specific_count = sum(1 for a in all_actions if not (a.endswith(':*') or a == '*'))
        
        if wildcard_count > specific_count:
            pytest.warning(
                f"Policy has more wildcard permissions ({wildcard_count}) than "
                f"specific permissions ({specific_count}). This may indicate "
                f"over-simplification. Consider specifying exact permissions needed."
            )

    def test_resource_arns_properly_formatted(self, github_actions_policy):
        """Verify Resource ARNs are properly formatted."""
        statements = github_actions_policy.get("Statement", [])
        
        for i, stmt in enumerate(statements):
            resources = stmt.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]
            
            for resource in resources:
                if resource != '*':
                    # Should be a valid ARN format or placeholder
                    if not (resource.startswith('arn:aws:') or 
                           'REPLACE' in resource or
                           'TODO' in resource or
                           '${' in resource):
                        pytest.fail(
                            f"Statement {i}: Resource '{resource}' doesn't appear to be "
                            f"a valid ARN or placeholder. Use format: "
                            f"arn:aws:service:region:account:resource"
                        )

    def test_s3_bucket_arns_include_objects(self, github_actions_policy):
        """Verify S3 bucket ARNs include both bucket and object permissions."""
        statements = github_actions_policy.get("Statement", [])
        
        s3_statements = [s for s in statements 
                        if any('s3:' in a for a in s.get('Action', []))]
        
        for stmt in s3_statements:
            resources = stmt.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]
            
            # Look for S3 ARNs
            s3_arns = [r for r in resources if 'arn:aws:s3:::' in r]
            
            if s3_arns:
                # Should have both bucket and bucket/* patterns
                has_bucket = any(not r.endswith('/*') for r in s3_arns)
                has_objects = any(r.endswith('/*') for r in s3_arns)
                
                if has_bucket and not has_objects:
                    pytest.warning(
                        f"Sid {stmt.get('Sid')}: S3 permissions may need both bucket "
                        f"and bucket/* resources for full functionality"
                    )


class TestPolicyPlaceholders:
    """Test that placeholder values are properly indicated."""

    def test_placeholders_clearly_marked(self, github_actions_policy_path):
        """Verify placeholder values are clearly marked."""
        content = github_actions_policy_path.read_text()
        
        placeholder_patterns = [
            'REPLACE_ME', 'REPLACE_', 'TODO', 'CHANGEME', 'FILL_IN',
            'YOUR_', 'ACCOUNT_ID', 'REGION', 'BUCKET_NAME'
        ]
        
        has_placeholders = any(pattern in content for pattern in placeholder_patterns)
        
        if has_placeholders:
            # This is good - it's a template
            # Verify each placeholder is in ALL_CAPS or clearly marked
            import re
            placeholders = []
            for pattern in placeholder_patterns:
                placeholders.extend(re.findall(rf'{pattern}[\w_]*', content))
            
            for placeholder in placeholders:
                # Placeholders should be in ALL_CAPS
                assert placeholder.isupper() or placeholder.startswith('${'), \
                    f"Placeholder '{placeholder}' should be in ALL_CAPS for visibility"

    def test_placeholder_comment_documentation(self, github_actions_policy_path):
        """Verify placeholders are documented if present."""
        content = github_actions_policy_path.read_text()
        
        if 'REPLACE' in content or 'TODO' in content:
            # Should have comments or documentation
            # Check for comment patterns (JSON doesn't support comments, but 
            # we might have them in the file as a guide)
            has_documentation = (
                'replace' in content.lower() or
                'change' in content.lower() or
                'update' in content.lower()
            )
            
            assert has_documentation, \
                "Policy with placeholders should include documentation on what to replace"


class TestPolicyConsistency:
    """Test consistency across policy statements."""

    def test_consistent_resource_naming(self, github_actions_policy):
        """Verify resource naming is consistent."""
        statements = github_actions_policy.get("Statement", [])
        
        # Extract all S3 bucket names from resources
        bucket_names = set()
        for stmt in statements:
            resources = stmt.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]
            
            for resource in resources:
                if 'arn:aws:s3:::' in resource:
                    # Extract bucket name
                    bucket_name = resource.split(':::')[1].split('/')[0]
                    bucket_names.add(bucket_name)
        
        # All S3 references should use the same bucket name or placeholder
        if len(bucket_names) > 1 and not any('REPLACE' in b for b in bucket_names):
            pytest.warning(
                f"Multiple different S3 bucket names found: {bucket_names}. "
                f"Verify this is intentional."
            )

    def test_consistent_region_references(self, github_actions_policy):
        """Verify region references are consistent."""
        statements = github_actions_policy.get("Statement", [])
        
        regions = set()
        for stmt in statements:
            resources = stmt.get('Resource', [])
            if isinstance(resources, str):
                resources = [resources]
            
            for resource in resources:
                if 'arn:aws:' in resource:
                    parts = resource.split(':')
                    if len(parts) > 3:
                        region = parts[3]
                        if region and region != '*':
                            regions.add(region)
        
        # Warn if multiple different regions are referenced
        if len(regions) > 1 and not any('REPLACE' in r for r in regions):
            pytest.warning(
                f"Multiple different regions found: {regions}. "
                f"Verify multi-region deployment is intentional."
            )