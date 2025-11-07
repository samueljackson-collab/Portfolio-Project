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
# Enhanced Tests for Production-Grade IAM Policy (200+ Permissions)
# ============================================================================

class TestEnhancedGitHubActionsPolicyCompleteness:
    """Test comprehensive permission coverage in enhanced policy."""

    def test_policy_has_minimum_statement_count(self, github_actions_policy):
        """Verify policy has sufficient statements for comprehensive coverage."""
        statements = github_actions_policy["Statement"]
        # Enhanced policy should have 15+ statements covering all services
        assert len(statements) >= 15, f"Expected 15+ statements, got {len(statements)}"

    def test_policy_covers_all_critical_services(self, github_actions_policy):
        """Verify policy includes all critical AWS services."""
        policy_str = json.dumps(github_actions_policy)
        
        critical_services = [
            "s3:", "dynamodb:", "kms:", "ec2:", "rds:", "eks:",
            "elasticloadbalancing:", "autoscaling:", "iam:",
            "logs:", "cloudwatch:", "secretsmanager:", "lambda:", "ecr:"
        ]
        
        for service in critical_services:
            assert service in policy_str, f"Policy missing {service} permissions"

    def test_policy_has_200_plus_permissions(self, github_actions_policy):
        """Verify policy grants 200+ unique permissions."""
        all_actions = []
        for stmt in github_actions_policy["Statement"]:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            all_actions.extend(actions)
        
        unique_actions = set(all_actions)
        assert len(unique_actions) >= 200, f"Expected 200+ permissions, got {len(unique_actions)}"


class TestVPCManagementPermissions:
    """Test VPC networking permissions (30+ actions)."""

    def test_vpc_statement_exists(self, github_actions_policy):
        """Verify VPC management statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("VPC" in sid for sid in sids), "VPC management statement not found"

    def test_vpc_create_delete_permissions(self, github_actions_policy):
        """Verify VPC creation and deletion permissions."""
        vpc_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "VPC" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                vpc_actions.extend(actions)
        
        assert any("CreateVpc" in a for a in vpc_actions)
        assert any("DeleteVpc" in a for a in vpc_actions)
        assert any("DescribeVpcs" in a for a in vpc_actions)

    def test_subnet_management_permissions(self, github_actions_policy):
        """Verify subnet management permissions."""
        vpc_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "VPC" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                vpc_actions.extend(actions)
        
        assert any("CreateSubnet" in a for a in vpc_actions)
        assert any("DeleteSubnet" in a for a in vpc_actions)
        assert any("DescribeSubnets" in a for a in vpc_actions)

    def test_internet_gateway_permissions(self, github_actions_policy):
        """Verify internet gateway permissions."""
        vpc_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "VPC" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                vpc_actions.extend(actions)
        
        assert any("CreateInternetGateway" in a for a in vpc_actions)
        assert any("AttachInternetGateway" in a for a in vpc_actions)
        assert any("DeleteInternetGateway" in a for a in vpc_actions)

    def test_nat_gateway_permissions(self, github_actions_policy):
        """Verify NAT gateway permissions."""
        vpc_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "VPC" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                vpc_actions.extend(actions)
        
        assert any("CreateNatGateway" in a for a in vpc_actions)
        assert any("DeleteNatGateway" in a for a in vpc_actions)

    def test_route_table_permissions(self, github_actions_policy):
        """Verify route table management permissions."""
        vpc_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "VPC" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                vpc_actions.extend(actions)
        
        assert any("CreateRouteTable" in a for a in vpc_actions)
        assert any("DeleteRouteTable" in a for a in vpc_actions)
        assert any("AssociateRouteTable" in a for a in vpc_actions)

    def test_elastic_ip_permissions(self, github_actions_policy):
        """Verify Elastic IP management permissions."""
        vpc_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "VPC" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                vpc_actions.extend(actions)
        
        assert any("AllocateAddress" in a for a in vpc_actions)
        assert any("ReleaseAddress" in a for a in vpc_actions)


class TestSecurityGroupPermissions:
    """Test security group permissions (13+ actions)."""

    def test_security_group_statement_exists(self, github_actions_policy):
        """Verify security group statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("SecurityGroup" in sid for sid in sids)

    def test_security_group_crud_permissions(self, github_actions_policy):
        """Verify security group CRUD permissions."""
        sg_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "SecurityGroup" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                sg_actions.extend(actions)
        
        assert any("CreateSecurityGroup" in a for a in sg_actions)
        assert any("DeleteSecurityGroup" in a for a in sg_actions)
        assert any("DescribeSecurityGroups" in a for a in sg_actions)

    def test_security_group_rule_permissions(self, github_actions_policy):
        """Verify security group rule management permissions."""
        sg_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "SecurityGroup" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                sg_actions.extend(actions)
        
        assert any("AuthorizeSecurityGroupIngress" in a for a in sg_actions)
        assert any("AuthorizeSecurityGroupEgress" in a for a in sg_actions)
        assert any("RevokeSecurityGroupIngress" in a for a in sg_actions)
        assert any("RevokeSecurityGroupEgress" in a for a in sg_actions)


