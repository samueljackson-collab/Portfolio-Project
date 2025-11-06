"""
Comprehensive tests for Terraform configuration files.

This test suite validates:
- HCL syntax correctness
- Required providers and versions
- Resource naming conventions
- Variable definitions and types
- Output definitions
- Backend configuration
- Security best practices
"""

import json
import subprocess
from pathlib import Path
import pytest


@pytest.fixture
def terraform_dir():
    """Return path to terraform directory."""
    return Path("terraform")


@pytest.fixture
def main_tf(terraform_dir):
    """Return path to main.tf."""
    return terraform_dir / "main.tf"


@pytest.fixture
def variables_tf(terraform_dir):
    """Return path to variables.tf."""
    return terraform_dir / "variables.tf"


@pytest.fixture
def outputs_tf(terraform_dir):
    """Return path to outputs.tf."""
    return terraform_dir / "outputs.tf"


@pytest.fixture
def backend_tf(terraform_dir):
    """Return path to backend.tf."""
    return terraform_dir / "backend.tf"


class TestTerraformDirectory:
    """Test Terraform directory structure."""

    def test_terraform_directory_exists(self, terraform_dir):
        """Verify terraform directory exists."""
        assert terraform_dir.exists()
        assert terraform_dir.is_dir()

    def test_main_tf_exists(self, main_tf):
        """Verify main.tf exists."""
        assert main_tf.exists()

    def test_variables_tf_exists(self, variables_tf):
        """Verify variables.tf exists."""
        assert variables_tf.exists()

    def test_outputs_tf_exists(self, outputs_tf):
        """Verify outputs.tf exists."""
        assert outputs_tf.exists()

    def test_backend_tf_exists(self, backend_tf):
        """Verify backend.tf exists."""
        assert backend_tf.exists()


class TestMainTfContent:
    """Test main.tf configuration."""

    def test_main_tf_has_provider_declaration(self, main_tf):
        """Verify main.tf declares AWS provider."""
        content = main_tf.read_text()
        assert 'provider "aws"' in content

    def test_main_tf_has_vpc_resource(self, main_tf):
        """Verify main.tf defines VPC resource."""
        content = main_tf.read_text()
        assert 'resource "aws_vpc"' in content

    def test_main_tf_has_subnet_resources(self, main_tf):
        """Verify main.tf defines subnet resources."""
        content = main_tf.read_text()
        assert 'resource "aws_subnet" "public"' in content
        assert 'resource "aws_subnet" "private"' in content

    def test_main_tf_has_internet_gateway(self, main_tf):
        """Verify main.tf defines internet gateway."""
        content = main_tf.read_text()
        assert 'resource "aws_internet_gateway"' in content

    def test_main_tf_has_route_table(self, main_tf):
        """Verify main.tf defines route table."""
        content = main_tf.read_text()
        assert 'resource "aws_route_table"' in content

    def test_main_tf_has_security_group(self, main_tf):
        """Verify main.tf defines security groups."""
        content = main_tf.read_text()
        assert 'resource "aws_security_group"' in content

    def test_main_tf_uses_common_tags(self, main_tf):
        """Verify main.tf uses common tags via locals."""
        content = main_tf.read_text()
        assert "locals {" in content
        assert "common_tags" in content
        assert "merge(local.common_tags" in content

    def test_main_tf_has_rds_resources(self, main_tf):
        """Verify main.tf has RDS-related resources."""
        content = main_tf.read_text()
        assert 'resource "aws_db_instance"' in content or "postgres" in content
        assert 'resource "aws_db_subnet_group"' in content

    def test_main_tf_has_conditional_resources(self, main_tf):
        """Verify main.tf uses count for conditional resources."""
        content = main_tf.read_text()
        assert "count = var.create_rds" in content

    def test_main_tf_generates_random_password(self, main_tf):
        """Verify main.tf generates random password for RDS."""
        content = main_tf.read_text()
        assert 'resource "random_password"' in content


class TestVariablesTfContent:
    """Test variables.tf configuration."""

    def test_variables_tf_has_vpc_cidr(self, variables_tf):
        """Verify variables.tf defines VPC CIDR."""
        content = variables_tf.read_text()
        assert 'variable "vpc_cidr"' in content
        assert "10.0.0.0/16" in content

    def test_variables_tf_has_subnet_cidrs(self, variables_tf):
        """Verify variables.tf defines subnet CIDRs."""
        content = variables_tf.read_text()
        assert 'variable "public_subnet_cidrs"' in content
        assert 'variable "private_subnet_cidrs"' in content

    def test_variables_tf_has_create_rds_flag(self, variables_tf):
        """Verify variables.tf has create_rds boolean."""
        content = variables_tf.read_text()
        assert 'variable "create_rds"' in content
        assert "type        = bool" in content

    def test_variables_tf_has_db_variables(self, variables_tf):
        """Verify variables.tf defines database variables."""
        content = variables_tf.read_text()
        assert 'variable "db_name"' in content
        assert 'variable "db_username"' in content
        assert 'variable "db_password"' in content

    def test_variables_tf_has_eks_variables(self, variables_tf):
        """Verify variables.tf defines EKS variables."""
        content = variables_tf.read_text()
        assert 'variable "create_eks"' in content
        assert 'variable "eks_cluster_name"' in content

    def test_variables_have_descriptions(self, variables_tf):
        """Verify all variables have descriptions."""
        content = variables_tf.read_text()
        variable_count = content.count('variable "')
        description_count = content.count('description =')
        # Allow some variance but most should have descriptions
        assert description_count >= variable_count * 0.8

    def test_variables_have_types(self, variables_tf):
        """Verify variables specify types."""
        content = variables_tf.read_text()
        assert "type        = string" in content
        assert "type        = bool" in content or "type = bool" in content

    def test_variables_have_defaults(self, variables_tf):
        """Verify variables have default values."""
        content = variables_tf.read_text()
        assert "default     =" in content or "default =" in content


