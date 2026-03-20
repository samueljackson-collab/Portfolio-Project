"""
Tests for AWS Landing Zone project.
Validates Terraform files exist, SCP policies are valid JSON,
and all required outputs and structure are present.

Run with: pytest tests/test_landing_zone.py -v
"""

import json
import os
import re
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def project_path(*parts: str) -> str:
    """Return absolute path relative to the project root."""
    return os.path.join(PROJECT_ROOT, *parts)


def read_file(path: str) -> str:
    with open(path, "r") as fh:
        return fh.read()


def load_json(path: str) -> dict:
    with open(path, "r") as fh:
        return json.load(fh)


def collect_scp_files() -> list[tuple[str, str]]:
    """Return list of (filename, full_path) for all JSON files in scp/policies/."""
    policies_dir = project_path("terraform", "scp", "policies")
    files = [
        (f, os.path.join(policies_dir, f))
        for f in sorted(os.listdir(policies_dir))
        if f.endswith(".json")
    ]
    return files


# ---------------------------------------------------------------------------
# Test: Required files and directories exist
# ---------------------------------------------------------------------------

class TestRequiredFilesExist:
    REQUIRED_FILES = [
        "terraform/organizations/main.tf",
        "terraform/organizations/variables.tf",
        "terraform/organizations/outputs.tf",
        "terraform/sso/main.tf",
        "terraform/sso/variables.tf",
        "terraform/scp/main.tf",
        "terraform/scp/variables.tf",
        "terraform/scp/policies/deny-root-actions.json",
        "terraform/scp/policies/require-mfa.json",
        "terraform/scp/policies/restrict-regions.json",
        "terraform/scp/policies/deny-internet-gateways.json",
        "docs/account-topology.md",
        "scripts/validate_scps.py",
        "demo_output/scp_validation.txt",
        "demo_output/org_structure.txt",
    ]

    @pytest.mark.parametrize("relative_path", REQUIRED_FILES)
    def test_file_exists(self, relative_path):
        full_path = project_path(relative_path)
        assert os.path.isfile(full_path), f"Required file missing: {full_path}"

    def test_scp_policies_directory_exists(self):
        policies_dir = project_path("terraform", "scp", "policies")
        assert os.path.isdir(policies_dir), f"Policies directory missing: {policies_dir}"

    def test_four_scp_policy_files_exist(self):
        files = collect_scp_files()
        assert len(files) == 4, (
            f"Expected 4 SCP JSON files, found {len(files)}: {[f for f, _ in files]}"
        )

    def test_docs_directory_exists(self):
        docs_dir = project_path("docs")
        assert os.path.isdir(docs_dir)

    def test_demo_output_directory_exists(self):
        demo_dir = project_path("demo_output")
        assert os.path.isdir(demo_dir)


# ---------------------------------------------------------------------------
# Test: SCP policies are valid JSON
# ---------------------------------------------------------------------------

class TestSCPPoliciesValidJSON:
    """Each SCP JSON file must parse without errors."""

    @pytest.mark.parametrize("filename,filepath", collect_scp_files())
    def test_policy_is_valid_json(self, filename, filepath):
        try:
            data = load_json(filepath)
        except json.JSONDecodeError as exc:
            pytest.fail(f"{filename} is not valid JSON: {exc}")
        assert isinstance(data, dict), f"{filename}: top-level value must be a JSON object"

    @pytest.mark.parametrize("filename,filepath", collect_scp_files())
    def test_policy_has_version_field(self, filename, filepath):
        data = load_json(filepath)
        assert "Version" in data, f"{filename}: missing 'Version' field"
        assert data["Version"] == "2012-10-17", (
            f"{filename}: Version should be '2012-10-17', got {data['Version']!r}"
        )

    @pytest.mark.parametrize("filename,filepath", collect_scp_files())
    def test_policy_has_statement_array(self, filename, filepath):
        data = load_json(filepath)
        assert "Statement" in data, f"{filename}: missing 'Statement' field"
        assert isinstance(data["Statement"], list), (
            f"{filename}: 'Statement' must be an array"
        )
        assert len(data["Statement"]) >= 1, (
            f"{filename}: 'Statement' array must have at least one entry"
        )

    @pytest.mark.parametrize("filename,filepath", collect_scp_files())
    def test_policy_statements_have_required_fields(self, filename, filepath):
        data = load_json(filepath)
        for idx, stmt in enumerate(data.get("Statement", [])):
            assert isinstance(stmt, dict), f"{filename} Statement[{idx}] must be an object"
            assert "Effect" in stmt, f"{filename} Statement[{idx}]: missing 'Effect'"
            assert stmt["Effect"] in ("Allow", "Deny"), (
                f"{filename} Statement[{idx}]: Effect must be 'Allow' or 'Deny'"
            )
            has_action = "Action" in stmt or "NotAction" in stmt
            assert has_action, (
                f"{filename} Statement[{idx}]: missing 'Action' or 'NotAction'"
            )
            assert "Resource" in stmt, f"{filename} Statement[{idx}]: missing 'Resource'"


