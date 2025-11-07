"""
Comprehensive tests for Terraform EKS module.

This test suite validates:
- EKS cluster configuration
- Node group setup
- IAM roles and policies
- Security configurations
- KMS encryption
- CloudWatch logging
"""

import re
import subprocess
from pathlib import Path
import pytest


@pytest.fixture
def eks_module_dir():
    """Return path to EKS module directory."""
    return Path("projects/01-sde-devops/PRJ-SDE-001/code-examples/terraform/modules/eks")


@pytest.fixture
def eks_main_tf(eks_module_dir):
    """Return path to EKS module main.tf."""
    return eks_module_dir / "main.tf"


@pytest.fixture
def eks_variables_tf(eks_module_dir):
    """Return path to EKS module variables.tf."""
    return eks_module_dir / "variables.tf"


@pytest.fixture
def eks_outputs_tf(eks_module_dir):
    """Return path to EKS module outputs.tf."""
    return eks_module_dir / "outputs.tf"


class TestEKSModuleFiles:
    """Test EKS module file existence and structure."""

    def test_eks_module_directory_exists(self, eks_module_dir):
        """Verify EKS module directory exists."""
        assert eks_module_dir.exists(), f"EKS module not found at {eks_module_dir}"
        assert eks_module_dir.is_dir(), f"{eks_module_dir} is not a directory"

    def test_required_files_exist(self, eks_module_dir):
        """Verify all required Terraform files exist."""
        required_files = ["main.tf", "variables.tf", "outputs.tf"]
        for filename in required_files:
            file_path = eks_module_dir / filename
            assert file_path.exists(), f"Required file {filename} not found"

    def test_user_data_script_exists(self, eks_module_dir):
        """Verify user_data.sh script exists."""
        user_data = eks_module_dir / "user_data.sh"
        assert user_data.exists(), "user_data.sh script not found"


class TestEKSClusterConfiguration:
    """Test EKS cluster resource configuration."""

    def test_eks_cluster_resource_exists(self, eks_main_tf):
        """Verify aws_eks_cluster resource is defined."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_eks_cluster"' in content, \
            "aws_eks_cluster resource not found"

    def test_cluster_uses_environment_naming(self, eks_main_tf):
        """Verify cluster uses environment in naming."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        cluster_block = re.search(
            r'resource "aws_eks_cluster" "main" \{[^}]*name\s*=\s*"[^"]*"',
            content,
            re.DOTALL
        )
        assert cluster_block, "Could not find cluster name"
        assert '${var.environment}' in cluster_block.group(0), \
            "Cluster name should include environment variable"

    def test_cluster_has_iam_role(self, eks_main_tf):
        """Verify cluster has IAM role attached."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'role_arn = aws_iam_role.cluster.arn' in content, \
            "Cluster should reference IAM role"

    def test_cluster_specifies_version(self, eks_main_tf):
        """Verify cluster specifies Kubernetes version."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        cluster_block = re.search(
            r'resource "aws_eks_cluster" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert cluster_block, "Could not find cluster block"
        assert 'version' in cluster_block.group(0), \
            "Cluster should specify Kubernetes version"


class TestEKSVPCConfiguration:
    """Test EKS VPC configuration."""

    def test_vpc_config_exists(self, eks_main_tf):
        """Verify VPC config block exists."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'vpc_config {' in content, "VPC config block not found"

    def test_private_endpoint_enabled(self, eks_main_tf):
        """Verify private endpoint access is enabled."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert re.search(r'endpoint_private_access\s*=\s*true', content), \
            "Private endpoint access should be enabled"

    def test_public_endpoint_configurable(self, eks_main_tf):
        """Verify public endpoint access is configurable."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'endpoint_public_access' in content, \
            "Public endpoint access should be configurable"
        assert 'var.enable_public_access' in content, \
            "Should use variable for public access configuration"

    def test_subnet_ids_from_variable(self, eks_main_tf):
        """Verify subnet IDs come from variables."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        vpc_block = re.search(r'vpc_config \{.*?\}', content, re.DOTALL)
        assert vpc_block, "Could not find VPC config"
        assert 'subnet_ids' in vpc_block.group(0), "Should specify subnet IDs"
        assert 'var.subnet_ids' in vpc_block.group(0), \
            "Subnet IDs should come from variable"


