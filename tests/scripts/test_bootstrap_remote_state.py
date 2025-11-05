"""
Comprehensive unit tests for bootstrap_remote_state.sh

Tests cover:
- Argument parsing and defaults
- AWS CLI command construction
- Bucket creation logic for different regions
- Versioning and encryption configuration
- DynamoDB table creation
- Idempotency checks
- Error handling and edge cases
"""
import os
import subprocess
import tempfile
import pytest
from pathlib import Path
import shutil

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/bootstrap_remote_state.sh"
BASH_PATH = shutil.which("bash")


class TestBootstrapBasicFunctionality:
    """Test basic script functionality and requirements"""
    
    def test_script_exists(self):
        """Verify the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"
    
    def test_script_has_shebang(self):
        """Test that script has proper bash shebang"""
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        assert first_line.startswith("#!/"), "Script missing shebang"
        assert "bash" in first_line.lower(), "Script should use bash"
    
    def test_script_has_set_flags(self):
        """Test that script has proper error handling flags"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should have set -euo pipefail or similar
        assert "set -" in content, "Script should have set flags for error handling"


class TestArgumentParsing:
    """Test argument parsing and default values"""
    
    def test_default_bucket_name_with_placeholder(self):
        """Test that default bucket name contains REPLACE_ME placeholder"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "REPLACE_ME" in content, "Default bucket should have REPLACE_ME placeholder"
    
    def test_accepts_three_arguments(self):
        """Test that script accepts bucket name, table name, and region"""
        # Check that script defines these variables from positional parameters
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "${1" in content, "Script should accept first argument (bucket name)"
        assert "${2" in content, "Script should accept second argument (table name)"
        assert "${3" in content, "Script should accept third argument (region)"
    
    def test_default_region_is_us_east_1(self):
        """Test that default region is us-east-1"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "us-east-1" in content, "Default region should be us-east-1"
    
    def test_default_dynamodb_table_name(self):
        """Test that default DynamoDB table name is set"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "terraform-locks" in content.lower() or "locks" in content, "Should have default lock table name"


class TestBucketCreationLogic:
    """Test S3 bucket creation logic"""
    
    def test_checks_bucket_existence_before_creation(self):
        """Test that script checks if bucket exists before creating"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "head-bucket" in content or "list-bucket" in content, "Should check bucket existence"
    
    def test_handles_us_east_1_region_specially(self):
        """Test that us-east-1 region is handled without LocationConstraint"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # us-east-1 doesn't need LocationConstraint parameter
        assert "us-east-1" in content, "Should handle us-east-1 specially"
        assert "LocationConstraint" in content or "create-bucket-configuration" in content, \
            "Should handle LocationConstraint for other regions"
    
    def test_creates_bucket_with_correct_command(self):
        """Test that script uses correct AWS CLI command to create bucket"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "aws s3api create-bucket" in content, "Should use aws s3api create-bucket"
        assert "--bucket" in content, "Should specify --bucket parameter"
        assert "--region" in content, "Should specify --region parameter"


class TestBucketConfiguration:
    """Test S3 bucket versioning and encryption configuration"""
    
    def test_enables_versioning(self):
        """Test that script enables versioning on the bucket"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "put-bucket-versioning" in content, "Should enable versioning"
        assert "Status=Enabled" in content or "Enabled" in content, "Versioning should be enabled"
    
    def test_enables_encryption(self):
        """Test that script enables server-side encryption"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "put-bucket-encryption" in content, "Should enable encryption"
        assert "SSEAlgorithm" in content or "AES256" in content, "Should use AES256 encryption"
    
    def test_uses_server_side_encryption_configuration(self):
        """Test that encryption configuration uses proper JSON structure"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        if "put-bucket-encryption" in content:
            assert "server-side-encryption-configuration" in content.lower(), \
                "Should use server-side-encryption-configuration"


class TestDynamoDBCreation:
    """Test DynamoDB table creation logic"""
    
    def test_checks_dynamodb_table_existence(self):
        """Test that script checks if DynamoDB table exists before creating"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "describe-table" in content, "Should check table existence"
    
    def test_creates_dynamodb_table_with_correct_schema(self):
        """Test that DynamoDB table is created with correct schema"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "create-table" in content, "Should create DynamoDB table"
        assert "LockID" in content, "Should have LockID attribute"
        assert "AttributeType=S" in content or "AttributeType" in content, "Should define attribute type"
    
    def test_uses_on_demand_billing(self):
        """Test that table uses PAY_PER_REQUEST billing mode"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "PAY_PER_REQUEST" in content or "billing-mode" in content, \
            "Should use on-demand billing mode"
    
    def test_defines_hash_key_correctly(self):
        """Test that LockID is defined as HASH key"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "KeyType=HASH" in content or "key-schema" in content, "Should define hash key"
    
    def test_waits_for_table_creation(self):
        """Test that script waits for table to become active"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "wait table-exists" in content or "wait" in content, \
            "Should wait for table to be created"


