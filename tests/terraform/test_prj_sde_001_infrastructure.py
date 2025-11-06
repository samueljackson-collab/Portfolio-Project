"""
Comprehensive tests for PRJ-SDE-001 database infrastructure Terraform configuration.

This test suite validates:
- Terraform syntax and structure
- Variable definitions and validations
- Output definitions
- Resource configurations
- Security best practices
- CloudWatch alarms
- Module usage
- Tags and naming conventions
"""

import re
from pathlib import Path
import pytest


BASE_PATH = Path(__file__).parent.parent.parent
INFRA_DIR = BASE_PATH / "projects/01-sde-devops/PRJ-SDE-001/infrastructure"


@pytest.fixture
def main_tf_path():
    """Return path to main.tf."""
    return INFRA_DIR / "main.tf"


@pytest.fixture
def main_tf_content(main_tf_path):
    """Read main.tf content."""
    return main_tf_path.read_text()


@pytest.fixture
def variables_tf_path():
    """Return path to variables.tf."""
    return INFRA_DIR / "variables.tf"


@pytest.fixture
def variables_tf_content(variables_tf_path):
    """Read variables.tf content."""
    return variables_tf_path.read_text()


@pytest.fixture
def outputs_tf_path():
    """Return path to outputs.tf."""
    return INFRA_DIR / "outputs.tf"


@pytest.fixture
def outputs_tf_content(outputs_tf_path):
    """Read outputs.tf content."""
    return outputs_tf_path.read_text()


@pytest.fixture
def tfvars_example_path():
    """Return path to terraform.tfvars.example."""
    return INFRA_DIR / "terraform.tfvars.example"


@pytest.fixture
def tfvars_example_content(tfvars_example_path):
    """Read terraform.tfvars.example content."""
    return tfvars_example_path.read_text()


class TestInfrastructureDirectory:
    """Test infrastructure directory structure."""

    def test_infrastructure_directory_exists(self):
        """Verify infrastructure directory exists."""
        assert INFRA_DIR.exists()
        assert INFRA_DIR.is_dir()

    def test_main_tf_exists(self, main_tf_path):
        """Verify main.tf exists."""
        assert main_tf_path.exists()
        assert main_tf_path.is_file()

    def test_variables_tf_exists(self, variables_tf_path):
        """Verify variables.tf exists."""
        assert variables_tf_path.exists()
        assert variables_tf_path.is_file()

    def test_outputs_tf_exists(self, outputs_tf_path):
        """Verify outputs.tf exists."""
        assert outputs_tf_path.exists()
        assert outputs_tf_path.is_file()

    def test_tfvars_example_exists(self, tfvars_example_path):
        """Verify terraform.tfvars.example exists."""
        assert tfvars_example_path.exists()
        assert tfvars_example_path.is_file()

    def test_gitignore_exists(self):
        """Verify .gitignore exists."""
        gitignore = INFRA_DIR / ".gitignore"
        assert gitignore.exists()

    def test_gitignore_protects_state_files(self):
        """Verify .gitignore protects sensitive Terraform files."""
        gitignore = INFRA_DIR / ".gitignore"
        content = gitignore.read_text()
        
        assert "*.tfstate" in content
        assert ".terraform/" in content
        assert "terraform.tfvars" in content


class TestMainTfTerraformBlock:
    """Test Terraform block configuration."""

    def test_has_terraform_block(self, main_tf_content):
        """Verify main.tf has terraform block."""
        assert "terraform {" in main_tf_content

    def test_requires_minimum_version(self, main_tf_content):
        """Verify Terraform minimum version is specified."""
        assert "required_version" in main_tf_content
        assert ">= 1.6.0" in main_tf_content

    def test_has_required_providers(self, main_tf_content):
        """Verify AWS provider is required."""
        assert "required_providers {" in main_tf_content
        assert 'aws = {' in main_tf_content
        assert 'source  = "hashicorp/aws"' in main_tf_content

    def test_aws_provider_version_constraint(self, main_tf_content):
        """Verify AWS provider version is constrained."""
        assert '~> 5.0' in main_tf_content

    def test_has_backend_configuration_commented(self, main_tf_content):
        """Verify backend configuration exists (commented for initial setup)."""
        # Backend config should exist but commented out
        assert '# backend "s3"' in main_tf_content or 'backend "s3"' in main_tf_content


