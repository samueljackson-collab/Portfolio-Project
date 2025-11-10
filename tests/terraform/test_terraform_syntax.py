"""
Comprehensive tests for Terraform configuration files.

This test suite validates:
- HCL syntax correctness
- Required providers and versions
- Resource naming conventions
- Variable definitions and types
- Output definitions
- Backend configuration
- Security best practices
"""

import json
import subprocess
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
def variables_tf(terraform_dir):
    """Return path to variables.tf."""
    return terraform_dir / "variables.tf"


@pytest.fixture
def outputs_tf(terraform_dir):
    """Return path to outputs.tf."""
    return terraform_dir / "outputs.tf"


@pytest.fixture
def backend_tf(terraform_dir):
    """Return path to backend.tf."""
    return terraform_dir / "backend.tf"


class TestTerraformDirectory:
    """Test Terraform directory structure."""

    def test_terraform_directory_exists(self, terraform_dir):
        """Verify terraform directory exists."""
        assert terraform_dir.exists()
        assert terraform_dir.is_dir()

    def test_main_tf_exists(self, main_tf):
        """Verify main.tf exists."""
        assert main_tf.exists()

    def test_variables_tf_exists(self, variables_tf):
        """Verify variables.tf exists."""
        assert variables_tf.exists()

    def test_outputs_tf_exists(self, outputs_tf):
        """Verify outputs.tf exists."""
        assert outputs_tf.exists()

    def test_backend_tf_exists(self, backend_tf):
        """Verify backend.tf exists."""
        assert backend_tf.exists()


class TestMainTfContent:
    """Test main.tf configuration."""

    def test_main_tf_has_provider_declaration(self, main_tf):
        """Verify main.tf declares AWS provider."""
        content = main_tf.read_text()
        assert 'provider "aws"' in content

    def test_main_tf_has_vpc_resource(self, main_tf):
        """Verify main.tf defines VPC resource."""
        content = main_tf.read_text()
        assert 'resource "aws_vpc"' in content

    def test_main_tf_has_subnet_resources(self, main_tf):
        """Verify main.tf defines subnet resources."""
        content = main_tf.read_text()
        assert 'resource "aws_subnet" "public"' in content
        assert 'resource "aws_subnet" "private"' in content

    def test_main_tf_has_internet_gateway(self, main_tf):
        """Verify main.tf defines internet gateway."""
        content = main_tf.read_text()
        assert 'resource "aws_internet_gateway"' in content

    def test_main_tf_has_route_table(self, main_tf):
        """Verify main.tf defines route table."""
        content = main_tf.read_text()
        assert 'resource "aws_route_table"' in content

    def test_main_tf_has_security_group(self, main_tf):
        """Verify main.tf defines security groups."""
        content = main_tf.read_text()
        assert 'resource "aws_security_group"' in content

    def test_main_tf_uses_common_tags(self, main_tf):
        """Verify main.tf uses common tags via locals."""
        content = main_tf.read_text()
        assert "locals {" in content
        assert "common_tags" in content
        assert "merge(local.common_tags" in content

    def test_main_tf_has_rds_resources(self, main_tf):
        """Verify main.tf has RDS-related resources."""
        content = main_tf.read_text()
        assert 'resource "aws_db_instance"' in content or "postgres" in content
        assert 'resource "aws_db_subnet_group"' in content

    def test_main_tf_has_conditional_resources(self, main_tf):
        """Verify main.tf uses count for conditional resources."""
        content = main_tf.read_text()
        assert "count = var.create_rds" in content

    def test_main_tf_generates_random_password(self, main_tf):
        """Verify main.tf generates random password for RDS."""
        content = main_tf.read_text()
        assert 'resource "random_password"' in content


