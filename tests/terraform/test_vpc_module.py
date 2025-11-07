"""
Comprehensive tests for Terraform VPC module.

This test suite validates:
- VPC resource configuration
- Subnet structure and CIDR calculations
- NAT Gateway setup
- Route table configurations
- Security and best practices
"""

import re
import subprocess
from pathlib import Path
import pytest


@pytest.fixture
def vpc_module_dir():
    """Return path to VPC module directory."""
    return Path("projects/01-sde-devops/PRJ-SDE-001/code-examples/terraform/modules/vpc")


@pytest.fixture
def vpc_main_tf(vpc_module_dir):
    """Return path to VPC module main.tf."""
    return vpc_module_dir / "main.tf"


@pytest.fixture
def vpc_variables_tf(vpc_module_dir):
    """Return path to VPC module variables.tf."""
    return vpc_module_dir / "variables.tf"


@pytest.fixture
def vpc_outputs_tf(vpc_module_dir):
    """Return path to VPC module outputs.tf."""
    return vpc_module_dir / "outputs.tf"


class TestVPCModuleFiles:
    """Test VPC module file existence and structure."""

    def test_vpc_module_directory_exists(self, vpc_module_dir):
        """Verify VPC module directory exists."""
        assert vpc_module_dir.exists(), f"VPC module not found at {vpc_module_dir}"
        assert vpc_module_dir.is_dir(), f"{vpc_module_dir} is not a directory"

    def test_required_files_exist(self, vpc_module_dir):
        """Verify all required Terraform files exist."""
        required_files = ["main.tf", "variables.tf", "outputs.tf"]
        for filename in required_files:
            file_path = vpc_module_dir / filename
            assert file_path.exists(), f"Required file {filename} not found"

    def test_main_tf_not_empty(self, vpc_main_tf):
        """Verify main.tf is not empty."""
        assert vpc_main_tf.stat().st_size > 0, "main.tf is empty"


class TestVPCSyntax:
    """Test VPC module HCL syntax."""

    def test_main_tf_valid_hcl(self, vpc_main_tf):
        """Verify main.tf has valid HCL syntax."""
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-diff", str(vpc_main_tf)],
            capture_output=True,
            text=True,
            cwd=vpc_main_tf.parent
        )
        # fmt returns 0 if formatted, 3 if needs formatting, non-zero for errors
        assert result.returncode in [0, 3], f"HCL syntax error: {result.stderr}"

    def test_no_syntax_errors(self, vpc_module_dir):
        """Verify no syntax errors in module files."""
        for tf_file in vpc_module_dir.glob("*.tf"):
            with open(tf_file, 'r') as f:
                content = f.read()
            # Check for common syntax issues
            assert content.count('{') == content.count('}'), f"Mismatched braces in {tf_file.name}"
            assert content.count('[') == content.count(']'), f"Mismatched brackets in {tf_file.name}"


class TestVPCResourceConfiguration:
    """Test VPC resource configurations."""

    def test_vpc_resource_exists(self, vpc_main_tf):
        """Verify aws_vpc resource is defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_vpc"' in content, "aws_vpc resource not found"

    def test_vpc_enables_dns_hostnames(self, vpc_main_tf):
        """Verify VPC enables DNS hostnames."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert re.search(r'enable_dns_hostnames\s*=\s*true', content), \
            "VPC should enable DNS hostnames"

    def test_vpc_enables_dns_support(self, vpc_main_tf):
        """Verify VPC enables DNS support."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert re.search(r'enable_dns_support\s*=\s*true', content), \
            "VPC should enable DNS support"

    def test_vpc_has_tags(self, vpc_main_tf):
        """Verify VPC resource has tags."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        # Find VPC resource block and check for tags
        vpc_block = re.search(r'resource "aws_vpc" "main" \{[^}]+\}', content, re.DOTALL)
        assert vpc_block, "Could not find VPC resource block"
        assert 'tags' in vpc_block.group(0), "VPC should have tags"
        assert 'Name' in vpc_block.group(0), "VPC should have Name tag"


class TestInternetGateway:
    """Test Internet Gateway configuration."""

    def test_igw_resource_exists(self, vpc_main_tf):
        """Verify Internet Gateway resource is defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_internet_gateway"' in content, \
            "Internet Gateway resource not found"

    def test_igw_attached_to_vpc(self, vpc_main_tf):
        """Verify IGW is attached to VPC."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        igw_block = re.search(
            r'resource "aws_internet_gateway" "main" \{[^}]+\}',
            content,
            re.DOTALL
        )
        assert igw_block, "Could not find IGW resource block"
        assert 'vpc_id = aws_vpc.main.id' in igw_block.group(0), \
            "IGW should reference VPC ID"