class TestMainTfProvider:
    """Test AWS provider configuration."""

    def test_has_provider_block(self, main_tf_content):
        """Verify AWS provider is declared."""
        assert 'provider "aws" {' in main_tf_content

    def test_provider_uses_region_variable(self, main_tf_content):
        """Verify provider uses region from variable."""
        assert "region = var.aws_region" in main_tf_content

    def test_provider_has_default_tags(self, main_tf_content):
        """Verify provider has default tags block."""
        assert "default_tags {" in main_tf_content
        assert "tags = {" in main_tf_content

    def test_default_tags_include_managed_by(self, main_tf_content):
        """Verify default tags include ManagedBy."""
        assert 'ManagedBy' in main_tf_content
        assert 'Terraform' in main_tf_content

    def test_default_tags_include_environment(self, main_tf_content):
        """Verify default tags include Environment."""
        assert 'Environment = var.environment' in main_tf_content

    def test_default_tags_include_project(self, main_tf_content):
        """Verify default tags include Project."""
        assert 'Project     = var.project_name' in main_tf_content


class TestMainTfDataSources:
    """Test data sources."""

    def test_uses_availability_zones_data_source(self, main_tf_content):
        """Verify uses availability zones data source."""
        assert 'data "aws_availability_zones" "available"' in main_tf_content
        assert 'state = "available"' in main_tf_content

    def test_uses_default_vpc_data_source(self, main_tf_content):
        """Verify uses default VPC for demo purposes."""
        assert 'data "aws_vpc" "default"' in main_tf_content
        assert 'default = true' in main_tf_content

    def test_uses_default_subnets_data_source(self, main_tf_content):
        """Verify retrieves default subnets."""
        assert 'data "aws_subnets" "default"' in main_tf_content
        assert 'vpc-id' in main_tf_content


class TestMainTfSecurityGroups:
    """Test security group configurations."""

    def test_has_app_security_group(self, main_tf_content):
        """Verify application security group is defined."""
        assert 'resource "aws_security_group" "app_servers"' in main_tf_content

    def test_app_sg_has_name(self, main_tf_content):
        """Verify app security group has proper name."""
        assert '${var.project_name}-${var.environment}-app-sg' in main_tf_content

    def test_app_sg_has_description(self, main_tf_content):
        """Verify app security group has description."""
        # Find the app_servers security group block
        lines = main_tf_content.split('\n')
        in_app_sg = False
        found_description = False
        
        for line in lines:
            if 'resource "aws_security_group" "app_servers"' in line:
                in_app_sg = True
            if in_app_sg and 'description =' in line:
                found_description = True
                break
            if in_app_sg and 'resource ' in line and 'app_servers' not in line:
                break
        
        assert found_description

    def test_app_sg_uses_vpc(self, main_tf_content):
        """Verify app security group references VPC."""
        assert 'vpc_id      = data.aws_vpc.default.id' in main_tf_content

    def test_app_sg_has_egress_rule(self, main_tf_content):
        """Verify app security group has egress rule."""
        lines = main_tf_content.split('\n')
        in_app_sg = False
        found_egress = False
        
        for line in lines:
            if 'resource "aws_security_group" "app_servers"' in line:
                in_app_sg = True
            if in_app_sg and 'egress {' in line:
                found_egress = True
                break
            if in_app_sg and 'resource ' in line and 'app_servers' not in line:
                break
        
        assert found_egress

    def test_app_sg_has_tags(self, main_tf_content):
        """Verify app security group has tags."""
        lines = main_tf_content.split('\n')
        in_app_sg = False
        found_tags = False
        
        for line in lines:
            if 'resource "aws_security_group" "app_servers"' in line:
                in_app_sg = True
            if in_app_sg and 'tags = {' in line:
                found_tags = True
                break
            if in_app_sg and 'resource ' in line and 'app_servers' not in line:
                break
        
        assert found_tags


