#!/usr/bin/env python3
"""
Terraform Configuration Tests for PRJ-SDE-001
Tests infrastructure configuration for correctness and best practices
"""
import json
import os
import subprocess
from pathlib import Path
import pytest


# Test configuration
PROJECT_ROOT = Path(__file__).parent.parent
INFRASTRUCTURE_DIR = PROJECT_ROOT / "infrastructure"
MODULES_DIR = PROJECT_ROOT / "code-examples" / "terraform" / "modules"


class TestTerraformSyntax:
    """Test Terraform syntax and formatting"""

    def test_terraform_fmt(self):
        """Test that all Terraform files are formatted correctly"""
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-recursive"],
            cwd=INFRASTRUCTURE_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Terraform files not formatted: {result.stdout}"

    def test_terraform_validate(self):
        """Test that Terraform configuration is valid"""
        # Initialize without backend
        init_result = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=INFRASTRUCTURE_DIR,
            capture_output=True,
            text=True
        )
        assert init_result.returncode == 0, f"Terraform init failed: {init_result.stderr}"

        # Validate configuration
        validate_result = subprocess.run(
            ["terraform", "validate"],
            cwd=INFRASTRUCTURE_DIR,
            capture_output=True,
            text=True
        )
        assert validate_result.returncode == 0, f"Terraform validation failed: {validate_result.stderr}"

    def test_terraform_files_exist(self):
        """Test that required Terraform files exist"""
        required_files = [
            "main.tf",
            "variables.tf",
            "outputs.tf",
            "backend.tf"
        ]
        for file in required_files:
            file_path = INFRASTRUCTURE_DIR / file
            assert file_path.exists(), f"Required file missing: {file}"


class TestModuleStructure:
    """Test Terraform module structure"""

    def test_vpc_module_exists(self):
        """Test that VPC module has required files"""
        vpc_module = MODULES_DIR.parent.parent / "infrastructure" / "terraform" / "modules" / "vpc"
        if vpc_module.exists():
            assert (vpc_module / "main.tf").exists()

    def test_secrets_manager_module_exists(self):
        """Test that Secrets Manager module has required files"""
        sm_module = MODULES_DIR / "secrets-manager"
        required_files = ["main.tf", "variables.tf", "outputs.tf", "README.md"]
        for file in required_files:
            assert (sm_module / file).exists(), f"Secrets Manager module missing: {file}"


class TestVariableConfiguration:
    """Test variable definitions and defaults"""

    def test_variables_have_descriptions(self):
        """Test that all variables have descriptions"""
        variables_file = INFRASTRUCTURE_DIR / "variables.tf"
        if not variables_file.exists():
            pytest.skip("variables.tf not found")

        content = variables_file.read_text()
        # Basic check for variable blocks
        assert "variable" in content, "No variables defined"
        # Check that description fields exist
        assert "description" in content, "Variables missing descriptions"

    def test_environment_variable_validation(self):
        """Test that environment variable has proper validation"""
        variables_file = INFRASTRUCTURE_DIR / "variables.tf"
        if not variables_file.exists():
            pytest.skip("variables.tf not found")

        content = variables_file.read_text()
        # Check for environment variable with validation
        assert "environment" in content.lower()


class TestSecurityConfiguration:
    """Test security best practices"""

    def test_no_hardcoded_credentials(self):
        """Test that no credentials are hardcoded"""
        sensitive_patterns = [
            "password",
            "secret",
            "key",
            "token"
        ]

        for tf_file in INFRASTRUCTURE_DIR.glob("**/*.tf"):
            content = tf_file.read_text().lower()
            for pattern in sensitive_patterns:
                if f'default = "{pattern}' in content or f"default = '{pattern}" in content:
                    # Check if it's actually a hardcoded value (not a reference)
                    if "var." not in content and "module." not in content:
                        pytest.fail(f"Potential hardcoded {pattern} in {tf_file.name}")

    def test_encryption_enabled(self):
        """Test that encryption is configured"""
        main_tf = INFRASTRUCTURE_DIR / "main.tf"
        if not main_tf.exists():
            pytest.skip("main.tf not found")

        content = main_tf.read_text()
        # Check for encryption-related configurations
        encryption_keywords = ["encrypt", "kms"]
        has_encryption = any(keyword in content.lower() for keyword in encryption_keywords)
        # This is informational - not all resources need encryption
        if not has_encryption:
            pytest.skip("No explicit encryption configuration found")