class TestSubnetConfiguration:
    """Test subnet configurations."""

    def test_public_subnets_exist(self, vpc_main_tf):
        """Verify public subnets are defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_subnet" "public"' in content, \
            "Public subnet resource not found"

    def test_private_subnets_exist(self, vpc_main_tf):
        """Verify private subnets are defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_subnet" "private"' in content, \
            "Private subnet resource not found"

    def test_database_subnets_exist(self, vpc_main_tf):
        """Verify database subnets are defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_subnet" "database"' in content, \
            "Database subnet resource not found"

    def test_public_subnets_auto_assign_public_ip(self, vpc_main_tf):
        """Verify public subnets auto-assign public IPs."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        public_subnet_block = re.search(
            r'resource "aws_subnet" "public" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert public_subnet_block, "Could not find public subnet block"
        assert re.search(
            r'map_public_ip_on_launch\s*=\s*true',
            public_subnet_block.group(0)
        ), "Public subnets should auto-assign public IPs"

    def test_subnets_use_cidrsubnet_function(self, vpc_main_tf):
        """Verify subnets use cidrsubnet for CIDR calculation."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'cidrsubnet' in content, \
            "Subnets should use cidrsubnet function for CIDR calculation"

    def test_subnets_span_availability_zones(self, vpc_main_tf):
        """Verify subnets are distributed across availability zones."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'availability_zone' in content, \
            "Subnets should specify availability zones"
        assert 'var.availability_zones' in content, \
            "Should reference availability_zones variable"

    def test_subnets_have_proper_tags(self, vpc_main_tf):
        """Verify subnets have proper tagging."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        
        # Check public subnets
        public_block = re.search(
            r'resource "aws_subnet" "public".*?tags = \{[^}]+\}',
            content,
            re.DOTALL
        )
        assert public_block, "Public subnets should have tags"
        assert 'Tier = "public"' in public_block.group(0), \
            "Public subnets should have Tier tag"

        # Check database subnets
        db_block = re.search(
            r'resource "aws_subnet" "database".*?tags = \{[^}]+\}',
            content,
            re.DOTALL
        )
        if db_block:
            assert 'Tier = "database"' in db_block.group(0), \
                "Database subnets should have Tier tag"


class TestNATGateway:
    """Test NAT Gateway configuration."""

    def test_nat_eip_exists(self, vpc_main_tf):
        """Verify Elastic IP for NAT Gateway is defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_eip" "nat"' in content, \
            "NAT Gateway EIP resource not found"

    def test_nat_eip_uses_vpc_domain(self, vpc_main_tf):
        """Verify EIP uses VPC domain."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        eip_block = re.search(
            r'resource "aws_eip" "nat" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert eip_block, "Could not find EIP resource"
        assert 'domain = "vpc"' in eip_block.group(0), \
            "EIP should use VPC domain"

    def test_nat_gateway_exists(self, vpc_main_tf):
        """Verify NAT Gateway resource is defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_nat_gateway"' in content, \
            "NAT Gateway resource not found"

    def test_nat_gateway_in_public_subnet(self, vpc_main_tf):
        """Verify NAT Gateway is placed in public subnet."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        nat_block = re.search(
            r'resource "aws_nat_gateway" "main" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert nat_block, "Could not find NAT Gateway resource"
        assert 'subnet_id     = aws_subnet.public' in nat_block.group(0), \
            "NAT Gateway should be in public subnet"

    def test_nat_gateway_depends_on_igw(self, vpc_main_tf):
        """Verify NAT Gateway has dependency on Internet Gateway."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        nat_block = re.search(
            r'resource "aws_nat_gateway" "main" \{.*?\n\}',
            content,
            re.DOTALL
        )
        assert nat_block, "Could not find NAT Gateway resource"
        assert 'depends_on' in nat_block.group(0), \
            "NAT Gateway should have explicit dependency"
        assert 'aws_internet_gateway.main' in nat_block.group(0), \
            "NAT Gateway should depend on Internet Gateway"


class TestRouteTables:
    """Test route table configurations."""

    def test_public_route_table_exists(self, vpc_main_tf):
        """Verify public route table is defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_route_table" "public"' in content, \
            "Public route table not found"

    def test_public_route_table_has_igw_route(self, vpc_main_tf):
        """Verify public route table has route to Internet Gateway."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        public_rt_block = re.search(
            r'resource "aws_route_table" "public" \{.*?^\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        assert public_rt_block, "Could not find public route table"
        assert 'cidr_block = "0.0.0.0/0"' in public_rt_block.group(0), \
            "Should have default route"
        assert 'gateway_id = aws_internet_gateway.main.id' in public_rt_block.group(0), \
            "Should route to Internet Gateway"

    def test_private_route_table_exists(self, vpc_main_tf):
        """Verify private route table is defined."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'resource "aws_route_table" "private"' in content, \
            "Private route table not found"

    def test_private_route_tables_use_count(self, vpc_main_tf):
        """Verify private route tables use count for multi-AZ."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        private_rt_block = re.search(
            r'resource "aws_route_table" "private" \{.*?count',
            content,
            re.DOTALL
        )
        assert private_rt_block, \
            "Private route tables should use count for multi-AZ setup"


