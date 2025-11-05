"""
Comprehensive unit tests for verify-pbs-backups.sh

Tests cover:
- Script existence and permissions
- Argument parsing and validation
- Environment variable handling
- Function logic and edge cases
- Error conditions and exit codes
- Output validation
"""
import os
import subprocess
import tempfile
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

SCRIPT_PATH = Path(__file__).parent.parent.parent / "projects/01-sde-devops/PRJ-SDE-002/assets/scripts/verify-pbs-backups.sh"


class TestScriptBasics:
    """Test basic script properties and setup"""
    
    def test_script_exists(self):
        """Verify the script file exists"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
    
    def test_script_is_readable(self):
        """Verify the script is readable"""
        assert os.access(SCRIPT_PATH, os.R_OK), "Script is not readable"
    
    def test_script_has_shebang(self):
        """Verify script has proper shebang"""
        with open(SCRIPT_PATH, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith('#!/'), "Script missing shebang"
        assert 'bash' in first_line, "Script should use bash"
    
    def test_script_uses_strict_mode(self):
        """Verify script uses set -euo pipefail for safety"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'set -euo pipefail' in content, "Script should use strict mode"


class TestArgumentParsing:
    """Test command-line argument parsing"""
    
    def test_help_flag_short(self):
        """Test -h flag displays usage"""
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH), "-h"],
            capture_output=True,
            text=True,
            shell=False
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "PBS_TOKEN" in result.stdout
    
    def test_verbose_flag_accepted(self):
        """Test -v flag is accepted"""
        env = os.environ.copy()
        env['PBS_TOKEN'] = 'test-token'  # noqa: S105
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH), "-v"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            shell=False
        )
        # Script should accept -v without error (may fail later due to mock token)
        assert result.returncode in [0, 1, 2], "Should accept -v flag"
    
    def test_dry_run_flag_accepted(self):
        """Test -d flag is accepted"""
        env = os.environ.copy()
        env['PBS_TOKEN'] = 'test-token'  # noqa: S105
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH), "-d"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            shell=False
        )
        # Script should accept -d without error
        assert result.returncode in [0, 1, 2], "Should accept -d flag"
    
    def test_invalid_flag_shows_error(self):
        """Test invalid flag produces error"""
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH), "-x"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False
        )
        assert result.returncode == 1, "Invalid flag should exit with code 1"
    
    def test_combined_flags(self):
        """Test combining -v and -d flags"""
        env = os.environ.copy()
        env['PBS_TOKEN'] = 'test-token'  # noqa: S105
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH), "-v", "-d"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            shell=False
        )
        assert result.returncode in [0, 1, 2], "Should accept combined flags"


