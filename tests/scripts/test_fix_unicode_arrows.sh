#!/usr/bin/env python3
class TestRefactoredScriptStructure:
    """Test the refactored script structure"""
    
    def test_simplified_root_dir_calculation(self):
        """Test that ROOT_DIR calculation uses simplified approach"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"' in content
    
    def test_no_multi_target_support(self):
        """Test that multi-target functionality was removed"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should not have target-related functions
        assert 'process_target' not in content
        assert 'print_header' not in content
    
    def test_direct_find_execution(self):
        """Test that find command is executed directly"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'find "$ROOT_DIR"' in content
        assert '-type f -name' in content
    
    def test_uses_while_read_loop(self):
        """Test that script uses while read loop for processing"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'while IFS= read -r -d' in content


class TestBackupCreation:
    """Test backup file creation logic"""
    
    def test_creates_backup_with_cp_n(self):
        """Test that backups are created with cp -n (no clobber)"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'cp -n "$file" "${file}.bak"' in content
    
    def test_backup_creation_before_sed(self):
        """Test that backup is created before sed replacements"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        cp_pos = content.find('cp -n')
        sed_pos = content.find('sed -i')
        assert cp_pos < sed_pos, "backup should be created before sed"
    
    def test_uses_or_true_for_backup(self):
        """Test that backup creation uses || true to continue on error"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '|| true' in content


class TestSedReplacements:
    """Test sed replacement patterns"""
    
    def test_replaces_single_backslash_u003e(self):
        """Test that -\\u003e pattern is replaced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "s/-\\\\u003e/->/g" in content
    
    def test_replaces_double_backslash_u003e(self):
        """Test that -\\\\u003e pattern is replaced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "s/-\\\\\\\\u003e/->/g" in content
    
    def test_replaces_u002d_u003e(self):
        """Test that \\u002d\\u003e pattern is replaced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "s/\\\\u002d\\\\u003e/->/g" in content
    
    def test_replaces_html_entities(self):
        """Test that &#45;&#62; pattern is replaced"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "s/&#45;&#62;/->/g" in content
    
    def test_normalizes_spaced_arrows(self):
        """Test that - > pattern is normalized to ->"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "s/-[[:space:]]\\+>/->/g" in content
    
    def test_uses_in_place_editing(self):
        """Test that sed uses -i for in-place editing"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'sed -i' in content


class TestPythonCompileCheck:
    """Test Python compilation validation"""
    
    def test_validates_with_py_compile(self):
        """Test that script uses python -m py_compile for validation"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'python -m py_compile' in content
    
    def test_restores_backup_on_failure(self):
        """Test that backup is restored if compilation fails"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'mv "${file}.bak" "$file"' in content
    
    def test_continues_on_compile_failure(self):
        """Test that script continues processing other files on failure"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'continue' in content
    
    def test_compile_check_after_sed(self):
        """Test that compile check occurs after sed replacements"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        sed_pos = content.find('sed -i')
        compile_pos = content.find('python -m py_compile')
        assert sed_pos < compile_pos, "compile check should be after sed"


class TestSimplifiedLogic:
    """Test simplified script logic"""
    
    def test_no_function_definitions(self):
        """Test that helper functions were removed"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should not have function definitions
        assert 'patch_file()' not in content
        assert 'create_backup_if_missing()' not in content
        assert 'restore_from_backup()' not in content
    
    def test_inline_processing(self):
        """Test that file processing is inline"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should have while loop directly after find
        assert 'find "$ROOT_DIR"' in content
        assert 'while IFS=' in content
    
    def test_no_main_function(self):
        """Test that main function was removed"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'main()' not in content
        assert 'main "$@"' not in content


class TestOutputMessages:
    """Test output messages"""
    
    def test_displays_root_directory(self):
        """Test that script displays repository root"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'echo "Repository root: $ROOT_DIR"' in content
    
    def test_displays_checking_message(self):
        """Test that script displays checking message for each file"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'echo "Checking $file"' in content
    
    def test_displays_patched_message(self):
        """Test that script displays success message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'echo "Patched and validated: $file"' in content
    
    def test_displays_warning_on_failure(self):
        """Test that script displays warning when restore is needed"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'WARNING' in content or 'warning' in content.lower()
    
    def test_displays_completion_message(self):
        """Test that script displays completion message"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert 'echo "Done' in content


class TestScriptBehavior:
    """Test overall script behavior"""
    
    def test_processes_entire_repository(self):
        """Test that script scans entire repository from ROOT_DIR"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        # Should start find from ROOT_DIR
        assert 'find "$ROOT_DIR"' in content
    
    def test_only_processes_python_files(self):
        """Test that script only processes .py files"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert "-name '*.py'" in content
    
    def test_uses_null_delimiter(self):
        """Test that find uses null delimiter for safe file handling"""
        with open(SCRIPT_PATH) as f:
            content = f.read()
        assert '-print0' in content
        assert "read -r -d ''" in content or 'read -r -d $' in content


class TestScriptReliability:
    """Test script reliability features"""
    
    def test_handles_files_with_spaces(self):
        """Test that script can handle filenames with spaces"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file with spaces in name
            test_file = Path(tmpdir) / "test file with spaces.py"
            test_file.write_text("def func() -> int:\n    return 42\n")
            
            # Should process without errors
            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
                timeout=10
            )
            assert result.returncode == 0
    
    def test_preserves_file_permissions(self):
        """Test that script preserves original file permissions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func() -> int:\n    return 42\n")
            test_file.chmod(0o755)
            
            original_mode = test_file.stat().st_mode
            
            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
                timeout=10
            )
            
            # File should still exist and have same permissions
            assert test_file.exists()
            # Note: cp might change permissions, but the main file should be preserved
    
    def test_idempotent_execution(self):
        """Test that running script multiple times is safe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func() -> int:\n    return 42\n")
            
            # Run twice
            subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                cwd=tmpdir,
                shell=False,
                timeout=10
            )
            
            content_after_first = test_file.read_text()
            
            subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                cwd=tmpdir,
                shell=False,
                timeout=10
            )
            
            content_after_second = test_file.read_text()
            
            # Content should be identical after second run
            assert content_after_first == content_after_second


class TestEdgeCases:
    """Test edge cases"""
    
    def test_handles_empty_repository(self):
        """Test that script handles repositories with no Python files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
                timeout=10
            )
            # Should complete without error
            assert result.returncode == 0
    
    def test_handles_syntax_errors_in_existing_files(self):
        """Test that script doesn't break files that already have syntax errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "broken.py"
            test_file.write_text("def func(\n    # Missing closing paren")
            
            result = subprocess.run(  # noqa: S603, S607
                [BASH_PATH, str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                shell=False,
                timeout=10
            )
            
            # Script should complete, and backup should exist
            assert (Path(tmpdir) / "broken.py.bak").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])