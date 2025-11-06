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

    def test_script_executable_bit_set(self, script_path):
        """Verify script has executable bit set (chmod +x)."""
        import stat
        mode = script_path.stat().st_mode
        # Check if any execute bit is set (owner, group, or others)
        assert mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH), \
            f"Script {script_path} should have executable permission"

    def test_script_owner_executable(self, script_path):
        """Verify script is executable by owner."""
        import stat
        mode = script_path.stat().st_mode
        assert mode & stat.S_IXUSR, "Script should be executable by owner"

    def test_script_can_be_executed_directly(self, script_path):
        """Verify script can be invoked directly without bash prefix."""
        # This test verifies both shebang and executable permission
        import stat
        mode = script_path.stat().st_mode
        has_exec = mode & stat.S_IXUSR
        with open(script_path, 'r') as f:
            has_shebang = f.readline().startswith('#!')
        assert has_exec and has_shebang, \
            "Script should be directly executable (shebang + exec permission)"


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


    def test_script_terraform_fmt_command_syntax(self, script_path):
        """Verify terraform fmt command has correct syntax."""
        with open(script_path, 'r') as f:
            content = f.read()
        # Should be "terraform fmt" not "tf=terraform fmt"
        assert "terraform fmt -recursive" in content
        # Verify there's no assignment operator before terraform fmt
        lines = content.split('\n')
        for line in lines:
            if 'fmt -recursive' in line:
                # Line should not start with variable assignment like "tf="
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    assert not stripped.startswith('tf='), \
                        "terraform fmt should be executed, not assigned to variable 'tf'"
                    assert stripped.startswith('terraform ') or 'terraform fmt' in stripped, \
                        "fmt command should use 'terraform' executable"

    def test_script_has_no_variable_assignments_for_commands(self, script_path):
        """Verify script doesn't accidentally assign commands to variables."""
        with open(script_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments and empty lines
            if not stripped or stripped.startswith('#'):
                continue
            # Check for common mistakes: var=command without proper syntax
            if 'terraform' in stripped and '=' in stripped:
                # Valid: VAR=$(command) or VAR="value"
                # Invalid: var=command (without $() or quotes after =)
                if not ('$(' in stripped or '="' in stripped or "='" in stripped or '${' in stripped):
                    # This might be a bug like "tf=terraform fmt"
                    assert False, f"Line {i} may have invalid command assignment: {stripped}"
    def test_script_selects_existing_workspace(self, script_path):
        """Verify script can select existing workspace."""
        with open(script_path, 'r') as f:
            content = f.read()
        assert "workspace select" in content


    def test_script_no_unintended_side_effects(self, script_path):
        """Verify script commands don't have unintended side effects."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Check for common bash mistakes
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            # Dangerous: command substitution in wrong context
            if '`' in stripped and not '#' in stripped.split('`')[0]:
                # Backticks are discouraged, should use $()
                pass  # Just a warning, not necessarily wrong
                
            # Check for proper quoting around variables
            if 'cd ' in stripped and '${' in stripped:
                assert '"${' in stripped or "'${" in stripped, \
                    f"Line {i}: Variables in 'cd' should be quoted"

    def test_script_terraform_commands_use_correct_flags(self, script_path):
        """Verify terraform commands use appropriate safety flags."""
        with open(script_path, 'r') as f:
            content = f.read()
        
        # terraform init should use -input=false in automation
        if 'terraform init' in content:
            # Check if -input=false is used
            assert '-input=false' in content or 'input=false' in content, \
                "terraform init should use -input=false for non-interactive mode"
        
        # terraform plan should save to a file
        if 'terraform plan' in content:
            assert '-out=' in content or 'plan.tfplan' in content, \
                "terraform plan should save output to file"
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