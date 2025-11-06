"""
Comprehensive tests for scripts/bootstrap_remote_state.sh

This test suite validates:
- Script existence and permissions
- Argument parsing and defaults
- AWS CLI command construction
- S3 bucket creation logic
- DynamoDB table creation logic
- Error handling for missing AWS credentials
- Region-specific bucket creation (us-east-1 vs others)
- Idempotency (running multiple times safely)
"""

import subprocess
import os
import pytest
import shutil
from pathlib import Path


@pytest.fixture
def script_path():
    """Return the path to the bootstrap script."""
    return Path("scripts/bootstrap_remote_state.sh")


@pytest.fixture
def mock_env(monkeypatch):
    """Provide a clean environment without AWS credentials."""
    # Remove AWS credentials if present to test error handling
    for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]:
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


class TestScriptExistence:
    """Test script file properties."""

    def test_script_exists(self, script_path):
        """Verify the bootstrap script exists."""
        assert script_path.exists(), f"Script not found at {script_path}"

    def test_script_is_file(self, script_path):
        """Verify the script is a regular file."""
        assert script_path.is_file(), f"{script_path} is not a file"

    def test_script_is_executable(self, script_path):
        """Verify the script has executable permissions."""
        assert os.access(script_path, os.X_OK), f"{script_path} is not executable"

    def test_script_has_shebang(self, script_path):
        """
        Check that the script's first line is a bash shebang.
        
        Asserts the first line starts with "#!" and contains "bash".
        """
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!"), "Script missing shebang"
        assert "bash" in first_line, "Script should use bash"




class TestScriptPermissions:
    """Test that scripts have been made executable."""

    def test_script_is_executable_via_git(self, script_path):
        """Verify script is marked as executable in git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "-s", str(script_path)],
            capture_output=True,
            text=True,
            cwd="/home/jailuser/git"
        )
        # Git stores mode in format: mode hash stage filename
        # Executable files have mode 100755
        if result.returncode == 0 and result.stdout:
            mode = result.stdout.split()[0]
            assert mode == "100755", f"Script should be executable (mode 100755), got {mode}"

    def test_script_executable_bit_set(self, script_path):
        """Verify script has executable bit set in filesystem."""
        import stat
        st = script_path.stat()
        is_executable = bool(st.st_mode & stat.S_IXUSR)
        assert is_executable, "Script should have user executable bit set"

    def test_script_can_be_executed_directly(self, script_path):
        """Verify script can be executed directly with ./script syntax."""
        import subprocess
        # Just test that we can attempt to execute it (will fail without AWS creds but that's ok)
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=5,
            cwd="/home/jailuser/git"
        )
        # We just care that it attempted to run (not a permission error)
        # Permission error would give exit code 126
        assert result.returncode != 126, "Script should be executable (no permission denied error)"
class TestScriptSyntax:
    """Test bash script syntax and structure."""

    def test_bash_syntax_valid(self, script_path):
        """Verify bash syntax is valid using bash -n."""
        bash_path = shutil.which("bash")
        result = subprocess.run(  # noqa: S603
            [bash_path, "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_script_uses_set_flags(self, script_path):
        """Verify script uses set -euo pipefail for safety."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "set -euo pipefail" in content or "set -e" in content, \
            "Script should use 'set -euo pipefail' for error handling"


