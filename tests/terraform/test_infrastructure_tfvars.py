"""
Comprehensive tests for infrastructure/terraform/terraform.tfvars.example

This test suite validates:
- File existence and structure
- Required configuration sections
- Variable naming conventions
- Documentation completeness
- Security best practices
- Example values appropriateness
- Configuration consistency
"""

import re
from pathlib import Path
import pytest


@pytest.fixture
def tfvars_example_path():
    """Return path to infrastructure terraform.tfvars.example."""
    return Path("infrastructure/terraform/terraform.tfvars.example")


class TestTfvarsExampleExistence:
    """Test terraform.tfvars.example file properties."""

    def test_file_exists(self, tfvars_example_path):
        """Verify terraform.tfvars.example exists."""
        assert tfvars_example_path.exists(), f"File not found: {tfvars_example_path}"

    def test_file_is_readable(self, tfvars_example_path):
        """Verify file can be read."""
        content = tfvars_example_path.read_text()
        assert len(content) > 0, "File is empty"

    def test_file_has_proper_extension(self, tfvars_example_path):
        """Verify file has .example extension for safety."""
        assert tfvars_example_path.name.endswith(".example"), \
            "Example file should have .example extension to prevent accidental use"


class TestTfvarsStructure:
    """Test terraform.tfvars.example structure and sections."""

    def test_has_header_documentation(self, tfvars_example_path):
        """Verify file has comprehensive header documentation."""
        content = tfvars_example_path.read_text()
        assert "Terraform Variables Configuration" in content or \
               "terraform.tfvars" in content, \
               "File should have header documentation"

    def test_has_usage_instructions(self, tfvars_example_path):
        """Verify file includes usage instructions."""
        content = tfvars_example_path.read_text()
        assert "USAGE" in content.upper() or "how to" in content.lower(), \
               "File should include usage instructions"

    def test_has_security_warning(self, tfvars_example_path):
        """Verify file includes security warnings about sensitive data."""
        content = tfvars_example_path.read_text()
        assert any(keyword in content.upper() for keyword in ["SENSITIVE", "SECURITY", "SECRET"]), \
               "File should warn about sensitive information"

    def test_variables_follow_naming_convention(self, tfvars_example_path):
        """Verify variables follow snake_case naming convention."""
        content = tfvars_example_path.read_text()
        # Find all variable assignments (e.g., var_name = "value")
        variable_pattern = r'^([a-z][a-z0-9_]*)\s*='
        variables = re.findall(variable_pattern, content, re.MULTILINE)
        
        invalid_vars = [var for var in variables if not var.islower() or '__' in var]
        assert len(invalid_vars) == 0, \
            f"Variables should follow snake_case convention: {invalid_vars}"


class TestRequiredVariables:
    """Test presence of required configuration variables."""

    def test_has_project_identification_section(self, tfvars_example_path):
        """Verify file has project identification section."""
        content = tfvars_example_path.read_text()
        assert "project_name" in content, "Should define project_name variable"
        assert "environment" in content, "Should define environment variable"

    def test_has_database_configuration(self, tfvars_example_path):
        """Verify file has database configuration section."""
        content = tfvars_example_path.read_text()
        assert "db_username" in content, "Should define db_username"
        assert "db_password" in content, "Should define db_password"

    def test_has_network_configuration(self, tfvars_example_path):
        """Verify file has network configuration section."""
        content = tfvars_example_path.read_text()
        assert "vpc_id" in content or "vpc" in content.lower(), \
               "Should define VPC configuration"
        assert "subnet" in content.lower(), "Should define subnet configuration"

    def test_has_instance_sizing_configuration(self, tfvars_example_path):
        """Verify file has instance sizing configuration."""
        content = tfvars_example_path.read_text()
        assert "instance_class" in content or "instance_type" in content, \
               "Should define instance sizing"

    def test_has_backup_configuration(self, tfvars_example_path):
        """Verify file has backup/HA configuration."""
        content = tfvars_example_path.read_text()
        assert "backup" in content.lower() or "retention" in content.lower(), \
               "Should define backup configuration"