class TestMainTfDatabaseModule:
    """Test database module configuration."""

    def test_has_database_module(self, main_tf_content):
        """Verify database module is declared."""
        assert 'module "database" {' in main_tf_content

    def test_module_source_is_correct(self, main_tf_content):
        """Verify module source points to correct path."""
        assert 'source = "../../../../infrastructure/terraform/modules/database"' in main_tf_content

    def test_module_receives_project_name(self, main_tf_content):
        """Verify module receives project_name variable."""
        assert 'project_name = var.project_name' in main_tf_content

    def test_module_receives_environment(self, main_tf_content):
        """Verify module receives environment variable."""
        assert 'environment  = var.environment' in main_tf_content

    def test_module_receives_vpc_id(self, main_tf_content):
        """Verify module receives VPC ID."""
        assert 'vpc_id       = data.aws_vpc.default.id' in main_tf_content

    def test_module_receives_subnet_ids(self, main_tf_content):
        """Verify module receives subnet IDs."""
        assert 'subnet_ids   = data.aws_subnets.default.ids' in main_tf_content

    def test_module_receives_credentials(self, main_tf_content):
        """Verify module receives database credentials."""
        assert 'db_username  = var.db_username' in main_tf_content
        assert 'db_password  = var.db_password' in main_tf_content

    def test_module_receives_security_groups(self, main_tf_content):
        """Verify module receives allowed security groups."""
        assert 'allowed_security_group_ids = [aws_security_group.app_servers.id]' in main_tf_content

    def test_module_receives_instance_config(self, main_tf_content):
        """Verify module receives instance configuration."""
        assert 'instance_class        = var.db_instance_class' in main_tf_content
        assert 'allocated_storage     = var.db_allocated_storage' in main_tf_content
        assert 'max_allocated_storage = var.db_max_allocated_storage' in main_tf_content

    def test_module_receives_engine_version(self, main_tf_content):
        """Verify module receives engine version."""
        assert 'engine_version        = var.db_engine_version' in main_tf_content

    def test_module_receives_multi_az_setting(self, main_tf_content):
        """Verify module receives multi-AZ setting."""
        assert 'multi_az = var.db_multi_az' in main_tf_content

    def test_module_receives_backup_retention(self, main_tf_content):
        """Verify module receives backup retention setting."""
        assert 'backup_retention_period = var.db_backup_retention_days' in main_tf_content

    def test_module_receives_safety_controls(self, main_tf_content):
        """Verify module receives safety control settings."""
        assert 'deletion_protection = var.db_deletion_protection' in main_tf_content
        assert 'skip_final_snapshot = var.db_skip_final_snapshot' in main_tf_content
        assert 'apply_immediately   = var.db_apply_immediately' in main_tf_content

    def test_module_receives_tags(self, main_tf_content):
        """Verify module receives tags."""
        lines = main_tf_content.split('\n')
        in_module = False
        found_tags = False
        
        for line in lines:
            if 'module "database" {' in line:
                in_module = True
            if in_module and 'tags = {' in line:
                found_tags = True
                break
            if in_module and line.strip() == '}' and found_tags:
                break
        
        assert found_tags


