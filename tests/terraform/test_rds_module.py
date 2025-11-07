"""
Comprehensive tests for Terraform RDS module.

This test suite validates:
- RDS instance configuration
- High availability setup
- Encryption and security
- Backup and maintenance windows
- Parameter groups
- Performance Insights
"""

import re
from pathlib import Path
import pytest


@pytest.fixture
def rds_module_dir():
    """Return path to RDS module directory."""
    return Path("projects/01-sde-devops/PRJ-SDE-001/code-examples/terraform/modules/rds")


@pytest.fixture
def rds_main_tf(rds_module_dir):
    """Return path to RDS module main.tf."""
    return rds_module_dir / "main.tf"


@pytest.fixture
def rds_variables_tf(rds_module_dir):
    """Return path to RDS module variables.tf."""
    return rds_module_dir / "variables.tf"


@pytest.fixture
def rds_outputs_tf(rds_module_dir):
    """Return path to RDS module outputs.tf."""
    return rds_module_dir / "outputs.tf"


class TestRDSModuleFiles:
    """Test RDS module file existence and structure."""

    def test_rds_module_directory_exists(self, rds_module_dir):
        """Verify RDS module directory exists."""
        assert rds_module_dir.exists(), f"RDS module not found at {rds_module_dir}"

    def test_required_files_exist(self, rds_module_dir):
        """Verify all required Terraform files exist."""
        required_files = ["main.tf", "variables.tf", "outputs.tf"]
        for filename in required_files:
            file_path = rds_module_dir / filename
            assert file_path.exists(), f"Required file {filename} not found"


class TestRDSSubnetGroup:
    """Test RDS subnet group configuration."""

    def test_subnet_group_resource_exists(self, rds_main_tf):
        """Verify DB subnet group resource is defined."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_db_subnet_group"' in content, \
            "DB subnet group resource not found"

    def test_subnet_group_uses_variable(self, rds_main_tf):
        """Verify subnet group uses subnet IDs from variable."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        subnet_group_block = re.search(
            r'resource "aws_db_subnet_group" "main" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert subnet_group_block, "Could not find subnet group"
        assert 'subnet_ids = var.subnet_ids' in subnet_group_block.group(0), \
            "Should use variable for subnet IDs"


class TestRDSParameterGroup:
    """Test RDS parameter group configuration."""

    def test_parameter_group_exists(self, rds_main_tf):
        """Verify parameter group resource is defined."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_db_parameter_group"' in content, \
            "Parameter group resource not found"

    def test_parameter_group_specifies_family(self, rds_main_tf):
        """Verify parameter group specifies correct database family."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        param_group_block = re.search(
            r'resource "aws_db_parameter_group" "main" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert param_group_block, "Could not find parameter group"
        assert 'family' in param_group_block.group(0), \
            "Parameter group should specify family"

    def test_logging_parameters_configured(self, rds_main_tf):
        """Verify logging parameters are configured."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        
        logging_params = ['log_connections', 'log_disconnections', 'log_statement']
        for param in logging_params:
            assert param in content, f"Should configure {param} parameter"

    def test_performance_monitoring_enabled(self, rds_main_tf):
        """Verify pg_stat_statements is enabled."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'pg_stat_statements' in content, \
            "Should enable pg_stat_statements for performance monitoring"


class TestRDSInstanceConfiguration:
    """Test RDS instance resource configuration."""

    def test_rds_instance_resource_exists(self, rds_main_tf):
        """Verify RDS instance resource is defined."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_db_instance" "main"' in content, \
            "RDS instance resource not found"

    def test_instance_uses_postgres(self, rds_main_tf):
        """Verify instance uses PostgreSQL engine."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        instance_block = re.search(
            r'resource "aws_db_instance" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert instance_block, "Could not find RDS instance"
        assert 'engine         = "postgres"' in instance_block.group(0), \
            "Should use PostgreSQL engine"

    def test_instance_specifies_version(self, rds_main_tf):
        """Verify instance specifies engine version."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        instance_block = re.search(
            r'resource "aws_db_instance" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert instance_block, "Could not find RDS instance"
        assert 'engine_version' in instance_block.group(0), \
            "Should specify engine version"

    def test_instance_class_from_variable(self, rds_main_tf):
        """Verify instance class comes from variable."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'instance_class    = var.instance_class' in content, \
            "Instance class should use variable"

    def test_allocated_storage_from_variable(self, rds_main_tf):
        """Verify allocated storage comes from variable."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'allocated_storage = var.allocated_storage' in content, \
            "Allocated storage should use variable"


class TestRDSEncryption:
    """Test RDS encryption configuration."""

    def test_storage_encryption_enabled(self, rds_main_tf):
        """Verify storage encryption is enabled."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert re.search(r'storage_encrypted\s*=\s*true', content), \
            "Storage encryption should be enabled"

    def test_kms_key_used(self, rds_main_tf):
        """Verify KMS key is used for encryption."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        instance_block = re.search(
            r'resource "aws_db_instance" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert instance_block, "Could not find RDS instance"
        assert 'kms_key_id' in instance_block.group(0), \
            "Should specify KMS key for encryption"

    def test_kms_key_resource_exists(self, rds_main_tf):
        """Verify KMS key resource is defined."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_kms_key" "rds"' in content, \
            "KMS key resource not found"