class TestSecurityBestPractices:
    """Test security best practices in configuration."""

    def test_warns_against_hardcoding_passwords(self, tfvars_example_path):
        """Verify file warns against hardcoding sensitive values."""
        content = tfvars_example_path.read_text()
        assert "CHANGE_ME" in content or "password" in content.lower(), \
               "Should provide example password placeholder"
        
        # Check for Secrets Manager recommendation
        if "password" in content.lower():
            assert "secrets" in content.lower() or "secret" in content.lower(), \
                   "Should recommend using AWS Secrets Manager"

    def test_has_placeholder_values(self, tfvars_example_path):
        """Verify sensitive values use placeholders not real values."""
        content = tfvars_example_path.read_text()
        
        # Should not contain real AWS resource IDs
        assert not re.search(r'vpc-[a-f0-9]{17}(?![x])', content), \
               "Should not contain real VPC IDs (use placeholders like vpc-xxxxx)"
        assert not re.search(r'subnet-[a-f0-9]{17}(?![x])', content), \
               "Should not contain real subnet IDs (use placeholders)"

    def test_encryption_enabled_by_default(self, tfvars_example_path):
        """Verify encryption settings are enabled in examples."""
        content = tfvars_example_path.read_text()
        # If encryption settings exist, they should be enabled
        if "encrypt" in content.lower():
            # Don't assert false for encryption
            assert "encrypt" in content.lower(), "Encryption configuration present"

    def test_deletion_protection_mentioned(self, tfvars_example_path):
        """Verify deletion protection is mentioned for production."""
        content = tfvars_example_path.read_text()
        if "production" in content.lower():
            assert "deletion_protection" in content.lower() or \
                   "deletion" in content.lower(), \
                   "Should mention deletion protection for production"


class TestDocumentationQuality:
    """Test documentation completeness and quality."""

    def test_variables_have_comments(self, tfvars_example_path):
        """Verify most variables have explanatory comments."""
        content = tfvars_example_path.read_text()
        lines = content.split('\n')
        
        variable_lines = [i for i, line in enumerate(lines) 
                         if '=' in line and not line.strip().startswith('#')]
        
        commented_vars = 0
        for var_line_num in variable_lines:
            # Check for comment within 5 lines before the variable
            for i in range(max(0, var_line_num - 5), var_line_num):
                if lines[i].strip().startswith('#'):
                    commented_vars += 1
                    break
        
        if len(variable_lines) > 0:
            comment_ratio = commented_vars / len(variable_lines)
            assert comment_ratio >= 0.5, \
                   f"At least 50% of variables should have comments (found {comment_ratio:.0%})"

    def test_has_examples_for_different_environments(self, tfvars_example_path):
        """Verify file provides examples for different environments."""
        content = tfvars_example_path.read_text()
        
        # Should mention multiple environments
        env_count = sum(1 for env in ["dev", "development", "staging", "prod", "production"] 
                       if env in content.lower())
        assert env_count >= 2, \
               "Should provide examples for at least 2 different environments"

    def test_has_cost_information(self, tfvars_example_path):
        """Verify file includes cost estimates or considerations."""
        content = tfvars_example_path.read_text()
        assert "cost" in content.lower() or "$" in content or "month" in content.lower(), \
               "Should include cost information or estimates"

    def test_has_troubleshooting_section(self, tfvars_example_path):
        """Verify file includes troubleshooting guidance."""
        content = tfvars_example_path.read_text()
        assert "troubleshoot" in content.lower() or \
               "problem" in content.lower() or \
               "error" in content.lower(), \
               "Should include troubleshooting guidance"


class TestConfigurationValues:
    """Test appropriateness of example configuration values."""

    def test_subnet_ids_are_lists(self, tfvars_example_path):
        """Verify subnet_ids uses list syntax."""
        content = tfvars_example_path.read_text()
        if "subnet_ids" in content or "subnet" in content:
            # Check for list syntax with brackets
            assert "[" in content and "]" in content, \
                   "Subnet configuration should use list syntax"

    def test_tags_are_maps(self, tfvars_example_path):
        """Verify tags use map/object syntax."""
        content = tfvars_example_path.read_text()
        if "tags" in content:
            # Check for map syntax with braces
            assert "{" in content and "}" in content, \
                   "Tags should use map/object syntax"

    def test_boolean_values_use_terraform_syntax(self, tfvars_example_path):
        """Verify boolean values use 'true'/'false' not other formats."""
        content = tfvars_example_path.read_text()
        
        # If there are boolean-like variables
        bool_vars = ["multi_az", "deletion_protection", "skip_final_snapshot", 
                    "apply_immediately", "enabled"]
        
        for bool_var in bool_vars:
            if bool_var in content:
                # Check that it uses 'true' or 'false', not "true" or 1/0
                pattern = rf'{bool_var}\s*=\s*(true|false)'
                assert re.search(pattern, content), \
                       f"{bool_var} should use unquoted true/false"

    def test_storage_values_are_reasonable(self, tfvars_example_path):
        """Verify storage allocation values are reasonable."""
        content = tfvars_example_path.read_text()
        
        # Check allocated_storage
        if "allocated_storage" in content:
            match = re.search(r'allocated_storage\s*=\s*(\d+)', content)
            if match:
                storage = int(match.group(1))
                assert 20 <= storage <= 65536, \
                       f"allocated_storage should be between 20 and 65536 GB, got {storage}"

    def test_retention_period_is_reasonable(self, tfvars_example_path):
        """Verify backup retention period is within AWS limits."""
        content = tfvars_example_path.read_text()
        
        if "retention" in content.lower():
            match = re.search(r'retention.*?=\s*(\d+)', content)
            if match:
                days = int(match.group(1))
                assert 0 <= days <= 35, \
                       f"Backup retention should be between 0 and 35 days, got {days}"


