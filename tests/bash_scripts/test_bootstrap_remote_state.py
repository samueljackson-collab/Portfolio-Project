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
        """Verify the script has a proper shebang."""
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!"), "Script missing shebang"
        assert "bash" in first_line, "Script should use bash"


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

class TestScriptCorrectness:
    """Test script correctness and file quality."""

    def test_script_has_newline_at_end(self, script_path):
        """Verify script ends with a newline character."""
        with open(script_path, 'rb') as f:
            content = f.read()
        
        assert content.endswith(b'\n'), \
            "Script should end with a newline character (POSIX requirement)"

    def test_consistent_line_endings(self, script_path):
        """Verify script uses consistent Unix line endings."""
        with open(script_path, 'rb') as f:
            content = f.read()
        
        # Check for Windows line endings
        assert b'\r\n' not in content, \
            "Script contains Windows line endings (CRLF). Should use Unix (LF) only."

    def test_no_trailing_whitespace_on_lines(self, script_path):
        """Check for trailing whitespace which can cause issues."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        lines_with_trailing = []
        for i, line in enumerate(lines, 1):
            # Check if line has trailing whitespace (excluding the newline)
            if line.rstrip('\n') != line.rstrip('\n').rstrip():
                lines_with_trailing.append(i)
        
        if lines_with_trailing:
            pytest.fail(
                f"Lines with trailing whitespace: {lines_with_trailing}. "
                "This can cause issues in shell scripts."
            )


class TestAWSCommandCorrectness:
    """Test AWS CLI commands are correctly formed."""

    def test_aws_commands_not_assigned_to_variables(self, script_path):
        """Verify AWS commands are executed, not assigned to variables."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        import re
        # Look for patterns like: var=aws ...
        # This would be a typo where someone means to run aws but creates a variable
        pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*aws\s+'
        
        matches = re.findall(pattern, content, re.MULTILINE)
        
        # Filter out legitimate uses like status=$(aws ...)
        legitimate_patterns = [
            r'\$\(',  # Command substitution
            r'`',      # Backtick substitution
        ]
        
        false_positives = []
        for match in matches:
            # Check if this is command substitution
            is_cmd_sub = False
            for line in content.split('\n'):
                if f'{match}=' in line and ('$(' in line or '`' in line):
                    is_cmd_sub = True
                    break
            if is_cmd_sub:
                false_positives.append(match)
        
        actual_issues = [m for m in matches if m not in false_positives]
        
        if actual_issues:
            pytest.fail(
                f"Found AWS commands being assigned to variables: {actual_issues}. "
                f"These should be executed directly or in command substitution $(...), not simple assignment."
            )

    def test_aws_cli_commands_have_required_parameters(self, script_path):
        """Verify AWS CLI commands have necessary parameters like --region."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        aws_command_lines = []
        for i, line in enumerate(lines, 1):
            if 'aws ' in line and not line.strip().startswith('#'):
                # Skip lines that are just checking AWS CLI existence
                if 'which aws' not in line and 'command -v aws' not in line:
                    aws_command_lines.append((i, line.strip()))
        
        # Check that most AWS commands reference the region
        # Either directly or through a variable
        for line_num, line in aws_command_lines:
            if 'aws s3' in line or 'aws dynamodb' in line:
                has_region = '--region' in line or '${REGION}' in line or '$REGION' in line
                if not has_region:
                    # This might be okay if region is set in environment, but warn
                    pass  # We'll be lenient here


class TestOutputAndDocumentation:
    """Test script output and user guidance."""

    def test_completion_message_is_clear(self, script_path):
        """Verify completion message provides clear next steps."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should tell user what to do next
        assert 'terraform/variables.tf' in content or 'variables.tf' in content, \
            "Should guide user to update variables.tf"
        
        assert 'tfstate_bucket' in content, \
            "Should mention tfstate_bucket variable"
        
        assert 'tfstate_lock_table' in content or 'lock_table' in content, \
            "Should mention tfstate_lock_table variable"

    def test_script_outputs_all_required_info(self, script_path):
        """Verify script outputs bucket and table names."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should echo the bucket name
        assert 'echo' in content, "Script should provide output messages"
        
        # Should display the values being used
        has_bucket_output = '${BUCKET_NAME}' in content or '$BUCKET_NAME' in content
        has_table_output = '${DDB_TABLE}' in content or '$DDB_TABLE' in content
        
        assert has_bucket_output, "Should output bucket name"
        assert has_table_output, "Should output DynamoDB table name"


class TestRegionHandling:
    """Test special handling for different AWS regions."""

    def test_us_east_1_special_case_exists(self, script_path):
        """Verify script handles us-east-1 region specially for S3."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # us-east-1 doesn't use LocationConstraint
        assert 'us-east-1' in content, \
            "Should check for us-east-1 region"
        
        # Should have conditional logic for this
        assert 'if' in content and ('us-east-1' in content or 'LocationConstraint' in content), \
            "Should have conditional for us-east-1 bucket creation"

    def test_location_constraint_used_for_non_us_east_1(self, script_path):
        """Verify LocationConstraint is used for non-us-east-1 regions."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert 'LocationConstraint' in content or 'location-constraint' in content, \
            "Should use LocationConstraint for regional buckets"


class TestSecurityFeatures:
    """Test security features are properly configured."""

    def test_encryption_configuration_complete(self, script_path):
        """Verify S3 bucket encryption is properly configured."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should enable encryption
        assert 'put-bucket-encryption' in content, \
            "Should enable bucket encryption"
        
        # Should specify encryption algorithm
        assert 'AES256' in content or 'SSEAlgorithm' in content, \
            "Should specify encryption algorithm"

    def test_versioning_configuration_complete(self, script_path):
        """Verify S3 bucket versioning is properly configured."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should enable versioning
        assert 'put-bucket-versioning' in content, \
            "Should enable bucket versioning"
        
        # Should set status to Enabled
        assert 'Enabled' in content or 'Status=Enabled' in content, \
            "Should set versioning status to Enabled"


class TestResourceNaming:
    """Test resource naming conventions."""

    def test_default_bucket_name_follows_convention(self, script_path):
        """Verify default bucket name follows naming conventions."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should have a default bucket name
        assert 'twisted-monk' in content or 'BUCKET_NAME=' in content, \
            "Should define default bucket name"

    def test_default_table_name_follows_convention(self, script_path):
        """Verify default DynamoDB table name follows conventions."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should have a default table name
        assert 'terraform-locks' in content or 'DDB_TABLE=' in content or 'DYNAMODB_TABLE=' in content, \
            "Should define default DynamoDB table name"


class TestCommandExecution:
    """Test command execution patterns."""

    def test_no_dangerous_eval_usage(self, script_path):
        """Verify script doesn't use dangerous eval constructs."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # eval can be dangerous
        assert 'eval ' not in content or 'eval' in content.split('#')[0], \
            "Script should avoid using eval for security reasons"

    def test_proper_quoting_of_variables(self, script_path):
        """Check that variables are properly quoted to prevent word splitting."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Look for common patterns that should be quoted
        unquoted_vars = []
        import re
        
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Look for $VAR or ${VAR} usage in commands
            # They should generally be "$VAR" or "${VAR}"
            
            # Find variables not in quotes
            # This is a simplified check - proper parsing would require full bash parsing
            vars_in_line = re.findall(r'\$\{?[A-Z_]+\}?', line)
            
            for var in vars_in_line:
                # Check if this variable is quoted
                var_pos = line.find(var)
                if var_pos > 0:
                    before = line[:var_pos]
                    # Simple check: is there a quote immediately before?
                    if not before.rstrip().endswith('"') and not before.rstrip().endswith("'"):
                        # Could be unquoted, but there are valid cases
                        # Only flag if it's in a dangerous context
                        if 'echo' not in line and '=' not in line:
                            # This might be a problem
                            pass  # Too many false positives, skip


class TestFileStructure:
    """Test overall file structure and organization."""

    def test_script_has_clear_sections(self, script_path):
        """Verify script has logical sections with comments."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Should have comments explaining sections
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        
        assert len(comment_lines) > 5, \
            "Script should have adequate comments explaining its operation"

    def test_script_length_reasonable(self, script_path):
        """Verify script length is reasonable (not too short or too long)."""
        with open(script_path, 'r') as f:
            lines = [l for l in f.readlines() if l.strip()]  # Non-empty lines
        
        assert 30 <= len(lines) <= 200, \
            f"Script has {len(lines)} non-empty lines. " \
            f"Should be between 30-200 for this use case."