class TestRDSHighAvailability:
    """Test RDS high availability configuration."""

    def test_multi_az_enabled(self, rds_main_tf):
        """Verify Multi-AZ deployment is enabled."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert re.search(r'multi_az\s*=\s*true', content), \
            "Multi-AZ should be enabled for high availability"

    def test_read_replica_supported(self, rds_main_tf):
        """Verify read replica configuration exists."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_db_instance" "replica"' in content, \
            "Read replica resource not found"

    def test_replica_uses_count(self, rds_main_tf):
        """Verify read replica uses count for conditional creation."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        replica_block = re.search(
            r'resource "aws_db_instance" "replica" \{.*?count',
            content,
            re.DOTALL
        )
        assert replica_block, "Read replica should use count for conditional creation"

    def test_replica_references_main(self, rds_main_tf):
        """Verify read replica references main database."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        replica_block = re.search(
            r'resource "aws_db_instance" "replica" \{.*?\n\}',
            content,
            re.DOTALL
        )
        if replica_block:
            assert 'replicate_source_db' in replica_block.group(0), \
                "Replica should reference source database"


class TestRDSBackupConfiguration:
    """Test RDS backup configuration."""

    def test_backup_retention_configured(self, rds_main_tf):
        """Verify backup retention period is configured."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'backup_retention_period' in content, \
            "Backup retention period should be configured"

    def test_backup_retention_sufficient(self, rds_main_tf):
        """Verify backup retention period is sufficient (>= 7 days)."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        retention_match = re.search(r'backup_retention_period\s*=\s*(\d+)', content)
        if retention_match:
            retention_days = int(retention_match.group(1))
            assert retention_days >= 7, \
                f"Backup retention should be at least 7 days, found {retention_days}"

    def test_backup_window_configured(self, rds_main_tf):
        """Verify backup window is configured."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'backup_window' in content, \
            "Backup window should be configured"

    def test_maintenance_window_configured(self, rds_main_tf):
        """Verify maintenance window is configured."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'maintenance_window' in content, \
            "Maintenance window should be configured"

    def test_backup_and_maintenance_non_overlapping(self, rds_main_tf):
        """Verify backup and maintenance windows don't overlap."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        
        backup_match = re.search(r'backup_window\s*=\s*"([^"]+)"', content)
        maint_match = re.search(r'maintenance_window\s*=\s*"([^"]+)"', content)
        
        # Basic check that they're different
        if backup_match and maint_match:
            assert backup_match.group(1) != maint_match.group(1), \
                "Backup and maintenance windows should not overlap"


class TestRDSMonitoring:
    """Test RDS monitoring configuration."""

    def test_cloudwatch_logs_enabled(self, rds_main_tf):
        """Verify CloudWatch logs export is enabled."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'enabled_cloudwatch_logs_exports' in content, \
            "CloudWatch logs export should be enabled"

    def test_postgresql_logs_exported(self, rds_main_tf):
        """Verify PostgreSQL logs are exported to CloudWatch."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        logs_block = re.search(
            r'enabled_cloudwatch_logs_exports\s*=\s*\[.*?\]',
            content,
            re.DOTALL
        )
        assert logs_block, "Could not find CloudWatch logs configuration"
        assert '"postgresql"' in logs_block.group(0), \
            "Should export postgresql logs"

    def test_performance_insights_enabled(self, rds_main_tf):
        """Verify Performance Insights is enabled."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert re.search(r'performance_insights_enabled\s*=\s*true', content), \
            "Performance Insights should be enabled"

    def test_performance_insights_encrypted(self, rds_main_tf):
        """Verify Performance Insights uses KMS encryption."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        instance_block = re.search(
            r'resource "aws_db_instance" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        if instance_block and 'performance_insights_enabled' in instance_block.group(0):
            assert 'performance_insights_kms_key_id' in instance_block.group(0), \
                "Performance Insights should use KMS encryption"


class TestRDSCredentials:
    """Test RDS credentials management."""

    def test_username_from_variable(self, rds_main_tf):
        """Verify master username comes from variable."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'username = var.master_username' in content, \
            "Master username should use variable"

    def test_password_randomly_generated(self, rds_main_tf):
        """Verify password is randomly generated."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "random_password" "db_password"' in content, \
            "Should use random_password resource"
        assert 'password = random_password.db_password.result' in content, \
            "Should use randomly generated password"

    def test_password_stored_in_secrets_manager(self, rds_main_tf):
        """Verify password is stored in AWS Secrets Manager."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_secretsmanager_secret" "db_password"' in content, \
            "Should store password in Secrets Manager"

    def test_secrets_manager_has_recovery_window(self, rds_main_tf):
        """Verify Secrets Manager secret has recovery window."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        secret_block = re.search(
            r'resource "aws_secretsmanager_secret" "db_password" \{.*?\n\}',
            content,
            re.DOTALL
        )
        if secret_block:
            assert 'recovery_window_in_days' in secret_block.group(0), \
                "Secret should have recovery window configured"


class TestRDSSecurityGroups:
    """Test RDS security group configuration."""

    def test_security_group_referenced(self, rds_main_tf):
        """Verify security group is referenced."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'vpc_security_group_ids' in content, \
            "Should configure security groups"

    def test_security_group_resource_exists(self, rds_main_tf):
        """Verify security group resource is defined."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_security_group" "database"' in content, \
            "Database security group resource should exist"


class TestRDSDeletionProtection:
    """Test RDS deletion protection."""

    def test_deletion_protection_conditional(self, rds_main_tf):
        """Verify deletion protection is environment-dependent."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        
        deletion_line = re.search(
            r'deletion_protection\s*=.*var\.environment.*production',
            content
        )
        assert deletion_line, \
            "Deletion protection should be enabled for production"

    def test_skip_final_snapshot_conditional(self, rds_main_tf):
        """Verify skip_final_snapshot is environment-dependent."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        
        skip_snapshot = re.search(
            r'skip_final_snapshot\s*=.*var\.environment.*production',
            content
        )
        assert skip_snapshot, \
            "Should take final snapshot in production"

    def test_final_snapshot_identifier_for_production(self, rds_main_tf):
        """Verify final snapshot identifier is set for production."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'final_snapshot_identifier' in content, \
            "Should configure final snapshot identifier"


