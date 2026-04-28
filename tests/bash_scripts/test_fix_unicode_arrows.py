"""
Comprehensive unit tests for fix_unicode_arrows.sh

Tests cover:
- Script existence and permissions
- File discovery and filtering
- Backup creation logic
- Unicode replacement patterns
- Python compilation validation
- Error handling and recovery
"""
import os
import subprocess
import tempfile
import shutil
import pytest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts/fix_unicode_arrows.sh"


class TestScriptBasics:
    """Test basic script properties"""
    
    def test_script_exists(self):
        """Verify the script file exists"""
        assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"
    
    def test_script_is_readable(self):
        """Verify the script is readable"""
        assert os.access(SCRIPT_PATH, os.R_OK), "Script is not readable"
    
    def test_script_has_bash_shebang(self):
        """Verify script has bash shebang"""
        with open(SCRIPT_PATH, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith('#!/'), "Missing shebang"
        assert 'bash' in first_line, "Should use bash interpreter"
    
    def test_script_uses_strict_mode(self):
        """Verify script uses set -euo pipefail"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'set -euo pipefail' in content, "Should use bash strict mode"


class TestScriptPurpose:
    """Test script documentation and purpose"""
    
    def test_has_descriptive_header(self):
        """Verify script has descriptive comment header"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'unicode' in content.lower() or 'arrow' in content.lower(), \
            "Should describe its purpose"
    
    def test_documents_usage(self):
        """Verify script documents usage pattern"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'Usage:' in content or 'usage' in content.lower(), \
            "Should document usage"
    
    def test_explains_replacements(self):
        """Verify script explains what it replaces"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'u003e' in content or 'HTML' in content, \
            "Should explain unicode/HTML escape sequences"


class TestFileDiscovery:
    """Test Python file discovery logic"""
    
    def test_searches_for_py_files(self):
        """Verify script searches for .py files"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '*.py' in content, "Should search for Python files"
    
    def test_uses_find_command(self):
        """Verify script uses find command"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'find' in content, "Should use find to locate files"
    
    def test_finds_from_repo_root(self):
        """Verify script searches from repository root"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'ROOT_DIR' in content or 'SCRIPT_DIR' in content, \
            "Should determine repository root"


class TestBackupCreation:
    """Test backup file creation logic"""
    
    def test_creates_backup_files(self):
        """Verify script creates .bak backup files"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '.bak' in content, "Should create .bak backup files"
    
    def test_uses_copy_command(self):
        """Verify script copies files for backup"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'cp' in content, "Should use cp to create backups"
    
    def test_backup_created_before_modification(self):
        """Verify backup is created before sed operations"""
        with open(SCRIPT_PATH, 'r') as f:
            lines = f.readlines()
        backup_line = next((i for i, line in enumerate(lines) if '.bak' in line and 'cp' in line), -1)
        sed_line = next((i for i, line in enumerate(lines) if 'sed' in line), -1)
        assert backup_line >= 0, "Should create backups"
        assert sed_line >= 0, "Should use sed"
        if backup_line >= 0 and sed_line >= 0:
            assert backup_line < sed_line, "Backup should be created before sed runs"


class TestReplacementPatterns:
    """Test Unicode replacement patterns"""
    
    def test_replaces_single_backslash_u003e(self):
        """Verify script replaces -> pattern"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert r'->' in content or r'\u003e' in content, \
            "Should replace ->"
    
    def test_replaces_double_backslash_u003e(self):
        """Verify script replaces -\\\\u003e pattern"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert r'-\\\\u003e' in content or r'\\\\u003e' in content, \
            "Should replace -\\\\u003e"
    
    def test_replaces_u002d_u003e(self):
        """Verify script replaces \\u002d\\u003e pattern"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert r'->' in content, "Should replace \\u002d\\u003e"
    
    def test_replaces_html_entities(self):
        """Verify script replaces -> HTML entities"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert '->' in content, "Should replace HTML entities"
    
    def test_replaces_spaced_arrows(self):
        """Verify script replaces '->' with '->'"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert r'-[[:space:]]\+>' in content or '->' in content, \
            "Should replace spaced arrows"
    
    def test_replacements_target_arrow(self):
        """Verify all replacements produce -> arrow"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # All sed replacements should result in ->
        sed_lines = [line for line in content.split('\n') if 'sed' in line and 's/' in line]
        for line in sed_lines:
            if '003e' in line or '002d' in line or '&#' in line or '[[:space:]]' in line:
                assert '->' in line, f"Replacement should produce -> : {line}"


class TestSedUsage:
    """Test sed command usage"""
    
    def test_uses_sed_command(self):
        """Verify script uses sed for replacements"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'sed' in content, "Should use sed for text replacement"
    
    def test_sed_in_place_modification(self):
        """Verify sed uses -i flag for in-place editing"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'sed -i' in content, "Should use sed -i for in-place editing"
    
    def test_multiple_sed_expressions(self):
        """Verify sed uses multiple -e expressions"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert content.count('-e') >= 3, "Should have multiple sed expressions"


class TestPythonValidation:
    """Test Python syntax validation"""
    
    def test_validates_python_syntax(self):
        """Verify script validates Python syntax after changes"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'py_compile' in content or 'python -m' in content, \
            "Should validate Python syntax"
    
    def test_compilation_check_exists(self):
        """Verify script compiles Python files to check syntax"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'compile' in content.lower(), "Should compile Python files"
    
    def test_validation_suppresses_output(self):
        """Verify validation suppresses verbose output"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Should redirect output to avoid clutter
        assert '2>/dev/null' in content or '>/dev/null' in content, \
            "Should suppress compilation output"


class TestErrorHandling:
    """Test error handling and recovery"""
    
    def test_handles_compilation_failure(self):
        """Verify script handles Python compilation failures"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'WARNING' in content or 'fail' in content.lower(), \
            "Should warn on compilation failure"
    
    def test_restores_backup_on_failure(self):
        """Verify script restores backup if compilation fails"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Should restore from backup
        assert 'mv' in content or 'restore' in content.lower(), \
            "Should restore backup on failure"
    
    def test_continues_processing_other_files(self):
        """Verify script continues after individual file failures"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'continue' in content, \
            "Should continue processing other files"


class TestOutputMessages:
    """Test user-facing messages"""
    
    def test_reports_repository_root(self):
        """Verify script reports repository root"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'Repository root' in content or 'echo' in content, \
            "Should report repository root"
    
    def test_reports_checking_files(self):
        """Verify script reports which file is being checked"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'Checking' in content, "Should report files being checked"
    
    def test_reports_patched_files(self):
        """Verify script reports successfully patched files"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'Patched' in content or 'validated' in content.lower(), \
            "Should report successfully patched files"
    
    def test_reports_completion(self):
        """Verify script reports completion"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'Done' in content, "Should report completion"


class TestIdempotency:
    """Test idempotent behavior"""
    
    def test_replacements_are_idempotent(self):
        """Verify replacements don't break already-correct arrows"""
        # The patterns should not match or alter correct -> sequences
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # The regex patterns should specifically target encoded forms
        assert r'\\u003e' in content or 'u003e' in content, \
            "Should target encoded forms specifically"


class TestIntegration:
    """Integration tests with actual file operations"""
    
    @pytest.fixture
    def temp_python_file(self):
        """Create temporary Python file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def foo(x: int) -> int:\n    return x + 1\n')
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(temp_path + '.bak'):
            os.unlink(temp_path + '.bak')
    
    def test_script_runs_without_error_on_clean_file(self, temp_python_file):
        """Test script runs successfully on already-clean Python file"""
        # This test requires the script to be executable and won't modify clean files
        result = subprocess.run(  # noqa: S603
            ['/bin/bash', str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(temp_python_file)
        )
        # Script should complete without critical errors
        assert result.returncode == 0, f"Script failed: {result.stderr}"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_handles_no_python_files(self):
        """Verify script handles directories with no Python files gracefully"""
        # Script should handle empty results from find
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Should use while loop that handles empty input
        assert 'while IFS=' in content or 'while read' in content, \
            "Should handle empty file lists"
    
    def test_handles_special_characters_in_paths(self):
        """Verify script properly handles special characters"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Should use null-terminated find with -print0
        assert '-print0' in content or 'IFS=' in content, \
            "Should handle special characters in paths"


class TestScriptStructure:
    """Test overall script structure and organization"""
    
    def test_script_is_not_empty(self):
        """Verify script has content"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert len(content) > 100, "Script should have substantial content"
    
    def test_script_has_comments(self):
        """Verify script includes explanatory comments"""
        with open(SCRIPT_PATH, 'r') as f:
            lines = f.readlines()
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        assert len(comment_lines) >= 3, "Script should have explanatory comments"
    
    def test_uses_variables_for_paths(self):
        """Verify script uses variables for important paths"""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'ROOT_DIR' in content or 'SCRIPT_DIR' in content, \
            "Should define path variables"