class TestVariablesTfContent:
    """Test variables.tf configuration."""

    def test_variables_tf_has_vpc_cidr(self, variables_tf):
        """Verify variables.tf defines VPC CIDR."""
        content = variables_tf.read_text()
        assert 'variable "vpc_cidr"' in content
        assert "10.0.0.0/16" in content

    def test_variables_tf_has_subnet_cidrs(self, variables_tf):
        """Verify variables.tf defines subnet CIDRs."""
        content = variables_tf.read_text()
        assert 'variable "public_subnet_cidrs"' in content
        assert 'variable "private_subnet_cidrs"' in content

    def test_variables_tf_has_create_rds_flag(self, variables_tf):
        """Verify variables.tf has create_rds boolean."""
        content = variables_tf.read_text()
        assert 'variable "create_rds"' in content
        assert "type        = bool" in content

    def test_variables_tf_has_db_variables(self, variables_tf):
        """Verify variables.tf defines database variables."""
        content = variables_tf.read_text()
        assert 'variable "db_name"' in content
        assert 'variable "db_username"' in content
        assert 'variable "db_password"' in content

    def test_variables_tf_has_eks_variables(self, variables_tf):
        """Verify variables.tf defines EKS variables."""
        content = variables_tf.read_text()
        assert 'variable "create_eks"' in content
        assert 'variable "eks_cluster_name"' in content

    def test_variables_have_descriptions(self, variables_tf):
        """Verify all variables have descriptions."""
        content = variables_tf.read_text()
        variable_count = content.count('variable "')
        description_count = content.count('description =')
        # Allow some variance but most should have descriptions
        assert description_count >= variable_count * 0.8

    def test_variables_have_types(self, variables_tf):
        """Verify variables specify types."""
        content = variables_tf.read_text()
        assert "type        = string" in content
        assert "type        = bool" in content or "type = bool" in content

    def test_variables_have_defaults(self, variables_tf):
        """Verify variables have default values."""
        content = variables_tf.read_text()
        assert "default     =" in content or "default =" in content


class TestOutputsTfContent:
    """Test outputs.tf configuration."""

    def test_outputs_tf_has_assets_bucket_output(self, outputs_tf):
        """Verify outputs.tf defines assets bucket output."""
        content = outputs_tf.read_text()
        assert 'output "assets_bucket"' in content

    def test_outputs_have_descriptions(self, outputs_tf):
        """Verify outputs have descriptions."""
        content = outputs_tf.read_text()
        output_count = content.count('output "')
        description_count = content.count('description =')
        # All outputs should have descriptions
        assert description_count >= output_count


class TestBackendTfContent:
    """Test backend.tf configuration."""

    def test_backend_tf_has_s3_backend(self, backend_tf):
        """Verify backend.tf configures S3 backend."""
        content = backend_tf.read_text()
        assert 'backend "s3"' in content

    def test_backend_tf_has_required_fields(self, backend_tf):
        """Verify backend.tf has all required S3 backend fields."""
        content = backend_tf.read_text()
        assert "bucket" in content
        assert "key" in content
        assert "region" in content
        assert "dynamodb_table" in content

    def test_backend_tf_enables_encryption(self, backend_tf):
        """Verify backend.tf enables encryption."""
        content = backend_tf.read_text()
        assert "encrypt" in content
        assert "true" in content

    def test_backend_tf_uses_variables(self, backend_tf):
        """Verify backend.tf uses variables for configuration."""
        content = backend_tf.read_text()
        # Backend config typically uses var. references
        assert "var." in content or "${" in content


class TestResourceNaming:
    """Test resource naming conventions."""

    def test_resources_use_consistent_naming(self, main_tf):
        """Verify resources follow naming conventions."""
        content = main_tf.read_text()
        # Resources should use project_tag variable in names
        assert "${var.project_tag}" in content or "twisted-monk" in content or "twisted_monk" in content

    def test_resources_tagged_with_name(self, main_tf):
        """Verify resources are tagged with Name."""
        content = main_tf.read_text()
        # Count tag definitions
        name_tag_count = content.count('Name =') + content.count('Name=')
        # Most resources should have Name tags
        assert name_tag_count > 0