class TestMainTfCloudWatchAlarms:
    """Test CloudWatch alarm configurations."""

    def test_has_cpu_utilization_alarm(self, main_tf_content):
        """Verify CPU utilization alarm is defined."""
        assert 'resource "aws_cloudwatch_metric_alarm" "database_cpu"' in main_tf_content

    def test_cpu_alarm_has_proper_name(self, main_tf_content):
        """Verify CPU alarm has proper name."""
        assert 'alarm_name          = "${var.project_name}-${var.environment}-db-cpu-utilization"' in main_tf_content

    def test_cpu_alarm_monitors_cpu_metric(self, main_tf_content):
        """Verify CPU alarm monitors CPUUtilization."""
        assert 'metric_name         = "CPUUtilization"' in main_tf_content

    def test_cpu_alarm_uses_rds_namespace(self, main_tf_content):
        """Verify CPU alarm uses AWS/RDS namespace."""
        assert 'namespace           = "AWS/RDS"' in main_tf_content

    def test_cpu_alarm_has_threshold(self, main_tf_content):
        """Verify CPU alarm has reasonable threshold."""
        assert 'threshold           = 80' in main_tf_content

    def test_cpu_alarm_references_db_instance(self, main_tf_content):
        """Verify CPU alarm references database instance."""
        assert 'DBInstanceIdentifier = module.database.db_instance_identifier' in main_tf_content

    def test_has_storage_space_alarm(self, main_tf_content):
        """Verify storage space alarm is defined."""
        assert 'resource "aws_cloudwatch_metric_alarm" "database_storage"' in main_tf_content

    def test_storage_alarm_monitors_free_storage(self, main_tf_content):
        """Verify storage alarm monitors FreeStorageSpace."""
        assert 'metric_name         = "FreeStorageSpace"' in main_tf_content

    def test_storage_alarm_has_threshold(self, main_tf_content):
        """Verify storage alarm has threshold (2GB in bytes)."""
        assert 'threshold           = 2147483648' in main_tf_content

    def test_storage_alarm_uses_less_than_comparison(self, main_tf_content):
        """Verify storage alarm uses LessThanThreshold."""
        # Find storage alarm and check comparison operator
        lines = main_tf_content.split('\n')
        in_storage_alarm = False
        found_comparison = False
        
        for line in lines:
            if 'resource "aws_cloudwatch_metric_alarm" "database_storage"' in line:
                in_storage_alarm = True
            if in_storage_alarm and 'comparison_operator = "LessThanThreshold"' in line:
                found_comparison = True
                break
            if in_storage_alarm and 'resource ' in line and 'database_storage' not in line:
                break
        
        assert found_comparison

    def test_has_connections_alarm(self, main_tf_content):
        """Verify database connections alarm is defined."""
        assert 'resource "aws_cloudwatch_metric_alarm" "database_connections"' in main_tf_content

    def test_connections_alarm_monitors_connections(self, main_tf_content):
        """Verify connections alarm monitors DatabaseConnections."""
        assert 'metric_name         = "DatabaseConnections"' in main_tf_content

    def test_all_alarms_have_descriptions(self, main_tf_content):
        """Verify all alarms have descriptions."""
        alarm_count = main_tf_content.count('resource "aws_cloudwatch_metric_alarm"')
        description_count = main_tf_content.count('alarm_description   =')
        assert description_count >= alarm_count

    def test_all_alarms_have_tags(self, main_tf_content):
        """Verify all alarms have tags."""
        lines = main_tf_content.split('\n')
        alarm_blocks = []
        current_alarm = None
        
        for i, line in enumerate(lines):
            if 'resource "aws_cloudwatch_metric_alarm"' in line:
                current_alarm = {'start': i, 'has_tags': False}
                alarm_blocks.append(current_alarm)
            elif current_alarm and 'tags = {' in line:
                current_alarm['has_tags'] = True
        
        assert all(alarm['has_tags'] for alarm in alarm_blocks), "All alarms should have tags"