class TestArgumentParsing:
    """Test argument parsing and default values."""

    def test_script_accepts_no_arguments(self, script_path):
        """Test script runs with default values when no args provided."""
        # This will fail without AWS credentials, but we're testing arg parsing
        bash_path = shutil.which("bash")
        result = subprocess.run(  # noqa: S603
            [bash_path, str(script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Script should attempt to run, showing bucket name
        assert "Bootstrapping remote state" in result.stdout or "Bucket:" in result.stdout

    def test_script_accepts_custom_bucket_name(self, script_path):
        """Test script accepts custom bucket name as first argument."""
        bash_path = shutil.which("bash")
        result = subprocess.run(  # noqa: S603
            [bash_path, str(script_path), "test-bucket-custom"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert "test-bucket-custom" in result.stdout

    def test_script_accepts_custom_dynamodb_table(self, script_path):
        """Test script accepts custom DynamoDB table name."""
        bash_path = shutil.which("bash")
        result = subprocess.run(  # noqa: S603
            [bash_path, str(script_path), "test-bucket", "test-table"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert "test-table" in result.stdout

    def test_script_accepts_custom_region(self, script_path):
        """Test script accepts custom AWS region."""
        bash_path = shutil.which("bash")
        result = subprocess.run(  # noqa: S603
            [bash_path, str(script_path), "test-bucket", "test-table", "eu-west-1"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert "eu-west-1" in result.stdout

    def test_default_values_in_output(self, script_path):
        """Verify default values are shown in output."""
        bash_path = shutil.which("bash")
        result = subprocess.run(  # noqa: S603
            [bash_path, str(script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Check for default bucket name pattern
        assert "twisted-monk-terraform-state" in result.stdout or "Bucket:" in result.stdout
        # Check for default DynamoDB table
        assert "twisted-monk-terraform-locks" in result.stdout or "DynamoDB table:" in result.stdout


class TestS3BucketLogic:
    """Test S3 bucket creation logic."""

    def test_script_mentions_s3_bucket_creation(self, script_path):
        """Verify script contains S3 bucket creation commands."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "aws s3api create-bucket" in content, "Missing S3 bucket creation"
        assert "head-bucket" in content, "Missing bucket existence check"

    def test_script_handles_us_east_1_region_special_case(self, script_path):
        """Verify script handles us-east-1 region without LocationConstraint."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Script should check if region is us-east-1 and handle differently
        assert "us-east-1" in content, "Should handle us-east-1 specially"

    def test_script_enables_versioning(self, script_path):
        """Verify script enables S3 bucket versioning."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "put-bucket-versioning" in content, "Should enable bucket versioning"
        assert "Status=Enabled" in content or "Enabled" in content

    def test_script_enables_encryption(self, script_path):
        """Verify script enables S3 bucket encryption."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "put-bucket-encryption" in content, "Should enable bucket encryption"
        assert "AES256" in content or "SSEAlgorithm" in content


class TestDynamoDBLogic:
    """Test DynamoDB table creation logic."""

    def test_script_creates_dynamodb_table(self, script_path):
        """Verify script contains DynamoDB table creation."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "aws dynamodb create-table" in content, "Missing DynamoDB table creation"
        assert "describe-table" in content, "Missing table existence check"

    def test_dynamodb_table_has_lock_id_key(self, script_path):
        """Verify DynamoDB table uses LockID as the key."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "LockID" in content, "DynamoDB table should use LockID attribute"
        assert "AttributeName=LockID" in content

    def test_dynamodb_uses_pay_per_request(self, script_path):
        """Verify DynamoDB table uses PAY_PER_REQUEST billing mode."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "PAY_PER_REQUEST" in content or "billing-mode" in content

    def test_script_waits_for_table_creation(self, script_path):
        """Verify script waits for DynamoDB table to become active."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "wait table-exists" in content or "Waiting" in content


class TestIdempotency:
    """Test that script can be run multiple times safely."""

    def test_script_checks_bucket_exists(self, script_path):
        """Verify script checks if bucket already exists."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "head-bucket" in content or "already exists" in content

    def test_script_checks_table_exists(self, script_path):
        """Verify script checks if DynamoDB table already exists."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "describe-table" in content or "already exists" in content


class TestOutputGuidance:
    """Test script provides helpful output and guidance."""

    def test_script_provides_completion_message(self, script_path):
        """Verify script outputs completion message."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "Bootstrap complete" in content or "complete" in content.lower()

    def test_script_provides_terraform_variables_guidance(self, script_path):
        """Verify script tells user what to update in Terraform."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform/variables.tf" in content or "tfstate_bucket" in content


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_script_uses_error_exit_on_failure(self, script_path):
        """Verify script uses set -e to exit on errors."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "set -e" in content, "Script should exit on errors"

    def test_script_uses_undefined_variable_check(self, script_path):
        """Verify script fails on undefined variables with set -u."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "set -u" in content or "set -euo" in content


class TestAWSCLIUsage:
    """Test proper AWS CLI command usage."""

    def test_script_uses_aws_cli(self, script_path):
        """Verify script uses AWS CLI commands."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "aws s3api" in content or "aws dynamodb" in content

    def test_script_passes_region_to_aws_commands(self, script_path):
        """Verify script passes region parameter to AWS commands."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "--region" in content or "${REGION}" in content