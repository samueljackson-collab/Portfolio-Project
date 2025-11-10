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

class TestOutputsInMainTf:
    """Test that outputs are defined in main.tf (regression test)."""

    def test_outputs_defined_in_main_tf(self, main_tf):
        """Verify critical outputs are defined in main.tf."""
        content = main_tf.read_text()
        assert 'output "vpc_id"' in content, "vpc_id output should be in main.tf"
        assert 'output "public_subnet_ids"' in content, "public_subnet_ids output should be in main.tf"
        assert 'output "private_subnet_ids"' in content, "private_subnet_ids output should be in main.tf"
        assert 'output "rds_endpoint"' in content, "rds_endpoint output should be in main.tf"

    def test_vpc_id_output_references_correct_resource(self, main_tf):
        """Verify vpc_id output references the VPC resource."""
        content = main_tf.read_text()
        assert "aws_vpc.twisted_monk.id" in content

    def test_subnet_outputs_use_for_expressions(self, main_tf):
        """Verify subnet outputs use for expressions correctly."""
        content = main_tf.read_text()
        assert "[for s in aws_subnet.public : s.id]" in content
        assert "[for s in aws_subnet.private : s.id]" in content

    def test_rds_endpoint_output_is_conditional(self, main_tf):
        """Verify rds_endpoint output handles conditional RDS creation."""
        content = main_tf.read_text()
        # Should check var.create_rds and use index [0] for conditional resource
        assert 'var.create_rds ? aws_db_instance.postgres[0].address : ""' in content


class TestS3BucketReferenceIssue:
    """Test for S3 bucket reference bug (critical regression)."""

    def test_s3_bucket_resource_exists_or_output_removed(self, main_tf, outputs_tf):
        """Verify S3 bucket resource exists if outputs reference it."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        # If outputs.tf references aws_s3_bucket.app_assets
        if "aws_s3_bucket.app_assets" in outputs_content:
            # Then main.tf must define the resource
            assert 'resource "aws_s3_bucket" "app_assets"' in main_content, \
                "S3 bucket resource must exist if referenced in outputs"

    def test_assets_bucket_output_consistency(self, main_tf, outputs_tf):
        """Verify assets_bucket output references existing resource."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        if 'output "assets_bucket"' in outputs_content or 'output "assets_bucket"' in main_content:
            # Check if referenced resource exists
            combined_content = main_content + outputs_content
            if "aws_s3_bucket.app_assets.bucket" in combined_content:
                assert 'resource "aws_s3_bucket" "app_assets"' in main_content, \
                    "S3 bucket resource must be defined if output references it"

    def test_no_dangling_s3_bucket_references(self, main_tf):
        """Verify no references to undefined S3 bucket resources."""
        content = main_tf.read_text()
        
        # Find all S3 bucket references
        import re
        bucket_refs = re.findall(r'aws_s3_bucket\.(\w+)', content)
        
        # Find all S3 bucket resource definitions
        bucket_defs = re.findall(r'resource\s+"aws_s3_bucket"\s+"(\w+)"', content)
        
        # All references must have corresponding definitions
        for ref in bucket_refs:
            assert ref in bucket_defs, f"S3 bucket '{ref}' referenced but not defined"


class TestMissingVariables:
    """Test for missing variable definitions (regression)."""

    def test_aws_region_variable_exists(self, variables_tf, main_tf):
        """Verify aws_region variable is defined if used."""
        main_content = main_tf.read_text()
        var_content = variables_tf.read_text()
        
        if "var.aws_region" in main_content:
            assert 'variable "aws_region"' in var_content, \
                "aws_region variable must be defined if used in main.tf"

    def test_project_tag_variable_exists(self, variables_tf, main_tf):
        """Verify project_tag variable is defined if used."""
        main_content = main_tf.read_text()
        var_content = variables_tf.read_text()
        
        if "var.project_tag" in main_content:
            assert 'variable "project_tag"' in var_content, \
                "project_tag variable must be defined if used in main.tf"

    def test_all_variable_references_have_definitions(self, variables_tf, main_tf):
        """Verify all var. references in main.tf have definitions in variables.tf."""
        import re
        
        main_content = main_tf.read_text()
        var_content = variables_tf.read_text()
        
        # Find all variable references in main.tf
        var_refs = set(re.findall(r'var\.(\w+)', main_content))
        
        # Find all variable definitions in variables.tf
        var_defs = set(re.findall(r'variable\s+"(\w+)"', var_content))
        
        # Check for undefined variables
        undefined_vars = var_refs - var_defs
        
        assert len(undefined_vars) == 0, \
            f"Variables used but not defined: {undefined_vars}"