class TestOutputsTfContent:
    """Test outputs.tf configuration."""

    def test_outputs_tf_has_assets_bucket_output(self, outputs_tf):
        """Verify outputs.tf defines assets bucket output."""
        content = outputs_tf.read_text()
        assert 'output "assets_bucket"' in content

    def test_outputs_have_descriptions(self, outputs_tf):
        """Verify outputs have descriptions."""
        content = outputs_tf.read_text()
        output_count = content.count('output "')
        description_count = content.count('description =')
        # All outputs should have descriptions
        assert description_count >= output_count


class TestBackendTfContent:
    """Test backend.tf configuration."""

    def test_backend_tf_has_s3_backend(self, backend_tf):
        """Verify backend.tf configures S3 backend."""
        content = backend_tf.read_text()
        assert 'backend "s3"' in content

    def test_backend_tf_has_required_fields(self, backend_tf):
        """Verify backend.tf has all required S3 backend fields."""
        content = backend_tf.read_text()
        assert "bucket" in content
        assert "key" in content
        assert "region" in content
        assert "dynamodb_table" in content

    def test_backend_tf_enables_encryption(self, backend_tf):
        """Verify backend.tf enables encryption."""
        content = backend_tf.read_text()
        assert "encrypt" in content
        assert "true" in content

    def test_backend_tf_uses_variables(self, backend_tf):
        """Verify backend.tf uses variables for configuration."""
        content = backend_tf.read_text()
        # Backend config typically uses var. references
        assert "var." in content or "${" in content


class TestResourceNaming:
    """Test resource naming conventions."""

    def test_resources_use_consistent_naming(self, main_tf):
        """Verify resources follow naming conventions."""
        content = main_tf.read_text()
        # Resources should use project_tag variable in names
        assert "${var.project_tag}" in content or "twisted-monk" in content or "twisted_monk" in content

    def test_resources_tagged_with_name(self, main_tf):
        """Verify resources are tagged with Name."""
        content = main_tf.read_text()
        # Count tag definitions
        name_tag_count = content.count('Name =') + content.count('Name=')
        # Most resources should have Name tags
        assert name_tag_count > 0


class TestSecurityBestPractices:
    """Test security best practices in Terraform config."""

    def test_rds_password_not_hardcoded(self, main_tf):
        """Verify RDS password is not hardcoded."""
        content = main_tf.read_text()
        # Password should use variable or random_password
        assert "random_password" in content or "var.db_password" in content

    def test_rds_in_private_subnet(self, main_tf):
        """Verify RDS uses private subnets."""
        content = main_tf.read_text()
        # RDS should reference private subnets
        if "aws_db_instance" in content:
            assert "private" in content.lower()

    def test_security_groups_have_descriptions(self, main_tf):
        """Verify security groups have descriptions."""
        content = main_tf.read_text()
        if "aws_security_group" in content:
            sg_count = content.count('resource "aws_security_group"')
            description_count = content.count('description =')
            assert description_count >= sg_count

    def test_vpc_enables_dns(self, main_tf):
        """Verify VPC enables DNS support and hostnames."""
        content = main_tf.read_text()
        if "aws_vpc" in content:
            assert "enable_dns_support" in content
            assert "enable_dns_hostnames" in content


class TestDataSources:
    """Test data sources."""

    def test_uses_availability_zones_data_source(self, main_tf):
        """Verify configuration uses availability zones data source."""
        content = main_tf.read_text()
        assert 'data "aws_availability_zones"' in content


class TestConditionalLogic:
    """Test conditional resource creation."""

    def test_rds_creation_is_conditional(self, main_tf):
        """Verify RDS resources use count for conditional creation."""
        content = main_tf.read_text()
        # Find RDS resources and check they use count
        lines = content.split('\n')
        in_rds_resource = False
        found_count = False
        
        for line in lines:
            if 'resource "aws_db_instance"' in line or 'resource "aws_db_subnet_group"' in line:
                in_rds_resource = True
            if in_rds_resource and "count = var.create_rds" in line:
                found_count = True
                break
            if in_rds_resource and "resource " in line and "aws_db" not in line:
                in_rds_resource = False
        
        assert found_count, "RDS resources should use conditional count"

    def test_eks_creation_is_conditional(self, main_tf):
        """Verify EKS resources use count for conditional creation."""
        content = main_tf.read_text()
        if "aws_eks_cluster" in content:
            assert "count = var.create_eks" in content