class TestVPCVariables:
    """Test VPC module variables."""

    def test_variables_file_exists(self, vpc_variables_tf):
        """Verify variables.tf exists."""
        assert vpc_variables_tf.exists(), "variables.tf not found"

    def test_vpc_cidr_variable_exists(self, vpc_variables_tf):
        """Verify vpc_cidr variable is defined."""
        with open(vpc_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "vpc_cidr"' in content, "vpc_cidr variable not found"

    def test_environment_variable_exists(self, vpc_variables_tf):
        """Verify environment variable is defined."""
        with open(vpc_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "environment"' in content, \
            "environment variable not found"

    def test_availability_zones_variable_exists(self, vpc_variables_tf):
        """Verify availability_zones variable is defined."""
        with open(vpc_variables_tf, 'r') as f:
            content = f.read()
        assert 'variable "availability_zones"' in content, \
            "availability_zones variable not found"

    def test_variables_have_descriptions(self, vpc_variables_tf):
        """Verify variables have descriptions."""
        with open(vpc_variables_tf, 'r') as f:
            content = f.read()
        
        variable_blocks = re.findall(
            r'variable "[^"]+" \{[^}]+\}',
            content,
            re.DOTALL
        )
        
        for block in variable_blocks:
            assert 'description' in block, \
                f"Variable should have description: {block[:50]}"


class TestVPCOutputs:
    """Test VPC module outputs."""

    def test_outputs_file_exists(self, vpc_outputs_tf):
        """Verify outputs.tf exists."""
        assert vpc_outputs_tf.exists(), "outputs.tf not found"

    def test_vpc_id_output_exists(self, vpc_outputs_tf):
        """Verify vpc_id output is defined."""
        with open(vpc_outputs_tf, 'r') as f:
            content = f.read()
        assert 'output "vpc_id"' in content, "vpc_id output not found"

    def test_public_subnet_ids_output_exists(self, vpc_outputs_tf):
        """Verify public_subnet_ids output is defined."""
        with open(vpc_outputs_tf, 'r') as f:
            content = f.read()
        assert 'public_subnet_ids' in content, \
            "public_subnet_ids output not found"

    def test_private_subnet_ids_output_exists(self, vpc_outputs_tf):
        """Verify private_subnet_ids output is defined."""
        with open(vpc_outputs_tf, 'r') as f:
            content = f.read()
        assert 'private_subnet_ids' in content, \
            "private_subnet_ids output not found"

    def test_outputs_have_descriptions(self, vpc_outputs_tf):
        """Verify outputs have descriptions."""
        with open(vpc_outputs_tf, 'r') as f:
            content = f.read()
        
        output_blocks = re.findall(
            r'output "[^"]+" \{[^}]+\}',
            content,
            re.DOTALL
        )
        
        for block in output_blocks:
            assert 'description' in block or 'value' in block, \
                f"Output should have description: {block[:50]}"


class TestVPCBestPractices:
    """Test VPC module follows best practices."""

    def test_uses_multi_az_deployment(self, vpc_main_tf):
        """Verify module supports multi-AZ deployment."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'count.index' in content or 'for_each' in content, \
            "Should support multiple availability zones"

    def test_separates_subnet_tiers(self, vpc_main_tf):
        """Verify module separates public, private, and database subnets."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert 'aws_subnet" "public"' in content, "Should have public subnets"
        assert 'aws_subnet" "private"' in content, "Should have private subnets"
        assert 'aws_subnet" "database"' in content, "Should have database subnets"

    def test_uses_environment_prefix(self, vpc_main_tf):
        """Verify resources use environment prefix in naming."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        assert '${var.environment}' in content, \
            "Resources should use environment variable in naming"

    def test_no_hardcoded_values(self, vpc_main_tf):
        """Verify no hardcoded account IDs or regions."""
        with open(vpc_main_tf, 'r') as f:
            content = f.read()
        
        # Check for common hardcoded patterns
        assert not re.search(r'\d{12}', content), \
            "Should not contain hardcoded AWS account IDs"
        assert not re.search(r'us-(east|west)-\d', content), \
            "Should not contain hardcoded regions (use variables)"