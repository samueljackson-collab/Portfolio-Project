"""
Comprehensive tests for projects/01-sde-devops/PRJ-SDE-001/infrastructure

This test suite validates:
- Terraform configuration syntax and structure
- Module usage and integration
- Variable definitions and validation rules
- Output definitions
- CloudWatch monitoring setup
- Security group configuration
- Resource naming conventions
"""

import re
from pathlib import Path
import pytest


@pytest.fixture
def infrastructure_dir():
    """Return path to PRJ-SDE-001 infrastructure directory."""
    return Path("projects/01-sde-devops/PRJ-SDE-001/infrastructure")


@pytest.fixture
def main_tf(infrastructure_dir):
    """Return path to main.tf."""
    return infrastructure_dir / "main.tf"


@pytest.fixture
def variables_tf(infrastructure_dir):
    """Return path to variables.tf."""
    return infrastructure_dir / "variables.tf"


@pytest.fixture
def outputs_tf(infrastructure_dir):
    """Return path to outputs.tf."""
    return infrastructure_dir / "outputs.tf"


@pytest.fixture
def tfvars_example(infrastructure_dir):
    """Return path to terraform.tfvars.example."""
    return infrastructure_dir / "terraform.tfvars.example"


class TestInfrastructureDirectory:
    """Test infrastructure directory structure."""

    def test_directory_exists(self, infrastructure_dir):
        """Verify infrastructure directory exists."""
        assert infrastructure_dir.exists()
        assert infrastructure_dir.is_dir()

    def test_has_required_files(self, infrastructure_dir):
        """Verify all required Terraform files exist."""
        required_files = ["main.tf", "variables.tf", "outputs.tf", "terraform.tfvars.example"]
        for filename in required_files:
            filepath = infrastructure_dir / filename
            assert filepath.exists(), f"Missing required file: {filename}"


class TestMainTfConfiguration:
    """Test main.tf configuration."""

    def test_main_tf_exists(self, main_tf):
        """Verify main.tf exists and is readable."""
        assert main_tf.exists()
        content = main_tf.read_text()
        assert len(content) > 0

    def test_has_terraform_block(self, main_tf):
        """Verify main.tf has terraform configuration block."""
        content = main_tf.read_text()
        assert "terraform {" in content, "Should have terraform configuration block"
        assert "required_version" in content, "Should specify required Terraform version"

    def test_required_version_appropriate(self, main_tf):
        """Verify Terraform version requirement is appropriate."""
        content = main_tf.read_text()
        match = re.search(r'required_version\s*=\s*"([^"]+)"', content)
        assert match, "Should specify required_version"
        version_spec = match.group(1)
        # Should use >= 1.0 or higher
        assert ">=" in version_spec, "Should use >= for version constraint"

    def test_has_aws_provider(self, main_tf):
        """Verify AWS provider is configured."""
        content = main_tf.read_text()
        assert 'provider "aws"' in content, "Should configure AWS provider"
        assert "region" in content, "Provider should specify region"

    def test_has_required_providers_block(self, main_tf):
        """Verify required_providers block specifies AWS."""
        content = main_tf.read_text()
        assert "required_providers" in content, "Should declare required providers"
        assert "hashicorp/aws" in content or '"aws"' in content, \
               "Should specify AWS provider source"

    def test_has_backend_configuration_commented(self, main_tf):
        """Verify backend configuration is present (even if commented for examples)."""
        content = main_tf.read_text()
        assert "backend" in content.lower(), \
               "Should include backend configuration (commented or active)"

    def test_uses_data_sources_for_vpc(self, main_tf):
        """Verify configuration uses data sources appropriately."""
        content = main_tf.read_text()
        assert 'data "aws_' in content, "Should use AWS data sources"
        # For demo purposes, it might use default VPC
        assert "aws_vpc" in content or "aws_subnets" in content, \
               "Should reference VPC data sources"

    def test_has_database_module(self, main_tf):
        """Verify main.tf uses the database module."""
        content = main_tf.read_text()
        assert 'module "database"' in content, "Should define database module"
        assert "source" in content, "Module should specify source"

    def test_module_source_path_correct(self, main_tf):
        """Verify module source path is correct."""
        content = main_tf.read_text()
        match = re.search(r'module\s+"database"\s*\{[^}]*source\s*=\s*"([^"]+)"', 
                         content, re.DOTALL)
        assert match, "Database module should have source"
        source = match.group(1)
        # Should point to shared modules
        assert "modules/database" in source or "infrastructure" in source, \
               f"Module source should point to modules directory: {source}"

    def test_security_group_for_app_servers(self, main_tf):
        """Verify security group is created for application servers."""
        content = main_tf.read_text()
        assert 'resource "aws_security_group"' in content, \
               "Should create security group"
        assert "app" in content.lower(), \
               "Security group should be for application servers"

    def test_security_group_has_description(self, main_tf):
        """Verify security group has description."""
        content = main_tf.read_text()
        if 'resource "aws_security_group"' in content:
            # Extract security group block
            match = re.search(r'resource "aws_security_group"[^{]*\{([^}]+)\}', 
                            content, re.DOTALL)
            if match:
                sg_block = match.group(1)
                assert "description" in sg_block, \
                       "Security group should have description"

    def test_security_group_allows_egress(self, main_tf):
        """Verify security group allows necessary egress traffic."""
        content = main_tf.read_text()
        if "aws_security_group" in content:
            assert "egress" in content, "Security group should have egress rules"


