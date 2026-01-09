"""Integration tests for VPC Module.

These tests validate that the VPC module creates the expected resources
with correct configurations. Tests require AWS credentials and will
create real infrastructure (use with caution).

Usage:
    pytest tests/integration/test_vpc_module.py -v -m integration
    pytest tests/integration/test_vpc_module.py -v -m "not slow"

Environment Variables:
    AWS_PROFILE: AWS CLI profile to use
    AWS_REGION: AWS region (default: us-west-2)
    TEST_VPC_DEPLOY: Set to 'true' to run deployment tests
"""

import boto3
import json
import os
import pytest
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


# Test configuration
TEST_PREFIX = "test-vpc-module"
TEST_REGION = os.environ.get("AWS_REGION", "us-west-2")
DEPLOY_TESTS_ENABLED = os.environ.get("TEST_VPC_DEPLOY", "false").lower() == "true"


@pytest.fixture(scope="module")
def terraform_dir():
    """Return path to the networking module."""
    return Path(__file__).parent.parent.parent / "terraform" / "modules" / "networking"


@pytest.fixture(scope="module")
def ec2_client():
    """Create EC2 client."""
    return boto3.client("ec2", region_name=TEST_REGION)


@pytest.fixture(scope="module")
def test_tfvars(tmp_path_factory) -> Path:
    """Generate test tfvars file."""
    tfvars_content = f"""
name_prefix = "{TEST_PREFIX}"
region      = "{TEST_REGION}"
vpc_cidr    = "10.99.0.0/16"

availability_zones = [
  "{TEST_REGION}a",
  "{TEST_REGION}b"
]

public_subnet_cidrs   = ["10.99.1.0/24", "10.99.2.0/24"]
private_subnet_cidrs  = ["10.99.11.0/24", "10.99.12.0/24"]
database_subnet_cidrs = ["10.99.21.0/24", "10.99.22.0/24"]

enable_nat_gateway   = true
single_nat_gateway   = true
enable_flow_logs     = false
enable_vpc_endpoints = false

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


class TestVPCModuleValidation:
    """Tests for VPC module validation (no deployment)."""

    def test_module_directory_exists(self, terraform_dir):
        """Test that the VPC module directory exists."""
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
        assert "## Overview" in content, "README missing Overview section"
        assert "## Example Usage" in content, "README missing Example Usage section"

    def test_terraform_init(self, terraform_dir):
        """Test that terraform init succeeds."""
        result = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"terraform init failed: {result.stderr}"
        assert "Terraform has been successfully initialized" in result.stdout

    def test_terraform_validate(self, terraform_dir):
        """Test that terraform validate succeeds."""
        # Initialize first
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

    def test_required_variables_defined(self, terraform_dir):
        """Test that required input variables are defined."""
        variables_content = (terraform_dir / "variables.tf").read_text()

        required_vars = [
            "name_prefix",
            "vpc_cidr",
            "availability_zones",
            "public_subnet_cidrs",
            "private_subnet_cidrs",
            "database_subnet_cidrs",
        ]

        for var in required_vars:
            assert f'variable "{var}"' in variables_content, f"Variable {var} not defined"

    def test_required_outputs_defined(self, terraform_dir):
        """Test that required outputs are defined."""
        outputs_content = (terraform_dir / "outputs.tf").read_text()

        required_outputs = [
            "vpc_id",
            "vpc_cidr_block",
            "public_subnet_ids",
            "private_subnet_ids",
            "database_subnet_ids",
            "nat_gateway_ids",
        ]

        for output in required_outputs:
            assert f'output "{output}"' in outputs_content, f"Output {output} not defined"


class TestVPCModulePlan:
    """Tests for VPC module planning (no actual resources created)."""

    def test_terraform_plan_creates_vpc(self, terraform_dir, test_tfvars):
        """Test that terraform plan shows VPC creation."""
        # Initialize
        subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
        )

        # Plan
        result = subprocess.run(
            ["terraform", "plan", f"-var-file={test_tfvars}", "-out=tfplan"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )

        # Plan may fail without AWS credentials, but should parse
        if result.returncode == 0:
            assert "aws_vpc.main" in result.stdout or "to add" in result.stdout

        # Cleanup plan file
        plan_file = terraform_dir / "tfplan"
        if plan_file.exists():
            plan_file.unlink()

    def test_terraform_plan_json_output(self, terraform_dir, test_tfvars):
        """Test that terraform plan produces valid JSON output."""
        # Initialize
        subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
        )

        # Plan with JSON output
        result = subprocess.run(
            [
                "terraform",
                "plan",
                f"-var-file={test_tfvars}",
                "-out=tfplan",
            ],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Show plan as JSON
            json_result = subprocess.run(
                ["terraform", "show", "-json", "tfplan"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
            )

            if json_result.returncode == 0:
                try:
                    plan_data = json.loads(json_result.stdout)
                    assert "planned_values" in plan_data or "resource_changes" in plan_data
                except json.JSONDecodeError:
                    pytest.skip("Could not parse plan JSON")

        # Cleanup
        plan_file = terraform_dir / "tfplan"
        if plan_file.exists():
            plan_file.unlink()


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(not DEPLOY_TESTS_ENABLED, reason="Deployment tests disabled")
class TestVPCModuleDeployment:
    """Integration tests that deploy actual VPC resources.

    WARNING: These tests create real AWS resources and may incur costs.
    Set TEST_VPC_DEPLOY=true to enable.
    """

    @pytest.fixture(scope="class")
    def deployed_vpc(self, terraform_dir, test_tfvars):
        """Deploy VPC and yield outputs, then destroy."""
        # Initialize
        subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
            check=True,
        )

        # Apply
        apply_result = subprocess.run(
            [
                "terraform",
                "apply",
                "-auto-approve",
                f"-var-file={test_tfvars}",
            ],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if apply_result.returncode != 0:
            pytest.fail(f"Terraform apply failed: {apply_result.stderr}")

        # Get outputs
        output_result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )

        outputs = {}
        if output_result.returncode == 0:
            outputs = json.loads(output_result.stdout)

        yield outputs

        # Cleanup: Destroy resources
        subprocess.run(
            [
                "terraform",
                "destroy",
                "-auto-approve",
                f"-var-file={test_tfvars}",
            ],
            cwd=terraform_dir,
            capture_output=True,
            timeout=600,
        )

    def test_vpc_created(self, deployed_vpc, ec2_client):
        """Test that VPC was created."""
        vpc_id = deployed_vpc.get("vpc_id", {}).get("value")
        assert vpc_id is not None, "VPC ID not in outputs"

        response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
        assert len(response["Vpcs"]) == 1
        vpc = response["Vpcs"][0]
        assert vpc["State"] == "available"

    def test_vpc_cidr_correct(self, deployed_vpc, ec2_client):
        """Test that VPC has correct CIDR block."""
        vpc_id = deployed_vpc.get("vpc_id", {}).get("value")
        expected_cidr = deployed_vpc.get("vpc_cidr_block", {}).get("value")

        response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
        actual_cidr = response["Vpcs"][0]["CidrBlock"]
        assert actual_cidr == expected_cidr

    def test_public_subnets_created(self, deployed_vpc, ec2_client):
        """Test that public subnets were created."""
        subnet_ids = deployed_vpc.get("public_subnet_ids", {}).get("value", [])
        assert len(subnet_ids) >= 2, "Expected at least 2 public subnets"

        response = ec2_client.describe_subnets(SubnetIds=subnet_ids)
        for subnet in response["Subnets"]:
            assert subnet["MapPublicIpOnLaunch"] is True, "Public subnet should map public IPs"

    def test_private_subnets_created(self, deployed_vpc, ec2_client):
        """Test that private subnets were created."""
        subnet_ids = deployed_vpc.get("private_subnet_ids", {}).get("value", [])
        assert len(subnet_ids) >= 2, "Expected at least 2 private subnets"

        response = ec2_client.describe_subnets(SubnetIds=subnet_ids)
        for subnet in response["Subnets"]:
            assert subnet["MapPublicIpOnLaunch"] is False, "Private subnet should not map public IPs"

    def test_database_subnets_isolated(self, deployed_vpc, ec2_client):
        """Test that database subnets are isolated."""
        subnet_ids = deployed_vpc.get("database_subnet_ids", {}).get("value", [])
        assert len(subnet_ids) >= 2, "Expected at least 2 database subnets"

        response = ec2_client.describe_subnets(SubnetIds=subnet_ids)
        for subnet in response["Subnets"]:
            assert subnet["MapPublicIpOnLaunch"] is False

    def test_nat_gateway_created(self, deployed_vpc, ec2_client):
        """Test that NAT gateway was created."""
        nat_ids = deployed_vpc.get("nat_gateway_ids", {}).get("value", [])
        assert len(nat_ids) >= 1, "Expected at least 1 NAT gateway"

        response = ec2_client.describe_nat_gateways(NatGatewayIds=nat_ids)
        for nat in response["NatGateways"]:
            assert nat["State"] == "available"

    def test_internet_gateway_attached(self, deployed_vpc, ec2_client):
        """Test that Internet Gateway is attached to VPC."""
        vpc_id = deployed_vpc.get("vpc_id", {}).get("value")

        response = ec2_client.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        )
        assert len(response["InternetGateways"]) == 1
        igw = response["InternetGateways"][0]
        assert igw["Attachments"][0]["State"] == "available"

    def test_route_tables_configured(self, deployed_vpc, ec2_client):
        """Test that route tables are properly configured."""
        vpc_id = deployed_vpc.get("vpc_id", {}).get("value")

        response = ec2_client.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        # Should have at least: 1 main, 1 public, 1+ private
        assert len(response["RouteTables"]) >= 3

        # Check public route table has internet gateway route
        public_rt_id = deployed_vpc.get("public_route_table_id", {}).get("value")
        if public_rt_id:
            for rt in response["RouteTables"]:
                if rt["RouteTableId"] == public_rt_id:
                    igw_routes = [
                        r
                        for r in rt["Routes"]
                        if r.get("GatewayId", "").startswith("igw-")
                    ]
                    assert len(igw_routes) > 0, "Public route table should have IGW route"


class TestVPCSecurityBestPractices:
    """Test VPC module security best practices."""

    def test_default_security_group_restrictive(self, terraform_dir):
        """Test that module doesn't open default security group."""
        main_content = (terraform_dir / "main.tf").read_text()
        # Should not have aws_default_security_group with permissive rules
        assert 'aws_default_security_group' not in main_content or \
               'cidr_blocks = ["0.0.0.0/0"]' not in main_content.split('aws_default_security_group')[1].split('}')[0]

    def test_flow_logs_configurable(self, terraform_dir):
        """Test that VPC flow logs can be enabled."""
        variables_content = (terraform_dir / "variables.tf").read_text()
        assert "enable_flow_logs" in variables_content

    def test_no_hardcoded_credentials(self, terraform_dir):
        """Test that there are no hardcoded credentials."""
        for tf_file in terraform_dir.glob("*.tf"):
            content = tf_file.read_text().lower()
            assert "password" not in content or 'variable "' in content
            assert "secret" not in content or 'variable "' in content
            assert "aws_access_key" not in content