# ---------------------------------------------------------------------------
# Test: SCP policy content correctness
# ---------------------------------------------------------------------------

class TestSCPPolicyContent:
    def test_deny_root_actions_denies_root_principal(self):
        path = project_path("terraform", "scp", "policies", "deny-root-actions.json")
        data = load_json(path)
        stmt = data["Statement"][0]
        assert stmt["Effect"] == "Deny"
        conditions = stmt.get("Condition", {})
        all_conditions_str = json.dumps(conditions)
        assert ":root" in all_conditions_str, (
            "deny-root-actions.json should condition on root principal ARN"
        )

    def test_require_mfa_denies_without_mfa(self):
        path = project_path("terraform", "scp", "policies", "require-mfa.json")
        data = load_json(path)
        stmt = data["Statement"][0]
        assert stmt["Effect"] == "Deny"
        conditions = stmt.get("Condition", {})
        cond_str = json.dumps(conditions)
        assert "MultiFactorAuth" in cond_str, (
            "require-mfa.json should check MultiFactorAuthPresent condition"
        )

    def test_restrict_regions_has_allowed_regions(self):
        path = project_path("terraform", "scp", "policies", "restrict-regions.json")
        data = load_json(path)
        policy_str = json.dumps(data)
        assert "us-east-1" in policy_str, "restrict-regions.json must include us-east-1"
        assert "us-west-2" in policy_str, "restrict-regions.json must include us-west-2"
        assert "eu-west-1" in policy_str, "restrict-regions.json must include eu-west-1"
        assert "aws:RequestedRegion" in policy_str, (
            "restrict-regions.json must use aws:RequestedRegion condition key"
        )

    def test_deny_internet_gateways_targets_ec2(self):
        path = project_path(
            "terraform", "scp", "policies", "deny-internet-gateways.json"
        )
        data = load_json(path)
        policy_str = json.dumps(data)
        assert "ec2:" in policy_str, "deny-internet-gateways.json should target ec2 actions"
        assert "InternetGateway" in policy_str or "internet" in policy_str.lower(), (
            "deny-internet-gateways.json should reference internet gateway actions"
        )

    def test_deny_root_actions_has_three_actions(self):
        path = project_path("terraform", "scp", "policies", "deny-root-actions.json")
        data = load_json(path)
        stmt = data["Statement"][0]
        actions = stmt.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        assert len(actions) == 3, (
            f"deny-root-actions.json Statement[0] should have exactly 3 actions, "
            f"found {len(actions)}: {actions}"
        )


# ---------------------------------------------------------------------------
# Test: Terraform files contain required resources and outputs
# ---------------------------------------------------------------------------

class TestOrganizationsTerraform:
    def setup_method(self):
        self.main_tf = read_file(project_path("terraform", "organizations", "main.tf"))
        self.variables_tf = read_file(project_path("terraform", "organizations", "variables.tf"))
        self.outputs_tf = read_file(project_path("terraform", "organizations", "outputs.tf"))

    def test_main_tf_has_organization_resource(self):
        assert "aws_organizations_organization" in self.main_tf

    def test_main_tf_has_security_ou(self):
        assert "aws_organizations_organizational_unit" in self.main_tf
        assert "security" in self.main_tf.lower()

    def test_main_tf_has_infrastructure_ou(self):
        assert "infrastructure" in self.main_tf.lower()

    def test_main_tf_has_workloads_ou(self):
        assert "workloads" in self.main_tf.lower()

    def test_main_tf_has_sandbox_ou(self):
        assert "sandbox" in self.main_tf.lower()

    def test_main_tf_has_four_accounts(self):
        account_count = self.main_tf.count('resource "aws_organizations_account"')
        assert account_count == 4, (
            f"Expected 4 aws_organizations_account resources, found {account_count}"
        )

    def test_main_tf_has_scp_policy_attachments(self):
        assert "aws_organizations_policy_attachment" in self.main_tf

    def test_outputs_tf_has_organization_id(self):
        assert "organization_id" in self.outputs_tf

    def test_outputs_tf_has_root_id(self):
        assert "root_id" in self.outputs_tf

    def test_outputs_tf_has_ou_ids(self):
        assert "security_ou_id" in self.outputs_tf
        assert "infrastructure_ou_id" in self.outputs_tf
        assert "workloads_ou_id" in self.outputs_tf
        assert "sandbox_ou_id" in self.outputs_tf

    def test_outputs_tf_has_all_account_ids(self):
        assert "security_audit_account_id" in self.outputs_tf
        assert "log_archive_account_id" in self.outputs_tf
        assert "shared_services_account_id" in self.outputs_tf
        assert "sandbox_dev_account_id" in self.outputs_tf

    def test_variables_tf_has_email_domain(self):
        assert "email_domain" in self.variables_tf

    def test_variables_tf_has_account_names(self):
        assert "account_names" in self.variables_tf