class TestLoadBalancerPermissions:
    """Test elastic load balancing permissions (17+ actions)."""

    def test_load_balancer_statement_exists(self, github_actions_policy):
        """Verify load balancer statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("LoadBalanc" in sid for sid in sids)

    def test_load_balancer_crud_permissions(self, github_actions_policy):
        """Verify load balancer CRUD permissions."""
        lb_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "LoadBalanc" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                lb_actions.extend(actions)
        
        assert any("CreateLoadBalancer" in a for a in lb_actions)
        assert any("DeleteLoadBalancer" in a for a in lb_actions)
        assert any("DescribeLoadBalancers" in a for a in lb_actions)

    def test_target_group_permissions(self, github_actions_policy):
        """Verify target group management permissions."""
        lb_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "LoadBalanc" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                lb_actions.extend(actions)
        
        assert any("CreateTargetGroup" in a for a in lb_actions)
        assert any("DeleteTargetGroup" in a for a in lb_actions)
        assert any("RegisterTargets" in a for a in lb_actions)
        assert any("DeregisterTargets" in a for a in lb_actions)

    def test_listener_permissions(self, github_actions_policy):
        """Verify listener management permissions."""
        lb_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "LoadBalanc" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                lb_actions.extend(actions)
        
        assert any("CreateListener" in a for a in lb_actions)
        assert any("DeleteListener" in a for a in lb_actions)


class TestAutoScalingPermissions:
    """Test auto scaling permissions (12+ actions)."""

    def test_auto_scaling_statement_exists(self, github_actions_policy):
        """Verify auto scaling statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("AutoScaling" in sid for sid in sids)

    def test_auto_scaling_group_permissions(self, github_actions_policy):
        """Verify ASG management permissions."""
        asg_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "AutoScaling" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                asg_actions.extend(actions)
        
        assert any("CreateAutoScalingGroup" in a for a in asg_actions)
        assert any("DeleteAutoScalingGroup" in a for a in asg_actions)
        assert any("UpdateAutoScalingGroup" in a for a in asg_actions)

    def test_launch_configuration_permissions(self, github_actions_policy):
        """Verify launch configuration permissions."""
        asg_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "AutoScaling" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                asg_actions.extend(actions)
        
        assert any("CreateLaunchConfiguration" in a for a in asg_actions)
        assert any("DeleteLaunchConfiguration" in a for a in asg_actions)


