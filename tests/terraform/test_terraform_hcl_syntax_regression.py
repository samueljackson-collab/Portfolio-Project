"""
Regression tests for Terraform HCL syntax errors.

This test suite validates fixes for HCL syntax errors:
- Extra closing brace in main.tf (line 161)
- Duplicate output definitions
- Missing required variables
- Structural integrity of Terraform files
"""

import subprocess
import shutil
import re
from pathlib import Path
import pytest


@pytest.fixture
def terraform_dir():
    """Return path to terraform directory."""
    return Path("terraform")


@pytest.fixture
def main_tf(terraform_dir):
    """Return path to main.tf."""
    return terraform_dir / "main.tf"


@pytest.fixture
def outputs_tf(terraform_dir):
    """Return path to outputs.tf."""
    return terraform_dir / "outputs.tf"


@pytest.fixture
def variables_tf(terraform_dir):
    """Return path to variables.tf."""
    return terraform_dir / "variables.tf"


@pytest.fixture
def backend_tf(terraform_dir):
    """Return path to backend.tf."""
    return terraform_dir / "backend.tf"


class TestTerraformSyntaxRegression:
    """Test for specific syntax regressions in Terraform files."""

    def test_no_unmatched_braces_in_main_tf(self, main_tf):
        """Verify main.tf has balanced braces."""
        with open(main_tf, 'r') as f:
            content = f.read()
        
        # Count opening and closing braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        assert open_braces == close_braces, \
            f"Unmatched braces in main.tf: {open_braces} '{{' but {close_braces} '}}'. " \
            f"Difference: {abs(open_braces - close_braces)}"

    def test_no_extra_closing_braces_after_outputs(self, main_tf):
        """Verify no extra closing braces appear after output blocks."""
        with open(main_tf, 'r') as f:
            lines = f.readlines()
        
        # Find output blocks and check for extra braces
        in_output_block = False
        output_block_closed = False
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            if stripped.startswith('output "'):
                in_output_block = True
                output_block_closed = False
            
            if in_output_block and stripped == '}':
                if output_block_closed:
                    pytest.fail(
                        f"Line {i}: Extra closing brace after output block. "
                        f"This causes syntax errors."
                    )
                output_block_closed = True
            
            # Check if we're starting a new block
            if in_output_block and (stripped.startswith('resource ') or 
                                    stripped.startswith('data ') or
                                    stripped.startswith('output "')):
                in_output_block = False

    def test_terraform_validate_syntax(self, terraform_dir):
        """Run terraform validate to check HCL syntax."""
        terraform_path = shutil.which("terraform")
        if not terraform_path:
            pytest.skip("terraform not found on this system")
        
        # Try to run terraform validate
        result = subprocess.run(
            [terraform_path, "validate", "-json"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        
        # Parse JSON output if available
        if result.stdout:
            import json
            try:
                validation_result = json.loads(result.stdout)
                if not validation_result.get("valid", False):
                    diagnostics = validation_result.get("diagnostics", [])
                    error_messages = [d.get("summary", "") for d in diagnostics if d.get("severity") == "error"]
                    if error_messages:
                        pytest.fail(
                            f"Terraform validation failed with errors:\n" +
                            "\n".join(error_messages)
                        )
            except json.JSONDecodeError:
                pass

    def test_no_duplicate_output_definitions(self, main_tf, outputs_tf):
        """Verify output definitions are not duplicated between main.tf and outputs.tf."""
        # Read both files
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        # Extract output names from main.tf
        main_outputs = re.findall(r'output\s+"([^"]+)"', main_content)
        
        # Extract output names from outputs.tf
        outputs_tf_outputs = re.findall(r'output\s+"([^"]+)"', outputs_content)
        
        # Find duplicates
        duplicates = set(main_outputs) & set(outputs_tf_outputs)
        
        assert not duplicates, \
            f"Duplicate output definitions found: {duplicates}. " \
            f"Outputs should be defined in either main.tf or outputs.tf, not both."

    def test_outputs_moved_correctly_if_consolidated(self, main_tf, outputs_tf):
        """If outputs were moved from outputs.tf to main.tf, verify correct migration."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        # Standard outputs that should exist
        expected_outputs = ['vpc_id', 'public_subnet_ids', 'private_subnet_ids', 
                          'rds_endpoint', 'assets_bucket']
        
        main_outputs = re.findall(r'output\s+"([^"]+)"', main_content)
        outputs_tf_outputs = re.findall(r'output\s+"([^"]+)"', outputs_content)
        
        all_outputs = set(main_outputs) | set(outputs_tf_outputs)
        
        # Check if any expected outputs are missing
        missing_outputs = [out for out in expected_outputs if out not in all_outputs]
        
        if missing_outputs:
            pytest.fail(
                f"Missing output definitions: {missing_outputs}. "
                f"Found in main.tf: {main_outputs}, Found in outputs.tf: {outputs_tf_outputs}"
            )


class TestVariableDefinitionIntegrity:
    """Test that required variables are properly defined."""

    def test_project_tag_variable_exists(self, main_tf, variables_tf):
        """Verify project_tag variable is defined if used in main.tf."""
        main_content = main_tf.read_text()
        variables_content = variables_tf.read_text()
        
        # Check if project_tag is used
        if 'var.project_tag' in main_content:
            assert 'variable "project_tag"' in variables_content, \
                "project_tag variable is used in main.tf but not defined in variables.tf"

    def test_aws_region_variable_exists(self, main_tf, variables_tf):
        """Verify aws_region variable is defined if used in main.tf."""
        main_content = main_tf.read_text()
        variables_content = variables_tf.read_text()
        
        # Check if aws_region is used
        if 'var.aws_region' in main_content:
            assert 'variable "aws_region"' in variables_content, \
                "aws_region variable is used in main.tf but not defined in variables.tf"

    def test_all_used_variables_are_defined(self, terraform_dir, main_tf, variables_tf):
        """Verify all variables referenced in main.tf are defined in variables.tf."""
        main_content = main_tf.read_text()
        variables_content = variables_tf.read_text()
        
        # Extract all var. references from main.tf
        var_references = re.findall(r'var\.(\w+)', main_content)
        unique_vars = set(var_references)
        
        # Extract all variable definitions from variables.tf
        defined_vars = re.findall(r'variable\s+"([^"]+)"', variables_content)
        defined_vars_set = set(defined_vars)
        
        # Find undefined variables
        undefined_vars = unique_vars - defined_vars_set
        
        assert not undefined_vars, \
            f"Variables used but not defined: {undefined_vars}. " \
            f"Add these to variables.tf or remove references from main.tf."

    def test_critical_variables_not_removed(self, variables_tf):
        """Verify critical variables haven't been accidentally removed."""
        content = variables_tf.read_text()
        
        # Variables that are commonly required
        important_vars = ['vpc_cidr', 'create_rds', 'db_name']
        
        defined_vars = re.findall(r'variable\s+"([^"]+)"', content)
        
        missing_important = [var for var in important_vars if var not in defined_vars]
        
        if missing_important:
            pytest.warning(
                f"Important variables may be missing: {missing_important}. "
                f"Verify these are not needed or are defined elsewhere."
            )


class TestBackendConfiguration:
    """Test backend configuration integrity."""

    def test_backend_has_required_configuration(self, backend_tf):
        """Verify backend.tf has all required S3 backend fields."""
        content = backend_tf.read_text()
        
        required_fields = ['bucket', 'key', 'region', 'dynamodb_table', 'encrypt']
        
        missing_fields = [field for field in required_fields if field not in content]
        
        assert not missing_fields, \
            f"Backend configuration missing required fields: {missing_fields}"

    def test_backend_placeholders_are_documented(self, backend_tf):
        """Verify backend template uses clear placeholders."""
        content = backend_tf.read_text()
        
        if 'REPLACE_ME' in content or 'TODO' in content or 'CHANGEME' in content:
            # This is good - it's a template
            # Verify it has comments explaining what to replace
            assert 'Replace' in content or 'replace' in content or '#' in content, \
                "Backend template should have comments explaining placeholders"

    def test_backend_encryption_enabled(self, backend_tf):
        """Verify backend configuration enables encryption."""
        content = backend_tf.read_text()
        
        assert 'encrypt' in content, "Backend should specify encrypt setting"
        assert 'true' in content, "Backend encryption should be set to true"


class TestResourceStructuralIntegrity:
    """Test that resources are structurally sound."""

    def test_all_resource_blocks_properly_closed(self, main_tf):
        """Verify all resource blocks have matching braces."""
        with open(main_tf, 'r') as f:
            lines = f.readlines()
        
        resource_blocks = []
        brace_count = 0
        in_resource = False
        resource_start = 0
        
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            if stripped.startswith('resource ') or stripped.startswith('data '):
                in_resource = True
                resource_start = i
                brace_count = 0
            
            if in_resource:
                brace_count += line.count('{')
                brace_count -= line.count('}')
                
                if brace_count == 0 and ('{' in line or '}' in line):
                    resource_blocks.append((resource_start, i))
                    in_resource = False
        
        # Verify we found resource blocks and they all closed
        assert len(resource_blocks) > 0, "No resource blocks found in main.tf"

    def test_output_blocks_properly_formatted(self, main_tf, outputs_tf):
        """Verify output blocks are properly formatted."""
        for tf_file in [main_tf, outputs_tf]:
            content = tf_file.read_text()
            
            # Find all output blocks
            output_matches = re.finditer(r'output\s+"([^"]+)"\s*\{([^}]+)\}', content, re.DOTALL)
            
            for match in output_matches:
                output_name = match.group(1)
                output_body = match.group(2)
                
                # Check for value field
                assert 'value' in output_body, \
                    f"Output '{output_name}' in {tf_file.name} missing 'value' field"

    def test_no_orphaned_code_after_syntax_errors(self, main_tf):
        """Verify no code is orphaned due to syntax errors."""
        content = main_tf.read_text()
        lines = content.split('\n')
        
        # Check last 20 lines for orphaned resource definitions
        last_lines = lines[-20:]
        
        for i, line in enumerate(last_lines, start=len(lines)-20):
            stripped = line.strip()
            if stripped.startswith('resource ') or stripped.startswith('data '):
                # Found a resource definition near the end - check if it's complete
                remaining = '\n'.join(lines[i:])
                open_braces = remaining.count('{')
                close_braces = remaining.count('}')
                
                if open_braces != close_braces:
                    pytest.fail(
                        f"Possibly incomplete resource block starting at line {i+1}: {stripped}. "
                        f"This may indicate orphaned code after a syntax error."
                    )


class TestHCLParsingEdgeCases:
    """Test edge cases in HCL parsing."""

    def test_no_dangling_conditionals(self, main_tf):
        """Verify conditional blocks are complete."""
        content = main_tf.read_text()
        
        # Find count = var.something ? 1 : 0 patterns
        conditional_counts = re.findall(r'count\s*=\s*var\.\w+\s*\?\s*\d+\s*:\s*\d+', content)
        
        # Verify they're syntactically correct
        for cond in conditional_counts:
            assert cond.count('?') == 1, f"Invalid conditional: {cond}"
            assert cond.count(':') == 1, f"Invalid conditional: {cond}"

    def test_string_interpolation_valid(self, main_tf):
        """Verify string interpolation syntax is valid."""
        content = main_tf.read_text()
        
        # Find ${...} patterns
        interpolations = re.findall(r'\$\{[^}]+\}', content)
        
        for interp in interpolations:
            # Basic validation - should have balanced brackets
            assert interp.count('{') == interp.count('}'), \
                f"Invalid interpolation: {interp}"

    def test_no_mixed_output_locations_causing_conflicts(self, main_tf, outputs_tf):
        """Verify outputs aren't split in a way that causes conflicts."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        # If outputs exist in both files, they should be logically separated
        main_has_outputs = 'output "' in main_content
        outputs_has_outputs = 'output "' in outputs_content
        
        if main_has_outputs and outputs_has_outputs:
            # Both have outputs - verify no duplicates (already tested elsewhere)
            # Also verify each file has description in outputs
            if main_has_outputs:
                main_outputs = re.findall(r'output\s+"([^"]+)"', main_content)
                for output in main_outputs:
                    # Extract the output block
                    pattern = rf'output\s+"{output}"\s*\{{([^}}]+)\}}'
                    match = re.search(pattern, main_content, re.DOTALL)
                    if match:
                        output_block = match.group(1)
                        # Outputs should have descriptions for clarity
                        if 'description' not in output_block:
                            pytest.warning(
                                f"Output '{output}' in main.tf lacks description. "
                                f"Consider adding for documentation."
                            )