class TestCloudWatchMonitoring:
    """Test CloudWatch monitoring configuration."""

    def test_has_cloudwatch_alarms(self, main_tf):
        """Verify CloudWatch alarms are configured."""
        content = main_tf.read_text()
        assert "aws_cloudwatch_metric_alarm" in content, \
               "Should configure CloudWatch alarms"

    def test_monitors_cpu_utilization(self, main_tf):
        """Verify CPU utilization monitoring is configured."""
        content = main_tf.read_text()
        if "cloudwatch" in content:
            assert "CPUUtilization" in content or "cpu" in content.lower(), \
                   "Should monitor CPU utilization"

    def test_monitors_storage_space(self, main_tf):
        """Verify storage space monitoring is configured."""
        content = main_tf.read_text()
        if "cloudwatch" in content:
            assert "storage" in content.lower() or "FreeStorageSpace" in content, \
                   "Should monitor storage space"

    def test_monitors_database_connections(self, main_tf):
        """Verify database connections monitoring is configured."""
        content = main_tf.read_text()
        if "cloudwatch" in content:
            assert "connection" in content.lower() or "DatabaseConnections" in content, \
                   "Should monitor database connections"

    def test_alarms_have_descriptions(self, main_tf):
        """Verify CloudWatch alarms have descriptions."""
        content = main_tf.read_text()
        if "aws_cloudwatch_metric_alarm" in content:
            # Count alarm resources
            alarm_count = content.count('resource "aws_cloudwatch_metric_alarm"')
            description_count = content.count("alarm_description")
            assert description_count >= alarm_count, \
                   "All CloudWatch alarms should have descriptions"

    def test_alarm_thresholds_are_reasonable(self, main_tf):
        """Verify alarm thresholds are set to reasonable values."""
        content = main_tf.read_text()
        
        # Check CPU threshold (should be 70-90%)
        cpu_match = re.search(r'CPUUtilization.*?threshold\s*=\s*(\d+)', 
                             content, re.DOTALL)
        if cpu_match:
            threshold = int(cpu_match.group(1))
            assert 70 <= threshold <= 95, \
                   f"CPU threshold should be 70-95%, got {threshold}%"