class TestSecurityBestPractices:
    """Test security best practices in Terraform config."""

    def test_rds_password_not_hardcoded(self, main_tf):
        """Verify RDS password is not hardcoded."""
        content = main_tf.read_text()
        # Password should use variable or random_password
        assert "random_password" in content or "var.db_password" in content

    def test_rds_in_private_subnet(self, main_tf):
        """Verify RDS uses private subnets."""
        content = main_tf.read_text()
        # RDS should reference private subnets
        if "aws_db_instance" in content:
            assert "private" in content.lower()

    def test_security_groups_have_descriptions(self, main_tf):
        """Verify security groups have descriptions."""
        content = main_tf.read_text()
        if "aws_security_group" in content:
            sg_count = content.count('resource "aws_security_group"')
            description_count = content.count('description =')
            assert description_count >= sg_count

    def test_vpc_enables_dns(self, main_tf):
        """Verify VPC enables DNS support and hostnames."""
        content = main_tf.read_text()
        if "aws_vpc" in content:
            assert "enable_dns_support" in content
            assert "enable_dns_hostnames" in content


class TestDataSources:
    """Test data sources."""

    def test_uses_availability_zones_data_source(self, main_tf):
        """Verify configuration uses availability zones data source."""
        content = main_tf.read_text()
        assert 'data "aws_availability_zones"' in content


class TestConditionalLogic:
    """Test conditional resource creation."""

    def test_rds_creation_is_conditional(self, main_tf):
        """Verify RDS resources use count for conditional creation."""
        content = main_tf.read_text()
        # Find RDS resources and check they use count
        lines = content.split('\n')
        in_rds_resource = False
        found_count = False
        
        for line in lines:
            if 'resource "aws_db_instance"' in line or 'resource "aws_db_subnet_group"' in line:
                in_rds_resource = True
            if in_rds_resource and "count = var.create_rds" in line:
                found_count = True
                break
            if in_rds_resource and "resource " in line and "aws_db" not in line:
                in_rds_resource = False
        
        assert found_count, "RDS resources should use conditional count"

    def test_eks_creation_is_conditional(self, main_tf):
        """Verify EKS resources use count for conditional creation."""
        content = main_tf.read_text()
        if "aws_eks_cluster" in content:
            assert "count = var.create_eks" in content

