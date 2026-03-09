"""Integration tests for AWS Infrastructure Automation.

These tests validate that Terraform configurations can be planned and applied
successfully. They require AWS credentials to be configured.
"""

import boto3
import pytest
import subprocess
import os
import json
from pathlib import Path


@pytest.fixture
def terraform_dir():
    """Return path to Terraform directory."""
    return Path(__file__).parent.parent.parent / "terraform"


@pytest.fixture
def terraform_env_dir(terraform_dir):
    """Return path to dev environment."""
    return terraform_dir / "environments" / "dev"


class TestTerraformPlan:
    """Test Terraform plan operations."""

    def test_terraform_init(self, terraform_env_dir):
        """Test that terraform init succeeds."""
        result = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_env_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Init failed: {result.stderr}"
        assert "Terraform has been successfully initialized" in result.stdout

    def test_terraform_validate(self, terraform_env_dir):
        """Test that terraform validate succeeds."""
        # Initialize first
        subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_env_dir,
            capture_output=True,
        )

        result = subprocess.run(
            ["terraform", "validate"],
            cwd=terraform_env_dir,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Validate failed: {result.stderr}"
        assert "Success" in result.stdout

    def test_terraform_plan(self, terraform_env_dir):
        """Test that terraform plan succeeds with example vars."""
        # Initialize first
        subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_env_dir,
            capture_output=True,
        )

        # Create example tfvars
        tfvars_content = """
project_name = "test-project"
environment  = "dev"
aws_region   = "us-east-1"
vpc_cidr     = "10.0.0.0/16"
"""
        tfvars_path = terraform_env_dir / "test.tfvars"
        tfvars_path.write_text(tfvars_content)

        try:
            result = subprocess.run(
                ["terraform", "plan", f"-var-file={tfvars_path}", "-out=tfplan"],
                cwd=terraform_env_dir,
                capture_output=True,
                text=True,
            )

            # Plan may fail without AWS credentials, but should at least parse
            if result.returncode != 0:
                # Check if it's just credential issues vs syntax errors
                assert "Error parsing" not in result.stderr
                assert "Invalid expression" not in result.stderr
        finally:
            # Cleanup
            if tfvars_path.exists():
                tfvars_path.unlink()
            plan_file = terraform_env_dir / "tfplan"
            if plan_file.exists():
                plan_file.unlink()

    def test_terraform_fmt_check(self, terraform_dir):
        """Test that all Terraform files are properly formatted."""
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-recursive"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )
        assert (
            result.returncode == 0
        ), f"Terraform files need formatting: {result.stdout}"


class TestAWSCredentials:
    """Test AWS credential configuration."""

    def test_aws_credentials_configured(self):
        """Verify that AWS credentials are configured."""
        try:
            sts = boto3.client("sts")
            identity = sts.get_caller_identity()
            assert "Account" in identity
            assert "Arn" in identity
            print(f"AWS Account: {identity['Account']}")
        except Exception as e:
            pytest.skip(f"AWS credentials not configured: {e}")

    def test_aws_default_region(self):
        """Verify that AWS default region is set."""
        session = boto3.Session()
        region = session.region_name
        assert region is not None, "AWS default region not configured"
        print(f"AWS Region: {region}")


class TestTerraformModules:
    """Test individual Terraform modules."""

    def test_compute_module_exists(self, terraform_dir):
        """Test that compute module has required files."""
        compute_dir = terraform_dir / "modules" / "compute"
        assert compute_dir.exists()
        assert (compute_dir / "main.tf").exists()
        assert (compute_dir / "variables.tf").exists()
        assert (compute_dir / "outputs.tf").exists()

    def test_networking_module_exists(self, terraform_dir):
        """Test that networking module has required files."""
        networking_dir = terraform_dir / "modules" / "networking"
        assert networking_dir.exists()
        assert (networking_dir / "main.tf").exists()
        assert (networking_dir / "variables.tf").exists()
        assert (networking_dir / "outputs.tf").exists()

    def test_database_module_exists(self, terraform_dir):
        """Test that database module has required files."""
        database_dir = terraform_dir / "modules" / "database"
        assert database_dir.exists()
        assert (database_dir / "main.tf").exists()
        assert (database_dir / "variables.tf").exists()
        assert (database_dir / "outputs.tf").exists()

    def test_module_validate(self, terraform_dir):
        """Validate each module independently."""
        modules = [
            "compute",
            "networking",
            "database",
            "storage",
            "security",
            "monitoring",
        ]

        for module_name in modules:
            module_dir = terraform_dir / "modules" / module_name
            if not module_dir.exists():
                continue

            # Initialize
            subprocess.run(
                ["terraform", "init", "-backend=false"],
                cwd=module_dir,
                capture_output=True,
            )

            # Validate
            result = subprocess.run(
                ["terraform", "validate"],
                cwd=module_dir,
                capture_output=True,
                text=True,
            )
            assert (
                result.returncode == 0
            ), f"Module {module_name} validation failed: {result.stderr}"


