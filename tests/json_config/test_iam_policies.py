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

# ============================================================================
# EXPANDED TESTS FOR ENHANCED IAM POLICY
# ============================================================================

class TestGitHubActionsPolicyEnhanced:
    """Enhanced tests for the expanded GitHub Actions CI policy"""
    
    def test_policy_has_16_statements(self, github_actions_policy):
        """Verify policy has all 16 permission statements"""
        assert len(github_actions_policy['Statement']) == 16
    
    def test_all_statements_have_sids(self, github_actions_policy):
        """Verify all statements have descriptive Sids"""
        for stmt in github_actions_policy['Statement']:
            assert 'Sid' in stmt
            assert len(stmt['Sid']) > 0
    
    def test_vpc_management_statement(self, github_actions_policy):
        """Test VPC Management permissions"""
        vpc_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'VPCManagement')
        
        assert vpc_stmt['Effect'] == 'Allow'
        assert 'ec2:CreateVpc' in vpc_stmt['Action']
        assert 'ec2:DeleteVpc' in vpc_stmt['Action']
        assert 'ec2:CreateSubnet' in vpc_stmt['Action']
        assert 'ec2:CreateInternetGateway' in vpc_stmt['Action']
        assert 'ec2:CreateRouteTable' in vpc_stmt['Action']
        assert len(vpc_stmt['Action']) >= 20
    
    def test_security_group_management(self, github_actions_policy):
        """Test Security Group Management permissions"""
        sg_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'SecurityGroupManagement')
        
        assert sg_stmt['Effect'] == 'Allow'
        assert 'ec2:CreateSecurityGroup' in sg_stmt['Action']
        assert 'ec2:DeleteSecurityGroup' in sg_stmt['Action']
        assert 'ec2:AuthorizeSecurityGroupIngress' in sg_stmt['Action']
        assert 'ec2:AuthorizeSecurityGroupEgress' in sg_stmt['Action']
    
    def test_ec2_instance_management(self, github_actions_policy):
        """Test EC2 Instance Management permissions"""
        ec2_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'EC2InstanceManagement')
        
        assert ec2_stmt['Effect'] == 'Allow'
        assert 'ec2:RunInstances' in ec2_stmt['Action']
        assert 'ec2:TerminateInstances' in ec2_stmt['Action']
        assert 'ec2:DescribeInstances' in ec2_stmt['Action']
    
    def test_load_balancing_permissions(self, github_actions_policy):
        """Test Load Balancing permissions"""
        lb_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'LoadBalancing')
        
        assert lb_stmt['Effect'] == 'Allow'
        assert any('elasticloadbalancing:CreateLoadBalancer' in action for action in lb_stmt['Action'])
        assert any('elasticloadbalancing:DeleteLoadBalancer' in action for action in lb_stmt['Action'])
        assert any('elasticloadbalancing:DescribeLoadBalancers' in action for action in lb_stmt['Action'])
    
    def test_auto_scaling_permissions(self, github_actions_policy):
        """Test Auto Scaling permissions"""
        as_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'AutoScaling')
        
        assert as_stmt['Effect'] == 'Allow'
        assert 'autoscaling:CreateAutoScalingGroup' in as_stmt['Action']
        assert 'autoscaling:DeleteAutoScalingGroup' in as_stmt['Action']
        assert 'autoscaling:UpdateAutoScalingGroup' in as_stmt['Action']
    
    def test_rds_management_permissions(self, github_actions_policy):
        """Test RDS Management permissions"""
        rds_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'RDSManagement')
        
        assert rds_stmt['Effect'] == 'Allow'
        assert 'rds:CreateDBInstance' in rds_stmt['Action']
        assert 'rds:DeleteDBInstance' in rds_stmt['Action']
        assert 'rds:DescribeDBInstances' in rds_stmt['Action']
        assert 'rds:CreateDBSubnetGroup' in rds_stmt['Action']
    
    def test_eks_management_permissions(self, github_actions_policy):
        """Test EKS Management permissions"""
        eks_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'EKSManagement')
        
        assert eks_stmt['Effect'] == 'Allow'
        assert 'eks:CreateCluster' in eks_stmt['Action']
        assert 'eks:DeleteCluster' in eks_stmt['Action']
        assert 'eks:DescribeCluster' in eks_stmt['Action']
    
    def test_iam_for_eks_and_services(self, github_actions_policy):
        """Test IAM permissions for EKS and services"""
        iam_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'IAMForEKSAndServices')
        
        assert iam_stmt['Effect'] == 'Allow'
        assert 'iam:CreateRole' in iam_stmt['Action']
        assert 'iam:DeleteRole' in iam_stmt['Action']
        assert 'iam:AttachRolePolicy' in iam_stmt['Action']
        assert 'iam:PassRole' in iam_stmt['Action']
    
    def test_s3_application_buckets(self, github_actions_policy):
        """Test S3 Application Buckets permissions"""
        s3_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'S3ApplicationBuckets')
        
        assert s3_stmt['Effect'] == 'Allow'
        assert 's3:CreateBucket' in s3_stmt['Action']
        assert 's3:DeleteBucket' in s3_stmt['Action']
        assert 's3:PutBucketPolicy' in s3_stmt['Action']
    
    def test_cloudwatch_logs_and_metrics(self, github_actions_policy):
        """Test CloudWatch Logs and Metrics permissions"""
        cw_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'CloudWatchLogsAndMetrics')
        
        assert cw_stmt['Effect'] == 'Allow'
        assert 'logs:CreateLogGroup' in cw_stmt['Action']
        assert 'logs:CreateLogStream' in cw_stmt['Action']
        assert 'logs:PutLogEvents' in cw_stmt['Action']
        assert 'cloudwatch:PutMetricData' in cw_stmt['Action']
    
    def test_secrets_manager_permissions(self, github_actions_policy):
        """Test Secrets Manager permissions"""
        sm_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'SecretsManager')
        
        assert sm_stmt['Effect'] == 'Allow'
        assert 'secretsmanager:GetSecretValue' in sm_stmt['Action']
        assert 'secretsmanager:DescribeSecret' in sm_stmt['Action']
    
    def test_lambda_management_permissions(self, github_actions_policy):
        """Test Lambda Management permissions"""
        lambda_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'LambdaManagement')
        
        assert lambda_stmt['Effect'] == 'Allow'
        assert 'lambda:CreateFunction' in lambda_stmt['Action']
        assert 'lambda:DeleteFunction' in lambda_stmt['Action']
        assert 'lambda:UpdateFunctionCode' in lambda_stmt['Action']
    
    def test_ecr_access_permissions(self, github_actions_policy):
        """Test ECR Access permissions"""
        ecr_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'ECRAccess')
        
        assert ecr_stmt['Effect'] == 'Allow'
        assert 'ecr:GetAuthorizationToken' in ecr_stmt['Action']
        assert 'ecr:BatchCheckLayerAvailability' in ecr_stmt['Action']
        assert 'ecr:PutImage' in ecr_stmt['Action']
    
    def test_kms_has_condition(self, github_actions_policy):
        """Test KMS statement has proper conditions"""
        kms_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'KMSAccess')
        
        assert 'Condition' in kms_stmt
        assert 'StringEquals' in kms_stmt['Condition']
        assert 'kms:ViaService' in kms_stmt['Condition']['StringEquals']
        
        via_services = kms_stmt['Condition']['StringEquals']['kms:ViaService']
        assert isinstance(via_services, list)
        assert len(via_services) >= 2