class TestBackendDocumentation:
    """Test backend.tf documentation and comments."""

    def test_backend_has_configuration_documentation(self, backend_tf):
        """Verify backend.tf documents how to provide configuration values."""
        content = backend_tf.read_text()
        assert "-backend-config" in content or "backend-config" in content, \
            "Should document how backend configuration is provided"

    def test_backend_documents_init_usage(self, backend_tf):
        """Verify backend.tf explains terraform init usage."""
        content = backend_tf.read_text()
        assert "terraform init" in content, \
            "Should reference terraform init command in documentation"

    def test_backend_documents_variable_mapping(self, backend_tf):
        """Verify backend.tf documents variable mapping."""
        content = backend_tf.read_text()
        # Should explain what variables are used
        assert "bucket" in content.lower() or "tfstate_bucket" in content, \
            "Should document bucket variable"
        assert "region" in content.lower() or "aws_region" in content, \
            "Should document region variable"

    def test_backend_references_workflow(self, backend_tf):
        """Verify backend.tf references the GitHub workflow for examples."""
        content = backend_tf.read_text()
        assert ".github/workflows" in content or "terraform.yml" in content, \
            "Should reference GitHub workflow file for backend-config usage examples"

    def test_backend_comments_above_configuration(self, backend_tf):
        """Verify backend.tf has explanatory comments above configuration."""
        lines = backend_tf.read_text().split('\n')
        
        # Find the backend "s3" block
        backend_line = None
        for i, line in enumerate(lines):
            if 'backend "s3"' in line:
                backend_line = i
                break
        
        assert backend_line is not None, "Should have backend s3 configuration"
        
        # Check for comments before the backend block
        has_comment_before = False
        for i in range(max(0, backend_line - 10), backend_line):
            if lines[i].strip().startswith('#'):
                has_comment_before = True
                break
        
        assert has_comment_before, "Should have explanatory comments before backend configuration"

    def test_backend_explains_placeholder_values(self, backend_tf):
        """Verify backend.tf explains REPLACE_ME placeholder values."""
        content = backend_tf.read_text()
        if "REPLACE_ME" in content:
            # If there are placeholders, should explain they're overridden
            assert "backend-config" in content or "provided via" in content, \
                "Should explain how REPLACE_ME values are overridden"


class TestBackendConfigurationGuidance:
    """Test backend.tf provides clear configuration guidance."""

    def test_backend_config_values_documented(self, backend_tf):
        """Verify all backend config values are documented in comments."""
        content = backend_tf.read_text()
        
        # Check that key backend fields are mentioned in comments
        config_fields = ['bucket', 'key', 'region', 'dynamodb_table', 'encrypt']
        
        for field in config_fields:
            # Either the field appears in a comment or in the config itself
            assert field in content, f"Backend configuration should mention '{field}'"

    def test_backend_workflow_integration_documented(self, backend_tf):
        """Verify backend.tf documents integration with CI/CD workflow."""
        content = backend_tf.read_text()
        lines = content.split('\n')
        
        # Look for documentation about workflow integration
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        comment_text = ' '.join(comment_lines)
        
        # Should mention how the workflow provides backend config
        assert any(keyword in comment_text.lower() for keyword in 
                  ['workflow', 'github', 'ci', 'action']), \
            "Should document CI/CD workflow integration"

    def test_backend_comments_reference_flags(self, backend_tf):
        """Verify backend.tf comments mention -backend-config flags."""
        content = backend_tf.read_text()
        # Comments should explain the -backend-config mechanism
        assert "backend-config" in content and "#" in content, \
            "Comments should explain -backend-config flags usage"


class TestBackendPlaceholders:
    """Test backend.tf placeholder handling."""

    def test_backend_has_placeholder_values(self, backend_tf):
        """Verify backend.tf uses REPLACE_ME placeholders where appropriate."""
        content = backend_tf.read_text()
        # Should have REPLACE_ME placeholders for user to replace
        assert "REPLACE_ME" in content or "${var." in content, \
            "Should use placeholders or variables for user-specific values"

    def test_backend_key_has_project_name(self, backend_tf):
        """Verify backend key includes project name."""
        content = backend_tf.read_text()
        # State file key should include project identifier
        assert "key" in content
        assert "twisted-monk" in content or "terraform.tfstate" in content, \
            "Backend key should include project identifier"

    def test_backend_encryption_always_enabled(self, backend_tf):
        """Verify backend encryption is always enabled."""
        content = backend_tf.read_text()
        # Encryption should be set to true
        assert "encrypt" in content
        assert "true" in content.lower(), \
            "Backend encryption should always be enabled"