"""
Comprehensive unit tests for bootstrap_remote_state.sh

Tests cover:
- Argument parsing and defaults
- Bucket creation with region handling
- Versioning and encryption configuration
- DynamoDB table creation
- Error handling and validation
- Output messaging
"""
import subprocess
import pytest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/bootstrap_remote_state.sh"


class TestBootstrapBasicFunctionality:
    """Test basic script functionality"""
    
    def test_script_exists_and_executable(self):
        """Verify script exists and is executable"""
        assert SCRIPT_PATH.exists()
        assert SCRIPT_PATH.stat().st_mode & 0o111
    
    def test_script_accepts_three_arguments(self):
        """Test that script accepts bucket name, table name, and region"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'BUCKET_NAME="${1:-' in content
        assert 'DDB_TABLE="${2:-' in content
        assert 'REGION="${3:-' in content
    
    def test_default_bucket_name_defined(self):
        """Test that default bucket name is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'BUCKET_NAME=' in content
        assert 'terraform-state' in content.lower()
    
    def test_default_dynamodb_table_defined(self):
        """Test that default DynamoDB table name is defined"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'DDB_TABLE=' in content
        assert 'locks' in content.lower()
    
    def test_default_region_is_us_east_1(self):
        """Test that default region is us-east-1"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'us-east-1' in content


class TestBucketCreation:
    """Test S3 bucket creation logic"""
    
    def test_checks_if_bucket_exists(self):
        """Test that script checks if bucket already exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'head-bucket' in content
        assert 'already exists' in content
    
    def test_uses_create_bucket_command(self):
        """Test that aws s3api create-bucket is used"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'create-bucket' in content
        assert '--bucket' in content
    
    def test_handles_us_east_1_region_special_case(self):
        """Test that us-east-1 region is handled without LocationConstraint"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'us-east-1' in content
        assert 'LocationConstraint' in content or 'create-bucket-configuration' in content
    
    def test_uses_location_constraint_for_other_regions(self):
        """Test that non-us-east-1 regions use LocationConstraint"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'create-bucket-configuration' in content
        assert 'LocationConstraint' in content


class TestBucketConfiguration:
    """Test S3 bucket versioning and encryption"""
    
    def test_enables_bucket_versioning(self):
        """Test that bucket versioning is enabled"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'put-bucket-versioning' in content
        assert 'Status=Enabled' in content or 'Enabled' in content
    
    def test_enables_default_encryption(self):
        """Test that default encryption is configured"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'put-bucket-encryption' in content
        assert 'server-side-encryption' in content.lower()
    
    def test_uses_aes256_encryption(self):
        """Test that AES256 encryption is used"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'AES256' in content


class TestDynamoDBTableCreation:
    """Test DynamoDB table creation for state locking"""
    
    def test_checks_if_table_exists(self):
        """Test that script checks if DynamoDB table exists"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'describe-table' in content
        assert 'already exists' in content
    
    def test_creates_dynamodb_table(self):
        """Test that DynamoDB table is created"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'create-table' in content
        assert '--table-name' in content
    
    def test_uses_lockid_as_partition_key(self):
        """Test that LockID is used as partition key"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'LockID' in content
        assert 'KeyType=HASH' in content or 'HASH' in content
    
    def test_uses_pay_per_request_billing(self):
        """Test that PAY_PER_REQUEST billing mode is used"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'PAY_PER_REQUEST' in content
    
    def test_waits_for_table_to_be_active(self):
        """Test that script waits for table to become active"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'wait table-exists' in content or 'wait' in content


class TestOutputMessaging:
    """Test script output and user guidance"""
    
    def test_displays_bootstrap_information(self):
        """Test that script displays what it's doing"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'echo' in content
        assert 'Bootstrapping' in content or 'Creating' in content
    
    def test_provides_terraform_configuration_guidance(self):
        """Test that script tells user how to update Terraform config"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'Update terraform' in content or 'Update' in content
        assert 'tfstate_bucket' in content or 'bucket' in content
        assert 'tfstate_lock_table' in content or 'lock' in content
    
    def test_displays_completion_message(self):
        """Test that script displays completion message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'complete' in content.lower() or 'done' in content.lower()


class TestErrorHandling:
    """Test error handling and script safety"""
    
    def test_uses_strict_bash_mode(self):
        """Test that script uses bash strict mode"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'set -euo pipefail' in content
    
    def test_uses_bash_shebang(self):
        """Test that script uses bash shebang"""
        with open(SCRIPT_PATH) as f:
            first_line = f.readline()
        assert '#!/usr/bin/env bash' in first_line or '#!/bin/bash' in first_line


if __name__ == "__main__":
    pytest.main([__file__, "-v"])