class TestVariablesConfiguration:
    """Test variables.tf configuration."""

    def test_variables_tf_exists(self, variables_tf):
        """Verify variables.tf exists."""
        assert variables_tf.exists()

    def test_has_region_variable(self, variables_tf):
        """Verify aws_region variable is defined."""
        content = variables_tf.read_text()
        assert 'variable "aws_region"' in content, \
               "Should define aws_region variable"

    def test_has_project_name_variable(self, variables_tf):
        """Verify project_name variable is defined."""
        content = variables_tf.read_text()
        assert 'variable "project_name"' in content, \
               "Should define project_name variable"

    def test_has_environment_variable(self, variables_tf):
        """Verify environment variable is defined."""
        content = variables_tf.read_text()
        assert 'variable "environment"' in content, \
               "Should define environment variable"

    def test_environment_has_validation(self, variables_tf):
        """Verify environment variable has validation rule."""
        content = variables_tf.read_text()
        if 'variable "environment"' in content:
            # Extract environment variable block
            match = re.search(r'variable "environment"[^{]*\{([^}]+)\}', 
                            content, re.DOTALL)
            if match:
                env_block = match.group(1)
                assert "validation" in env_block, \
                       "environment variable should have validation rule"
                assert "contains" in env_block, \
                       "Should validate against allowed values"

    def test_has_database_variables(self, variables_tf):
        """Verify database configuration variables are defined."""
        content = variables_tf.read_text()
        required_db_vars = ["db_username", "db_password", "db_instance_class"]
        for var in required_db_vars:
            assert f'variable "{var}"' in content, \
                   f"Should define {var} variable"

    def test_sensitive_variables_marked(self, variables_tf):
        """Verify sensitive variables are marked as sensitive."""
        content = variables_tf.read_text()
        
        # Check db_username
        username_match = re.search(r'variable "db_username"[^}]+', 
                                  content, re.DOTALL)
        if username_match:
            assert "sensitive" in username_match.group(0).lower(), \
                   "db_username should be marked sensitive"
        
        # Check db_password
        password_match = re.search(r'variable "db_password"[^}]+', 
                                  content, re.DOTALL)
        if password_match:
            assert "sensitive" in password_match.group(0).lower(), \
                   "db_password should be marked sensitive"

    def test_password_has_length_validation(self, variables_tf):
        """Verify db_password has minimum length validation."""
        content = variables_tf.read_text()
        password_match = re.search(r'variable "db_password"[^}]+\}', 
                                  content, re.DOTALL)
        if password_match:
            password_block = password_match.group(0)
            assert "validation" in password_block, \
                   "db_password should have validation"
            assert "length" in password_block, \
                   "Should validate password length"

    def test_storage_variables_have_validation(self, variables_tf):
        """Verify storage variables have appropriate validation."""
        content = variables_tf.read_text()
        
        storage_vars = ["db_allocated_storage", "db_max_allocated_storage"]
        for var in storage_vars:
            if f'variable "{var}"' in content:
                var_match = re.search(f'variable "{var}"[^}}]+}}', 
                                    content, re.DOTALL)
                if var_match:
                    var_block = var_match.group(0)
                    assert "validation" in var_block, \
                           f"{var} should have validation rule"

    def test_backup_retention_has_validation(self, variables_tf):
        """Verify backup retention period has validation."""
        content = variables_tf.read_text()
        if 'variable "db_backup_retention_days"' in content:
            retention_match = re.search(
                r'variable "db_backup_retention_days"[^}]+\}', 
                content, re.DOTALL
            )
            if retention_match:
                retention_block = retention_match.group(0)
                assert "validation" in retention_block, \
                       "backup_retention_days should have validation"

    def test_variables_have_descriptions(self, variables_tf):
        """Verify all variables have descriptions."""
        content = variables_tf.read_text()
        variable_count = content.count('variable "')
        description_count = content.count('description =')
        
        # All variables should have descriptions
        assert description_count == variable_count, \
               f"All variables should have descriptions ({description_count}/{variable_count})"

    def test_variables_have_types(self, variables_tf):
        """Verify variables specify types."""
        content = variables_tf.read_text()
        variable_count = content.count('variable "')
        type_count = content.count('type =')
        
        # All variables should have types
        assert type_count == variable_count, \
               f"All variables should have types ({type_count}/{variable_count})"

    def test_boolean_variables_have_defaults(self, variables_tf):
        """Verify boolean variables have sensible defaults."""
        content = variables_tf.read_text()
        
        bool_vars = ["db_multi_az", "db_deletion_protection", 
                    "db_skip_final_snapshot", "db_apply_immediately"]
        
        for bool_var in bool_vars:
            if f'variable "{bool_var}"' in content:
                var_match = re.search(f'variable "{bool_var}"[^}}]+}}', 
                                    content, re.DOTALL)
                if var_match:
                    var_block = var_match.group(0)
                    assert "default" in var_block, \
                           f"{bool_var} should have a default value"


