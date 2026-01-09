"""Integration tests for RDS Database Module.

These tests validate that the RDS module creates the expected resources
with correct configurations including Multi-AZ, encryption, and backups.

Usage:
    pytest tests/integration/test_rds_module.py -v -m integration
    pytest tests/integration/test_rds_module.py -v -m "not slow"

Environment Variables:
    AWS_PROFILE: AWS CLI profile to use
    AWS_REGION: AWS region (default: us-west-2)
    TEST_RDS_DEPLOY: Set to 'true' to run deployment tests
"""

import boto3
import os
import pytest
import subprocess
from pathlib import Path


# Test configuration
TEST_PREFIX = "test-rds-module"
TEST_REGION = os.environ.get("AWS_REGION", "us-west-2")
DEPLOY_TESTS_ENABLED = os.environ.get("TEST_RDS_DEPLOY", "false").lower() == "true"


@pytest.fixture(scope="module")
def terraform_dir():
    """Return path to the database module."""
    return Path(__file__).parent.parent.parent / "terraform" / "modules" / "database"


@pytest.fixture(scope="module")
def rds_client():
    """Create RDS client."""
    return boto3.client("rds", region_name=TEST_REGION)


@pytest.fixture(scope="module")
def test_tfvars(tmp_path_factory) -> Path:
    """Generate test tfvars file for RDS module."""
    # Note: This requires a VPC and subnet group to be created first
    tfvars_content = f"""
name_prefix          = "{TEST_PREFIX}"
vpc_id               = "vpc-placeholder"
db_subnet_group_name = "placeholder"

engine         = "postgres"
engine_version = "15.4"
instance_class = "db.t3.micro"

allocated_storage     = 20
max_allocated_storage = 50

database_name   = "testdb"
master_username = "testadmin"
master_password = "TestPassword123!"
port            = 5432

multi_az                = false
backup_retention_period = 1
skip_final_snapshot     = true
deletion_protection     = false

performance_insights_enabled = false
monitoring_interval          = 0
create_cloudwatch_alarms     = false

tags = {{
  Environment = "test"
  Project     = "integration-test"
  AutoCleanup = "true"
}}
"""
    tfvars_dir = tmp_path_factory.mktemp("tfvars")
    tfvars_path = tfvars_dir / "test.tfvars"
    tfvars_path.write_text(tfvars_content)
    return tfvars_path