class TestPolicyVariableSubstitution:
    """Test policy template variables"""
    
    def test_policy_contains_template_variables(self, github_actions_policy_path):
        """Test policy file contains template variables for customization"""
        with open(github_actions_policy_path) as f:
            content = f.read()
        
        # Should contain template variables
        assert '${TFSTATE_BUCKET_NAME}' in content
        assert '${TFSTATE_LOCK_TABLE}' in content
        assert '${AWS_REGION}' in content
        assert '${AWS_ACCOUNT_ID}' in content
    
    def test_dynamo_db_resource_uses_variables(self, github_actions_policy_path):
        """Test DynamoDB resource ARN uses template variables"""
        with open(github_actions_policy_path) as f:
            policy = json.load(f)
        
        dynamo_stmt = next(s for s in policy['Statement'] if s['Sid'] == 'DynamoDBLock')
        resource = dynamo_stmt['Resource']
        
        assert '${AWS_REGION}' in resource
        assert '${AWS_ACCOUNT_ID}' in resource
        assert '${TFSTATE_LOCK_TABLE}' in resource


class TestPolicyConfigExample:
    """Test policy-config.example.json file"""
    
    def test_policy_config_example_exists(self):
        """Test policy configuration example file exists"""
        config_path = Path("terraform/iam/policy-config.example.json")
        assert config_path.exists()
    
    def test_policy_config_example_valid_json(self):
        """Test policy configuration example is valid JSON"""
        config_path = Path("terraform/iam/policy-config.example.json")
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert config is not None
        assert isinstance(config, dict)
    
    def test_policy_config_has_required_fields(self):
        """Test policy configuration has required template fields"""
        config_path = Path("terraform/iam/policy-config.example.json")
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Should have instructions or variable mappings
        assert len(config) > 0