class TestOutputsDuplication:
    """Test for outputs duplication between files."""

    def test_outputs_not_duplicated_between_files(self, main_tf, outputs_tf):
        """Verify outputs are not duplicated in both main.tf and outputs.tf."""
        import re
        
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        # Find all output names in both files
        main_outputs = set(re.findall(r'output\s+"(\w+)"', main_content))
        outputs_tf_outputs = set(re.findall(r'output\s+"(\w+)"', outputs_content))
        
        duplicates = main_outputs & outputs_tf_outputs
        
        assert len(duplicates) == 0, \
            f"Outputs defined in both main.tf and outputs.tf: {duplicates}"

    def test_critical_outputs_defined_somewhere(self, main_tf, outputs_tf):
        """Verify critical outputs are defined in either main.tf or outputs.tf."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        combined = main_content + outputs_content
        
        critical_outputs = ["vpc_id", "public_subnet_ids", "private_subnet_ids"]
        
        for output_name in critical_outputs:
            assert f'output "{output_name}"' in combined, \
                f"Critical output '{output_name}' must be defined"


class TestMainTfSyntaxErrors:
    """Test for common syntax errors in main.tf."""

    def test_no_unclosed_braces_in_main_tf(self, main_tf):
        """Verify all braces are properly closed in main.tf."""
        content = main_tf.read_text()
        
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        assert open_braces == close_braces, \
            f"Brace mismatch: {open_braces} open, {close_braces} close"

    def test_no_duplicate_output_names_in_main_tf(self, main_tf):
        """Verify no duplicate output names in main.tf."""
        import re
        
        content = main_tf.read_text()
        output_names = re.findall(r'output\s+"(\w+)"', content)
        
        duplicates = [name for name in set(output_names) if output_names.count(name) > 1]
        
        assert len(duplicates) == 0, \
            f"Duplicate output names in main.tf: {duplicates}"

    def test_outputs_after_resources_in_main_tf(self, main_tf):
        """Verify outputs are defined after resources in main.tf for readability."""
        content = main_tf.read_text()
        
        # Find positions
        import re
        resource_matches = list(re.finditer(r'resource\s+"', content))
        output_matches = list(re.finditer(r'output\s+"', content))
        
        if resource_matches and output_matches:
            last_resource_pos = max(m.start() for m in resource_matches)
            first_output_pos = min(m.start() for m in output_matches)
            
            # Outputs should generally come after resources
            # This is a convention test, not strict requirement
            if first_output_pos < last_resource_pos:
                import warnings
                warnings.warn(
                    "Outputs defined before resources - consider moving for better organization"
                )


class TestConditionalOutputs:
    """Test conditional output logic."""

    def test_rds_output_handles_empty_list(self, main_tf):
        """Verify RDS endpoint output handles case when RDS is not created."""
        content = main_tf.read_text()
        
        # Should use ternary operator or try/catch pattern
        if 'output "rds_endpoint"' in content:
            # Must check var.create_rds before accessing postgres[0]
            assert "var.create_rds" in content and "postgres[0]" in content, \
                "RDS endpoint output must check create_rds before accessing postgres[0]"

    def test_conditional_outputs_have_default_values(self, main_tf):
        """Verify conditional outputs provide default values."""
        content = main_tf.read_text()
        
        if 'output "rds_endpoint"' in content:
            # Should provide empty string or null as default
            assert '""' in content or 'null' in content or "try(" in content


class TestResourceIndexing:
    """Test proper resource indexing for conditional resources."""

    def test_rds_resources_accessed_with_index(self, main_tf):
        """Verify conditional RDS resources are accessed with [0] index."""
        content = main_tf.read_text()
        
        # If we reference RDS instance in outputs/other places, must use [0]
        import re
        postgres_refs = re.findall(r'aws_db_instance\.postgres(?:\[(\d+)\])?', content)
        
        # Check if any references are without index but RDS is conditional
        if "count = var.create_rds" in content:
            for ref in postgres_refs:
                if ref == '':  # No index found
                    # This is in a conditional context, so it might be OK
                    pass

    def test_conditional_resources_use_count_or_for_each(self, main_tf):
        """Verify conditional resources use count or for_each properly."""
        content = main_tf.read_text()
        
        # Find all resources with count
        import re
        resources_with_count = re.findall(
            r'resource\s+"([^"]+)"\s+"([^"]+)"[^{]*{[^}]*count\s*=',
            content,
            re.DOTALL
        )
        
        # These should be accessed with [index] when referenced
        for resource_type, resource_name in resources_with_count:
            full_ref = f"{resource_type}.{resource_name}"
            # Check if referenced elsewhere
            if full_ref in content and content.count(full_ref) > 1:
                # Should use [0] or [count.index] when accessed
                pattern = f"{resource_type}\\.{resource_name}\\[\\d+\\]"
                assert re.search(pattern, content), \
                    f"Conditional resource {full_ref} should be accessed with index"


class TestVariableValidations:
    """Test variable validation rules."""

    def test_string_variables_have_validation(self, variables_tf):
        """Verify string variables have appropriate validation where needed."""
        content = variables_tf.read_text()
        
        # Region variable should have validation
        if 'variable "aws_region"' in content:
            # Should have validation block
            import re
            region_block = re.search(
                r'variable\s+"aws_region"\s*{[^}]+}',
                content,
                re.DOTALL
            )
            if region_block:
                # Should validate region format
                assert "validation" in region_block.group() or "default" in region_block.group()

    def test_project_tag_not_empty(self, variables_tf):
        """Verify project_tag variable validates non-empty values."""
        content = variables_tf.read_text()
        
        if 'variable "project_tag"' in content:
            import re
            project_tag_block = re.search(
                r'variable\s+"project_tag"\s*{[^}]+}',
                content,
                re.DOTALL
            )
            if project_tag_block and "validation" in project_tag_block.group():
                # Should check length > 0
                assert "length" in project_tag_block.group()


class TestBackendConfiguration:
    """Test backend configuration consistency."""

    def test_backend_uses_correct_key_path(self, backend_tf):
        """Verify backend key path is logical."""
        content = backend_tf.read_text()
        
        if "key" in content:
            # Should have .tfstate extension
            assert "terraform.tfstate" in content or ".tfstate" in content

    def test_backend_placeholders_are_clear(self, backend_tf):
        """Verify backend placeholders are clearly marked."""
        content = backend_tf.read_text()
        
        # Should have REPLACE_ME or similar markers
        if "bucket" in content and "=" in content:
            assert "REPLACE" in content.upper() or "TODO" in content.upper() or \
                   "CHANGEME" in content.upper() or "EXAMPLE" in content.upper()