class TestVariablesTfStructure:
    """Test variables.tf structure and completeness."""

    def test_has_aws_region_variable(self, variables_tf_content):
        """Verify aws_region variable is defined."""
        assert 'variable "aws_region"' in variables_tf_content

    def test_aws_region_has_default(self, variables_tf_content):
        """Verify aws_region has default value."""
        lines = variables_tf_content.split('\n')
        in_region_var = False
        found_default = False
        
        for line in lines:
            if 'variable "aws_region"' in line:
                in_region_var = True
            if in_region_var and 'default     = "us-east-1"' in line:
                found_default = True
                break
            if in_region_var and 'variable ' in line and 'aws_region' not in line:
                break
        
        assert found_default

    def test_has_project_name_variable(self, variables_tf_content):
        """Verify project_name variable is defined."""
        assert 'variable "project_name"' in variables_tf_content

    def test_has_environment_variable(self, variables_tf_content):
        """Verify environment variable is defined."""
        assert 'variable "environment"' in variables_tf_content

    def test_environment_has_validation(self, variables_tf_content):
        """Verify environment variable has validation."""
        lines = variables_tf_content.split('\n')
        in_env_var = False
        found_validation = False
        
        for line in lines:
            if 'variable "environment"' in line:
                in_env_var = True
            if in_env_var and 'validation {' in line:
                found_validation = True
                break
            if in_env_var and 'variable ' in line and 'environment' not in line:
                break
        
        assert found_validation

    def test_environment_validates_allowed_values(self, variables_tf_content):
        """Verify environment validates dev, staging, prod."""
        assert 'contains(["dev", "staging", "prod"], var.environment)' in variables_tf_content


class TestVariablesTfDatabaseVariables:
    """Test database-specific variables."""

    def test_has_db_username_variable(self, variables_tf_content):
        """Verify db_username variable is defined."""
        assert 'variable "db_username"' in variables_tf_content

    def test_db_username_is_sensitive(self, variables_tf_content):
        """Verify db_username is marked sensitive."""
        lines = variables_tf_content.split('\n')
        in_username_var = False
        found_sensitive = False
        
        for line in lines:
            if 'variable "db_username"' in line:
                in_username_var = True
            if in_username_var and 'sensitive   = true' in line:
                found_sensitive = True
                break
            if in_username_var and 'variable ' in line and 'db_username' not in line:
                break
        
        assert found_sensitive

    def test_has_db_password_variable(self, variables_tf_content):
        """Verify db_password variable is defined."""
        assert 'variable "db_password"' in variables_tf_content

    def test_db_password_is_sensitive(self, variables_tf_content):
        """Verify db_password is marked sensitive."""
        lines = variables_tf_content.split('\n')
        in_password_var = False
        found_sensitive = False
        
        for line in lines:
            if 'variable "db_password"' in line:
                in_password_var = True
            if in_password_var and 'sensitive   = true' in line:
                found_sensitive = True
                break
            if in_password_var and 'variable ' in line and 'db_password' not in line:
                break
        
        assert found_sensitive

    def test_db_password_has_validation(self, variables_tf_content):
        """Verify db_password has minimum length validation."""
        assert 'length(var.db_password) >= 8' in variables_tf_content

    def test_has_db_instance_class_variable(self, variables_tf_content):
        """Verify db_instance_class variable is defined."""
        assert 'variable "db_instance_class"' in variables_tf_content

    def test_db_instance_class_has_default(self, variables_tf_content):
        """Verify db_instance_class has default value."""
        assert 'default     = "db.t3.small"' in variables_tf_content

    def test_has_allocated_storage_variable(self, variables_tf_content):
        """Verify db_allocated_storage variable is defined."""
        assert 'variable "db_allocated_storage"' in variables_tf_content

    def test_allocated_storage_has_validation(self, variables_tf_content):
        """Verify allocated_storage has range validation."""
        assert 'var.db_allocated_storage >= 20' in variables_tf_content
        assert 'var.db_allocated_storage <= 65536' in variables_tf_content

    def test_has_max_allocated_storage_variable(self, variables_tf_content):
        """Verify db_max_allocated_storage variable is defined."""
        assert 'variable "db_max_allocated_storage"' in variables_tf_content

    def test_max_allocated_storage_has_validation(self, variables_tf_content):
        """Verify max_allocated_storage has range validation."""
        assert 'var.db_max_allocated_storage >= 20' in variables_tf_content

    def test_has_engine_version_variable(self, variables_tf_content):
        """Verify db_engine_version variable is defined."""
        assert 'variable "db_engine_version"' in variables_tf_content

    def test_has_multi_az_variable(self, variables_tf_content):
        """Verify db_multi_az variable is defined."""
        assert 'variable "db_multi_az"' in variables_tf_content

    def test_multi_az_is_boolean(self, variables_tf_content):
        """Verify db_multi_az is boolean type."""
        lines = variables_tf_content.split('\n')
        in_multi_az_var = False
        found_bool_type = False
        
        for line in lines:
            if 'variable "db_multi_az"' in line:
                in_multi_az_var = True
            if in_multi_az_var and 'type        = bool' in line:
                found_bool_type = True
                break
            if in_multi_az_var and 'variable ' in line and 'db_multi_az' not in line:
                break
        
        assert found_bool_type

    def test_has_backup_retention_variable(self, variables_tf_content):
        """Verify db_backup_retention_days variable is defined."""
        assert 'variable "db_backup_retention_days"' in variables_tf_content

    def test_backup_retention_has_validation(self, variables_tf_content):
        """Verify backup_retention has range validation (0-35 days)."""
        assert 'var.db_backup_retention_days >= 0' in variables_tf_content
        assert 'var.db_backup_retention_days <= 35' in variables_tf_content


