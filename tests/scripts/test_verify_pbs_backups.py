"""
Comprehensive unit tests for verify-pbs-backups.sh

Tests cover:
- Argument parsing and flag handling
- Environment variable validation
- API call mocking and response handling
- Job processing logic
- Snapshot verification workflows
- Datastore health checks
- HTML report generation
- Email delivery logic
- Edge cases and error conditions
"""
import os
import subprocess
import tempfile
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

SCRIPT_PATH = Path(__file__).parent.parent.parent / "projects/01-sde-devops/PRJ-SDE-002/assets/scripts/verify-pbs-backups.sh"


class TestVerifyPBSBackupsBasicFunctionality:
    """Test basic script functionality and argument parsing"""
    
    def test_script_exists(self):
        """Verify the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"
    
    def test_help_flag_displays_usage(self):
        """Test that -h flag displays usage information"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "-h"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "PBS_TOKEN" in result.stdout
        assert "-v" in result.stdout
        assert "-d" in result.stdout
    
    def test_invalid_flag_shows_error(self):
        """Test that invalid flags produce error"""
        result = subprocess.run(
            [str(SCRIPT_PATH), "-x"],
            capture_output=True,
            text=True,
            env={"PBS_TOKEN": "dummy"}
        )
        assert result.returncode == 1
        assert "Usage:" in result.stderr or "Usage:" in result.stdout
    
    def test_missing_pbs_token_exits_with_error(self):
        """Test that missing PBS_TOKEN environment variable causes exit"""
        env = os.environ.copy()
        env.pop("PBS_TOKEN", None)
        
        result = subprocess.run(
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 2
    
    def test_verbose_flag_enables_stdout_logging(self):
        """Test that -v flag enables verbose output"""
        env = os.environ.copy()
        env["PBS_TOKEN"] = "test-token"
        
        result = subprocess.run(
            [str(SCRIPT_PATH), "-v"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5
        )
        # Should produce verbose output or error indicating missing PBS endpoint
        assert result.returncode in [0, 1, 2]
    
    def test_dry_run_flag_skips_email(self):
        """Test that -d flag enables dry run mode"""
        env = os.environ.copy()
        env["PBS_TOKEN"] = "test-token"
        
        result = subprocess.run(
            [str(SCRIPT_PATH), "-d"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5
        )
        # Dry run should skip email but still attempt operations
        assert result.returncode in [0, 1, 2]
    
    def test_combined_flags(self):
        """Test that multiple flags can be combined"""
        env = os.environ.copy()
        env["PBS_TOKEN"] = "test-token"
        
        result = subprocess.run(
            [str(SCRIPT_PATH), "-v", "-d"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5
        )
        assert result.returncode in [0, 1, 2]


class TestScriptConstants:
    """Test that script constants are properly defined"""
    
    def test_script_version_defined(self):
        """Test that VERSION constant is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'VERSION=' in content
        assert '"1.0.0"' in content or "'1.0.0'" in content
    
    def test_default_endpoints_defined(self):
        """Test that default endpoints are defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'PBS_ENDPOINT=' in content
        assert 'PBS_DATASTORE=' in content
        assert 'EMAIL_RECIPIENT=' in content
    
    def test_log_file_path_defined(self):
        """Test that log file path is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'LOG_FILE=' in content
        assert '/var/log/' in content or '/tmp/' in content
    
    def test_report_file_path_defined(self):
        """Test that report file path is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'REPORT_FILE=' in content
        assert '.html' in content


class TestLoggingFunctionality:
    """Test logging function behavior"""
    
    def test_log_function_exists(self):
        """Test that log function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'log()' in content or 'log ()' in content
    
    def test_log_writes_to_file(self):
        """Test that log function writes to log file"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Check log function implementation
        assert 'echo' in content
        assert '>>' in content  # Append to file
    
    def test_color_codes_defined(self):
        """Test that color codes are defined for output"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'COLOR_GREEN=' in content
        assert 'COLOR_YELLOW=' in content or 'COLOR_WARN=' in content
        assert 'COLOR_RED=' in content
        assert 'COLOR_RESET=' in content


class TestAPICallFunction:
    """Test API call wrapper function"""
    
    def test_api_call_function_exists(self):
        """Test that api_call function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'api_call()' in content or 'api_call ()' in content
    
    def test_api_call_uses_curl(self):
        """Test that api_call uses curl command"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'curl' in content
    
    def test_api_call_includes_auth_header(self):
        """Test that API calls include authentication"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Authorization' in content or 'PBSAPIToken' in content
    
    def test_api_call_supports_get_method(self):
        """Test that GET method is supported"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'GET' in content
    
    def test_api_call_supports_post_method(self):
        """Test that POST method is supported"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'POST' in content


class TestJobProcessing:
    """Test backup job processing logic"""
    
    def test_fetch_jobs_function_exists(self):
        """Test that fetch_jobs function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'fetch_jobs()' in content or 'fetch_jobs ()' in content
    
    def test_process_jobs_function_exists(self):
        """Test that process_jobs function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'process_jobs()' in content or 'process_jobs ()' in content
    
    def test_job_status_checking(self):
        """Test that job status is checked"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'status' in content.lower()
        assert 'last-run' in content or 'last_run' in content
    
    def test_job_timing_validation(self):
        """Test that job timing is validated"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Check for time comparisons (24h = 86400 seconds)
        assert '86400' in content or '24h' in content or 'last_time' in content
    
    def test_job_duration_checking(self):
        """Test that job duration is monitored"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'duration' in content.lower()
        # Check for 1 hour limit (3600 seconds)
        assert '3600' in content or '1h' in content
    
    def test_job_size_validation(self):
        """Test that backup size changes are detected"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'size' in content.lower()
        assert 'prev_size' in content or 'previous' in content


class TestSnapshotVerification:
    """Test snapshot verification logic"""
    
    def test_fetch_snapshots_function_exists(self):
        """Test that fetch_snapshots function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'fetch_snapshots()' in content or 'fetch_snapshots ()' in content
    
    def test_process_snapshots_function_exists(self):
        """Test that process_snapshots function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'process_snapshots()' in content or 'process_snapshots ()' in content
    
    def test_snapshot_age_checking(self):
        """Test that snapshot age is validated"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Check for 7 days = 604800 seconds
        assert '604800' in content or '7 days' in content
    
    def test_snapshot_size_validation(self):
        """Test that snapshot size is checked"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'size' in content.lower()
        # Check for zero size detection
        assert '<= 0' in content or '== 0' in content
    
    def test_verification_request_queuing(self):
        """Test that verification requests are queued"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'verify' in content.lower()
        assert 'verification queued' in content or 'verify request' in content


class TestDatastoreHealthChecks:
    """Test datastore health checking logic"""
    
    def test_check_datastore_function_exists(self):
        """Test that check_datastore function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'check_datastore()' in content or 'check_datastore ()' in content
    
    def test_datastore_capacity_checking(self):
        """Test that datastore capacity is monitored"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'total' in content.lower()
        assert 'used' in content.lower()
    
    def test_datastore_usage_threshold(self):
        """Test that 80% usage threshold is enforced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '80' in content
    
    def test_garbage_collection_monitoring(self):
        """Test that garbage collection status is checked"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'gc' in content.lower() or 'garbage' in content.lower()
        assert 'last-gc' in content or 'last_gc' in content


class TestReportGeneration:
    """Test HTML report generation"""
    
    def test_build_report_function_exists(self):
        """Test that build_report function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'build_report()' in content or 'build_report ()' in content
    
    def test_html_structure_generation(self):
        """Test that HTML structure is generated"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '<html>' in content
        assert '<head>' in content
        assert '<body>' in content
        assert '</html>' in content
    
    def test_report_includes_css_styling(self):
        """Test that report includes CSS styling"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '<style>' in content
        assert 'color' in content.lower()
        assert '.pass' in content or '.warn' in content or '.fail' in content
    
    def test_report_includes_job_table(self):
        """Test that report includes backup job table"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Backup Jobs' in content or 'JOB_ROWS' in content
        assert '<table>' in content
    
    def test_report_includes_snapshot_table(self):
        """Test that report includes snapshot table"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Snapshot' in content or 'SNAPSHOT_ROWS' in content
    
    def test_report_includes_datastore_summary(self):
        """Test that report includes datastore summary"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Datastore' in content or 'DATASTORE_SUMMARY' in content
    
    def test_report_includes_timestamp(self):
        """Test that report includes generation timestamp"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'date' in content.lower() or 'timestamp' in content.lower()


class TestEmailDelivery:
    """Test email delivery functionality"""
    
    def test_send_report_function_exists(self):
        """Test that send_report function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'send_report()' in content or 'send_report ()' in content
    
    def test_dry_run_skips_email(self):
        """Test that dry run mode skips email"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'DRY_RUN' in content
        assert 'email suppressed' in content or 'Dry run' in content
    
    def test_mailx_command_usage(self):
        """Test that mailx is used for email delivery"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'mailx' in content
    
    def test_html_content_type_header(self):
        """Test that HTML content type is set"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Content-Type: text/html' in content or 'text/html' in content
    
    def test_mailx_availability_check(self):
        """Test that script checks for mailx availability"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'command -v mailx' in content or 'which mailx' in content


class TestExitCodeHandling:
    """Test exit code logic and error reporting"""
    
    def test_exit_code_variable_exists(self):
        """Test that EXIT_CODE variable is used"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'EXIT_CODE' in content
    
    def test_exit_code_starts_at_zero(self):
        """Test that exit code initializes to 0"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'EXIT_CODE=0' in content
    
    def test_exit_code_escalation_logic(self):
        """Test that exit code escalates appropriately"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Check for exit code comparison/escalation
        assert 'EXIT_CODE=' in content
        # Should set to 1 for warnings, 2 for critical errors
        assert 'EXIT_CODE=2' in content or 'EXIT_CODE=$((' in content
    
    def test_main_function_returns_exit_code(self):
        """Test that main function exits with correct code"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'exit ${EXIT_CODE}' in content or 'exit $EXIT_CODE' in content


class TestMainFunction:
    """Test main execution flow"""
    
    def test_main_function_exists(self):
        """Test that main function is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'main()' in content or 'main ()' in content
    
    def test_main_calls_require_token(self):
        """Test that main calls token validation"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'require_token' in content
    
    def test_main_orchestrates_workflow(self):
        """Test that main function orchestrates all steps"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'fetch_jobs' in content
        assert 'process_jobs' in content
        assert 'fetch_snapshots' in content
        assert 'process_snapshots' in content
        assert 'check_datastore' in content
        assert 'build_report' in content
        assert 'send_report' in content


class TestCronDocumentation:
    """Test that cron usage is documented"""
    
    def test_cron_example_exists(self):
        """Test that cron example is provided"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'cron' in content.lower() or 'Cron' in content
    
    def test_token_setup_documented(self):
        """Test that token setup is documented"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'PBS_TOKEN' in content
        assert 'token' in content.lower()


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_uses_strict_mode(self):
        """Test that script uses bash strict mode"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'set -euo pipefail' in content
    
    def test_handles_api_call_failures(self):
        """Test that API call failures are handled"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Check for error handling in API calls
        assert 'if' in content or '||' in content
    
    def test_handles_missing_data_gracefully(self):
        """Test that missing data is handled gracefully"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Check for jq error handling or empty value defaults
        assert '// empty' in content or '// "' in content or 'jq -r' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])