class TestEKSEncryption:
    """Test EKS encryption configuration."""

    def test_encryption_config_exists(self, eks_main_tf):
        """Verify encryption config is defined."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'encryption_config {' in content, \
            "Encryption config not found"

    def test_uses_kms_for_secrets(self, eks_main_tf):
        """Verify KMS is used for secrets encryption."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        encryption_block = re.search(
            r'encryption_config \{.*?\}',
            content,
            re.DOTALL
        )
        assert encryption_block, "Could not find encryption config"
        assert 'resources = ["secrets"]' in encryption_block.group(0), \
            "Should encrypt secrets"

    def test_kms_key_resource_exists(self, eks_main_tf):
        """Verify KMS key resource is defined."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_kms_key" "eks"' in content, \
            "KMS key resource not found"

    def test_kms_key_rotation_enabled(self, eks_main_tf):
        """Verify KMS key rotation is enabled."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        kms_block = re.search(
            r'resource "aws_kms_key" "eks" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert kms_block, "Could not find KMS key block"
        assert re.search(r'enable_key_rotation\s*=\s*true', kms_block.group(0)), \
            "KMS key rotation should be enabled"

    def test_kms_key_has_deletion_window(self, eks_main_tf):
        """Verify KMS key has deletion window configured."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        kms_block = re.search(
            r'resource "aws_kms_key" "eks" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert kms_block, "Could not find KMS key block"
        assert 'deletion_window_in_days' in kms_block.group(0), \
            "KMS key should have deletion window"


class TestEKSLogging:
    """Test EKS CloudWatch logging configuration."""

    def test_cluster_logging_enabled(self, eks_main_tf):
        """Verify cluster logging is enabled."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'enabled_cluster_log_types' in content, \
            "Cluster logging should be configured"

    def test_logs_critical_components(self, eks_main_tf):
        """Verify critical components are logged."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        
        critical_logs = ['api', 'audit', 'authenticator']
        log_block = re.search(
            r'enabled_cluster_log_types\s*=\s*\[.*?\]',
            content,
            re.DOTALL
        )
        assert log_block, "Could not find log types configuration"
        
        for log_type in critical_logs:
            assert f'"{log_type}"' in log_block.group(0), \
                f"Should log {log_type} events"

    def test_cloudwatch_log_group_exists(self, eks_main_tf):
        """Verify CloudWatch log group is created."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_cloudwatch_log_group" "eks"' in content, \
            "CloudWatch log group not found"

    def test_log_retention_configured(self, eks_main_tf):
        """Verify log retention is configured."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        log_group_block = re.search(
            r'resource "aws_cloudwatch_log_group" "eks" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert log_group_block, "Could not find log group"
        assert 'retention_in_days' in log_group_block.group(0), \
            "Log retention should be configured"


class TestEKSIAMConfiguration:
    """Test EKS IAM roles and policies."""

    def test_cluster_iam_role_exists(self, eks_main_tf):
        """Verify cluster IAM role is defined."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_iam_role" "cluster"' in content, \
            "Cluster IAM role not found"

    def test_cluster_role_has_assume_policy(self, eks_main_tf):
        """Verify cluster role has proper assume role policy."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        role_block = re.search(
            r'resource "aws_iam_role" "cluster" \{.*?assume_role_policy.*?\}',
            content,
            re.DOTALL
        )
        assert role_block, "Cluster role should have assume role policy"
        assert 'eks.amazonaws.com' in role_block.group(0), \
            "Should allow EKS service to assume role"

    def test_required_policies_attached(self, eks_main_tf):
        """Verify required AWS managed policies are attached."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        
        required_policies = [
            'AmazonEKSClusterPolicy',
            'AmazonEKSVPCResourceController'
        ]
        
        for policy in required_policies:
            assert policy in content, f"Should attach {policy}"

    def test_node_iam_role_exists(self, eks_main_tf):
        """Verify node IAM role is defined."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_iam_role" "node"' in content, \
            "Node IAM role not found"


class TestEKSNodeGroups:
    """Test EKS node group configuration."""

    def test_node_group_resource_exists(self, eks_main_tf):
        """Verify node group resource is defined."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_eks_node_group"' in content, \
            "Node group resource not found"

    def test_node_group_scaling_configured(self, eks_main_tf):
        """Verify node group has scaling configuration."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        node_group_block = re.search(
            r'resource "aws_eks_node_group" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert node_group_block, "Could not find node group"
        assert 'scaling_config {' in node_group_block.group(0), \
            "Node group should have scaling config"

    def test_node_group_has_min_max_desired(self, eks_main_tf):
        """Verify scaling config has min, max, and desired size."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        scaling_block = re.search(
            r'scaling_config \{.*?\}',
            content,
            re.DOTALL
        )
        assert scaling_block, "Could not find scaling config"
        assert 'min_size' in scaling_block.group(0), "Should specify min_size"
        assert 'max_size' in scaling_block.group(0), "Should specify max_size"
        assert 'desired_size' in scaling_block.group(0), "Should specify desired_size"

    def test_node_group_uses_private_subnets(self, eks_main_tf):
        """Verify node group uses private subnets."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        node_group_block = re.search(
            r'resource "aws_eks_node_group" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert node_group_block, "Could not find node group"
        assert 'subnet_ids' in node_group_block.group(0), \
            "Should specify subnet IDs"
        assert 'var.private_subnet_ids' in node_group_block.group(0), \
            "Should use private subnets"

    def test_node_group_has_update_config(self, eks_main_tf):
        """Verify node group has update configuration."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        node_group_block = re.search(
            r'resource "aws_eks_node_group" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert node_group_block, "Could not find node group"
        assert 'update_config {' in node_group_block.group(0), \
            "Should have update config for rolling updates"