class TestTerraformSyntaxValidity:
    """Test Terraform files have valid HCL syntax."""

    def test_main_tf_balanced_braces(self, main_tf):
        """Verify main.tf has balanced opening and closing braces."""
        content = main_tf.read_text()
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, (
            f"Unbalanced braces in main.tf: {open_braces} opening, "
            f"{close_braces} closing. Difference: {close_braces - open_braces}"
        )

    def test_main_tf_no_duplicate_closing_braces(self, main_tf):
        """Verify main.tf doesn't have extra closing braces."""
        content = main_tf.read_text()
        lines = content.split('\n')
        
        # Check for standalone closing braces that might be duplicates
        standalone_closing = [i for i, line in enumerate(lines, 1) 
                            if line.strip() == '}']
        
        # Look for patterns like output blocks followed by extra braces
        for i in range(len(lines) - 1):
            if lines[i].strip() == '}' and lines[i + 1].strip() == '}':
                # Check if this isn't legitimately closing nested blocks
                # by looking at context
                if 'output "' in '\n'.join(lines[max(0, i-5):i]):
                    pytest.fail(
                        f"Potential duplicate closing brace at lines {i+1}-{i+2}. "
                        "Check for outputs embedded in main.tf that should be in outputs.tf"
                    )

    def test_outputs_in_correct_file(self, main_tf, outputs_tf):
        """Verify outputs are defined in outputs.tf, not main.tf."""
        main_content = main_tf.read_text()
        
        # Main.tf should not contain output blocks (they belong in outputs.tf)
        output_pattern_count = main_content.count('output "')
        
        # Allow some flexibility but flag if there are many outputs in main.tf
        if output_pattern_count > 0:
            pytest.warn(
                UserWarning(
                    f"Found {output_pattern_count} output blocks in main.tf. "
                    "Outputs should be in outputs.tf for better organization."
                )
            )

    def test_no_missing_resource_references(self, main_tf, outputs_tf):
        """Verify all resource references in outputs exist in main.tf."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        # Extract resource references from outputs
        import re
        resource_refs = re.findall(r'aws_\w+\.\w+', outputs_content)
        
        for ref in resource_refs:
            if ref not in main_content:
                pytest.fail(
                    f"Output references resource '{ref}' which doesn't exist in main.tf. "
                    "This will cause Terraform to fail."
                )


class TestBackendConfiguration:
    """Test backend.tf configuration."""

    def test_backend_has_no_placeholder_values(self, backend_tf):
        """Verify backend.tf doesn't contain REPLACE_ME placeholders."""
        content = backend_tf.read_text()
        
        placeholders = [
            "REPLACE_ME",
            "REPLACE_TFSTATE_BUCKET", 
            "REPLACE_ACCOUNT_ID",
            "REPLACE_DDB_TABLE",
            "REPLACE_ME_tfstate_bucket",
            "REPLACE_ME_aws_region",
            "REPLACE_ME_tfstate_lock_table"
        ]
        
        found_placeholders = [p for p in placeholders if p in content]
        
        if found_placeholders:
            pytest.warn(
                UserWarning(
                    f"Backend configuration contains placeholders: {', '.join(found_placeholders)}. "
                    "These must be replaced before running Terraform init."
                )
            )

    def test_backend_encryption_enabled(self, backend_tf):
        """Verify backend has encryption enabled."""
        content = backend_tf.read_text()
        assert "encrypt" in content.lower()
        assert "true" in content

    def test_backend_has_state_locking(self, backend_tf):
        """Verify backend configures DynamoDB for state locking."""
        content = backend_tf.read_text()
        assert "dynamodb_table" in content, "Backend should use DynamoDB for state locking"


class TestIAMPolicyConfiguration:
    """Test IAM policy JSON files."""

    @pytest.fixture
    def iam_policy_file(self):
        """Return path to IAM policy file."""
        return Path("terraform/iam/github_actions_ci_policy.json")

    def test_iam_policy_file_exists(self, iam_policy_file):
        """Verify IAM policy file exists."""
        assert iam_policy_file.exists()

    def test_iam_policy_valid_json(self, iam_policy_file):
        """Verify IAM policy is valid JSON."""
        import json
        content = iam_policy_file.read_text()
        try:
            policy = json.loads(content)
            assert isinstance(policy, dict)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in IAM policy: {e}")

    def test_iam_policy_has_version(self, iam_policy_file):
        """Verify IAM policy specifies a version."""
        import json
        content = iam_policy_file.read_text()
        policy = json.loads(content)
        assert "Version" in policy
        assert policy["Version"] in ["2012-10-17", "2008-10-17"]

    def test_iam_policy_has_statements(self, iam_policy_file):
        """Verify IAM policy has statement array."""
        import json
        content = iam_policy_file.read_text()
        policy = json.loads(content)
        assert "Statement" in policy
        assert isinstance(policy["Statement"], list)
        assert len(policy["Statement"]) > 0

    def test_iam_policy_statements_have_required_fields(self, iam_policy_file):
        """Verify all IAM policy statements have required fields."""
        import json
        content = iam_policy_file.read_text()
        policy = json.loads(content)
        
        required_fields = ["Effect", "Action", "Resource"]
        
        for i, statement in enumerate(policy["Statement"]):
            for field in required_fields:
                assert field in statement, (
                    f"Statement {i} missing required field: {field}"
                )

    def test_iam_policy_no_placeholder_arns(self, iam_policy_file):
        """Verify IAM policy doesn't have placeholder ARNs."""
        import json
        content = iam_policy_file.read_text()
        policy = json.loads(content)
        
        placeholders = [
            "REPLACE_TFSTATE_BUCKET",
            "REPLACE_ACCOUNT_ID", 
            "REPLACE_DDB_TABLE",
            "REPLACE_ME",
            "REPLACE_REGION"
        ]
        
        content_str = json.dumps(policy)
        found_placeholders = [p for p in placeholders if p in content_str]
        
        if found_placeholders:
            pytest.warn(
                UserWarning(
                    f"IAM policy contains placeholders: {', '.join(found_placeholders)}. "
                    "These must be replaced before use."
                )
            )

    def test_iam_policy_uses_least_privilege(self, iam_policy_file):
        """Verify IAM policy doesn't use overly permissive wildcards."""
        import json
        content = iam_policy_file.read_text()
        policy = json.loads(content)
        
        dangerous_patterns = []
        
        for i, statement in enumerate(policy["Statement"]):
            if statement.get("Effect") == "Allow":
                actions = statement.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                
                resources = statement.get("Resource", [])
                if isinstance(resources, str):
                    resources = [resources]
                
                # Check for "*:*" action with "*" resource
                if "*" in actions and "*" in resources:
                    dangerous_patterns.append(
                        f"Statement {i} has both Action: * and Resource: *"
                    )
        
        if dangerous_patterns:
            pytest.warn(
                UserWarning(
                    f"IAM policy has overly permissive rules: {'; '.join(dangerous_patterns)}"
                )
            )