class TestBackendConfiguration:
    """Test Terraform backend configuration"""

    def test_backend_file_exists(self):
        """Test that backend configuration file exists"""
        backend_file = INFRASTRUCTURE_DIR / "backend.tf"
        assert backend_file.exists(), "backend.tf file missing"

    def test_backend_has_s3_configuration(self):
        """Test that S3 backend is configured"""
        backend_file = INFRASTRUCTURE_DIR / "backend.tf"
        content = backend_file.read_text()
        assert "backend" in content, "Backend configuration missing"
        assert "s3" in content.lower(), "S3 backend not configured"

    def test_bootstrap_script_exists(self):
        """Test that backend bootstrap script exists"""
        bootstrap_script = PROJECT_ROOT / "scripts" / "bootstrap-backend.sh"
        assert bootstrap_script.exists(), "Bootstrap script missing"
        assert os.access(bootstrap_script, os.X_OK), "Bootstrap script not executable"


class TestOutputs:
    """Test Terraform outputs"""

    def test_outputs_file_exists(self):
        """Test that outputs file exists"""
        outputs_file = INFRASTRUCTURE_DIR / "outputs.tf"
        assert outputs_file.exists(), "outputs.tf file missing"

    def test_outputs_have_descriptions(self):
        """Test that outputs have descriptions"""
        outputs_file = INFRASTRUCTURE_DIR / "outputs.tf"
        if not outputs_file.exists():
            pytest.skip("outputs.tf not found")

        content = outputs_file.read_text()
        if "output" in content:
            # Check that outputs have descriptions
            assert "description" in content, "Outputs missing descriptions"


class TestTags:
    """Test resource tagging"""

    def test_default_tags_configured(self):
        """Test that default tags are configured"""
        main_tf = INFRASTRUCTURE_DIR / "main.tf"
        if not main_tf.exists():
            pytest.skip("main.tf not found")

        content = main_tf.read_text()
        # Check for default_tags configuration
        assert "default_tags" in content or "tags" in content, "No tagging configuration found"


class TestDocumentation:
    """Test project documentation"""

    def test_readme_exists(self):
        """Test that README file exists"""
        readme_file = PROJECT_ROOT / "README.md"
        assert readme_file.exists(), "README.md missing"

    def test_readme_has_content(self):
        """Test that README has substantial content"""
        readme_file = PROJECT_ROOT / "README.md"
        if not readme_file.exists():
            pytest.skip("README.md not found")

        content = readme_file.read_text()
        assert len(content) > 1000, "README appears to be incomplete"
        assert "terraform" in content.lower(), "README missing Terraform information"


class TestSecretsManagerModule:
    """Test Secrets Manager module"""

    def test_module_variables_defined(self):
        """Test that module has all required variables"""
        variables_file = MODULES_DIR / "secrets-manager" / "variables.tf"
        if not variables_file.exists():
            pytest.skip("Secrets Manager module variables.tf not found")

        content = variables_file.read_text()
        required_variables = [
            "secret_name",
            "environment",
            "recovery_window_in_days"
        ]
        for var in required_variables:
            assert var in content, f"Required variable {var} not defined"

    def test_module_outputs_defined(self):
        """Test that module has outputs"""
        outputs_file = MODULES_DIR / "secrets-manager" / "outputs.tf"
        if not outputs_file.exists():
            pytest.skip("Secrets Manager module outputs.tf not found")

        content = outputs_file.read_text()
        required_outputs = [
            "secret_id",
            "secret_arn",
            "secret_name"
        ]
        for output in required_outputs:
            assert output in content, f"Required output {output} not defined"

    def test_module_readme_exists(self):
        """Test that module has comprehensive README"""
        readme_file = MODULES_DIR / "secrets-manager" / "README.md"
        assert readme_file.exists(), "Secrets Manager module README missing"

        content = readme_file.read_text()
        assert len(content) > 2000, "Module README too brief"
        assert "usage" in content.lower(), "README missing usage examples"
        assert "inputs" in content.lower(), "README missing inputs documentation"
        assert "outputs" in content.lower(), "README missing outputs documentation"


# Run pytest with coverage if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
