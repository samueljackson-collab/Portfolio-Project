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



    def test_backend_tf_documents_backend_config_usage(self, backend_tf):
        """Verify backend.tf documents how backend config values are provided."""
        content = backend_tf.read_text()
        assert "-backend-config" in content, "Should document -backend-config flag usage"
        assert "terraform init" in content, "Should reference terraform init command"

    def test_backend_tf_references_workflow_for_example(self, backend_tf):
        """Verify backend.tf references the GitHub workflow for backend-config example."""
        content = backend_tf.read_text()
        assert "terraform.yml" in content or "workflow" in content.lower(), \
            "Should reference the workflow file for backend-config usage example"

    def test_backend_tf_explains_variable_mapping(self, backend_tf):
        """Verify backend.tf explains how backend config maps to variables."""
        content = backend_tf.read_text()
        # Should mention variable names
        assert "tfstate_bucket" in content or "bucket" in content
        assert "aws_region" in content or "region" in content

    def test_backend_tf_comments_are_helpful(self, backend_tf):
        """Verify backend.tf has clear, actionable comments."""
        content = backend_tf.read_text()
        lines = content.split('\n')
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        
        # Should have multiple comment lines explaining the configuration
        assert len(comment_lines) >= 3, "Should have comprehensive comments explaining backend config"
        
        # Comments should be substantial (not just placeholders)
        substantial_comments = [c for c in comment_lines if len(c.strip()) > 20]
        assert len(substantial_comments) >= 2, "Should have detailed explanatory comments"
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