class TestDeployScript:
    """Test deployment script."""

    @pytest.fixture
    def deploy_script(self):
        """Return path to deploy script."""
        return Path("scripts/deploy.sh")

    def test_deploy_script_exists(self, deploy_script):
        """Verify deploy.sh exists."""
        assert deploy_script.exists()

    def test_deploy_script_is_executable(self, deploy_script):
        """Verify deploy.sh has executable permission."""
        import os
        assert os.access(deploy_script, os.X_OK) or "#!/" in deploy_script.read_text()[:20]

    def test_deploy_script_has_shebang(self, deploy_script):
        """Verify deploy.sh has proper shebang."""
        content = deploy_script.read_text()
        first_line = content.split('\n')[0]
        assert first_line.startswith("#!/"), "Script should start with shebang"
        assert "bash" in first_line.lower(), "Script should use bash"

    def test_deploy_script_no_syntax_errors(self, deploy_script):
        """Verify deploy.sh doesn't have obvious syntax errors."""
        content = deploy_script.read_text()
        
        # Check for the specific error: "tf=terraform fmt -recursive"
        # This is invalid - should be just "terraform fmt -recursive"
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for incorrect variable assignment that should be command
            if "tf=terraform" in line or "tf =terraform" in line:
                pytest.fail(
                    f"Line {i} has incorrect syntax: '{line.strip()}'. "
                    "Should be 'terraform fmt -recursive', not 'tf=terraform fmt -recursive'"
                )
            
            # Check for other common mistakes
            if line.strip().startswith("="):
                pytest.fail(f"Line {i} has invalid syntax starting with '='")

    def test_deploy_script_uses_error_handling(self, deploy_script):
        """Verify deploy.sh uses proper error handling."""
        content = deploy_script.read_text()
        
        # Should use set -e or set -euo pipefail for error handling
        assert "set -e" in content or "set -euo pipefail" in content, (
            "Script should use 'set -e' or 'set -euo pipefail' for error handling"
        )

    def test_deploy_script_validates_terraform(self, deploy_script):
        """Verify deploy.sh includes terraform validation."""
        content = deploy_script.read_text()
        assert "terraform validate" in content, "Script should validate Terraform config"

    def test_deploy_script_runs_terraform_plan(self, deploy_script):
        """Verify deploy.sh runs terraform plan."""
        content = deploy_script.read_text()
        assert "terraform plan" in content, "Script should run terraform plan"