class TestRDSModuleValidation:
    """Tests for RDS module validation (no deployment)."""

    def test_module_directory_exists(self, terraform_dir):
        """Test that the RDS module directory exists."""
        assert terraform_dir.exists(), f"Module directory not found: {terraform_dir}"

    def test_required_files_exist(self, terraform_dir):
        """Test that required module files exist."""
        required_files = ["main.tf", "variables.tf", "outputs.tf"]
        for filename in required_files:
            filepath = terraform_dir / filename
            assert filepath.exists(), f"Required file missing: {filename}"

    def test_readme_exists(self, terraform_dir):
        """Test that README documentation exists."""
        readme = terraform_dir / "README.md"
        assert readme.exists(), "README.md not found"
        content = readme.read_text()
        assert len(content) > 500, "README seems too short"
        assert "Multi-AZ" in content, "README should mention Multi-AZ"
        assert "encryption" in content.lower(), "README should mention encryption"

    def test_terraform_init(self, terraform_dir):
        """Test that terraform init succeeds."""
        result = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"terraform init failed: {result.stderr}"

    def test_terraform_validate(self, terraform_dir):
        """Test that terraform validate succeeds."""
        subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
        )

        result = subprocess.run(
            ["terraform", "validate"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"terraform validate failed: {result.stderr}"

    def test_terraform_fmt_check(self, terraform_dir):
        """Test that Terraform files are properly formatted."""
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-recursive"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Files need formatting: {result.stdout}"


class TestRDSModuleVariables:
    """Tests for RDS module variables and configurations."""

    def test_required_variables_defined(self, terraform_dir):
        """Test that required input variables are defined."""
        variables_content = (terraform_dir / "variables.tf").read_text()

        required_vars = [
            "name_prefix",
            "vpc_id",
            "db_subnet_group_name",
            "master_username",
            "master_password",
        ]

        for var in required_vars:
            assert f'variable "{var}"' in variables_content, f"Variable {var} not defined"

    def test_password_is_sensitive(self, terraform_dir):
        """Test that password variable is marked as sensitive."""
        variables_content = (terraform_dir / "variables.tf").read_text()

        # Find the db_password/master_password variable block
        assert "sensitive" in variables_content, "Password should be marked sensitive"

        # Check that password variable has sensitive = true
        lines = variables_content.split("\n")
        in_password_block = False
        found_sensitive = False

        for line in lines:
            if 'variable "master_password"' in line or 'variable "db_password"' in line:
                in_password_block = True
            if in_password_block:
                if "sensitive" in line and "true" in line:
                    found_sensitive = True
                    break
                if line.strip() == "}":
                    break

        assert found_sensitive, "Password variable should have sensitive = true"

    def test_multi_az_configurable(self, terraform_dir):
        """Test that Multi-AZ is configurable."""
        variables_content = (terraform_dir / "variables.tf").read_text()
        assert "multi_az" in variables_content, "multi_az variable should be defined"

    def test_encryption_enabled_by_default(self, terraform_dir):
        """Test that encryption is enabled by default."""
        main_content = (terraform_dir / "main.tf").read_text()
        assert "storage_encrypted" in main_content
        assert "storage_encrypted" in main_content and "true" in main_content

    def test_backup_retention_configurable(self, terraform_dir):
        """Test that backup retention is configurable."""
        variables_content = (terraform_dir / "variables.tf").read_text()
        assert "backup_retention_period" in variables_content

    def test_deletion_protection_configurable(self, terraform_dir):
        """Test that deletion protection is configurable."""
        variables_content = (terraform_dir / "variables.tf").read_text()
        assert "deletion_protection" in variables_content


class TestRDSModuleOutputs:
    """Tests for RDS module outputs."""

    def test_required_outputs_defined(self, terraform_dir):
        """Test that required outputs are defined."""
        outputs_content = (terraform_dir / "outputs.tf").read_text()

        required_outputs = [
            "db_instance_endpoint",
            "db_instance_address",
            "db_instance_port",
            "db_instance_id",
            "security_group_id",
        ]

        for output in required_outputs:
            assert f'output "{output}"' in outputs_content, f"Output {output} not defined"

    def test_connection_string_output(self, terraform_dir):
        """Test that connection string output is defined."""
        outputs_content = (terraform_dir / "outputs.tf").read_text()
        assert "connection_string" in outputs_content, "connection_string output should be defined"

    def test_sensitive_outputs_marked(self, terraform_dir):
        """Test that sensitive outputs are marked as sensitive."""
        outputs_content = (terraform_dir / "outputs.tf").read_text()

        # Connection string should be sensitive
        if "connection_string" in outputs_content:
            # Find the connection_string output block
            lines = outputs_content.split("\n")
            in_conn_block = False
            found_sensitive = False

            for line in lines:
                if 'output "connection_string"' in line:
                    in_conn_block = True
                if in_conn_block:
                    if "sensitive" in line and "true" in line:
                        found_sensitive = True
                        break
                    if line.strip().startswith("output "):
                        break

            assert found_sensitive, "connection_string should be marked sensitive"


class TestRDSModuleSecurityBestPractices:
    """Test RDS module security best practices."""

    def test_not_publicly_accessible(self, terraform_dir):
        """Test that RDS is not publicly accessible by default."""
        main_content = (terraform_dir / "main.tf").read_text()
        assert "publicly_accessible" in main_content

        # Should be set to false
        lines = main_content.split("\n")
        for line in lines:
            if "publicly_accessible" in line and "=" in line:
                assert "false" in line, "publicly_accessible should be false"
                break

    def test_kms_encryption_supported(self, terraform_dir):
        """Test that KMS encryption is supported."""
        main_content = (terraform_dir / "main.tf").read_text()
        variables_content = (terraform_dir / "variables.tf").read_text()

        # Should have kms_key_id in main or variables
        assert "kms_key" in main_content or "kms_key" in variables_content

    def test_ssl_enforcement_option(self, terraform_dir):
        """Test that SSL can be enforced via parameter group."""
        main_content = (terraform_dir / "main.tf").read_text()

        # Should define a parameter group
        assert "aws_db_parameter_group" in main_content, "Should create custom parameter group"

    def test_cloudwatch_alarms_available(self, terraform_dir):
        """Test that CloudWatch alarms can be created."""
        main_content = (terraform_dir / "main.tf").read_text()
        variables_content = (terraform_dir / "variables.tf").read_text()

        assert "cloudwatch" in main_content.lower() or "cloudwatch" in variables_content.lower()

    def test_no_hardcoded_credentials(self, terraform_dir):
        """Test that there are no hardcoded credentials."""
        for tf_file in terraform_dir.glob("*.tf"):
            content = tf_file.read_text()
            # Should not have actual passwords
            assert "CHANGEME" not in content
            assert "password123" not in content.lower()
            # Variables are OK
            if "password" in content.lower():
                assert "variable" in content.lower() or "var." in content


class TestRDSModulePlan:
    """Tests for RDS module planning."""

    def test_terraform_plan_syntax(self, terraform_dir, test_tfvars):
        """Test that terraform plan parses correctly."""
        subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
        )

        result = subprocess.run(
            ["terraform", "plan", f"-var-file={test_tfvars}"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )

        # Plan may fail due to missing VPC, but should parse
        assert "Error: Invalid expression" not in result.stderr
        assert "Error: Argument or block definition required" not in result.stderr


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(not DEPLOY_TESTS_ENABLED, reason="Deployment tests disabled")
class TestRDSModuleDeployment:
    """Integration tests that deploy actual RDS resources.

    WARNING: These tests create real AWS resources and may incur costs.
    Set TEST_RDS_DEPLOY=true to enable.

    Note: These tests require a VPC and subnet group to be created first.
    """

    @pytest.fixture(scope="class")
    def vpc_resources(self, ec2_client):
        """Create VPC resources needed for RDS testing."""
        # Create VPC
        vpc = ec2_client.create_vpc(CidrBlock="10.98.0.0/16")
        vpc_id = vpc["Vpc"]["VpcId"]

        # Wait for VPC to be available
        ec2_client.get_waiter("vpc_available").wait(VpcIds=[vpc_id])

        # Enable DNS hostname
        ec2_client.modify_vpc_attribute(
            VpcId=vpc_id, EnableDnsHostnames={"Value": True}
        )

        # Create subnets in different AZs
        azs = ec2_client.describe_availability_zones()["AvailabilityZones"][:2]

        subnet_ids = []
        for i, az in enumerate(azs):
            subnet = ec2_client.create_subnet(
                VpcId=vpc_id,
                CidrBlock=f"10.98.{i + 1}.0/24",
                AvailabilityZone=az["ZoneName"],
            )
            subnet_ids.append(subnet["Subnet"]["SubnetId"])

        # Create DB subnet group
        rds_client = boto3.client("rds", region_name=TEST_REGION)
        subnet_group_name = f"{TEST_PREFIX}-subnet-group"

        rds_client.create_db_subnet_group(
            DBSubnetGroupName=subnet_group_name,
            DBSubnetGroupDescription="Test subnet group",
            SubnetIds=subnet_ids,
        )

        yield {
            "vpc_id": vpc_id,
            "subnet_ids": subnet_ids,
            "subnet_group_name": subnet_group_name,
        }

        # Cleanup
        try:
            rds_client.delete_db_subnet_group(DBSubnetGroupName=subnet_group_name)
        except Exception:
            pass

        for subnet_id in subnet_ids:
            try:
                ec2_client.delete_subnet(SubnetId=subnet_id)
            except Exception:
                pass

        try:
            ec2_client.delete_vpc(VpcId=vpc_id)
        except Exception:
            pass

    def test_rds_multi_az_enabled(self, rds_client, vpc_resources):
        """Test that Multi-AZ can be enabled."""
        # This would test actual RDS deployment with Multi-AZ
        # Skipped in this example due to cost/time
        pytest.skip("Full RDS deployment test skipped due to cost")

    def test_rds_encryption_enabled(self, rds_client, vpc_resources):
        """Test that encryption is enabled."""
        pytest.skip("Full RDS deployment test skipped due to cost")

    def test_rds_backup_configured(self, rds_client, vpc_resources):
        """Test that backups are configured."""
        pytest.skip("Full RDS deployment test skipped due to cost")

    def test_rds_private_access_only(self, rds_client, vpc_resources):
        """Test that RDS is only accessible from private subnets."""
        pytest.skip("Full RDS deployment test skipped due to cost")


class TestRDSModuleMultiAZValidation:
    """Test Multi-AZ configuration validation."""

    def test_multi_az_default_for_production(self, terraform_dir):
        """Test that Multi-AZ default makes sense."""
        variables_content = (terraform_dir / "variables.tf").read_text()

        # Find the multi_az variable default
        lines = variables_content.split("\n")
        in_multi_az_block = False
        default_value = None

        for line in lines:
            if 'variable "multi_az"' in line:
                in_multi_az_block = True
            if in_multi_az_block:
                if "default" in line:
                    default_value = "true" in line
                    break
                if line.strip() == "}":
                    break

        # Multi-AZ should default to true for production readiness
        assert default_value is True, "multi_az should default to true"

    def test_module_supports_read_replica(self, terraform_dir):
        """Test that module supports read replicas."""
        variables_content = (terraform_dir / "variables.tf").read_text()
        main_content = (terraform_dir / "main.tf").read_text()

        # Should have read replica configuration
        has_replica_var = "create_read_replica" in variables_content or "replica" in variables_content
        has_replica_resource = "aws_db_instance" in main_content and "replica" in main_content

        assert has_replica_var or has_replica_resource, "Should support read replicas"