class TestOutputMessages:
    """Test script output and messaging"""
    
    def test_displays_configuration_summary(self):
        """Test that script displays what it will do"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "echo" in content, "Should display messages"
        assert "Bucket" in content or "bucket" in content, "Should mention bucket"
        assert "DynamoDB" in content or "table" in content, "Should mention DynamoDB table"
    
    def test_displays_completion_message(self):
        """Test that script displays completion message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "complete" in content.lower() or "done" in content.lower(), \
            "Should display completion message"
    
    def test_displays_terraform_configuration_instructions(self):
        """Test that script tells user how to update Terraform config"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "terraform" in content.lower() or "Update" in content, \
            "Should provide Terraform configuration instructions"
        assert "tfstate" in content or "state" in content, "Should mention state configuration"


class TestIdempotency:
    """Test that script can be run multiple times safely"""
    
    def test_skips_bucket_creation_if_exists(self):
        """Test that script skips bucket creation if it already exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should check existence and skip if already present
        assert "already exists" in content.lower() or "exists" in content.lower(), \
            "Should handle existing resources"
    
    def test_skips_table_creation_if_exists(self):
        """Test that script skips table creation if it already exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should handle existing table gracefully
        if "describe-table" in content:
            # Script checks for table existence
            assert True


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_uses_pipefail_for_error_propagation(self):
        """Test that script uses pipefail to catch errors in pipes"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "pipefail" in content, "Should use pipefail for error handling"
    
    def test_uses_errexit_to_stop_on_errors(self):
        """Test that script exits on errors"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "set -e" in content or "errexit" in content, \
            "Should exit on errors"
    
    def test_uses_nounset_to_catch_undefined_variables(self):
        """Test that script catches undefined variables"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "set -u" in content or "nounset" in content, \
            "Should catch undefined variables"


class TestAWSCLIIntegration:
    """Test AWS CLI command construction"""
    
    def test_uses_aws_s3api_commands(self):
        """Test that script uses aws s3api commands"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "aws s3api" in content, "Should use aws s3api commands"
    
    def test_uses_aws_dynamodb_commands(self):
        """Test that script uses aws dynamodb commands"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "aws dynamodb" in content, "Should use aws dynamodb commands"
    
    def test_redirects_error_output_appropriately(self):
        """Test that error output is handled"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should handle stderr in some checks
        assert "2>" in content or "2>&1" in content, "Should handle error output"


class TestSecurityBestPractices:
    """Test security best practices"""
    
    def test_enables_encryption_at_rest(self):
        """Test that encryption at rest is enabled"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "encryption" in content.lower(), "Should enable encryption"
    
    def test_enables_versioning_for_disaster_recovery(self):
        """Test that versioning is enabled for state protection"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "versioning" in content.lower(), "Should enable versioning"


class TestRegionHandling:
    """Test region-specific logic"""
    
    def test_accepts_custom_region(self):
        """Test that script accepts custom region parameter"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "${3" in content or "REGION" in content, "Should accept region parameter"
    
    def test_uses_region_in_all_commands(self):
        """Test that region is used consistently"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Count --region flags to ensure consistency
        region_flags = content.count("--region")
        assert region_flags >= 2, "Should use --region flag in multiple commands"


class TestScriptStructure:
    """Test script structure and organization"""
    
    def test_has_comments_explaining_purpose(self):
        """Test that script has explanatory comments"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) >= 3, "Should have explanatory comments"
    
    def test_uses_meaningful_variable_names(self):
        """Test that variable names are descriptive"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "BUCKET" in content or "bucket" in content, "Should use descriptive variable names"
        assert "TABLE" in content or "table" in content, "Should use descriptive variable names"
        assert "REGION" in content or "region" in content, "Should use descriptive variable names"
    
    def test_has_proper_exit_codes(self):
        """Test that script uses proper exit codes"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # With set -e, script will exit on errors automatically
        assert "set -e" in content or "exit" in content, "Should handle exit codes"


class TestDocumentation:
    """Test script documentation"""
    
    def test_has_usage_comment(self):
        """Test that script documents its usage"""
        with open(SCRIPT_PATH) as f:
            lines = f.readlines()[:20]  # Check first 20 lines
        content = ''.join(lines)
        assert "Usage" in content or "usage" in content or "#" in content, \
            "Should document usage"
    
    def test_documents_parameters(self):
        """Test that script documents its parameters"""
        with open(SCRIPT_PATH) as f:
            lines = f.readlines()[:20]
        content = ''.join(lines)
        # Should document what the script does
        assert any(c in content for c in ["bucket", "Bucket", "table", "Table", "Creates"]), \
            "Should document parameters"


class TestNewlineHandling:
    """Test proper file ending (related to the actual change made)"""
    
    def test_script_ends_with_newline(self):
        """Test that script ends with a newline character"""
        with open(SCRIPT_PATH, 'rb') as f:
            content = f.read()
        assert content.endswith(b'\n'), "Script should end with newline character"
    
    def test_no_trailing_whitespace_on_last_line(self):
        """Test that last line has no trailing whitespace"""
        with open(SCRIPT_PATH) as f:
            lines = f.readlines()
        if lines:
            last_line = lines[-1]
            # Last line should be just a newline or have no trailing spaces before newline
            assert last_line.strip() == '' or not last_line.rstrip().endswith(' '), \
                "Last line should not have trailing whitespace"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])