class TestSSOTerraform:
    def setup_method(self):
        self.main_tf = read_file(project_path("terraform", "sso", "main.tf"))

    def test_has_permission_set_administrator(self):
        assert "AdministratorAccess" in self.main_tf

    def test_has_permission_set_readonly(self):
        assert "ReadOnlyAccess" in self.main_tf

    def test_has_permission_set_devops(self):
        assert "DevOpsAccess" in self.main_tf

    def test_has_permission_set_security_audit(self):
        assert "SecurityAuditAccess" in self.main_tf

    def test_has_account_assignments(self):
        assignment_count = self.main_tf.count("aws_ssoadmin_account_assignment")
        assert assignment_count >= 6, (
            f"Expected at least 6 account assignment resources, found {assignment_count}"
        )

    def test_uses_ssoadmin_resources(self):
        assert "aws_ssoadmin_permission_set" in self.main_tf
        assert "aws_ssoadmin_instances" in self.main_tf


class TestSCPTerraform:
    def setup_method(self):
        self.main_tf = read_file(project_path("terraform", "scp", "main.tf"))

    def test_has_four_policy_resources(self):
        count = self.main_tf.count('resource "aws_organizations_policy"')
        assert count == 4, f"Expected 4 SCP policy resources, found {count}"

    def test_reads_json_files(self):
        assert 'file(' in self.main_tf, "SCP main.tf should use file() to read JSON policies"

    def test_attaches_deny_root_to_root(self):
        assert "deny_root_actions_root" in self.main_tf or "root" in self.main_tf

    def test_attaches_restrict_regions_to_workloads(self):
        assert "workloads" in self.main_tf.lower()

    def test_attaches_deny_igw_to_security(self):
        assert "security" in self.main_tf.lower()


# ---------------------------------------------------------------------------
# Test: documentation content
# ---------------------------------------------------------------------------

class TestDocumentation:
    def setup_method(self):
        self.topology_md = read_file(project_path("docs", "account-topology.md"))

    def test_topology_has_ascii_tree(self):
        assert "├──" in self.topology_md or "└──" in self.topology_md, (
            "account-topology.md should contain an ASCII org tree"
        )

    def test_topology_mentions_all_accounts(self):
        for account in ["security-audit", "log-archive", "shared-services", "sandbox-dev"]:
            assert account in self.topology_md, (
                f"account-topology.md should mention account '{account}'"
            )

    def test_topology_mentions_all_ous(self):
        for ou in ["Security", "Infrastructure", "Workloads", "Sandbox"]:
            assert ou in self.topology_md, (
                f"account-topology.md should mention OU '{ou}'"
            )

    def test_topology_has_access_matrix(self):
        assert "Access Matrix" in self.topology_md or "access matrix" in self.topology_md.lower()

    def test_topology_has_naming_convention(self):
        assert "Naming" in self.topology_md or "naming" in self.topology_md.lower()

    def test_topology_has_network_section(self):
        assert "Network" in self.topology_md or "network" in self.topology_md.lower()

    def test_topology_has_scp_table(self):
        assert "SCP" in self.topology_md or "DenyRootActions" in self.topology_md


# ---------------------------------------------------------------------------
# Test: demo output files are well-formed
# ---------------------------------------------------------------------------

class TestDemoOutput:
    def test_scp_validation_output_has_pass_lines(self):
        content = read_file(project_path("demo_output", "scp_validation.txt"))
        pass_count = content.count("[PASS]")
        assert pass_count >= 13, (
            f"Expected at least 13 [PASS] entries in scp_validation.txt, found {pass_count}"
        )
        assert "[FAIL]" not in content, "scp_validation.txt should have no [FAIL] entries"

    def test_scp_validation_output_has_summary(self):
        content = read_file(project_path("demo_output", "scp_validation.txt"))
        assert "checks passed" in content, "scp_validation.txt should have a summary line"
        assert "All SCPs are valid" in content

    def test_org_structure_output_has_tree(self):
        content = read_file(project_path("demo_output", "org_structure.txt"))
        assert "├──" in content or "└──" in content

    def test_org_structure_has_all_accounts(self):
        content = read_file(project_path("demo_output", "org_structure.txt"))
        for account in ["security-audit", "log-archive", "shared-services", "sandbox-dev"]:
            assert account in content, f"org_structure.txt missing account: {account}"

    def test_org_structure_has_scps_applied_section(self):
        content = read_file(project_path("demo_output", "org_structure.txt"))
        assert "SCPs Applied" in content or "deny-root-actions" in content
