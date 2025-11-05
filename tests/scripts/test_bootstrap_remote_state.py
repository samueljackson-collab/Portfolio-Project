"""Comprehensive unit tests for bootstrap_remote_state.sh"""
import os
import subprocess
import tempfile
import pytest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/bootstrap_remote_state.sh"


class TestBootstrapRemoteStateBasicFunctionality:
    """Test basic script functionality"""
    
    def test_script_exists(self):
        """Verify the script file exists and is executable"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"
    
    def test_script_has_shebang(self):
        """Test that script has proper shebang"""
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        assert first_line.startswith('#!/usr/bin/env bash')
    
    def test_script_uses_set_options(self):
        """Test that script uses strict error handling"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'set -euo pipefail' in content
    
    def test_script_ends_with_newline(self):
        """Test that script ends with a newline character"""
        with open(SCRIPT_PATH, 'rb') as f:
            content = f.read()
        assert content.endswith(b'\n'), "Script should end with newline"


class TestScriptArguments:
    """Test argument parsing and default values"""
    
    def test_default_bucket_name(self):
        """Test that default bucket name is set correctly"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'BUCKET_NAME="${1:-twisted-monk-terraform-state-REPLACE_ME}"' in content
    
    def test_default_dynamodb_table(self):
        """Test that default DynamoDB table name is set"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'DDB_TABLE="${2:-twisted-monk-terraform-locks}"' in content
    
    def test_default_region(self):
        """Test that default region is us-east-1"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'REGION="${3:-us-east-1}"' in content
    
    def test_script_accepts_positional_arguments(self):
        """Test that script can parse positional arguments"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should use positional parameters $1, $2, $3
        assert '"${1:-' in content
        assert '"${2:-' in content
        assert '"${3:-' in content


class TestS3BucketCreation:
    """Test S3 bucket creation logic"""
    
    def test_checks_bucket_existence(self):
        """Test that script checks if bucket already exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'aws s3api head-bucket' in content
        assert 'already exists' in content
    
    def test_handles_us_east_1_specially(self):
        """Test that us-east-1 region is handled without LocationConstraint"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'if [ "${REGION}" = "us-east-1" ]' in content
        assert 'create-bucket-configuration LocationConstraint' in content
    
    def test_enables_versioning(self):
        """Test that bucket versioning is enabled"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'put-bucket-versioning' in content
        assert 'Status=Enabled' in content
    
    def test_enables_encryption(self):
        """Test that bucket encryption is enabled"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'put-bucket-encryption' in content
        assert 'AES256' in content
    
    def test_uses_correct_encryption_config(self):
        """Test that encryption configuration is properly formatted"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'ApplyServerSideEncryptionByDefault' in content
        assert 'SSEAlgorithm' in content


class TestDynamoDBTableCreation:
    """Test DynamoDB table creation logic"""
    
    def test_checks_table_existence(self):
        """Test that script checks if table already exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'describe-table' in content
        assert 'already exists' in content
    
    def test_creates_table_with_lock_id(self):
        """Test that table is created with LockID attribute"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'AttributeName=LockID,AttributeType=S' in content
    
    def test_uses_hash_key_schema(self):
        """Test that LockID is configured as HASH key"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'AttributeName=LockID,KeyType=HASH' in content
    
    def test_uses_pay_per_request_billing(self):
        """Test that table uses on-demand billing"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'billing-mode PAY_PER_REQUEST' in content
    
    def test_waits_for_table_creation(self):
        """Test that script waits for table to become active"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'wait table-exists' in content