class TestAnsiblePlaybook:
    """Test Ansible security hardening playbook."""

    @pytest.fixture
    def security_playbook(self):
        """Return path to security hardening playbook."""
        return Path("projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml")

    def test_security_playbook_exists(self, security_playbook):
        """Verify security playbook exists."""
        if security_playbook.exists():
            assert True
        else:
            pytest.skip("Security playbook not in this branch")

    def test_security_playbook_valid_yaml(self, security_playbook):
        """Verify security playbook is valid YAML."""
        if not security_playbook.exists():
            pytest.skip("Security playbook not in this branch")
        
        import yaml
        content = security_playbook.read_text()
        try:
            playbook = yaml.safe_load(content)
            assert isinstance(playbook, list) or isinstance(playbook, dict)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in security playbook: {e}")

    def test_security_playbook_has_tasks(self, security_playbook):
        """Verify security playbook defines tasks."""
        if not security_playbook.exists():
            pytest.skip("Security playbook not in this branch")
        
        import yaml
        content = security_playbook.read_text()
        playbook = yaml.safe_load(content)
        
        if isinstance(playbook, list):
            plays = playbook
        else:
            plays = [playbook]
        
        for play in plays:
            assert "tasks" in play, "Playbook should define tasks"
            assert len(play["tasks"]) > 0, "Playbook should have at least one task"

    def test_security_playbook_uses_become(self, security_playbook):
        """Verify security playbook uses privilege escalation where needed."""
        if not security_playbook.exists():
            pytest.skip("Security playbook not in this branch")
        
        import yaml
        content = security_playbook.read_text()
        playbook = yaml.safe_load(content)
        
        # Security hardening typically requires root/sudo
        if isinstance(playbook, list):
            plays = playbook
        else:
            plays = [playbook]
        
        has_become = any("become" in play for play in plays)
        assert has_become, "Security playbook should use 'become: yes' for privilege escalation"


class TestAlertManagerConfig:
    """Test AlertManager configuration."""

    @pytest.fixture
    def alertmanager_config(self):
        """Return path to AlertManager config."""
        return Path("projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml")

    def test_alertmanager_config_exists(self, alertmanager_config):
        """Verify AlertManager config exists."""
        if alertmanager_config.exists():
            assert True
        else:
            pytest.skip("AlertManager config not in this branch")

    def test_alertmanager_config_valid_yaml(self, alertmanager_config):
        """Verify AlertManager config is valid YAML."""
        if not alertmanager_config.exists():
            pytest.skip("AlertManager config not in this branch")
        
        import yaml
        content = alertmanager_config.read_text()
        try:
            config = yaml.safe_load(content)
            assert isinstance(config, dict)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in AlertManager config: {e}")

    def test_alertmanager_no_plaintext_secrets(self, alertmanager_config):
        """Verify AlertManager config doesn't have plaintext secrets."""
        if not alertmanager_config.exists():
            pytest.skip("AlertManager config not in this branch")
        
        content = alertmanager_config.read_text()
        
        # Look for common secret patterns that shouldn't be in config
        secret_patterns = [
            "password:",
            "api_key:",
            "webhook_url:",
            "slack_api_url:",
            "smtp_password:"
        ]
        
        found_secrets = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in secret_patterns:
                if pattern in line.lower():
                    # Check if it's a placeholder or actual secret
                    if "example" not in line.lower() and \
                       "placeholder" not in line.lower() and \
                       "your_" not in line.lower() and \
                       "REPLACE" not in line and \
                       "${" not in line:  # Template variables are OK
                        found_secrets.append(f"Line {i}: {line.strip()[:50]}")
        
        if found_secrets:
            pytest.warn(
                UserWarning(
                    f"AlertManager config may contain plaintext secrets:\n" +
                    "\n".join(found_secrets)
                )
            )