class TestEKSPermissions:
    """Test EKS Kubernetes permissions (10+ actions)."""

    def test_eks_statement_exists(self, github_actions_policy):
        """Verify EKS statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("EKS" in sid for sid in sids)

    def test_eks_cluster_permissions(self, github_actions_policy):
        """Verify EKS cluster management permissions."""
        eks_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "EKS" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                eks_actions.extend(actions)
        
        assert any("CreateCluster" in a for a in eks_actions)
        assert any("DeleteCluster" in a for a in eks_actions)
        assert any("DescribeCluster" in a for a in eks_actions)
        assert any("UpdateClusterVersion" in a for a in eks_actions)

    def test_eks_nodegroup_permissions(self, github_actions_policy):
        """Verify EKS node group permissions."""
        eks_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "EKS" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                eks_actions.extend(actions)
        
        assert any("CreateNodegroup" in a for a in eks_actions)
        assert any("DeleteNodegroup" in a for a in eks_actions)


class TestSecretsManagerPermissions:
    """Test Secrets Manager permissions (7+ actions)."""

    def test_secrets_manager_statement_exists(self, github_actions_policy):
        """Verify Secrets Manager statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("Secret" in sid for sid in sids)

    def test_secrets_manager_crud_permissions(self, github_actions_policy):
        """Verify Secrets Manager CRUD permissions."""
        sm_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "Secret" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                sm_actions.extend(actions)
        
        assert any("CreateSecret" in a for a in sm_actions)
        assert any("DeleteSecret" in a for a in sm_actions)
        assert any("GetSecretValue" in a for a in sm_actions)
        assert any("PutSecretValue" in a for a in sm_actions)

    def test_secrets_manager_resource_scoped(self, github_actions_policy):
        """Verify Secrets Manager permissions are resource-scoped."""
        for stmt in github_actions_policy["Statement"]:
            if "Secret" in stmt.get("Sid", ""):
                resource = stmt.get("Resource", "")
                # Should have project-specific scoping
                assert "${PROJECT_NAME}" in str(resource) or "secret:" in str(resource)


class TestLambdaPermissions:
    """Test Lambda function permissions (7+ actions)."""

    def test_lambda_statement_exists(self, github_actions_policy):
        """Verify Lambda statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("Lambda" in sid for sid in sids)

    def test_lambda_function_permissions(self, github_actions_policy):
        """Verify Lambda function management permissions."""
        lambda_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "Lambda" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                lambda_actions.extend(actions)
        
        assert any("CreateFunction" in a for a in lambda_actions)
        assert any("DeleteFunction" in a for a in lambda_actions)
        assert any("UpdateFunctionCode" in a for a in lambda_actions)
        assert any("InvokeFunction" in a for a in lambda_actions)


class TestECRPermissions:
    """Test ECR container registry permissions (11+ actions)."""

    def test_ecr_statement_exists(self, github_actions_policy):
        """Verify ECR statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("ECR" in sid for sid in sids)

    def test_ecr_authentication_permissions(self, github_actions_policy):
        """Verify ECR authentication permissions."""
        ecr_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "ECR" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                ecr_actions.extend(actions)
        
        assert any("GetAuthorizationToken" in a for a in ecr_actions)

    def test_ecr_image_management_permissions(self, github_actions_policy):
        """Verify ECR image management permissions."""
        ecr_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "ECR" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                ecr_actions.extend(actions)
        
        assert any("PutImage" in a for a in ecr_actions)
        assert any("BatchGetImage" in a for a in ecr_actions)
        assert any("BatchCheckLayerAvailability" in a for a in ecr_actions)

    def test_ecr_repository_permissions(self, github_actions_policy):
        """Verify ECR repository management permissions."""
        ecr_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "ECR" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                ecr_actions.extend(actions)
        
        assert any("CreateRepository" in a for a in ecr_actions)
        assert any("DeleteRepository" in a for a in ecr_actions)