class TestOutputsConfiguration:
    """Test outputs.tf configuration."""

    def test_outputs_tf_exists(self, outputs_tf):
        """Verify outputs.tf exists."""
        assert outputs_tf.exists()

    def test_outputs_database_endpoint(self, outputs_tf):
        """Verify database endpoint is output."""
        content = outputs_tf.read_text()
        assert 'output "database_endpoint"' in content or \
               "db_endpoint" in content, \
               "Should output database endpoint"

    def test_outputs_security_group_id(self, outputs_tf):
        """Verify security group ID is output."""
        content = outputs_tf.read_text()
        assert "security_group" in content.lower(), \
               "Should output security group IDs"

    def test_outputs_have_descriptions(self, outputs_tf):
        """Verify all outputs have descriptions."""
        content = outputs_tf.read_text()
        output_count = content.count('output "')
        description_count = content.count('description =')
        
        # Most outputs should have descriptions
        assert description_count >= output_count * 0.9, \
               f"Most outputs should have descriptions ({description_count}/{output_count})"

    def test_has_connection_string_output(self, outputs_tf):
        """Verify connection string is provided as output."""
        content = outputs_tf.read_text()
        assert "connection" in content.lower() or "postgresql://" in content, \
               "Should provide connection string in outputs"

    def test_connection_string_excludes_password(self, outputs_tf):
        """Verify connection string doesn't expose actual password."""
        content = outputs_tf.read_text()
        if "postgresql://" in content:
            # Should have placeholder for password, not actual value
            assert "PASSWORD" in content or "xxx" in content.lower(), \
                   "Connection string should use password placeholder"

    def test_has_next_steps_output(self, outputs_tf):
        """Verify helpful next steps are provided in outputs."""
        content = outputs_tf.read_text()
        assert "next_steps" in content.lower() or "next" in content.lower(), \
               "Should provide next steps guidance in outputs"

    def test_outputs_cloudwatch_alarms(self, outputs_tf):
        """Verify CloudWatch alarm information is output."""
        content = outputs_tf.read_text()
        if "cloudwatch" in content.lower():
            assert "alarm" in content.lower(), \
                   "Should output CloudWatch alarm information"


class TestResourceNaming:
    """Test resource naming conventions."""

    def test_resources_use_consistent_naming(self, main_tf):
        """Verify resources follow consistent naming pattern."""
        content = main_tf.read_text()
        
        # Should use project_name and environment in names
        if "project_name" in content and "environment" in content:
            # Resources should interpolate these variables
            assert "${var.project_name}" in content or "var.project_name" in content, \
                   "Should use project_name variable in resource names"

    def test_resources_have_name_tags(self, main_tf):
        """Verify resources are tagged with Name."""
        content = main_tf.read_text()
        
        # Find resource blocks
        resource_count = content.count('resource "aws_')
        name_tag_count = content.count('Name =')
        
        # Most resources should have Name tags
        if resource_count > 0:
            assert name_tag_count >= resource_count * 0.7, \
                   "Most resources should have Name tags"


class TestTfvarsExample:
    """Test terraform.tfvars.example file."""

    def test_tfvars_example_exists(self, tfvars_example):
        """Verify terraform.tfvars.example exists."""
        assert tfvars_example.exists()

    def test_matches_variable_definitions(self, variables_tf, tfvars_example):
        """Verify example file covers variables from variables.tf."""
        var_content = variables_tf.read_text()
        tfvars_content = tfvars_example.read_text()
        
        # Extract variable names from variables.tf
        variables = re.findall(r'variable "([^"]+)"', var_content)
        
        # Check that required variables (no defaults) are in example
        required_vars = ["project_name", "db_username", "db_password"]
        for var in required_vars:
            if var in variables:
                assert var in tfvars_content, \
                       f"Example file should include {var}"

    def test_has_example_values(self, tfvars_example):
        """Verify example file has actual example values."""
        content = tfvars_example.read_text()
        
        # Should have actual assignments
        assignment_count = content.count('=')
        assert assignment_count >= 5, \
               "Example file should have multiple variable assignments"


class TestSecurityPractices:
    """Test security best practices."""

    def test_default_tags_applied(self, main_tf):
        """Verify provider has default tags configuration."""
        content = main_tf.read_text()
        if 'provider "aws"' in content:
            assert "default_tags" in content or "tags" in content, \
                   "Provider should configure default tags"

    def test_uses_data_sources_not_hardcoded_ids(self, main_tf):
        """Verify configuration uses data sources instead of hardcoded IDs."""
        content = main_tf.read_text()
        
        # Should use data sources
        assert 'data "aws_' in content, "Should use data sources"
        
        # Should not have hardcoded AWS resource IDs in main logic
        # (comments and examples are okay)
        lines = [line for line in content.split('\n') 
                if not line.strip().startswith('#')]
        code_content = '\n'.join(lines)
        
        # Allow placeholder patterns like vpc-xxxxx
        real_vpc_pattern = r'vpc-[a-f0-9]{17}(?!x)'
        real_subnet_pattern = r'subnet-[a-f0-9]{17}(?!x)'
        
        assert not re.search(real_vpc_pattern, code_content), \
               "Should not hardcode real VPC IDs"
        assert not re.search(real_subnet_pattern, code_content), \
               "Should not hardcode real subnet IDs"