class TestRDSStorageType:
    """Test RDS storage configuration."""

    def test_uses_gp3_storage(self, rds_main_tf):
        """Verify instance uses gp3 storage type."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        assert 'storage_type      = "gp3"' in content, \
            "Should use gp3 storage for better performance"


class TestRDSVariables:
    """Test RDS module variables."""

    def test_variables_file_exists(self, rds_variables_tf):
        """Verify variables.tf exists."""
        assert rds_variables_tf.exists(), "variables.tf not found"

    def test_environment_variable_exists(self, rds_variables_tf):
        """Verify environment variable is defined."""
        with open(rds_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "environment"' in content, \
            "environment variable not found"

    def test_instance_class_variable_exists(self, rds_variables_tf):
        """Verify instance_class variable is defined."""
        with open(rds_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "instance_class"' in content, \
            "instance_class variable not found"

    def test_storage_variables_exist(self, rds_variables_tf):
        """Verify storage-related variables are defined."""
        with open(rds_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "allocated_storage"' in content, \
            "allocated_storage variable not found"

    def test_database_name_variable_exists(self, rds_variables_tf):
        """Verify database_name variable is defined."""
        with open(rds_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "database_name"' in content, \
            "database_name variable not found"


class TestRDSOutputs:
    """Test RDS module outputs."""

    def test_outputs_file_exists(self, rds_outputs_tf):
        """Verify outputs.tf exists."""
        assert rds_outputs_tf.exists(), "outputs.tf not found"

    def test_endpoint_output_exists(self, rds_outputs_tf):
        """Verify endpoint output is defined."""
        with open(rds_outputs_tf, 'r') as f:
            content = f.read()
        assert 'endpoint' in content, "Endpoint output not found"

    def test_database_name_output_exists(self, rds_outputs_tf):
        """Verify database name output is defined."""
        with open(rds_outputs_tf, 'r') as f:
            content = f.read()
        assert 'database' in content or 'db_name' in content, \
            "Database name output not found"


class TestRDSBestPractices:
    """Test RDS module follows best practices."""

    def test_uses_parameter_group(self, rds_main_tf):
        """Verify instance uses custom parameter group."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        instance_block = re.search(
            r'resource "aws_db_instance" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert instance_block, "Could not find RDS instance"
        assert 'parameter_group_name' in instance_block.group(0), \
            "Should use custom parameter group"

    def test_uses_subnet_group(self, rds_main_tf):
        """Verify instance uses DB subnet group."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        instance_block = re.search(
            r'resource "aws_db_instance" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert instance_block, "Could not find RDS instance"
        assert 'db_subnet_group_name' in instance_block.group(0), \
            "Should use DB subnet group"

    def test_tags_resources(self, rds_main_tf):
        """Verify resources are properly tagged."""
        with open(rds_main_tf, 'r') as f:
            content = f.read()
        
        # Check instance has tags
        instance_block = re.search(
            r'resource "aws_db_instance" "main" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert instance_block and 'tags' in instance_block.group(0), \
            "RDS instance should have tags"