class TestCloudWatchPermissions:
    """Test CloudWatch logging and metrics permissions."""

    def test_cloudwatch_statement_exists(self, github_actions_policy):
        """Verify CloudWatch statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("CloudWatch" in sid or "Log" in sid for sid in sids)

    def test_cloudwatch_logs_permissions(self, github_actions_policy):
        """Verify CloudWatch Logs permissions."""
        cw_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "CloudWatch" in stmt.get("Sid", "") or "Log" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                cw_actions.extend(actions)
        
        assert any("CreateLogGroup" in a for a in cw_actions)
        assert any("PutLogEvents" in a for a in cw_actions)

    def test_cloudwatch_metrics_permissions(self, github_actions_policy):
        """Verify CloudWatch Metrics permissions."""
        cw_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "CloudWatch" in stmt.get("Sid", "") or "Log" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                cw_actions.extend(actions)
        
        assert any("PutMetricData" in a for a in cw_actions)
        assert any("GetMetricData" in a for a in cw_actions)


class TestIAMServiceRolePermissions:
    """Test IAM permissions for service roles."""

    def test_iam_statement_exists(self, github_actions_policy):
        """Verify IAM statement exists."""
        sids = [stmt.get("Sid", "") for stmt in github_actions_policy["Statement"]]
        assert any("IAM" in sid for sid in sids)

    def test_iam_role_permissions(self, github_actions_policy):
        """Verify IAM role management permissions."""
        iam_actions = []
        for stmt in github_actions_policy["Statement"]:
            if "IAM" in stmt.get("Sid", ""):
                actions = stmt.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                iam_actions.extend(actions)
        
        assert any("CreateRole" in a for a in iam_actions)
        assert any("DeleteRole" in a for a in iam_actions)
        assert any("PassRole" in a for a in iam_actions)

    def test_iam_permissions_are_scoped(self, github_actions_policy):
        """Verify IAM permissions are properly scoped."""
        for stmt in github_actions_policy["Statement"]:
            if "IAM" in stmt.get("Sid", ""):
                resource = stmt.get("Resource", "")
                # IAM permissions should be scoped to project roles
                if resource != "*":
                    assert "${PROJECT_NAME}" in str(resource) or "role/" in str(resource)


class TestPolicyConfigExample:
    """Test the policy-config.example.json template file."""

    def test_policy_config_example_exists(self):
        """Verify policy-config.example.json exists."""
        config_path = Path("terraform/iam/policy-config.example.json")
        assert config_path.exists()

    def test_policy_config_valid_json(self):
        """Verify policy-config.example.json is valid JSON."""
        config_path = Path("terraform/iam/policy-config.example.json")
        with open(config_path) as f:
            config = json.load(f)
        assert config is not None

    def test_policy_config_has_variables_section(self):
        """Verify config has variables section."""
        config_path = Path("terraform/iam/policy-config.example.json")
        with open(config_path) as f:
            config = json.load(f)
        assert "variables" in config

    def test_policy_config_has_required_variables(self):
        """Verify config defines all required variables."""
        config_path = Path("terraform/iam/policy-config.example.json")
        with open(config_path) as f:
            config = json.load(f)
        
        variables = config.get("variables", {})
        required_vars = [
            "TFSTATE_BUCKET_NAME",
            "TFSTATE_LOCK_TABLE",
            "AWS_REGION",
            "AWS_ACCOUNT_ID",
            "PROJECT_NAME"
        ]
        
        for var in required_vars:
            assert var in variables, f"Missing required variable: {var}"

    def test_policy_config_has_deployment_steps(self):
        """Verify config includes deployment steps."""
        config_path = Path("terraform/iam/policy-config.example.json")
        with open(config_path) as f:
            config = json.load(f)
        
        assert "deployment_steps" in config
        assert isinstance(config["deployment_steps"], list)
        assert len(config["deployment_steps"]) >= 5

    def test_policy_config_has_security_notes(self):
        """Verify config includes security notes."""
        config_path = Path("terraform/iam/policy-config.example.json")
        with open(config_path) as f:
            config = json.load(f)
        
        assert "security_notes" in config
        assert isinstance(config["security_notes"], list)
        assert len(config["security_notes"]) >= 3

    def test_policy_config_has_scope_summary(self):
        """Verify config includes scope summary."""
        config_path = Path("terraform/iam/policy-config.example.json")
        with open(config_path) as f:
            config = json.load(f)
        
        assert "scope_summary" in config
        scope = config["scope_summary"]
        assert "services_covered" in scope
        assert "total_permissions" in scope

    def test_policy_config_mentions_least_privilege(self):
        """Verify config emphasizes least privilege principle."""
        config_path = Path("terraform/iam/policy-config.example.json")
        content = config_path.read_text()
        assert "least-privilege" in content.lower() or "least privilege" in content.lower()


class TestPolicyVariableConsistency:
    """Test consistency between policy and config template."""

    def test_policy_variables_match_config(self):
        """Verify policy uses variables defined in config."""
        policy_path = Path("terraform/iam/github_actions_ci_policy.json")
        config_path = Path("terraform/iam/policy-config.example.json")
        
        with open(policy_path) as f:
            policy_content = f.read()
        
        with open(config_path) as f:
            config = json.load(f)
        
        variables = config.get("variables", {})
        for var_name in variables.keys():
            # Policy should reference these variables
            assert f"${{{var_name}}}" in policy_content, f"Policy missing variable: {var_name}"