class TestPolicySecurityBestPractices:
    """Test policy follows security best practices"""
    
    def test_no_wildcard_resources_in_critical_statements(self, github_actions_policy):
        """Test critical statements don't use wildcard resources"""
        critical_sids = ['TerraformStateAccess', 'DynamoDBLock', 'IAMForEKSAndServices']
        
        for sid in critical_sids:
            stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == sid)
            resources = stmt.get('Resource', [])
            
            if isinstance(resources, list):
                for resource in resources:
                    # Allow * for KMS with conditions
                    if sid != 'KMSAccess':
                        assert not resource.endswith('/*') or '${' in resource
    
    def test_all_statements_have_effect(self, github_actions_policy):
        """Test all statements explicitly define Effect"""
        for stmt in github_actions_policy['Statement']:
            assert 'Effect' in stmt
            assert stmt['Effect'] in ['Allow', 'Deny']
    
    def test_no_full_admin_access(self, github_actions_policy):
        """Test policy doesn't grant full admin access"""
        for stmt in github_actions_policy['Statement']:
            actions = stmt.get('Action', [])
            if isinstance(actions, list):
                assert '*:*' not in actions
                assert '*' not in actions
    
    def test_policy_version_is_current(self, github_actions_policy):
        """Test policy uses current version"""
        assert github_actions_policy['Version'] == '2012-10-17'


class TestPolicyPermissionCoverage:
    """Test comprehensive permission coverage"""
    
    def test_compute_permissions_coverage(self, github_actions_policy):
        """Test comprehensive compute permissions"""
        ec2_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'EC2InstanceManagement')
        
        # Should have read, write, and manage permissions
        actions = ec2_stmt['Action']
        assert any('Describe' in a for a in actions)  # Read
        assert any('Run' in a or 'Create' in a for a in actions)  # Write
        assert any('Terminate' in a or 'Delete' in a for a in actions)  # Manage
    
    def test_networking_permissions_coverage(self, github_actions_policy):
        """Test comprehensive networking permissions"""
        vpc_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'VPCManagement')
        sg_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'SecurityGroupManagement')
        
        # Combined should cover VPC, subnets, IGW, routes, security groups
        all_actions = vpc_stmt['Action'] + sg_stmt['Action']
        
        assert any('Vpc' in a for a in all_actions)
        assert any('Subnet' in a for a in all_actions)
        assert any('InternetGateway' in a for a in all_actions)
        assert any('RouteTable' in a for a in all_actions)
        assert any('SecurityGroup' in a for a in all_actions)
    
    def test_data_permissions_coverage(self, github_actions_policy):
        """Test comprehensive data service permissions"""
        rds_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'RDSManagement')
        s3_stmt = next(s for s in github_actions_policy['Statement'] if s['Sid'] == 'S3ApplicationBuckets')
        
        # Should cover database and storage
        assert len(rds_stmt['Action']) >= 5
        assert len(s3_stmt['Action']) >= 5


class TestPolicyEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_policy_handles_empty_resource_lists(self, github_actions_policy):
        """Test statements handle resource specifications correctly"""
        for stmt in github_actions_policy['Statement']:
            if 'Resource' in stmt:
                resource = stmt['Resource']
                if isinstance(resource, list):
                    assert len(resource) > 0
    
    def test_policy_action_lists_not_empty(self, github_actions_policy):
        """Test all action lists are non-empty"""
        for stmt in github_actions_policy['Statement']:
            actions = stmt['Action']
            if isinstance(actions, list):
                assert len(actions) > 0
            else:
                assert isinstance(actions, str)
                assert len(actions) > 0
    
    def test_policy_sids_are_unique(self, github_actions_policy):
        """Test all Sids are unique"""
        sids = [stmt['Sid'] for stmt in github_actions_policy['Statement']]
        assert len(sids) == len(set(sids))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])