"""
tests/test_configs.py
pytest suite validating DSC PowerShell files and Ansible YAML files
for the Active Directory Automation project.

Run:
    pip install pytest pyyaml
    pytest tests/test_configs.py -v
"""

import os
import re
import yaml
import pytest
from pathlib import Path

# Project root relative to this test file
PROJECT_ROOT = Path(__file__).parent.parent
DSC_DIR      = PROJECT_ROOT / "dsc"
PLAYBOOK_DIR = PROJECT_ROOT / "ansible" / "playbooks"
ROLE_DIR     = PROJECT_ROOT / "ansible" / "roles"
INVENTORY_DIR= PROJECT_ROOT / "ansible" / "inventory"


# ===========================================================================
# Helpers
# ===========================================================================

def read_file(path: Path) -> str:
    assert path.exists(), f"Expected file not found: {path}"
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> object:
    content = read_file(path)
    return yaml.safe_load(content)


# ===========================================================================
# DSC FILE TESTS
# ===========================================================================

class TestDomainSetupDSC:
    """Validate dsc/DomainSetup.ps1 structure and content."""

    DSC_FILE = DSC_DIR / "DomainSetup.ps1"

    def test_file_exists(self):
        assert self.DSC_FILE.exists(), "DomainSetup.ps1 must exist"

    def test_contains_configuration_keyword(self):
        content = read_file(self.DSC_FILE)
        assert re.search(r"\bConfiguration\b", content), \
            "Must contain 'Configuration' keyword"

    def test_contains_domain_controller_block(self):
        content = read_file(self.DSC_FILE)
        assert "DomainController" in content

    def test_imports_adds_dsc_resource(self):
        content = read_file(self.DSC_FILE)
        assert "ActiveDirectoryDsc" in content

    def test_imports_networking_dsc_resource(self):
        content = read_file(self.DSC_FILE)
        assert "NetworkingDsc" in content

    def test_windows_feature_adds(self):
        content = read_file(self.DSC_FILE)
        assert "AD-Domain-Services" in content

    def test_windows_feature_dns(self):
        content = read_file(self.DSC_FILE)
        assert '"DNS"' in content or "'DNS'" in content

    def test_adds_domain_resource(self):
        content = read_file(self.DSC_FILE)
        assert "ADDomain" in content

    def test_wait_for_domain_resource(self):
        content = read_file(self.DSC_FILE)
        assert "WaitForADDomain" in content

    def test_ou_structure_present(self):
        content = read_file(self.DSC_FILE)
        for ou in ["IT", "HR", "Finance", "Operations", "ServiceAccounts", "Servers", "Workstations"]:
            assert ou in content, f"Expected OU '{ou}' not found in DomainSetup.ps1"

    def test_password_policy_resource(self):
        content = read_file(self.DSC_FILE)
        assert "ADDefaultDomainPasswordPolicy" in content

    def test_ad_recycle_bin(self):
        content = read_file(self.DSC_FILE)
        assert "ADOptionalFeature" in content or "Recycle Bin" in content

    def test_config_data_block(self):
        content = read_file(self.DSC_FILE)
        assert "ConfigData" in content or "AllNodes" in content

    def test_minimum_line_count(self):
        content = read_file(self.DSC_FILE)
        line_count = len(content.splitlines())
        assert line_count >= 200, f"Expected 200+ lines, got {line_count}"


class TestUsersAndGroupsDSC:
    """Validate dsc/UsersAndGroups.ps1."""

    DSC_FILE = DSC_DIR / "UsersAndGroups.ps1"

    def test_file_exists(self):
        assert self.DSC_FILE.exists()

    def test_configuration_block(self):
        content = read_file(self.DSC_FILE)
        assert "Configuration" in content

    def test_imports_ad_dsc(self):
        content = read_file(self.DSC_FILE)
        assert "ActiveDirectoryDsc" in content

    def test_user_accounts_present(self):
        content = read_file(self.DSC_FILE)
        expected_users = ["jsmith", "mmartinez", "adavis", "kjohnson", "mwhite", "phall"]
        for user in expected_users:
            assert user in content, f"User '{user}' not found in UsersAndGroups.ps1"

    def test_twenty_or_more_users(self):
        content = read_file(self.DSC_FILE)
        # Count ADUser resource blocks
        user_blocks = re.findall(r"\bADUser\b\s+\w+", content)
        assert len(user_blocks) >= 20, f"Expected 20+ users, found {len(user_blocks)}"

    def test_security_groups_defined(self):
        content = read_file(self.DSC_FILE)
        for group in ["IT-Admins", "HR-Users", "Finance-Users", "DevOps-Team", "Help-Desk"]:
            assert group in content, f"Group '{group}' not found"

    def test_group_membership_assignments(self):
        content = read_file(self.DSC_FILE)
        assert "ADGroupMember" in content

    def test_service_accounts_present(self):
        content = read_file(self.DSC_FILE)
        for svc in ["svc-backup", "svc-monitoring", "svc-deploy"]:
            assert svc in content, f"Service account '{svc}' not found"

    def test_user_principal_names(self):
        content = read_file(self.DSC_FILE)
        assert "corp.contoso.local" in content

    def test_depends_on_chaining(self):
        content = read_file(self.DSC_FILE)
        assert "DependsOn" in content


