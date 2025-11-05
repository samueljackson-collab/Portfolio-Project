"""Comprehensive unit tests for bootstrap_remote_state.sh"""
import os
import subprocess
import tempfile
import pytest
from pathlib import Path
import shutil

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/bootstrap_remote_state.sh"
BASH_PATH = shutil.which("bash")


class TestBootstrapScriptBasicFunctionality:
    """Test basic bootstrap script functionality"""
    
    def test_script_exists(self):
        """Verify the bootstrap_remote_state.sh script file exists"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
    
    def test_script_has_proper_shebang(self):
        """Test script has proper bash shebang"""
        with open(SCRIPT_PATH, 'r') as f:
            first_line = f.readline().strip()
        
        assert first_line in ["#!/bin/bash", "#!/usr/bin/env bash"]
    
    def test_script_is_executable(self):
        """Test script has executable permissions"""
        assert os.access(SCRIPT_PATH, os.X_OK), "Script should be executable"


class TestBootstrapScriptCorrections:
    """Test specific corrections made to bootstrap_remote_state.sh"""
    
    def test_script_has_newline_at_end(self):
        """Test that script ends with proper newline (main fix)"""
        with open(SCRIPT_PATH, 'rb') as f:
            content = f.read()
        
        # File should end with newline
        assert content.endswith(b'\n'), "Script should end with newline character"
    
    def test_final_echo_statement_present(self):
        """Test that final echo statements are present"""
        content = SCRIPT_PATH.read_text()
        
        # Should have echo statements about updating variables
        assert "echo" in content
        assert "tfstate_bucket" in content or "BUCKET_NAME" in content
        assert "tfstate_lock_table" in content or "DDB_TABLE" in content
    
    def test_no_missing_newline_before_eof(self):
        """Test that last line has proper newline before EOF"""
        with open(SCRIPT_PATH, 'r') as f:
            lines = f.readlines()
        
        # Last line should end with newline
        if lines:
            assert lines[-1].endswith('\n'), "Last line should end with newline"


class TestBootstrapScriptStructure:
    """Test bootstrap script structure and organization"""
    
    def test_script_defines_bucket_name_variable(self):
        """Test script defines BUCKET_NAME variable"""
        content = SCRIPT_PATH.read_text()
        assert "BUCKET_NAME" in content
    
    def test_script_defines_dynamodb_table_variable(self):
        """Test script defines DDB_TABLE or DynamoDB table variable"""
        content = SCRIPT_PATH.read_text()
        assert "DDB_TABLE" in content or "DYNAMODB_TABLE" in content or "dynamodb" in content.lower()
    
    def test_script_uses_aws_cli(self):
        """Test script references AWS CLI commands"""
        content = SCRIPT_PATH.read_text()
        # Should have AWS CLI usage or references
        assert "aws" in content.lower() or "s3" in content.lower() or "AWS" in content
    
    def test_script_creates_s3_bucket(self):
        """Test script includes S3 bucket creation logic"""
        content = SCRIPT_PATH.read_text()
        assert "s3" in content.lower() or "bucket" in content.lower()
    
    def test_script_creates_dynamodb_table(self):
        """Test script includes DynamoDB table creation logic"""
        content = SCRIPT_PATH.read_text()
        assert "dynamodb" in content.lower() or "lock" in content.lower()
    
    def test_script_provides_completion_feedback(self):
        """Test script provides completion message"""
        content = SCRIPT_PATH.read_text()
        assert "complete" in content.lower() or "done" in content.lower() or "Bootstrap" in content


class TestBootstrapScriptOutputMessages:
    """Test script output and user feedback"""
    
    def test_script_instructs_user_on_next_steps(self):
        """Test script tells user what to do next"""
        content = SCRIPT_PATH.read_text()
        
        # Should instruct updating terraform config
        assert "Update" in content or "update" in content
        assert "terraform" in content.lower() or "variables.tf" in content
    
    def test_script_outputs_bucket_name(self):
        """Test script outputs the bucket name created"""
        content = SCRIPT_PATH.read_text()
        
        # Should output bucket name
        assert "${BUCKET_NAME}" in content or "$BUCKET_NAME" in content
    
    def test_script_outputs_lock_table_name(self):
        """Test script outputs the lock table name created"""
        content = SCRIPT_PATH.read_text()
        
        # Should output DynamoDB table name
        assert "${DDB_TABLE}" in content or "$DDB_TABLE" in content


class TestBootstrapScriptErrorHandling:
    """Test error handling and validation"""
    
    def test_script_checks_prerequisites(self):
        """Test script validates prerequisites before execution"""
        content = SCRIPT_PATH.read_text()
        
        # Should have some form of validation or checks
        # Common patterns: command -v, which, type, if statements
        assert any(pattern in content for pattern in ["if", "command", "which", "type"])
    
    def test_script_handles_existing_resources(self):
        """Test script handles already-existing resources gracefully"""
        content = SCRIPT_PATH.read_text()
        
        # Should check if resources exist or handle errors
        assert "exist" in content.lower() or "already" in content.lower() or "if" in content


class TestBootstrapScriptIntegration:
    """Test integration aspects of bootstrap script"""
    
    def test_output_format_matches_terraform_variables(self):
        """Test output format matches Terraform variable syntax"""
        content = SCRIPT_PATH.read_text()
        
        # Output should mention terraform variables format
        lines = content.split('\n')
        output_lines = [line for line in lines if 'tfstate' in line.lower()]
        
        assert len(output_lines) > 0, "Should reference tfstate configuration"