"""
Infrastructure validation tests for AWS Infrastructure Automation project.

These tests validate the Terraform configuration without deploying actual resources.
"""

import os
import json
import pytest
import subprocess
from pathlib import Path


class TestTerraformConfiguration:
    """Test suite for Terraform configuration validation."""

    @pytest.fixture(scope="class")
    def terraform_dir(self):
        """Get the path to the terraform directory."""
        return Path(__file__).parent.parent / "terraform"

    def test_terraform_files_exist(self, terraform_dir):
        """Verify all required Terraform files exist."""
        required_files = ['main.tf', 'variables.tf', 'outputs.tf']
        for filename in required_files:
            assert (terraform_dir / filename).exists(), f"Missing required file: {filename}"

    def test_terraform_format(self, terraform_dir):
        """Verify Terraform files are properly formatted."""
        result = subprocess.run(
            ['terraform', 'fmt', '-check', '-recursive'],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Terraform formatting issues found:\n{result.stdout}"

    def test_terraform_validate(self, terraform_dir):
        """Validate Terraform configuration syntax."""
        # Initialize Terraform (without backend)
        init_result = subprocess.run(
            ['terraform', 'init', '-backend=false'],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        assert init_result.returncode == 0, f"Terraform init failed:\n{init_result.stderr}"

        # Validate configuration
        validate_result = subprocess.run(
            ['terraform', 'validate'],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        assert validate_result.returncode == 0, f"Terraform validation failed:\n{validate_result.stderr}"

    def test_variable_definitions(self, terraform_dir):
        """Verify all required variables are defined."""
        variables_file = terraform_dir / 'variables.tf'
        content = variables_file.read_text()

        required_vars = [
            'region',
            'environment',
            'vpc_cidr',
            'availability_zones',
            'private_subnet_cidrs',
            'public_subnet_cidrs',
            'database_subnet_cidrs'
        ]

        for var in required_vars:
            assert f'variable "{var}"' in content, f"Missing required variable: {var}"

    def test_output_definitions(self, terraform_dir):
        """Verify outputs are properly defined."""
        outputs_file = terraform_dir / 'outputs.tf'
        content = outputs_file.read_text()

        expected_outputs = ['vpc_id', 'eks_cluster_name', 'rds_endpoint']
        for output in expected_outputs:
            assert f'output "{output}"' in content, f"Missing output: {output}"


class TestEnvironmentConfigurations:
    """Test suite for environment-specific configurations."""

    @pytest.fixture(scope="class")
    def terraform_dir(self):
        """Get the path to the terraform directory."""
        return Path(__file__).parent.parent / "terraform"

    def test_dev_tfvars_exists(self, terraform_dir):
        """Verify dev environment configuration exists."""
        assert (terraform_dir / 'dev.tfvars').exists()

    def test_production_tfvars_exists(self, terraform_dir):
        """Verify production environment configuration exists."""
        assert (terraform_dir / 'production.tfvars').exists()

    def test_backend_config_exists(self, terraform_dir):
        """Verify backend configuration exists."""
        assert (terraform_dir / 'backend.hcl').exists()


class TestDeploymentScripts:
    """Test suite for deployment and validation scripts."""

    @pytest.fixture(scope="class")
    def scripts_dir(self):
        """Get the path to the scripts directory."""
        return Path(__file__).parent.parent / "scripts"

    def test_deployment_scripts_exist(self, scripts_dir):
        """Verify all deployment scripts exist."""
        required_scripts = [
            'deploy-terraform.sh',
            'deploy-cdk.sh',
            'deploy-pulumi.sh',
            'validate.sh'
        ]

        for script in required_scripts:
            script_path = scripts_dir / script
            assert script_path.exists(), f"Missing deployment script: {script}"

    def test_scripts_are_executable(self, scripts_dir):
        """Verify scripts have executable permissions."""
        scripts = list(scripts_dir.glob('*.sh'))
        for script in scripts:
            assert os.access(script, os.X_OK), f"Script not executable: {script.name}"


class TestCDKConfiguration:
    """Test suite for AWS CDK configuration."""

    @pytest.fixture(scope="class")
    def cdk_dir(self):
        """Get the path to the CDK directory."""
        return Path(__file__).parent.parent / "cdk"

    def test_cdk_app_exists(self, cdk_dir):
        """Verify CDK app file exists."""
        assert (cdk_dir / 'app.py').exists()

    def test_cdk_json_exists(self, cdk_dir):
        """Verify cdk.json configuration exists."""
        cdk_json = cdk_dir / 'cdk.json'
        assert cdk_json.exists()

        # Validate JSON syntax
        with open(cdk_json) as f:
            data = json.load(f)
            assert 'app' in data, "Missing 'app' key in cdk.json"

    def test_cdk_requirements_exist(self, cdk_dir):
        """Verify CDK requirements file exists."""
        assert (cdk_dir / 'requirements.txt').exists()


class TestPulumiConfiguration:
    """Test suite for Pulumi configuration."""

    @pytest.fixture(scope="class")
    def pulumi_dir(self):
        """Get the path to the Pulumi directory."""
        return Path(__file__).parent.parent / "pulumi"

    def test_pulumi_yaml_exists(self, pulumi_dir):
        """Verify Pulumi.yaml configuration exists."""
        pulumi_yaml = pulumi_dir / 'Pulumi.yaml'
        assert pulumi_yaml.exists()

    def test_pulumi_main_exists(self, pulumi_dir):
        """Verify Pulumi main program exists."""
        assert (pulumi_dir / '__main__.py').exists()

    def test_pulumi_requirements_exist(self, pulumi_dir):
        """Verify Pulumi requirements file exists."""
        assert (pulumi_dir / 'requirements.txt').exists()


class TestSecurityBestPractices:
    """Test suite for security configuration validation."""

    @pytest.fixture(scope="class")
    def terraform_dir(self):
        """Get the path to the terraform directory."""
        return Path(__file__).parent.parent / "terraform"

    def test_rds_encryption_enabled(self, terraform_dir):
        """Verify RDS encryption is configured."""
        main_tf = (terraform_dir / 'main.tf').read_text()
        # Check for encryption-related configurations
        assert 'storage_encrypted' in main_tf or 'encrypted' in main_tf, \
            "RDS encryption should be explicitly configured"

    def test_backup_retention_configured(self, terraform_dir):
        """Verify backup retention is configured."""
        main_tf = (terraform_dir / 'main.tf').read_text()
        assert 'backup_retention_period' in main_tf, \
            "Backup retention should be configured"

    def test_multi_az_for_production(self, terraform_dir):
        """Verify Multi-AZ configuration exists."""
        main_tf = (terraform_dir / 'main.tf').read_text()
        assert 'multi_az' in main_tf.lower(), \
            "Multi-AZ configuration should be present"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