class TestGPOPoliciesDSC:
    """Validate dsc/GPOPolicies.ps1."""

    DSC_FILE = DSC_DIR / "GPOPolicies.ps1"

    def test_file_exists(self):
        assert self.DSC_FILE.exists()

    def test_configuration_block(self):
        content = read_file(self.DSC_FILE)
        assert "Configuration" in content

    def test_password_policy(self):
        content = read_file(self.DSC_FILE)
        assert "ADDefaultDomainPasswordPolicy" in content

    def test_fine_grained_password_policy(self):
        content = read_file(self.DSC_FILE)
        assert "ADFineGrainedPasswordPolicy" in content

    def test_gpo_resource(self):
        content = read_file(self.DSC_FILE)
        assert "GPO " in content or "GPOLink" in content

    def test_audit_policy_settings(self):
        content = read_file(self.DSC_FILE)
        assert "Audit" in content

    def test_screensaver_settings(self):
        content = read_file(self.DSC_FILE)
        assert "ScreenSave" in content

    def test_smb_hardening(self):
        content = read_file(self.DSC_FILE)
        assert "SMB" in content

    def test_ntlm_hardening(self):
        content = read_file(self.DSC_FILE)
        assert "LmCompatibilityLevel" in content or "NTLMv" in content or "Lsa" in content

    def test_it_admins_pso(self):
        content = read_file(self.DSC_FILE)
        assert "IT-Admins" in content


# ===========================================================================
# ANSIBLE YAML TESTS
# ===========================================================================

class TestADJoinPlaybook:
    """Validate ansible/playbooks/ad-join.yml."""

    PLAYBOOK = PLAYBOOK_DIR / "ad-join.yml"

    def test_file_exists(self):
        assert self.PLAYBOOK.exists()

    def test_valid_yaml(self):
        data = load_yaml(self.PLAYBOOK)
        assert data is not None

    def test_is_list(self):
        data = load_yaml(self.PLAYBOOK)
        assert isinstance(data, list), "Playbook must be a YAML list of plays"

    def test_has_hosts_field(self):
        data = load_yaml(self.PLAYBOOK)
        assert "hosts" in data[0]

    def test_targets_linux_servers(self):
        data = load_yaml(self.PLAYBOOK)
        assert data[0]["hosts"] == "linux_servers"

    def test_has_vars_block(self):
        data = load_yaml(self.PLAYBOOK)
        assert "vars" in data[0]

    def test_ad_domain_var(self):
        data = load_yaml(self.PLAYBOOK)
        assert "ad_domain" in data[0]["vars"]
        assert data[0]["vars"]["ad_domain"] == "corp.contoso.local"

    def test_has_tasks(self):
        data = load_yaml(self.PLAYBOOK)
        tasks = data[0].get("tasks") or data[0].get("pre_tasks") or []
        assert len(tasks) > 0

    def test_realmd_in_packages(self):
        content = read_file(self.PLAYBOOK)
        assert "realmd" in content

    def test_sssd_in_packages(self):
        content = read_file(self.PLAYBOOK)
        assert "sssd" in content

    def test_realm_join_task(self):
        content = read_file(self.PLAYBOOK)
        assert "realm join" in content or "realm_join" in content

    def test_sudoers_configuration(self):
        content = read_file(self.PLAYBOOK)
        assert "sudoers" in content or "sudo" in content.lower()

    def test_become_true(self):
        data = load_yaml(self.PLAYBOOK)
        assert data[0].get("become") is True


class TestADHardeningPlaybook:
    """Validate ansible/playbooks/ad-hardening.yml."""

    PLAYBOOK = PLAYBOOK_DIR / "ad-hardening.yml"

    def test_file_exists(self):
        assert self.PLAYBOOK.exists()

    def test_valid_yaml(self):
        data = load_yaml(self.PLAYBOOK)
        assert data is not None

    def test_targets_domain_controllers(self):
        data = load_yaml(self.PLAYBOOK)
        assert data[0]["hosts"] == "domain_controllers"

    def test_smb_hardening_task(self):
        content = read_file(self.PLAYBOOK)
        assert "SMB" in content or "smb" in content.lower()

    def test_ntlm_hardening_task(self):
        content = read_file(self.PLAYBOOK)
        assert "LmCompatibilityLevel" in content or "NTLMv1" in content

    def test_ldap_signing_task(self):
        content = read_file(self.PLAYBOOK)
        assert "LDAPServerIntegrity" in content or "LDAP" in content

    def test_audit_policy_task(self):
        content = read_file(self.PLAYBOOK)
        assert "auditpol" in content or "Audit" in content

    def test_fine_grained_password_policy(self):
        content = read_file(self.PLAYBOOK)
        assert "ADFineGrainedPasswordPolicy" in content or "FineGrained" in content

    def test_recycle_bin_task(self):
        content = read_file(self.PLAYBOOK)
        assert "Recycle Bin" in content

    def test_protected_users_task(self):
        content = read_file(self.PLAYBOOK)
        assert "Protected Users" in content

    def test_has_handlers(self):
        content = read_file(self.PLAYBOOK)
        assert "handlers" in content