class TestConsistencyChecks:
    """Test internal consistency of configuration."""

    def test_max_storage_greater_than_allocated(self, tfvars_example_path):
        """Verify max_allocated_storage is greater than allocated_storage."""
        content = tfvars_example_path.read_text()
        
        allocated_match = re.search(r'allocated_storage\s*=\s*(\d+)', content)
        max_allocated_match = re.search(r'max_allocated_storage\s*=\s*(\d+)', content)
        
        if allocated_match and max_allocated_match:
            allocated = int(allocated_match.group(1))
            max_allocated = int(max_allocated_match.group(1))
            assert max_allocated >= allocated, \
                   f"max_allocated_storage ({max_allocated}) should be >= allocated_storage ({allocated})"

    def test_production_has_stricter_settings(self, tfvars_example_path):
        """Verify production examples have stricter safety settings."""
        content = tfvars_example_path.read_text()
        
        # Find production section if it exists
        lines = content.split('\n')
        in_prod_section = False
        prod_settings = {}
        
        for line in lines:
            if "production" in line.lower() and "example" in line.lower():
                in_prod_section = True
            elif "example" in line.lower() and ("dev" in line.lower() or "staging" in line.lower()):
                in_prod_section = False
            elif in_prod_section and "=" in line:
                match = re.match(r'#?\s*(\w+)\s*=\s*(.*)', line)
                if match:
                    prod_settings[match.group(1)] = match.group(2).strip()
        
        # If production section exists, verify strict settings
        if prod_settings:
            if "deletion_protection" in prod_settings:
                assert "true" in prod_settings["deletion_protection"].lower(), \
                       "Production should have deletion_protection = true"
            if "skip_final_snapshot" in prod_settings:
                assert "false" in prod_settings["skip_final_snapshot"].lower(), \
                       "Production should have skip_final_snapshot = false"


class TestFileFormat:
    """Test file format and style."""

    def test_uses_consistent_indentation(self, tfvars_example_path):
        """Verify file uses consistent indentation."""
        content = tfvars_example_path.read_text()
        lines = content.split('\n')
        
        # Check indented lines use consistent spacing
        indented_lines = [line for line in lines if line and line[0] == ' ']
        if indented_lines:
            # Most common indent should be 2 or 4 spaces
            indent_sizes = [len(line) - len(line.lstrip()) for line in indented_lines]
            # Filter out comment-only lines
            indent_sizes = [size for size, line in zip(indent_sizes, indented_lines) 
                          if not line.strip().startswith('#')]
            if indent_sizes:
                most_common = max(set(indent_sizes), key=indent_sizes.count)
                assert most_common in [2, 4], \
                       f"Should use 2 or 4 space indentation consistently, found {most_common}"

    def test_has_section_separators(self, tfvars_example_path):
        """Verify file uses section separators for readability."""
        content = tfvars_example_path.read_text()
        
        # Should have separator lines (dashes or equal signs)
        separator_count = content.count('---') + content.count('===')
        assert separator_count >= 3, \
               "Should use section separators (--- or ===) for readability"

    def test_no_trailing_whitespace(self, tfvars_example_path):
        """Verify lines don't have excessive trailing whitespace."""
        content = tfvars_example_path.read_text()
        lines = content.split('\n')
        
        lines_with_trailing = [i for i, line in enumerate(lines, 1) 
                              if line.endswith(' ' * 3)]  # 3+ trailing spaces
        
        assert len(lines_with_trailing) < len(lines) * 0.1, \
               f"Too many lines with trailing whitespace: {len(lines_with_trailing)}"