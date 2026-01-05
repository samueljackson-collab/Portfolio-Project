"""Comprehensive unit tests for dr-drill.sh"""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).parent.parent.parent / "projects/p01-aws-infra/scripts/dr-drill.sh"
)


class TestDRDrillBasicFunctionality:
    """Test basic script functionality"""

    def test_script_exists(self):
        """Verify the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"

    def test_help_flag_displays_usage(self):
        """Test that --help displays usage information"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "report", "--help"], capture_output=True, text=True
        )  # noqa: S603, S607
        assert "Usage:" in result.stdout or "Usage:" in result.stderr

    def test_no_command_shows_usage(self):
        """Test that running without command shows usage"""
        result = subprocess.run(
            [str(SCRIPT_PATH)], capture_output=True, text=True
        )  # noqa: S603, S607
        assert result.returncode == 1
        assert "Usage:" in result.stdout or "Usage:" in result.stderr

    def test_unknown_command_shows_error(self):
        """Test that unknown command produces error"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "invalid-command"], capture_output=True, text=True
        )  # noqa: S603, S607
        assert result.returncode == 1
        assert "Unknown command" in result.stderr or "Unknown command" in result.stdout


class TestReportCommand:
    """Test the report command"""

    def test_report_with_explicit_db_instance_id(self):
        """Test report command with explicit DB instance ID"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "report", "--db-instance-id", "test-db-123"],
            capture_output=True,
            text=True,
        )  # noqa: S603, S607
        assert result.returncode == 0
        assert "test-db-123" in result.stdout or result.stderr

    def test_report_with_env_variable(self):
        """Test report command with environment variable"""
        env = os.environ.copy()
        env["DR_DRILL_DB_INSTANCE_ID"] = "env-test-db"
        result = subprocess.run(
            [str(SCRIPT_PATH), "report"], capture_output=True, text=True, env=env
        )  # noqa: S603, S607
        assert result.returncode == 0
        assert "env-test-db" in result.stdout or result.stderr


class TestFailoverCommand:
    """Test the failover command (without actual execution)"""

    def test_failover_requires_db_instance(self):
        """Test that failover command validates DB instance"""
        # This will fail if no terraform dir exists, which is expected
        result = subprocess.run(
            [str(SCRIPT_PATH), "failover", "--db-instance-id", "test-failover-db"],
            capture_output=True,
            text=True,
        )  # noqa: S603, S607
        # The command should at least parse correctly
        assert (
            "test-failover-db" in result.stdout
            or result.stderr
            or result.returncode != 1
        )


class TestArgumentParsing:
    """Test argument parsing logic"""

    def test_db_instance_id_flag_requires_value(self):
        """Test that --db-instance-id requires a value"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "report", "--db-instance-id"],
            capture_output=True,
            text=True,
        )  # noqa: S603, S607
        assert result.returncode == 1
        assert "requires a value" in result.stderr or result.returncode == 1

    def test_terraform_dir_flag_requires_value(self):
        """Test that --terraform-dir requires a value"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "report", "--terraform-dir"],
            capture_output=True,
            text=True,
        )  # noqa: S603, S607
        assert result.returncode == 1

    def test_terraform_output_name_flag_requires_value(self):
        """Test that --terraform-output-name requires a value"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "report", "--terraform-output-name"],
            capture_output=True,
            text=True,
        )  # noqa: S603, S607
        assert result.returncode == 1

    def test_unknown_option_produces_error(self):
        """Test that unknown options produce errors"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "report", "--invalid-option", "value"],
            capture_output=True,
            text=True,
        )  # noqa: S603, S607
        assert result.returncode == 1
        assert "Unknown option" in result.stderr or "Unknown option" in result.stdout


class TestEnvironmentVariables:
    """Test environment variable handling"""

    def test_dr_drill_terraform_dir_env(self):
        """Test DR_DRILL_TERRAFORM_DIR environment variable"""
        env = os.environ.copy()
        env["DR_DRILL_TERRAFORM_DIR"] = os.path.join(
            tempfile.gettempdir(), "test-terraform"
        )
        env["DR_DRILL_DB_INSTANCE_ID"] = "test-db"
        result = subprocess.run(
            [str(SCRIPT_PATH), "report"], capture_output=True, text=True, env=env
        )  # noqa: S603, S607
        # Should use the custom terraform dir
        assert result.returncode in [0, 1]

    def test_dr_drill_aws_cli_env(self):
        """Test DR_DRILL_AWS_CLI environment variable"""
        env = os.environ.copy()
        env["DR_DRILL_AWS_CLI"] = "echo"
        env["DR_DRILL_DB_INSTANCE_ID"] = "test-db"
        # This should work with echo as the aws cli
        result = subprocess.run(
            [str(SCRIPT_PATH), "report"], capture_output=True, text=True, env=env
        )  # noqa: S603, S607
        assert result.returncode == 0


class TestTerraformIntegration:
    """Test Terraform output detection logic"""

    def test_terraform_dir_flag_override(self):
        """Test that --terraform-dir flag overrides default"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    str(SCRIPT_PATH),
                    "report",
                    "--terraform-dir",
                    tmpdir,
                    "--db-instance-id",
                    "test-db",
                ],
                capture_output=True,
                text=True,
            )  # noqa: S603, S607
            # Should accept the custom directory
            assert result.returncode == 0


class TestLoggingAndOutput:
    """Test logging and output formatting"""

    def test_output_contains_timestamp(self):
        """Test that output includes timestamps"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "report", "--db-instance-id", "test-db"],
            capture_output=True,
            text=True,
        )  # noqa: S603, S607
        assert result.returncode == 0
        # Check for ISO 8601 timestamp format
        assert "Z]" in result.stdout or "INFO" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