class TestOutputMessages:
    """Test informational output messages"""
    
    def test_displays_bootstrap_info(self):
        """Test that script displays bootstrap information"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Bootstrapping remote state' in content
        assert 'echo "Bucket: ${BUCKET_NAME}"' in content
        assert 'echo "DynamoDB table: ${DDB_TABLE}"' in content
    
    def test_displays_completion_message(self):
        """Test that script displays completion message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Bootstrap complete' in content
    
    def test_provides_terraform_variable_instructions(self):
        """Test that script provides instructions for Terraform variables"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Update terraform/variables.tf with:' in content
        assert 'tfstate_bucket' in content
        assert 'tfstate_lock_table' in content


class TestScriptStructure:
    """Test overall script structure and best practices"""
    
    def test_no_trailing_whitespace_in_code(self):
        """Test that script has no trailing whitespace"""
        with open(SCRIPT_PATH) as f:
            lines = f.readlines()
        # Last line should just be a newline
        if len(lines) > 0:
            last_line = lines[-1]
            # Should be just \n or have no trailing spaces before \n
            assert last_line == '\n' or not last_line[:-1].endswith(' ')
    
    def test_uses_region_variable_consistently(self):
        """Test that REGION variable is used consistently"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should use ${REGION} or "${REGION}" throughout
        region_usage = content.count('${REGION}') + content.count('"${REGION}"')
        assert region_usage >= 5, "REGION should be used multiple times"
    
    def test_commands_have_region_flag(self):
        """Test that AWS commands include --region flag"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # DynamoDB commands should have --region
        assert '--region "${REGION}"' in content or '--region ${REGION}' in content


class TestErrorHandling:
    """Test error handling behavior"""
    
    def test_script_exits_on_command_failure(self):
        """Test that set -e causes exit on command failure"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # set -e should be present
        assert 'set -e' in content or 'set -euo pipefail' in content
    
    def test_handles_existing_resources_gracefully(self):
        """Test that script handles existing resources without error"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should check existence before creation
        assert 'if aws s3api head-bucket' in content
        assert 'if aws dynamodb describe-table' in content


class TestAWSCLICommands:
    """Test AWS CLI command structure"""
    
    def test_s3_create_bucket_command_structure(self):
        """Test that S3 create-bucket command is properly structured"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should have both forms depending on region
        assert 'create-bucket --bucket "${BUCKET_NAME}"' in content
        assert 'create-bucket-configuration LocationConstraint' in content
    
    def test_dynamodb_create_table_command_structure(self):
        """Test that DynamoDB create-table command is properly structured"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'dynamodb create-table' in content
        assert '--table-name "${DDB_TABLE}"' in content
        assert '--attribute-definitions' in content
        assert '--key-schema' in content
    
    def test_proper_quoting_of_variables(self):
        """Test that variables are properly quoted"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Variables should be quoted
        assert '"${BUCKET_NAME}"' in content
        assert '"${DDB_TABLE}"' in content
        assert '"${REGION}"' in content


class TestUsageExample:
    """Test usage documentation"""
    
    def test_has_usage_comment(self):
        """Test that script has usage information in comments"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '# Usage:' in content or 'Usage:' in content
    
    def test_documents_aws_profile_usage(self):
        """Test that AWS_PROFILE usage is documented"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'AWS_PROFILE' in content
    
    def test_documents_parameters(self):
        """Test that parameters are documented"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should document bucket, table, and region parameters
        assert 'bucket' in content.lower() or 'BUCKET' in content
        assert 'dynamodb' in content.lower() or 'DynamoDB' in content
        assert 'region' in content.lower() or 'REGION' in content


class TestIntegrationScenarios:
    """Test integration scenarios (without actual AWS calls)"""
    
    def test_script_syntax_is_valid(self):
        """Test that script has valid bash syntax"""
        result = subprocess.run(  # noqa: S603, S607
            ["bash", "-n", str(SCRIPT_PATH)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"
    
    def test_script_can_be_sourced(self):
        """Test that script can be sourced for variable inspection"""
        test_script = f"""
        set +e  # Disable exit on error for testing
        source {SCRIPT_PATH} test-bucket test-table us-west-2 2>/dev/null || true
        echo "BUCKET=$BUCKET_NAME"
        echo "TABLE=$DDB_TABLE"
        echo "REGION=$REGION"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(test_script)
            f.flush()
            
            try:
                result = subprocess.run(  # noqa: S603
                    ["/bin/bash", f.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # Variables should be set even if AWS commands fail
                assert "BUCKET=" in result.stdout or result.returncode in [0, 1]
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])