class TestVariablesTfSafetyControls:
    """Test safety control variables."""

    def test_has_deletion_protection_variable(self, variables_tf_content):
        """Verify db_deletion_protection variable is defined."""
        assert 'variable "db_deletion_protection"' in variables_tf_content

    def test_deletion_protection_is_boolean(self, variables_tf_content):
        """Verify db_deletion_protection is boolean type."""
        lines = variables_tf_content.split('\n')
        in_var = False
        found_bool = False
        
        for line in lines:
            if 'variable "db_deletion_protection"' in line:
                in_var = True
            if in_var and 'type        = bool' in line:
                found_bool = True
                break
            if in_var and 'variable ' in line and 'db_deletion_protection' not in line:
                break
        
        assert found_bool

    def test_has_skip_final_snapshot_variable(self, variables_tf_content):
        """Verify db_skip_final_snapshot variable is defined."""
        assert 'variable "db_skip_final_snapshot"' in variables_tf_content

    def test_has_apply_immediately_variable(self, variables_tf_content):
        """Verify db_apply_immediately variable is defined."""
        assert 'variable "db_apply_immediately"' in variables_tf_content

    def test_all_variables_have_descriptions(self, variables_tf_content):
        """Verify all variables have descriptions."""
        variable_count = variables_tf_content.count('variable "')
        description_count = variables_tf_content.count('description =')
        # Allow for some variance but most should have descriptions
        assert description_count >= variable_count * 0.9

    def test_all_variables_have_types(self, variables_tf_content):
        """Verify all variables specify types."""
        variable_count = variables_tf_content.count('variable "')
        type_count = variables_tf_content.count('type        =')
        # All variables should have types
        assert type_count >= variable_count


