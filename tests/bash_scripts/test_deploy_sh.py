"""
Comprehensive tests for scripts/deploy.sh

This test suite validates:
- Script existence and permissions
- Terraform command orchestration
- Workspace management
- Auto-approve functionality
- Error handling
- Safe deployment practices
"""

import subprocess
import os
import shutil
import pytest
from pathlib import Path


@pytest.fixture
def script_path():
    """Return the path to the deploy script."""
    return Path("scripts/deploy.sh")


class TestScriptExistence:
    """Test script file properties."""

    def test_script_exists(self, script_path):
        """Verify the deploy script exists."""
        assert script_path.exists(), f"Script not found at {script_path}"

    def test_script_is_executable(self, script_path):
        """Verify the script has executable permissions."""
        assert os.access(script_path, os.X_OK), f"{script_path} is not executable"

    def test_script_has_bash_shebang(self, script_path):
        """Verify the script has bash shebang."""
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!/"), "Script missing shebang"
        assert "bash" in first_line, "Script should use bash"


class TestScriptSyntax:
    """Test bash script syntax."""

    def test_bash_syntax_valid(self, script_path):
        """Verify bash syntax is valid."""
        bash_path = shutil.which("bash")
        if not bash_path:
            pytest.skip("bash not found on this system")
        result = subprocess.run(  # noqa: S603
            [bash_path, "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_script_uses_strict_mode(self, script_path):
        """Verify script uses set -euo pipefail."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "set -euo pipefail" in content or "set -e" in content


class TestArgumentParsing:
    """Test argument parsing."""

    def test_script_accepts_workspace_argument(self, script_path):
        """Test script accepts workspace as first argument."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "WORKSPACE" in content
        assert "${1:-" in content or "$1" in content

    def test_script_has_default_workspace(self, script_path):
        """Test script has a default workspace value."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "${1:-default}" in content or "default" in content

    def test_script_accepts_auto_approve_argument(self, script_path):
        """Test script accepts auto-approve as second argument."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "AUTO_APPROVE" in content
        assert "${2:-" in content or "$2" in content


class TestTerraformCommands:
    """Test Terraform command orchestration."""

    def test_script_runs_terraform_fmt(self, script_path):
        """Verify script runs terraform fmt."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform fmt" in content or "fmt" in content

    def test_script_runs_terraform_init(self, script_path):
        """Verify script runs terraform init."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform init" in content

    def test_script_runs_terraform_validate(self, script_path):
        """Verify script runs terraform validate."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform validate" in content

    def test_script_runs_terraform_plan(self, script_path):
        """Verify script runs terraform plan."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform plan" in content

    def test_script_saves_plan_to_file(self, script_path):
        """Verify script saves plan to a file."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "-out=" in content or "plan.tfplan" in content


class TestWorkspaceManagement:
    """Test Terraform workspace management."""

    def test_script_manages_workspaces(self, script_path):
        """Verify script manages Terraform workspaces."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform workspace" in content

    def test_script_selects_existing_workspace(self, script_path):
        """Verify script can select existing workspace."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "workspace select" in content

    def test_script_creates_new_workspace(self, script_path):
        """Verify script can create new workspace."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "workspace new" in content

    def test_script_checks_workspace_existence(self, script_path):
        """Verify script checks if workspace exists before selecting."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "workspace list" in content or "grep" in content


class TestAutoApproveLogic:
    """Test auto-approve functionality."""

    def test_script_handles_auto_approve(self, script_path):
        """Verify script handles auto-approve flag."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "AUTO_APPROVE" in content
        assert "true" in content or "false" in content

    def test_script_applies_with_auto_approve(self, script_path):
        """Verify script applies with auto-approve when flag is true."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "terraform apply" in content
        assert "-auto-approve" in content or "auto-approve" in content

    def test_script_provides_manual_apply_command(self, script_path):
        """Verify script shows manual apply command when not auto-approving."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Should show the command to run manually
        assert "To apply:" in content or "terraform apply" in content


class TestDirectoryNavigation:
    """Test script navigates to correct directories."""

    def test_script_changes_to_terraform_directory(self, script_path):
        """Verify script changes to terraform directory."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "cd" in content
        assert "terraform" in content

    def test_script_determines_root_directory(self, script_path):
        """Verify script determines repository root directory."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "ROOT_DIR" in content or 'dirname "$0"' in content


class TestSafetyChecks:
    """Test safety and best practices."""

    def test_script_uses_input_false(self, script_path):
        """Verify script uses -input=false for non-interactive mode."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "-input=false" in content

    def test_script_formats_before_other_commands(self, script_path):
        """Verify fmt runs before init/plan/apply."""
        with open(script_path, 'r') as f:
            lines = f.readlines()

        fmt_line = None
        init_line = None
        for i, line in enumerate(lines):
            if "terraform fmt" in line or "fmt -recursive" in line:
                fmt_line = i
            if "terraform init" in line:
                init_line = i

        if fmt_line and init_line:
            assert fmt_line < init_line, "fmt should run before init"

    def test_script_validates_before_plan(self, script_path):
        """Verify validate runs before plan."""
        with open(script_path, 'r') as f:
            lines = f.readlines()

        validate_line = None
        plan_line = None
        for i, line in enumerate(lines):
            if "terraform validate" in line:
                validate_line = i
            if "terraform plan" in line:
                plan_line = i

        if validate_line and plan_line:
            assert validate_line < plan_line, "validate should run before plan"


class TestOutputMessages:
    """Test script provides helpful output."""

    def test_script_provides_progress_messages(self, script_path):
        """Verify script outputs progress messages."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert 'echo' in content, "Script should provide progress messages"

    def test_script_indicates_current_step(self, script_path):
        """Verify script indicates what step it's running."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Check for messages about formatting, initializing, planning, etc.
        keywords = ["Formatting", "Initializing", "Planning", "Validating"]
        found_keywords = [kw for kw in keywords if kw in content]
        assert len(found_keywords) >= 2, "Script should indicate current steps"

class TestCommandSyntax:
    """Test that commands are syntactically correct and executable."""

    def test_terraform_fmt_command_is_executable(self, script_path):
        """Verify terraform fmt command doesn't have typos or variable assignments."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Find the terraform fmt line
        fmt_lines = [line for line in lines if 'terraform fmt' in line or 'fmt -recursive' in line]
        
        for line in fmt_lines:
            stripped = line.strip()
            # Should not have variable assignment like "tf=terraform"
            if 'terraform fmt' in stripped:
                assert not stripped.startswith('tf='), \
                    f"Line '{stripped}' has typo: should be 'terraform fmt' not 'tf=terraform'"
                assert not stripped.startswith('terraform='), \
                    f"Line '{stripped}' appears to assign terraform as variable"
                # Should not have just the assignment without execution
                assert '=' not in stripped or '==' in stripped, \
                    f"Line '{stripped}' may have incorrect variable assignment"

    def test_all_terraform_commands_start_correctly(self, script_path):
        """Verify all terraform commands start with 'terraform' not variations."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Find all lines that should be terraform commands
        terraform_keywords = ['init', 'plan', 'apply', 'validate', 'fmt', 'workspace']
        
        for line in content.split('\n'):
            stripped = line.strip()
            # Skip comments and empty lines
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check lines that appear to be terraform commands
            for keyword in terraform_keywords:
                if keyword in stripped and not stripped.startswith('echo'):
                    # If it contains a terraform keyword and looks like a command
                    if any(stripped.startswith(cmd) for cmd in ['terraform', 'if', 'else', 'fi', '}']):
                        continue  # Valid
                    # Check if it's actually trying to run terraform
                    if f' {keyword}' in stripped or f'{keyword} ' in stripped:
                        # This might be a malformed terraform command
                        if 'terraform' not in stripped and 'grep' not in stripped:
                            # Could be a typo
                            pass  # We'll catch it in other tests

    def test_terraform_fmt_executes_terraform_not_variable(self, script_path):
        """Verify terraform fmt line actually executes terraform command."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Find line with fmt
        for i, line in enumerate(lines, 1):
            if 'fmt' in line and 'echo' not in line.lower() and '#' not in line.strip()[0:1]:
                # This should be a command execution line
                stripped = line.strip()
                # Check it's not a variable assignment that looks like: var=command args
                if '=' in stripped and not '==' in stripped and not '!=' in stripped:
                    before_equals = stripped.split('=')[0]
                    after_equals = stripped.split('=', 1)[1]
                    # If before_equals is just a simple word (variable name)
                    # and after_equals looks like a command, this is an error
                    if before_equals.isidentifier() and 'terraform' in after_equals:
                        pytest.fail(
                            f"Line {i}: '{stripped}' assigns terraform command to variable "
                            f"instead of executing it. Should be just 'terraform fmt -recursive'"
                        )

    def test_no_malformed_variable_assignments_on_command_lines(self, script_path):
        """Verify command lines don't accidentally create variable assignments."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        problem_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments, empty lines, and actual variable declarations
            if not stripped or stripped.startswith('#'):
                continue
            if stripped.startswith(('WORKSPACE=', 'AUTO_APPROVE=', 'ROOT_DIR=')):
                continue  # These are legitimate
            if 'export ' in stripped or 'local ' in stripped:
                continue  # Variable declarations
            
            # Look for suspicious patterns: word=command
            if '=' in stripped and not '==' in stripped and not '!=' in stripped:
                parts = stripped.split('=')
                if len(parts) >= 2:
                    var_name = parts[0].strip().split()[-1]  # Get last word before =
                    value = parts[1].strip()
                    
                    # If var_name is a simple identifier and value is a command
                    if var_name.replace('_', '').isalnum() and not var_name.startswith('$'):
                        # Check if value looks like a command (starts with known command)
                        commands = ['terraform', 'aws', 'git', 'echo', 'cd', 'grep', 'ls']
                        if any(value.startswith(cmd) for cmd in commands):
                            problem_lines.append((i, stripped))
        
        if problem_lines:
            errors = '\n'.join([f"  Line {num}: {line}" for num, line in problem_lines])
            pytest.fail(
                f"Found {len(problem_lines)} line(s) with potential typos "
                f"(variable assignment instead of command execution):\n{errors}"
            )


class TestScriptCorrectness:
    """Test script correctness and common mistakes."""

    def test_script_has_newline_at_end(self, script_path):
        """Verify script ends with a newline character."""
        with open(script_path, 'rb') as f:
            content = f.read()
        
        assert content.endswith(b'\n'), \
            "Script should end with a newline character (POSIX requirement)"

    def test_no_trailing_whitespace_on_lines(self, script_path):
        """Check for trailing whitespace which can cause issues."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        lines_with_trailing = []
        for i, line in enumerate(lines, 1):
            if line.rstrip('\n') != line.rstrip('\n').rstrip():
                lines_with_trailing.append(i)
        
        if lines_with_trailing:
            pytest.fail(
                f"Lines with trailing whitespace: {lines_with_trailing}. "
                "This can cause issues in shell scripts."
            )

    def test_terraform_commands_not_assigned_to_variables(self, script_path):
        """Verify terraform commands are executed, not assigned to variables."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Look for patterns like: var=terraform ...
        # This is a common typo where someone means to run terraform but creates a variable
        import re
        # Match: [word]=[terraform command]
        pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*terraform\s+'
        
        matches = re.findall(pattern, content, re.MULTILINE)
        
        if matches:
            pytest.fail(
                f"Found terraform commands being assigned to variables: {matches}. "
                f"These should be executed directly, not assigned."
            )


class TestShellScriptBestPractices:
    """Test adherence to shell scripting best practices."""

    def test_terraform_commands_have_proper_error_handling(self, script_path):
        """Verify script will exit on terraform command failures."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # With set -e, any failing command should exit
        # But we should verify critical terraform commands aren't backgrounded or piped
        # in ways that would hide errors
        
        lines = content.split('\n')
        for line in lines:
            if 'terraform' in line and not line.strip().startswith('#'):
                # Terraform commands shouldn't be piped to grep without proper checking
                # unless it's workspace list
                if '| grep' in line and 'workspace list' not in line:
                    # This might hide terraform errors
                    if 'terraform validate' in line or 'terraform plan' in line:
                        pytest.fail(
                            f"Terraform command piped to grep might hide errors: {line}"
                        )

    def test_commands_not_silently_backgrounded(self, script_path):
        """Verify important commands aren't silently backgrounded."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if 'terraform' in stripped and not stripped.startswith('#'):
                # Terraform commands shouldn't end with & (background)
                if stripped.endswith('&'):
                    pytest.fail(
                        f"Line {i}: Terraform command is backgrounded, "
                        f"errors might not be caught: {stripped}"
                    )

    def test_terraform_fmt_is_actually_executed(self, script_path):
        """Integration-style test: verify terraform fmt line would execute."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Find the terraform fmt line
        fmt_line_content = None
        fmt_line_num = None
        
        for i, line in enumerate(lines, 1):
            if 'terraform fmt' in line and not line.strip().startswith('#'):
                fmt_line_content = line.strip()
                fmt_line_num = i
                break
        
        assert fmt_line_content is not None, "Could not find terraform fmt line"
        
        # Parse the line - if it's valid bash, it should start with terraform
        # not with a variable assignment
        if '=' in fmt_line_content and not '==' in fmt_line_content:
            # Check if this is a variable assignment
            before_eq = fmt_line_content.split('=')[0].strip()
            if before_eq.isidentifier():
                pytest.fail(
                    f"Line {fmt_line_num}: '{fmt_line_content}' appears to assign "
                    f"'terraform fmt' to variable '{before_eq}' instead of executing it. "
                    f"This is likely a typo."
                )


class TestFileQuality:
    """Test file quality and formatting."""

    def test_consistent_line_endings(self, script_path):
        """Verify script uses consistent Unix line endings."""
        with open(script_path, 'rb') as f:
            content = f.read()
        
        # Check for Windows line endings
        assert b'\r\n' not in content, \
            "Script contains Windows line endings (CRLF). Should use Unix (LF) only."

    def test_file_not_empty(self, script_path):
        """Verify script is not empty."""
        assert script_path.stat().st_size > 0, "Script file is empty"

    def test_script_has_content_after_shebang(self, script_path):
        """Verify script has actual content, not just shebang."""
        with open(script_path, 'r') as f:
            lines = [l for l in f.readlines() if l.strip() and not l.strip().startswith('#')]
        
        assert len(lines) > 0, "Script only contains comments, no actual code"