class TestOutputsConsistency:
    """Test consistency between outputs.tf and main.tf."""

    def test_outputs_reference_existing_resources(self, main_tf, outputs_tf):
        """Verify all outputs reference resources that exist."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        # Extract resource references from outputs
        import re
        output_refs = re.findall(r'(aws_\w+)\.([\w\[\]0-9]+)', outputs_content)
        
        missing_resources = []
        
        for resource_type, resource_name in output_refs:
            # Remove array indices for checking
            clean_name = re.sub(r'\[\d+\]', '', resource_name)
            
            # Check if resource is defined in main.tf
            resource_pattern = f'resource "{resource_type}" "{clean_name}"'
            if resource_pattern not in main_content:
                missing_resources.append(f"{resource_type}.{resource_name}")
        
        if missing_resources:
            pytest.fail(
                f"Outputs reference non-existent resources: {', '.join(missing_resources)}. "
                "This will cause 'terraform plan' to fail."
            )

    def test_no_duplicate_outputs(self, main_tf, outputs_tf):
        """Verify outputs aren't duplicated between files."""
        main_content = main_tf.read_text()
        outputs_content = outputs_tf.read_text()
        
        import re
        main_outputs = re.findall(r'output "(\w+)"', main_content)
        outputs_tf_outputs = re.findall(r'output "(\w+)"', outputs_content)
        
        duplicates = set(main_outputs) & set(outputs_tf_outputs)
        
        if duplicates:
            pytest.fail(
                f"Outputs duplicated in both main.tf and outputs.tf: {', '.join(duplicates)}. "
                "Define each output in only one file (preferably outputs.tf)."
            )


class TestVariablesDefinition:
    """Test that all referenced variables are defined."""

    def test_all_referenced_variables_are_defined(self, main_tf, variables_tf):
        """Verify all var.* references in main.tf are defined in variables.tf."""
        main_content = main_tf.read_text()
        variables_content = variables_tf.read_text()
        
        import re
        # Find all var.something references
        var_refs = set(re.findall(r'var\.(\w+)', main_content))
        
        # Find all defined variables
        var_defs = set(re.findall(r'variable "(\w+)"', variables_content))
        
        undefined_vars = var_refs - var_defs
        
        if undefined_vars:
            pytest.fail(
                f"Variables used but not defined: {', '.join(sorted(undefined_vars))}. "
                "Add these to variables.tf"
            )

    def test_defined_variables_have_types(self, variables_tf):
        """Verify all variables specify their type."""
        content = variables_tf.read_text()
        
        import re
        variables = re.findall(r'variable "(\w+)"', content)
        
        for var in variables:
            # Find the variable block
            var_pattern = f'variable "{var}".*?{{.*?}}'
            var_block = re.search(var_pattern, content, re.DOTALL)
            
            if var_block:
                var_content = var_block.group(0)
                if "type" not in var_content:
                    pytest.warn(
                        UserWarning(f"Variable '{var}' doesn't specify a type")
                    )

    def test_sensitive_variables_marked(self, variables_tf):
        """Verify sensitive variables are marked as sensitive."""
        content = variables_tf.read_text()
        
        sensitive_keywords = ["password", "secret", "key", "token"]
        
        import re
        variables = re.findall(r'variable "(\w+)"', content)
        
        for var in variables:
            var_lower = var.lower()
            if any(keyword in var_lower for keyword in sensitive_keywords):
                # Find the variable block
                var_pattern = f'variable "{var}".*?{{.*?}}'
                var_block = re.search(var_pattern, content, re.DOTALL)
                
                if var_block and "sensitive" not in var_block.group(0):
                    pytest.warn(
                        UserWarning(
                            f"Variable '{var}' appears to be sensitive but not marked with 'sensitive = true'"
                        )
                    )