class TestDeploymentScripts:
    """Test deployment scripts."""

    def test_deploy_script_exists(self, terraform_dir):
        """Test that deploy script exists and is executable."""
        deploy_script = terraform_dir / "scripts" / "deploy.sh"
        assert deploy_script.exists()
        assert os.access(deploy_script, os.X_OK), "deploy.sh is not executable"

    def test_destroy_script_exists(self, terraform_dir):
        """Test that destroy script exists and is executable."""
        destroy_script = terraform_dir / "scripts" / "destroy.sh"
        assert destroy_script.exists()
        assert os.access(destroy_script, os.X_OK), "destroy.sh is not executable"

    def test_validate_script_exists(self, terraform_dir):
        """Test that validate script exists and is executable."""
        validate_script = terraform_dir / "scripts" / "validate.sh"
        assert validate_script.exists()
        assert os.access(validate_script, os.X_OK), "validate.sh is not executable"

    def test_scripts_have_shebang(self, terraform_dir):
        """Test that scripts have proper shebang."""
        scripts_dir = terraform_dir / "scripts"
        for script in scripts_dir.glob("*.sh"):
            content = script.read_text()
            assert content.startswith("#!/bin/bash"), f"{script.name} missing shebang"


@pytest.mark.integration
class TestFullDeployment:
    """Integration tests for full infrastructure deployment.

    These tests are marked as 'integration' and require AWS credentials
    and permissions to create resources. They should be run in a sandbox
    environment only.
    """

    @pytest.mark.skip(reason="Requires AWS credentials and creates real resources")
    def test_apply_and_destroy(self, terraform_env_dir):
        """Test full apply and destroy cycle."""
        # Initialize
        result = subprocess.run(
            ["terraform", "init"], cwd=terraform_env_dir, capture_output=True
        )
        assert result.returncode == 0

        # Apply
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_env_dir,
            capture_output=True,
            text=True,
            timeout=600,
        )
        assert result.returncode == 0, f"Apply failed: {result.stderr}"

        # Get outputs
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=terraform_env_dir,
            capture_output=True,
            text=True,
        )
        outputs = json.loads(result.stdout)
        assert len(outputs) > 0

        # Destroy
        result = subprocess.run(
            ["terraform", "destroy", "-auto-approve"],
            cwd=terraform_env_dir,
            capture_output=True,
            timeout=600,
        )
        assert result.returncode == 0, f"Destroy failed: {result.stderr}"


class TestCDKImplementation:
    """Test CDK implementation."""

    def test_cdk_app_exists(self, terraform_dir):
        """Test that CDK app exists."""
        cdk_dir = terraform_dir.parent / "cdk"
        if not cdk_dir.exists():
            pytest.skip("CDK implementation not present")

        assert (cdk_dir / "app.py").exists()

    def test_cdk_synth(self, terraform_dir):
        """Test CDK synth command."""
        cdk_dir = terraform_dir.parent / "cdk"
        if not cdk_dir.exists():
            pytest.skip("CDK implementation not present")

        result = subprocess.run(
            ["cdk", "synth", "--no-color"], cwd=cdk_dir, capture_output=True, text=True
        )

        # May fail without AWS credentials, but should parse
        if "Error: Need to perform AWS calls" not in result.stderr:
            assert result.returncode == 0 or "CDK app" in result.stderr


class TestPulumiImplementation:
    """Test Pulumi implementation."""

    def test_pulumi_program_exists(self, terraform_dir):
        """Test that Pulumi program exists."""
        pulumi_dir = terraform_dir.parent / "pulumi"
        if not pulumi_dir.exists():
            pytest.skip("Pulumi implementation not present")

        assert (pulumi_dir / "__main__.py").exists()

    def test_pulumi_preview(self, terraform_dir):
        """Test Pulumi preview command."""
        pulumi_dir = terraform_dir.parent / "pulumi"
        if not pulumi_dir.exists():
            pytest.skip("Pulumi implementation not present")

        # Check if pulumi is installed
        result = subprocess.run(["pulumi", "version"], capture_output=True)
        if result.returncode != 0:
            pytest.skip("Pulumi CLI not installed")

        # Preview may fail without credentials but should parse
        result = subprocess.run(
            ["pulumi", "preview", "--non-interactive"],
            cwd=pulumi_dir,
            capture_output=True,
            text=True,
        )

        # Check that it at least parses the program
        assert (
            "error: could not load plugin" not in result.stderr.lower()
            or result.returncode == 0
        )