class TestEKSSecurityGroups:
    """Test EKS security group configuration."""

    def test_security_group_exists(self, eks_main_tf):
        """Verify security group is defined."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_security_group" "cluster"' in content, \
            "Cluster security group not found"


class TestEKSVariables:
    """Test EKS module variables."""

    def test_variables_file_exists(self, eks_variables_tf):
        """Verify variables.tf exists."""
        assert eks_variables_tf.exists(), "variables.tf not found"

    def test_environment_variable_exists(self, eks_variables_tf):
        """Verify environment variable is defined."""
        with open(eks_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "environment"' in content, \
            "environment variable not found"

    def test_kubernetes_version_variable_exists(self, eks_variables_tf):
        """Verify kubernetes_version variable is defined."""
        with open(eks_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "kubernetes_version"' in content, \
            "kubernetes_version variable not found"

    def test_node_scaling_variables_exist(self, eks_variables_tf):
        """Verify node scaling variables are defined."""
        with open(eks_variables_tf, 'r') as f:
            content = f.read()
        
        scaling_vars = ['desired_size', 'min_size', 'max_size']
        for var in scaling_vars:
            assert f'variable "{var}"' in content, \
                f"{var} variable not found"


class TestEKSOutputs:
    """Test EKS module outputs."""

    def test_outputs_file_exists(self, eks_outputs_tf):
        """Verify outputs.tf exists."""
        assert eks_outputs_tf.exists(), "outputs.tf not found"

    def test_cluster_id_output_exists(self, eks_outputs_tf):
        """Verify cluster_id output is defined."""
        with open(eks_outputs_tf, 'r') as f:
            content = f.read()
        assert 'cluster_id' in content or 'cluster_name' in content, \
            "Cluster identifier output not found"

    def test_cluster_endpoint_output_exists(self, eks_outputs_tf):
        """Verify cluster endpoint output is defined."""
        with open(eks_outputs_tf, 'r') as f:
            content = f.read()
        assert 'endpoint' in content, "Cluster endpoint output not found"


class TestEKSBestPractices:
    """Test EKS module follows best practices."""

    def test_uses_launch_template(self, eks_main_tf):
        """Verify node group uses launch template."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        node_group_block = re.search(
            r'resource "aws_eks_node_group" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        if node_group_block:
            assert 'launch_template {' in node_group_block.group(0), \
                "Should use launch template for better control"

    def test_has_proper_dependencies(self, eks_main_tf):
        """Verify cluster has proper resource dependencies."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        cluster_block = re.search(
            r'resource "aws_eks_cluster" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert cluster_block, "Could not find cluster block"
        assert 'depends_on' in cluster_block.group(0), \
            "Cluster should have explicit dependencies"

    def test_tags_resources(self, eks_main_tf):
        """Verify resources are properly tagged."""
        with open(eks_main_tf, 'r') as f:
            content = f.read()
        
        # Check cluster has tags
        cluster_block = re.search(
            r'resource "aws_eks_cluster" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert cluster_block and 'tags' in cluster_block.group(0), \
            "Cluster should have tags"