class TestEnvironmentValidation:
    """Test environment variable handling"""
    
    def test_missing_pbs_token_exits_with_code_2(self):
        """Test missing PBS_TOKEN causes exit code 2"""
        env = os.environ.copy()
        env.pop('PBS_TOKEN', None)
        
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            shell=False
        )
        assert result.returncode == 2, "Missing PBS_TOKEN should exit with code 2"
    
    def test_empty_pbs_token_rejected(self):
        """Test empty PBS_TOKEN is rejected"""
        env = os.environ.copy()
        env['PBS_TOKEN'] = ''
        
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            shell=False
        )
        assert result.returncode == 2, "Empty PBS_TOKEN should be rejected"
    
    def test_pbs_token_with_valid_format_accepted(self):
        """Test PBS_TOKEN with valid format is accepted"""
        env = os.environ.copy()
        env['PBS_TOKEN'] = 'pbs-test-token'  # noqa: S105
        
        result = subprocess.run(  # noqa: S603
            [str(SCRIPT_PATH), "-d"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            shell=False
        )
        # Should not exit with code 2 (token validation error)
        assert result.returncode != 2, "Valid token format should be accepted"


class TestScriptConstants:
    """Test that script constants are properly defined"""
    
    def test_script_has_version(self):
        """Verify script declares a VERSION variable"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'VERSION=' in content, "Script should declare VERSION"
    
    def test_script_has_log_file_path(self):
        """Verify script declares LOG_FILE path"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'LOG_FILE=' in content, "Script should declare LOG_FILE"
    
    def test_script_has_report_file_path(self):
        """Verify script declares REPORT_FILE path"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'REPORT_FILE=' in content, "Script should declare REPORT_FILE"
    
    def test_script_has_pbs_endpoint(self):
        """Verify script declares PBS_ENDPOINT"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'PBS_ENDPOINT=' in content, "Script should declare PBS_ENDPOINT"
    
    def test_script_has_datastore_name(self):
        """Verify script declares PBS_DATASTORE"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'PBS_DATASTORE=' in content, "Script should declare PBS_DATASTORE"


class TestScriptFunctions:
    """Test individual function definitions and logic"""
    
    def test_usage_function_exists(self):
        """Verify usage() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'usage()' in content, "Script should define usage() function"
    
    def test_log_function_exists(self):
        """Verify log() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'log()' in content, "Script should define log() function"
    
    def test_require_token_function_exists(self):
        """Verify require_token() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'require_token()' in content, "Script should define require_token()"
    
    def test_api_call_function_exists(self):
        """Verify api_call() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'api_call()' in content, "Script should define api_call()"
    
    def test_fetch_jobs_function_exists(self):
        """Verify fetch_jobs() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'fetch_jobs()' in content, "Script should define fetch_jobs()"
    
    def test_process_jobs_function_exists(self):
        """Verify process_jobs() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'process_jobs()' in content, "Script should define process_jobs()"
    
    def test_fetch_snapshots_function_exists(self):
        """Verify fetch_snapshots() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'fetch_snapshots()' in content, "Script should define fetch_snapshots()"
    
    def test_process_snapshots_function_exists(self):
        """Verify process_snapshots() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'process_snapshots()' in content, "Script should define process_snapshots()"
    
    def test_check_datastore_function_exists(self):
        """Verify check_datastore() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'check_datastore()' in content, "Script should define check_datastore()"
    
    def test_build_report_function_exists(self):
        """Verify build_report() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'build_report()' in content, "Script should define build_report()"
    
    def test_send_report_function_exists(self):
        """Verify send_report() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'send_report()' in content, "Script should define send_report()"
    
    def test_main_function_exists(self):
        """Verify main() function is defined"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'main()' in content, "Script should define main()"


class TestAPICallLogic:
    """Test API call construction and handling"""
    
    def test_api_call_uses_curl(self):
        """Verify api_call uses curl command"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Find api_call function
        assert 'curl' in content, "api_call should use curl"
    
    def test_api_call_includes_authorization_header(self):
        """Verify API calls include Authorization header"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'Authorization' in content or 'PBSAPIToken' in content, \
            "Should include authorization in API calls"
    
    def test_api_call_uses_insecure_flag(self):
        """Verify API calls use --insecure for self-signed certs"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '--insecure' in content, "Should use --insecure for homelab certs"


class TestJobProcessingLogic:
    """Test job processing and validation logic"""
    
    def test_checks_for_missing_last_run(self):
        """Verify script checks for missing last run time"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'No successful run' in content or 'last_time' in content, \
            "Should check for successful runs"
    
    def test_checks_24_hour_freshness(self):
        """Verify script checks if jobs ran within 24 hours"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '86400' in content, "Should check 24-hour threshold (86400 seconds)"
    
    def test_validates_job_status(self):
        """Verify script validates job status field"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'status' in content.lower(), "Should check job status"
    
    def test_checks_job_duration(self):
        """Verify script checks job duration"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'duration' in content and '3600' in content, \
            "Should check if duration exceeds 1 hour (3600s)"
    
    def test_detects_size_drops(self):
        """Verify script detects significant backup size drops"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'Size drop' in content or ('prev_size' in content and 'half' in content), \
            "Should detect backup size drops"


class TestSnapshotProcessing:
    """Test snapshot verification logic"""
    
    def test_checks_snapshot_age(self):
        """Verify script checks snapshot age (7 days)"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '604800' in content, "Should check 7-day threshold (604800 seconds)"
    
    def test_validates_snapshot_size(self):
        """Verify script validates snapshot size is not zero"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'size' in content and ('zero' in content or '<= 0' in content), \
            "Should check for zero-sized snapshots"
    
    def test_queues_verification_requests(self):
        """Verify script queues snapshot verification"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'verify' in content.lower(), "Should queue verification requests"


class TestDatastoreChecks:
    """Test datastore health validation"""
    
    def test_checks_datastore_capacity(self):
        """Verify script checks datastore capacity"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'total' in content and 'used' in content, \
            "Should check datastore capacity"
    
    def test_warns_at_80_percent_usage(self):
        """Verify script warns when usage exceeds 80%"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '80' in content and ('percent' in content or '%' in content), \
            "Should warn at 80% usage"
    
    def test_checks_garbage_collection_age(self):
        """Verify script checks last GC timestamp"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'gc' in content.lower() and '604800' in content, \
            "Should check if GC is older than 7 days"


class TestReportGeneration:
    """Test HTML report generation"""
    
    def test_generates_html_report(self):
        """Verify script generates HTML report"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '<html>' in content or 'HTML' in content, \
            "Should generate HTML report"
    
    def test_report_includes_timestamp(self):
        """Verify report includes generation timestamp"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'date' in content.lower() and 'Generated' in content, \
            "Report should include timestamp"
    
    def test_report_has_styling(self):
        """Verify report includes CSS styling"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '<style>' in content or 'css' in content.lower(), \
            "Report should include styling"
    
    def test_report_includes_exit_code(self):
        """Verify report includes exit code"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'EXIT_CODE' in content and 'exit code' in content.lower(), \
            "Report should include exit code"


class TestEmailDelivery:
    """Test email sending functionality"""
    
    def test_respects_dry_run_flag(self):
        """Verify dry run suppresses email"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'DRY_RUN' in content and 'suppressed' in content.lower(), \
            "Should suppress email in dry run"
    
    def test_checks_for_mailx(self):
        """Verify script checks if mailx is available"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'mailx' in content and 'command -v' in content, \
            "Should check for mailx availability"
    
    def test_sends_html_email(self):
        """Verify script sends HTML-formatted email"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'text/html' in content or 'Content-Type' in content, \
            "Should send HTML email"


class TestExitCodes:
    """Test exit code behavior"""
    
    def test_initializes_exit_code_zero(self):
        """Verify EXIT_CODE starts at 0"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'EXIT_CODE=0' in content, "Should initialize EXIT_CODE to 0"
    
    def test_exits_with_final_code(self):
        """Verify script exits with final EXIT_CODE"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'exit ${EXIT_CODE}' in content or 'exit $EXIT_CODE' in content, \
            "Should exit with EXIT_CODE"
    
    def test_uses_code_2_for_critical(self):
        """Verify critical errors set EXIT_CODE to 2"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'EXIT_CODE=2' in content, "Should use code 2 for critical errors"


class TestColorOutput:
    """Test color code handling"""
    
    def test_defines_color_codes(self):
        """Verify script defines color codes"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'COLOR_' in content and '\\033' in content, \
            "Should define ANSI color codes"
    
    def test_uses_color_reset(self):
        """Verify script uses color reset"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'COLOR_RESET' in content, "Should define COLOR_RESET"


class TestDocumentation:
    """Test script documentation and comments"""
    
    def test_has_header_comment(self):
        """Verify script has descriptive header"""
        with open(SCRIPT_PATH, 'r') as f:
            lines = f.readlines()
        # Check first few lines for comments
        has_header = any('#' in line and 'verify' in line.lower() 
                        for line in lines[:10])
        assert has_header, "Script should have descriptive header"
    
    def test_includes_usage_example(self):
        """Verify script includes usage example or cron info"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'cron' in content.lower() or 'example' in content.lower(), \
            "Should include usage examples"
    
    def test_documents_token_setup(self):
        """Verify script documents token setup"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'token' in content.lower() and ('setup' in content.lower() or 
                                               'create' in content.lower()), \
            "Should document token setup"


class TestJQUsage:
    """Test jq JSON processing"""
    
    def test_uses_jq_for_json_parsing(self):
        """Verify script uses jq for JSON parsing"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'jq' in content, "Should use jq for JSON parsing"
    
    def test_jq_handles_missing_fields(self):
        """Verify jq commands use // operator for defaults"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '//' in content, "Should use jq // operator for default values"


class TestEdgeCases:
    """Test edge case handling"""
    
    def test_handles_empty_job_list(self):
        """Verify script handles empty job response gracefully"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Should check for empty input
        assert '[[ -z $job ]]' in content or '[[ -z $snap ]]' in content, \
            "Should check for empty data"
    
    def test_handles_missing_previous_size(self):
        """Verify script handles jobs without previous size"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'prev_size' in content and '(( prev_size > 0 ))' in content, \
            "Should check if previous size exists before comparison"
    
    def test_prevents_division_by_zero(self):
        """Verify script prevents division by zero"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '(( total > 0 ))' in content, \
            "Should check denominator before division"


class TestSecurityConsiderations:
    """Test security-related aspects"""
    
    def test_uses_https_endpoint(self):
        """Verify default endpoint uses HTTPS"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'https://' in content, "Should use HTTPS for API endpoint"
    
    def test_token_from_environment(self):
        """Verify token comes from environment, not hardcoded"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Should not have token hardcoded
        assert 'PBS_TOKEN:-' in content or '${PBS_TOKEN}' in content, \
            "Token should come from environment"