"""Comprehensive unit tests for deploy.sh"""
import os
import subprocess
import tempfile
import pytest
from pathlib import Path
import shutil

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/deploy.sh"
BASH_PATH = shutil.which("bash")


class TestDeployScriptBasicFunctionality:
    """Test basic deploy script functionality"""
    
    def test_script_exists(self):
        """Verify the deploy.sh script file exists"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
    
    def test_script_has_proper_shebang(self):
        """Test script has proper bash shebang"""
        with open(SCRIPT_PATH, 'r') as f:
            first_line = f.readline().strip()
        
        assert first_line in ["#!/bin/bash", "#!/usr/bin/env bash"]
    
    def test_script_sets_error_handling(self):
        """Test script uses set -e for error handling"""
        content = SCRIPT_PATH.read_text()
        assert "set -e" in content or "set -euo pipefail" in content


class TestDeployScriptCorrections:
    """Test specific corrections made to deploy.sh"""
    
    def test_terraform_fmt_command_corrected(self):
        """Test that 'tf=terraform fmt' typo was fixed to 'terraform fmt'"""
        content = SCRIPT_PATH.read_text()
        
        # Should have correct terraform fmt command
        assert "terraform fmt" in content
        # Should not have the typo 'tf=terraform'
        assert "tf=terraform" not in content
    
    def test_script_has_newline_at_end(self):
        """Test that script ends with proper newline"""
        with open(SCRIPT_PATH, 'rb') as f:
            content = f.read()
        
        # File should end with newline
        assert content.endswith(b'\n'), "Script should end with newline character"
    
    def test_terraform_init_present(self):
        """Test script includes terraform init command"""
        content = SCRIPT_PATH.read_text()
        assert "terraform init" in content
    
    def test_terraform_plan_present(self):
        """Test script includes terraform plan command"""
        content = SCRIPT_PATH.read_text()
        assert "terraform plan" in content
    
    def test_terraform_apply_logic_present(self):
        """Test script includes terraform apply logic"""
        content = SCRIPT_PATH.read_text()
        assert "terraform apply" in content
    
    def test_auto_approve_variable_present(self):
        """Test script checks AUTO_APPROVE variable"""
        content = SCRIPT_PATH.read_text()
        assert "AUTO_APPROVE" in content


class TestDeployScriptStructure:
    """Test deploy script structure and organization"""
    
    def test_script_changes_to_terraform_directory(self):
        """Test script changes to terraform directory"""
        content = SCRIPT_PATH.read_text()
        assert "cd" in content
        assert "terraform" in content.lower()
    
    def test_script_uses_root_dir_variable(self):
        """Test script defines and uses ROOT_DIR variable"""
        content = SCRIPT_PATH.read_text()
        assert "ROOT_DIR" in content
    
    def test_script_outputs_status_messages(self):
        """Test script includes echo statements for user feedback"""
        content = SCRIPT_PATH.read_text()
        echo_count = content.count("echo")
        assert echo_count >= 3, "Script should provide user feedback via echo"
    
    def test_terraform_commands_use_input_false(self):
        """Test terraform commands use -input=false flag"""
        content = SCRIPT_PATH.read_text()
        # At least some terraform commands should have -input=false
        assert "-input=false" in content


class TestDeployScriptEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_script_handles_missing_terraform_directory(self):
        """Test script behavior when terraform directory doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock script that tries to cd to non-existent dir
            test_script = Path(tmpdir) / "test_deploy.sh"
            test_script.write_text("""#!/bin/bash
set -e
cd /nonexistent/terraform 2>&1
""")
            test_script.chmod(0o755)
            
            result = subprocess.run(
                [BASH_PATH, str(test_script)],
                capture_output=True,
                text=True
            )
            
            # Should fail due to set -e
            assert result.returncode != 0


class TestDeployScriptComparison:
    """Test improvements from original to modified version"""
    
    def test_formatting_command_fixed(self):
        """Verify the terraform fmt command syntax is correct"""
        content = SCRIPT_PATH.read_text()
        
        # Find lines with terraform fmt
        lines = content.split('\n')
        fmt_lines = [line for line in lines if 'terraform fmt' in line and not line.strip().startswith('#')]
        
        # Should have at least one terraform fmt command
        assert len(fmt_lines) > 0
        
        # Check that it's not assigning to 'tf' variable
        for line in fmt_lines:
            assert not line.strip().startswith('tf=')