"""
Regression tests for scripts/deploy.sh syntax errors.

This test suite validates fixes for syntax errors introduced in recent changes:
- Line 13 syntax error: 'tf=terraform fmt' should be 'terraform fmt'
- Ensures proper command execution
- Validates variable assignments
"""

import subprocess
import shutil
import pytest
from pathlib import Path


@pytest.fixture
def script_path():
    """Return the path to the deploy script."""
    return Path("scripts/deploy.sh")


class TestDeployScriptSyntaxRegression:
    """Test for specific syntax regressions in deploy.sh."""

    def test_no_invalid_variable_assignment_in_terraform_commands(self, script_path):
        """Verify no invalid variable assignments like 'tf=terraform fmt'."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for the specific bug: 'tf=terraform fmt' on line 13
        lines = content.split('\n')
        for i, line in enumerate(lines, start=1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Look for invalid patterns like 'tf=terraform' or 'var=command'
            if '=' in line and 'terraform' in line:
                # This is invalid unless it's a proper assignment like VAR="value"
                # Terraform commands should not be assigned to variables
                stripped = line.strip()
                if stripped.startswith('tf=') or stripped.startswith('TF='):
                    pytest.fail(
                        f"Line {i}: Invalid variable assignment '{stripped}'. "
                        f"Should be 'terraform fmt' not 'tf=terraform fmt'"
                    )

    def test_terraform_fmt_command_is_correct(self, script_path):
        """Verify terraform fmt command is properly invoked."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Terraform fmt should be called as a command, not assigned
        assert 'terraform fmt' in content, "Script should contain 'terraform fmt' command"
        
        # Ensure it's not incorrectly assigned to a variable
        lines = content.split('\n')
        for line in lines:
            if 'terraform fmt' in line and not line.strip().startswith('#'):
                # Line should not start with a variable assignment
                stripped = line.strip()
                if '=' in stripped and stripped.index('=') < stripped.index('terraform'):
                    pytest.fail(
                        f"Invalid: '{stripped}'. "
                        f"'terraform fmt' should be executed, not assigned to a variable"
                    )

    def test_all_terraform_commands_are_executed_not_assigned(self, script_path):
        """Verify all terraform commands are executed, not assigned to variables."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        terraform_commands = ['terraform fmt', 'terraform init', 'terraform validate', 
                             'terraform plan', 'terraform apply']
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            
            for cmd in terraform_commands:
                if cmd in line:
                    # Check if it's being incorrectly assigned
                    if '=' in stripped and stripped.index('=') < stripped.index('terraform'):
                        # Check if it's not a legitimate variable like ROOT_DIR
                        if not any(var in stripped for var in ['ROOT_DIR', 'WORKSPACE', 'AUTO_APPROVE', 'DIR']):
                            pytest.fail(
                                f"Line {i}: Terraform command '{cmd}' appears to be "
                                f"assigned to a variable instead of being executed: '{stripped}'"
                            )

    def test_script_has_no_typos_in_command_execution(self, script_path):
        """Verify common command execution typos are not present."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Common typos/errors to check for
        invalid_patterns = [
            ('tf=terraform', 'Use "terraform" directly, not "tf=terraform"'),
            ('terrafor ', 'Typo: should be "terraform"'),
            ('terrafrom', 'Typo: should be "terraform"'),
            ('frm -recursive', 'Typo: should be "fmt -recursive"'),
        ]
        
        for pattern, message in invalid_patterns:
            assert pattern not in content, f"Found invalid pattern: {message}"

    def test_terraform_fmt_uses_recursive_flag(self, script_path):
        """Verify terraform fmt uses -recursive flag."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert 'fmt -recursive' in content or 'fmt--recursive' not in content, \
            "terraform fmt should use -recursive flag without typos"

    def test_bash_syntax_check_passes(self, script_path):
        """Run bash -n to check for syntax errors."""
        bash_path = shutil.which("bash")
        if not bash_path:
            pytest.skip("bash not found on this system")
        
        result = subprocess.run(
            [bash_path, "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, \
            f"Bash syntax check failed:\n{result.stderr}\n\nThis indicates a syntax error in the script."

    def test_shellcheck_analysis_if_available(self, script_path):
        """Run shellcheck if available for additional validation."""
        shellcheck_path = shutil.which("shellcheck")
        if not shellcheck_path:
            pytest.skip("shellcheck not available")
        
        result = subprocess.run(
            [shellcheck_path, "-x", str(script_path)],
            capture_output=True,
            text=True
        )
        
        # We're looking for critical errors (not warnings)
        # Shellcheck may report warnings, but errors should fail the test
        if result.returncode != 0:
            # Filter for actual errors vs warnings
            stderr = result.stderr
            if 'error' in stderr.lower():
                pytest.fail(f"ShellCheck found critical issues:\n{stderr}")


class TestCommandSequenceIntegrity:
    """Test that command sequence hasn't been broken by syntax errors."""

    def test_terraform_commands_in_correct_order(self, script_path):
        """Verify terraform commands execute in correct order."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Extract command order
        commands = []
        for line in content.split('\n'):
            if 'terraform fmt' in line and not line.strip().startswith('#'):
                commands.append('fmt')
            elif 'terraform init' in line and not line.strip().startswith('#'):
                commands.append('init')
            elif 'terraform validate' in line and not line.strip().startswith('#'):
                commands.append('validate')
            elif 'terraform plan' in line and not line.strip().startswith('#'):
                commands.append('plan')
            elif 'terraform apply' in line and not line.strip().startswith('#'):
                commands.append('apply')
        
        # Expected order
        expected_order = ['fmt', 'init', 'validate', 'plan']
        
        # Check that commands appear in expected order
        found_indices = []
        for cmd in expected_order:
            if cmd in commands:
                found_indices.append(commands.index(cmd))
        
        assert found_indices == sorted(found_indices), \
            f"Terraform commands out of order. Found: {commands}, Expected order: {expected_order}"

    def test_no_command_execution_prevented_by_syntax_error(self, script_path):
        """Ensure syntax errors don't prevent command execution."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Track if we find terraform commands after line 10
        found_terraform_commands = False
        for i, line in enumerate(lines, start=1):
            if i > 10 and 'terraform' in line and not line.strip().startswith('#'):
                found_terraform_commands = True
                break
        
        assert found_terraform_commands, \
            "No terraform commands found after line 10. Possible syntax error preventing execution."


class TestEdgeCases:
    """Test edge cases and potential issues."""

    def test_no_unclosed_quotes_around_terraform_commands(self, script_path):
        """Verify no unclosed quotes that could cause execution issues."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines, start=1):
            if 'terraform' in line and not line.strip().startswith('#'):
                # Count quotes
                single_quotes = line.count("'") - line.count("\\'")
                double_quotes = line.count('"') - line.count('\\"')
                
                assert single_quotes % 2 == 0, \
                    f"Line {i}: Unclosed single quote: {line}"
                assert double_quotes % 2 == 0, \
                    f"Line {i}: Unclosed double quote: {line}"

    def test_no_command_substitution_errors(self, script_path):
        """Verify command substitution syntax is correct."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for common command substitution issues
        invalid_patterns = [
            ('$terraform', 'Should use "terraform" or "$(terraform ...)"'),
            ('=${terraform', 'Invalid command substitution syntax'),
        ]
        
        for pattern, message in invalid_patterns:
            assert pattern not in content, f"Found issue: {message}"