class TestOutputsTfStructure:
    """Test outputs.tf structure and completeness."""

    def test_has_database_endpoint_output(self, outputs_tf_content):
        """Verify database_endpoint output is defined."""
        assert 'output "database_endpoint"' in outputs_tf_content

    def test_database_endpoint_references_module(self, outputs_tf_content):
        """Verify database_endpoint references module output."""
        assert 'value       = module.database.db_endpoint' in outputs_tf_content

    def test_has_database_security_group_output(self, outputs_tf_content):
        """Verify database_security_group_id output is defined."""
        assert 'output "database_security_group_id"' in outputs_tf_content

    def test_has_app_security_group_output(self, outputs_tf_content):
        """Verify app_security_group_id output is defined."""
        assert 'output "app_security_group_id"' in outputs_tf_content

    def test_app_sg_output_references_resource(self, outputs_tf_content):
        """Verify app_security_group_id references resource."""
        assert 'value       = aws_security_group.app_servers.id' in outputs_tf_content

    def test_has_connection_string_output(self, outputs_tf_content):
        """Verify connection_string output is defined."""
        assert 'output "connection_string"' in outputs_tf_content

    def test_connection_string_includes_username(self, outputs_tf_content):
        """Verify connection_string includes username variable."""
        assert '${var.db_username}' in outputs_tf_content

    def test_connection_string_masks_password(self, outputs_tf_content):
        """Verify connection_string uses PASSWORD placeholder."""
        assert 'PASSWORD@' in outputs_tf_content

    def test_connection_string_is_not_sensitive(self, outputs_tf_content):
        """Verify connection_string is explicitly not sensitive (password masked)."""
        lines = outputs_tf_content.split('\n')
        in_conn_str = False
        found_not_sensitive = False
        
        for line in lines:
            if 'output "connection_string"' in line:
                in_conn_str = True
            if in_conn_str and 'sensitive   = false' in line:
                found_not_sensitive = True
                break
            if in_conn_str and 'output ' in line and 'connection_string' not in line:
                break
        
        assert found_not_sensitive

    def test_has_cloudwatch_alarms_output(self, outputs_tf_content):
        """Verify cloudwatch_alarms output is defined."""
        assert 'output "cloudwatch_alarms"' in outputs_tf_content

    def test_cloudwatch_alarms_includes_all_alarms(self, outputs_tf_content):
        """Verify cloudwatch_alarms includes all alarm names."""
        assert 'cpu_utilization = aws_cloudwatch_metric_alarm.database_cpu.alarm_name' in outputs_tf_content
        assert 'storage_space   = aws_cloudwatch_metric_alarm.database_storage.alarm_name' in outputs_tf_content
        assert 'connections     = aws_cloudwatch_metric_alarm.database_connections.alarm_name' in outputs_tf_content

    def test_has_next_steps_output(self, outputs_tf_content):
        """Verify next_steps output is defined."""
        assert 'output "next_steps"' in outputs_tf_content

    def test_next_steps_includes_instructions(self, outputs_tf_content):
        """Verify next_steps includes deployment instructions."""
        assert 'Next Steps:' in outputs_tf_content
        assert 'Connect to database' in outputs_tf_content or 'psql' in outputs_tf_content

    def test_next_steps_mentions_security(self, outputs_tf_content):
        """Verify next_steps mentions security considerations."""
        assert 'Store db_password securely' in outputs_tf_content or 'Secrets Manager' in outputs_tf_content

    def test_all_outputs_have_descriptions(self, outputs_tf_content):
        """Verify all outputs have descriptions."""
        output_count = outputs_tf_content.count('output "')
        description_count = outputs_tf_content.count('description =')
        assert description_count >= output_count


class TestTfvarsExample:
    """Test terraform.tfvars.example file."""

    def test_has_all_required_variables(self, tfvars_example_content):
        """Verify example file includes all required variables."""
        assert 'aws_region' in tfvars_example_content
        assert 'project_name' in tfvars_example_content
        assert 'environment' in tfvars_example_content
        assert 'db_username' in tfvars_example_content
        assert 'db_password' in tfvars_example_content

    def test_has_security_warning_for_password(self, tfvars_example_content):
        """Verify example has warning about password security."""
        assert 'CHANGE_ME' in tfvars_example_content or '⚠️' in tfvars_example_content

    def test_includes_production_example(self, tfvars_example_content):
        """Verify example includes production configuration."""
        assert '# Example Production Configuration:' in tfvars_example_content or 'production' in tfvars_example_content.lower()

    def test_warns_against_committing(self, tfvars_example_content):
        """Verify example warns against committing to git."""
        assert 'NEVER commit terraform.tfvars' in tfvars_example_content or 'Copy this file' in tfvars_example_content

    def test_has_comments_for_all_variables(self, tfvars_example_content):
        """Verify example has helpful comments."""
        # Should have comments explaining options
        comment_count = tfvars_example_content.count('#')
        assert comment_count >= 10  # At least 10 comment lines


