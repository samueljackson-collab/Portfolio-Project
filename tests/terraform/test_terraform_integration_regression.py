"""
Integration tests for Terraform configuration after recent changes.

This test suite validates:
- Overall Terraform configuration integrity
- Cross-file dependencies
- Module interactions
- Configuration completeness
"""

import re
from pathlib import Path
import pytest


@pytest.fixture
def terraform_dir():
    """Return path to terraform directory."""
    return Path("terraform")


class TestTerraformConfigurationIntegrity:
    """Test overall Terraform configuration integrity."""

    def test_all_terraform_files_present(self, terraform_dir):
        """Verify all essential Terraform files exist."""
        required_files = ['main.tf', 'variables.tf', 'outputs.tf', 'backend.tf']
        
        for filename in required_files:
            file_path = terraform_dir / filename
            assert file_path.exists(), \
                f"Required file {filename} is missing from terraform directory"

    def test_provider_configuration_complete(self, terraform_dir):
        """Verify provider configuration is complete."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        # Should have AWS provider
        assert 'provider "aws"' in content, "AWS provider not configured"
        
        # Provider should specify region
        assert 'region' in content, "Provider should specify region"

    def test_variables_used_in_main_are_defined(self, terraform_dir):
        """Verify all variables used in main.tf are defined."""
        main_tf = terraform_dir / "main.tf"
        variables_tf = terraform_dir / "variables.tf"
        
        main_content = main_tf.read_text()
        var_content = variables_tf.read_text()
        
        # Extract used variables
        used_vars = set(re.findall(r'var\.(\w+)', main_content))
        
        # Extract defined variables
        defined_vars = set(re.findall(r'variable\s+"(\w+)"', var_content))
        
        undefined = used_vars - defined_vars
        
        assert not undefined, \
            f"Variables used in main.tf but not defined in variables.tf: {undefined}"

    def test_outputs_reference_valid_resources(self, terraform_dir):
        """Verify outputs reference resources that exist."""
        main_tf = terraform_dir / "main.tf"
        outputs_tf = terraform_dir / "outputs.tf"
        
        main_content = main_tf.read_text()
        
        # Check outputs in both files
        for tf_file in [main_tf, outputs_tf]:
            if not tf_file.exists():
                continue
            
            content = tf_file.read_text()
            
            # Extract output values
            output_blocks = re.finditer(
                r'output\s+"([^"]+)"\s*\{([^}]+)\}',
                content,
                re.DOTALL
            )
            
            for match in output_blocks:
                output_name = match.group(1)
                output_value = match.group(2)
                
                # Extract resource references
                resource_refs = re.findall(
                    r'(aws_\w+)\.(\w+)',
                    output_value
                )
                
                for resource_type, resource_name in resource_refs:
                    # Verify resource exists in main.tf
                    resource_pattern = rf'resource\s+"{resource_type}"\s+"{resource_name}"'
                    
                    if not re.search(resource_pattern, main_content):
                        pytest.warning(
                            f"Output '{output_name}' in {tf_file.name} references "
                            f"{resource_type}.{resource_name}, but this resource "
                            f"is not found in main.tf"
                        )

    def test_conditional_resources_have_count_in_outputs(self, terraform_dir):
        """Verify outputs handle conditional resources with indexing."""
        main_tf = terraform_dir / "main.tf"
        
        main_content = main_tf.read_text()
        
        # Find resources with count
        resources_with_count = re.findall(
            r'resource\s+"(aws_\w+)"\s+"(\w+)"\s*\{[^}]*count\s*=',
            main_content,
            re.DOTALL
        )
        
        for resource_type, resource_name in resources_with_count:
            # Check if outputs reference this resource
            output_pattern = rf'{resource_type}\.{resource_name}'
            
            outputs_to_check = []
            for tf_file in [main_tf, terraform_dir / "outputs.tf"]:
                if tf_file.exists():
                    outputs_to_check.append(tf_file.read_text())
            
            for output_content in outputs_to_check:
                if output_pattern in output_content:
                    # Should use indexing [0] or [*]
                    indexed_pattern = rf'{resource_type}\.{resource_name}\[[\d*\]]'
                    
                    if not re.search(indexed_pattern, output_content):
                        pytest.warning(
                            f"Output references {resource_type}.{resource_name} "
                            f"which has count, but doesn't use indexing [0] or [*]"
                        )

    def test_backend_configuration_matches_usage(self, terraform_dir):
        """Verify backend configuration is properly set up."""
        backend_tf = terraform_dir / "backend.tf"
        content = backend_tf.read_text()
        
        # Should have S3 backend
        assert 'backend "s3"' in content, "S3 backend not configured"
        
        # Should have all required fields
        required_fields = ['bucket', 'key', 'region', 'dynamodb_table', 'encrypt']
        for field in required_fields:
            assert field in content, \
                f"Backend configuration missing {field}"

    def test_resource_dependencies_valid(self, terraform_dir):
        """Verify resource dependencies are valid."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        # Extract all depends_on references
        depends_on_pattern = r'depends_on\s*=\s*\[([^\]]+)\]'
        dependencies = re.findall(depends_on_pattern, content)
        
        # Extract all resource definitions
        resource_pattern = r'resource\s+"(aws_\w+)"\s+"(\w+)"'
        resources = re.findall(resource_pattern, content)
        resource_ids = {f'{rt}.{rn}' for rt, rn in resources}
        
        # Add data sources
        data_pattern = r'data\s+"(aws_\w+)"\s+"(\w+)"'
        data_sources = re.findall(data_pattern, content)
        resource_ids.update({f'data.{dt}.{dn}' for dt, dn in data_sources})
        
        # Verify all dependencies exist
        for dep_list in dependencies:
            deps = [d.strip() for d in dep_list.split(',')]
            for dep in deps:
                # Clean up the dependency reference
                dep_clean = dep.replace('aws_', '').replace('[0]', '').strip()
                
                # Check if dependency exists
                if dep_clean and dep_clean not in resource_ids:
                    # Try partial matching
                    matching = [r for r in resource_ids if dep_clean in r]
                    if not matching:
                        pytest.warning(
                            f"Dependency reference '{dep}' may not exist. "
                            f"Verify resource is defined."
                        )

    def test_no_circular_dependencies(self, terraform_dir):
        """Verify there are no circular dependencies."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        # Build dependency graph
        depends_graph = {}
        
        # Extract resources and their dependencies
        resource_blocks = re.finditer(
            r'resource\s+"(aws_\w+)"\s+"(\w+)"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
            content,
            re.DOTALL
        )
        
        for match in resource_blocks:
            resource_type = match.group(1)
            resource_name = match.group(2)
            resource_body = match.group(3)
            
            resource_id = f'{resource_type}.{resource_name}'
            
            # Find explicit depends_on
            depends_on_match = re.search(r'depends_on\s*=\s*\[([^\]]+)\]', resource_body)
            if depends_on_match:
                deps = [d.strip() for d in depends_on_match.group(1).split(',')]
                depends_graph[resource_id] = deps
            
            # Find implicit dependencies (resource references)
            implicit_deps = re.findall(r'(aws_\w+)\.(\w+)', resource_body)
            if implicit_deps:
                current_deps = depends_graph.get(resource_id, [])
                current_deps.extend([f'{dt}.{dn}' for dt, dn in implicit_deps])
                depends_graph[resource_id] = list(set(current_deps))
        
        # Check for circular dependencies using DFS
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in depends_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in depends_graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    pytest.fail(
                        f"Circular dependency detected involving: {node}. "
                        f"This will cause Terraform to fail."
                    )


class TestConfigurationCompleteness:
    """Test that configuration is complete and production-ready."""

    def test_security_groups_properly_configured(self, terraform_dir):
        """Verify security groups are properly configured."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        if 'resource "aws_security_group"' in content:
            # Should have ingress or egress rules
            sg_blocks = re.finditer(
                r'resource\s+"aws_security_group"\s+"(\w+)"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
                content,
                re.DOTALL
            )
            
            for match in sg_blocks:
                sg_name = match.group(1)
                sg_body = match.group(2)
                
                has_ingress = 'ingress {' in sg_body
                has_egress = 'egress {' in sg_body
                
                assert has_ingress or has_egress, \
                    f"Security group '{sg_name}' has no ingress or egress rules"

    def test_tags_applied_to_resources(self, terraform_dir):
        """Verify resources are properly tagged."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        # Count resources
        resource_count = content.count('resource "aws_')
        
        # Count tag usage
        tag_count = content.count('tags =') + content.count('tags=')
        
        # Most resources should be tagged
        if resource_count > 0:
            tag_ratio = tag_count / resource_count
            assert tag_ratio > 0.5, \
                f"Only {tag_count}/{resource_count} resources are tagged. " \
                f"Best practice is to tag all resources."

    def test_locals_block_exists_for_common_values(self, terraform_dir):
        """Verify locals block exists for common values."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        assert 'locals {' in content, \
            "Consider using locals block for common values and tags"
        
        assert 'common_tags' in content or 'tags' in content, \
            "Consider defining common tags in locals block"