class TestInventoryFile:
    """Validate ansible/inventory/lab.ini."""

    INVENTORY = INVENTORY_DIR / "lab.ini"

    def test_file_exists(self):
        assert self.INVENTORY.exists()

    def test_domain_controllers_group(self):
        content = read_file(self.INVENTORY)
        assert "[domain_controllers]" in content

    def test_linux_servers_group(self):
        content = read_file(self.INVENTORY)
        assert "[linux_servers]" in content

    def test_windows_workstations_group(self):
        content = read_file(self.INVENTORY)
        assert "[windows_workstations]" in content

    def test_dc01_present(self):
        content = read_file(self.INVENTORY)
        assert "dc01.corp.contoso.local" in content

    def test_dc02_present(self):
        content = read_file(self.INVENTORY)
        assert "dc02.corp.contoso.local" in content

    def test_dc01_ip_address(self):
        content = read_file(self.INVENTORY)
        assert "192.168.10.10" in content

    def test_linux_server_present(self):
        content = read_file(self.INVENTORY)
        assert "app01.corp.contoso.local" in content

    def test_workstation_present(self):
        content = read_file(self.INVENTORY)
        assert "ws001.corp.contoso.local" in content

    def test_winrm_connection_vars(self):
        content = read_file(self.INVENTORY)
        assert "winrm" in content

    def test_ad_domain_var(self):
        content = read_file(self.INVENTORY)
        assert "ad_domain=corp.contoso.local" in content


class TestRoleTasksFile:
    """Validate ansible/roles/ad-domain/tasks/main.yml."""

    TASKS = ROLE_DIR / "ad-domain" / "tasks" / "main.yml"

    def test_file_exists(self):
        assert self.TASKS.exists()

    def test_valid_yaml(self):
        data = load_yaml(self.TASKS)
        assert data is not None

    def test_is_list(self):
        data = load_yaml(self.TASKS)
        assert isinstance(data, list)

    def test_feature_install_task(self):
        content = read_file(self.TASKS)
        assert "AD-Domain-Services" in content or "win_feature" in content

    def test_domain_promotion_task(self):
        content = read_file(self.TASKS)
        assert "Install-ADDSForest" in content or "domain_promotion" in content

    def test_ou_creation_task(self):
        content = read_file(self.TASKS)
        assert "New-ADOrganizationalUnit" in content or "OU structure" in content

    def test_dcdiag_task(self):
        content = read_file(self.TASKS)
        assert "dcdiag" in content

    def test_dns_forwarder_task(self):
        content = read_file(self.TASKS)
        assert "forwarder" in content.lower() or "Set-DnsServerForwarder" in content

    def test_recycle_bin_task(self):
        content = read_file(self.TASKS)
        assert "Recycle Bin" in content


# ===========================================================================
# DEMO OUTPUT TESTS
# ===========================================================================

class TestDemoOutput:
    """Validate the generated AD report exists and has expected content."""

    REPORT = PROJECT_ROOT / "demo_output" / "ad_report.txt"

    def test_report_file_exists(self):
        assert self.REPORT.exists()

    def test_report_has_domain_header(self):
        content = read_file(self.REPORT)
        assert "corp.contoso.local" in content

    def test_report_has_ou_structure(self):
        content = read_file(self.REPORT)
        assert "OU Structure" in content

    def test_report_has_user_table(self):
        content = read_file(self.REPORT)
        assert "jsmith" in content

    def test_report_has_group_section(self):
        content = read_file(self.REPORT)
        assert "IT-Admins" in content

    def test_report_has_gpo_section(self):
        content = read_file(self.REPORT)
        assert "Group Policy" in content or "GPO" in content

    def test_report_minimum_lines(self):
        content = read_file(self.REPORT)
        line_count = len(content.splitlines())
        assert line_count >= 200, f"Expected 200+ lines, got {line_count}"

    def test_report_has_security_summary(self):
        content = read_file(self.REPORT)
        assert "PASS" in content or "WARN" in content

    def test_report_has_replication_section(self):
        content = read_file(self.REPORT)
        assert "Replication" in content


# ===========================================================================
# DOCS TESTS
# ===========================================================================

class TestDomainDesignDoc:
    """Validate docs/domain-design.md."""

    DOC = PROJECT_ROOT / "docs" / "domain-design.md"

    def test_file_exists(self):
        assert self.DOC.exists()

    def test_minimum_line_count(self):
        content = read_file(self.DOC)
        assert len(content.splitlines()) >= 200

    def test_has_ou_structure_section(self):
        content = read_file(self.DOC)
        assert "OU Structure" in content

    def test_has_naming_conventions(self):
        content = read_file(self.DOC)
        assert "Naming" in content

    def test_has_tier_model(self):
        content = read_file(self.DOC)
        assert "Tier" in content

    def test_has_gpo_section(self):
        content = read_file(self.DOC)
        assert "Group Policy" in content

    def test_has_delegation_section(self):
        content = read_file(self.DOC)
        assert "Delegation" in content
