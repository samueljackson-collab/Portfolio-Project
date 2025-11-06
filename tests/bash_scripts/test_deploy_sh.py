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


class TestTerraformFmtCommand:
    """Test terraform fmt command correctness."""

    def test_script_terraform_fmt_command_syntax(self, script_path):
        """Verify terraform fmt command has correct syntax."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Line should be 'terraform fmt -recursive', not 'tf=terraform fmt -recursive'
        assert "terraform fmt -recursive" in content or "terraform fmt" in content, \
            "Script should contain terraform fmt command"
        # Check for common typo where variable assignment is used instead
        assert "tf=terraform fmt" not in content, \
            "Script should not have variable assignment 'tf=' before terraform fmt command"

    def test_script_executes_fmt_not_assigns(self, script_path):
        """Verify fmt command is executed, not assigned to variable."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            if "fmt -recursive" in line:
                # Should be command execution, not variable assignment
                assert not line.strip().startswith("tf="), \
                    f"Line {i}: 'terraform fmt' should be executed, not assigned to 'tf' variable"
                # Should actually call terraform
                assert "terraform fmt" in line or line.strip().startswith("terraform"), \
                    f"Line {i}: Should execute 'terraform fmt' command"

    def test_script_fmt_command_not_noop(self, script_path):
        """Verify terraform fmt command will actually execute."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Find the fmt line
        fmt_lines = [line for line in content.split('\n') if 'fmt' in line and 'terraform' in line.lower()]
        assert len(fmt_lines) > 0, "Should have terraform fmt command"
        
        for line in fmt_lines:
            # Skip comments
            if line.strip().startswith('#'):
                continue
            # Ensure it's a command execution, not just a variable assignment
            if 'fmt -recursive' in line:
                assert not line.strip().startswith('tf='), \
                    "terraform fmt should be executed as command, not assigned to variable"

    def test_script_runs_recursive_fmt(self, script_path):
        """Verify script uses -recursive flag for terraform fmt."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "-recursive" in content or "recursive" in content, \
            "Script should use -recursive flag for terraform fmt"


class TestScriptCommandExecution:
    """Test that script commands are executed, not just assigned."""

    def test_no_unused_variable_assignments(self, script_path):
        """Verify script doesn't have unused variable assignments for commands."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        # Look for suspicious patterns like: cmd=actual_command
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments and empty lines
            if stripped.startswith('#') or not stripped:
                continue
            
            # Check for patterns like 'tf=terraform' or 'init=terraform init'
            if '=' in stripped and 'terraform' in stripped.lower():
                # This might be a variable assignment instead of command execution
                # Unless it's a proper variable like WORKSPACE="${1:-default}"
                if not any(var in stripped for var in ['WORKSPACE=', 'AUTO_APPROVE=', 'ROOT_DIR=', 'AWS_']):
                    # Check if it looks like a command being assigned
                    if stripped.startswith(('tf=', 'init=', 'plan=', 'apply=', 'validate=', 'fmt=')):
                        pytest.fail(f"Line {i}: Suspicious variable assignment '{stripped}' - "
                                  f"command may not execute")

    def test_terraform_commands_properly_invoked(self, script_path):
        """Verify all terraform commands are properly invoked as commands."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        terraform_command_count = 0
        for line in lines:
            # Count actual terraform command invocations
            if 'terraform ' in line and not line.strip().startswith('#'):
                terraform_command_count += 1
        
        # Script should have multiple terraform commands (fmt, init, workspace, validate, plan, apply)
        assert terraform_command_count >= 4, \
            f"Script should execute multiple terraform commands, found {terraform_command_count}"


class TestScriptPermissionChanges:
    """Test script file permission requirements."""

    def test_script_permission_bits(self, script_path):
        """Verify script has correct permission bits for execution."""
        import stat
        st = script_path.stat()
        mode = st.st_mode
        
        # Check owner execute bit
        assert mode & stat.S_IXUSR, "Owner should have execute permission"
        
        # Check group execute bit (common in many setups)
        assert mode & stat.S_IXGRP, "Group should have execute permission"

    def test_script_not_world_writable(self, script_path):
        """Verify script is not world-writable (security check)."""
        import stat
        st = script_path.stat()
        mode = st.st_mode
        
        # Script should not be world-writable
        assert not (mode & stat.S_IWOTH), \
            "Script should not be world-writable for security"

    def test_script_readable_by_owner(self, script_path):
        """Verify script is readable by owner."""
        import stat
        st = script_path.stat()
        mode = st.st_mode
        
        assert mode & stat.S_IRUSR, "Owner should have read permission"

    def test_script_is_regular_file(self, script_path):
        """Verify script is a regular file, not symlink or other type."""
        import stat
        st = script_path.stat()
        
        assert stat.S_ISREG(st.st_mode), \
            "Script should be a regular file"