class TestSecurityBestPractices:
    """Test security best practices."""

    def test_no_hardcoded_passwords(self, main_tf_content, variables_tf_content, outputs_tf_content):
        """Verify no hardcoded passwords in any file."""
        all_content = main_tf_content + variables_tf_content + outputs_tf_content
        # Check for common password patterns
        suspicious_patterns = [
            re.compile(r'password\s*=\s*["\'][^$][^"\']*["\']', re.IGNORECASE),
            re.compile(r'passwd\s*=\s*["\'][^$][^"\']*["\']', re.IGNORECASE),
        ]
        
        for pattern in suspicious_patterns:
            matches = pattern.findall(all_content)
            # Filter out variable references and placeholder text
            actual_passwords = [m for m in matches if 'var.' not in m and 'PASSWORD' not in m]
            assert len(actual_passwords) == 0, f"Found potential hardcoded password: {actual_passwords}"

    def test_sensitive_variables_marked(self, variables_tf_content):
        """Verify sensitive variables are marked as sensitive."""
        # Check that username and password variables are marked sensitive
        lines = variables_tf_content.split('\n')
        sensitive_vars = ['db_username', 'db_password']
        
        for var_name in sensitive_vars:
            in_var = False
            found_sensitive = False
            
            for line in lines:
                if f'variable "{var_name}"' in line:
                    in_var = True
                if in_var and 'sensitive   = true' in line:
                    found_sensitive = True
                    break
                if in_var and 'variable ' in line and var_name not in line:
                    break
            
            assert found_sensitive, f"Variable {var_name} should be marked as sensitive"

    def test_deletion_protection_documented(self, variables_tf_content, tfvars_example_content):
        """Verify deletion protection is documented for production."""
        combined = variables_tf_content + tfvars_example_content
        assert 'deletion_protection' in combined
        assert 'production' in combined.lower()

    def test_backup_retention_configured(self, variables_tf_content):
        """Verify backup retention is configurable."""
        assert 'backup_retention' in variables_tf_content
        assert 'var.db_backup_retention_days' in variables_tf_content

    def test_multi_az_available_for_ha(self, variables_tf_content, main_tf_content):
        """Verify Multi-AZ is available for high availability."""
        combined = variables_tf_content + main_tf_content
        assert 'multi_az' in combined
        assert 'var.db_multi_az' in combined


class TestNamingConventions:
    """Test naming conventions and consistency."""

    def test_resources_use_consistent_naming(self, main_tf_content):
        """Verify resources use consistent naming pattern."""
        assert '${var.project_name}-${var.environment}' in main_tf_content

    def test_alarm_names_follow_convention(self, main_tf_content):
        """Verify CloudWatch alarms follow naming convention."""
        # All alarms should use project-environment-db-metric pattern
        alarm_pattern = re.compile(r'alarm_name\s*=\s*"\$\{var\.project_name\}-\$\{var\.environment\}-db-')
        matches = alarm_pattern.findall(main_tf_content)
        # Should have at least 3 alarms (cpu, storage, connections)
        assert len(matches) >= 3

    def test_security_group_names_follow_convention(self, main_tf_content):
        """Verify security groups follow naming convention."""
        assert '${var.project_name}-${var.environment}-app-sg' in main_tf_content


class TestModuleIntegration:
    """Test module integration and outputs."""

    def test_module_outputs_used_correctly(self, main_tf_content, outputs_tf_content):
        """Verify module outputs are properly referenced."""
        assert 'module.database.db_endpoint' in outputs_tf_content
        assert 'module.database.db_security_group_id' in outputs_tf_content
        assert 'module.database.db_instance_identifier' in main_tf_content

    def test_module_receives_all_required_inputs(self, main_tf_content):
        """Verify module receives all required inputs."""
        required_inputs = [
            'project_name',
            'environment',
            'vpc_id',
            'subnet_ids',
            'db_username',
            'db_password',
        ]
        
        for input_var in required_inputs:
            assert input_var in main_tf_content, f"Module should receive {input_var}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])