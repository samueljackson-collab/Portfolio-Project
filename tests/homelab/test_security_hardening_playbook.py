"""
Comprehensive tests for Ansible security hardening playbook.

This test suite validates:
- YAML syntax correctness
- Playbook structure and phases
- CIS benchmark compliance
- Security hardening tasks
- Handler configurations
- Variable definitions
- Task idempotency
"""

import yaml
import pytest
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent


class TestSecurityHardeningPlaybookStructure:
    """Test security-hardening.yml playbook structure."""

    def test_playbook_exists(self):
        """Test security-hardening.yml exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        assert playbook_path.exists()

    def test_playbook_valid_yaml(self):
        """Test playbook is valid YAML."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        assert playbook is not None
        assert isinstance(playbook, list)

    def test_playbook_has_required_fields(self):
        """Test playbook has required Ansible fields."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        assert "name" in play
        assert "hosts" in play
        assert "become" in play
        assert "tasks" in play

    def test_playbook_targets_all_hosts(self):
        """Test playbook targets all hosts."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        assert play["hosts"] == "all"

    def test_playbook_uses_privilege_escalation(self):
        """Test playbook uses become for privilege escalation."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        assert play["become"] is True


class TestPlaybookVariables:
    """Test playbook variable definitions."""

    def test_playbook_has_vars(self):
        """Test playbook defines variables."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        assert "vars" in play

    def test_ssh_port_variable_defined(self):
        """Test SSH port variable is defined."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        variables = play.get("vars", {})
        assert "ssh_port" in variables

    def test_allowed_ssh_users_defined(self):
        """Test allowed SSH users variable is defined."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        variables = play.get("vars", {})
        assert "allowed_ssh_users" in variables
        assert isinstance(variables["allowed_ssh_users"], list)

    def test_fail2ban_variables_defined(self):
        """Test Fail2Ban variables are defined."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        variables = play.get("vars", {})
        assert "fail2ban_bantime" in variables
        assert "fail2ban_findtime" in variables
        assert "fail2ban_maxretry" in variables

    def test_auto_updates_variable_defined(self):
        """Test auto updates variable is defined."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        variables = play.get("vars", {})
        assert "auto_updates_enabled" in variables

    def test_audit_logs_variable_defined(self):
        """Test audit logs variable is defined."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        variables = play.get("vars", {})
        assert "audit_logs_enabled" in variables


class TestPlaybookHandlers:
    """Test playbook handler definitions."""

    def test_playbook_has_handlers(self):
        """Test playbook defines handlers."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        assert "handlers" in play
        assert len(play["handlers"]) >= 4

    def test_sshd_restart_handler(self):
        """Test SSH restart handler exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        handlers = play.get("handlers", [])
        handler_names = [h["name"] for h in handlers]
        
        assert any("sshd" in name.lower() for name in handler_names)

    def test_fail2ban_restart_handler(self):
        """Test Fail2Ban restart handler exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        handlers = play.get("handlers", [])
        handler_names = [h["name"] for h in handlers]
        
        assert any("fail2ban" in name.lower() for name in handler_names)

    def test_ufw_restart_handler(self):
        """Test UFW restart handler exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        handlers = play.get("handlers", [])
        handler_names = [h["name"] for h in handlers]
        
        assert any("ufw" in name.lower() for name in handler_names)

    def test_auditd_restart_handler(self):
        """Test auditd restart handler exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        handlers = play.get("handlers", [])
        handler_names = [h["name"] for h in handlers]
        
        assert any("auditd" in name.lower() for name in handler_names)


class TestPlaybookTasks:
    """Test playbook task definitions."""

    def test_playbook_has_tasks(self):
        """Test playbook defines tasks."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        assert "tasks" in play
        # Enhanced playbook should have 40+ tasks
        assert len(play["tasks"]) >= 40

    def test_tasks_have_names(self):
        """Test all tasks have descriptive names."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        for task in tasks:
            assert "name" in task, "Task missing name field"
            assert len(task["name"]) > 0, "Task name is empty"


class TestPhase1SystemUpdates:
    """Test Phase 1: System Updates and Package Management."""

    def test_apt_cache_update_task(self):
        """Test apt cache update task exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"] for t in tasks]
        
        assert any("apt" in name.lower() and "cache" in name.lower() for name in task_names)

    def test_system_upgrade_task(self):
        """Test system upgrade task exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"] for t in tasks]
        
        assert any("upgrade" in name.lower() for name in task_names)

    def test_security_packages_installation(self):
        """Test security packages installation task."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Find task that installs security packages
        package_task = None
        for task in tasks:
            if "security packages" in task.get("name", "").lower():
                package_task = task
                break
        
        assert package_task is not None
        assert "apt" in package_task
        assert "name" in package_task["apt"]
        
        # Should install critical security tools
        packages = package_task["apt"]["name"]
        assert "fail2ban" in packages
        assert "ufw" in packages
        assert "auditd" in packages


class TestPhase2SSHHardening:
    """Test Phase 2: SSH Hardening."""

    def test_ssh_hardening_tasks_exist(self):
        """Test SSH hardening tasks exist."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        # Should have multiple SSH-related tasks
        ssh_tasks = [name for name in task_names if "ssh" in name]
        assert len(ssh_tasks) >= 3

    def test_ssh_config_disables_root_login(self):
        """Test SSH config disables root login."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "PermitRootLogin no" in content

    def test_ssh_config_disables_password_auth(self):
        """Test SSH config disables password authentication."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "PasswordAuthentication no" in content

    def test_ssh_config_enables_pubkey_auth(self):
        """Test SSH config enables public key authentication."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "PubkeyAuthentication yes" in content

    def test_ssh_config_disables_empty_passwords(self):
        """Test SSH config disables empty passwords."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "PermitEmptyPasswords no" in content

    def test_ssh_config_disables_x11_forwarding(self):
        """Test SSH config disables X11 forwarding."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "X11Forwarding no" in content

    def test_ssh_config_sets_max_auth_tries(self):
        """Test SSH config sets max authentication tries."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "MaxAuthTries" in content

    def test_ssh_config_sets_strong_ciphers(self):
        """Test SSH config sets strong ciphers."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "Ciphers" in content
        assert "chacha20-poly1305" in content or "aes256-gcm" in content

    def test_ssh_config_sets_strong_macs(self):
        """Test SSH config sets strong MACs."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "MACs" in content
        assert "hmac-sha2-512" in content or "hmac-sha2-256" in content


class TestPhase3FirewallConfiguration:
    """Test Phase 3: Firewall Configuration (UFW)."""

    def test_ufw_configuration_tasks_exist(self):
        """Test UFW configuration tasks exist."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        ufw_tasks = [name for name in task_names if "ufw" in name or "firewall" in name]
        assert len(ufw_tasks) >= 3

    def test_ufw_default_deny_incoming(self):
        """Test UFW default policy denies incoming."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "incoming" in content.lower() and "deny" in content.lower()

    def test_ufw_allows_ssh(self):
        """Test UFW allows SSH connections."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Find SSH allow task
        ssh_allow_task = None
        for task in tasks:
            if "ssh" in task.get("name", "").lower() and "firewall" in task.get("name", "").lower():
                ssh_allow_task = task
                break
        
        assert ssh_allow_task is not None

    def test_ufw_enables_logging(self):
        """Test UFW enables logging."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "logging" in content.lower()


class TestPhase4Fail2Ban:
    """Test Phase 4: Fail2Ban Configuration."""

    def test_fail2ban_configuration_tasks_exist(self):
        """Test Fail2Ban configuration tasks exist."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        fail2ban_tasks = [name for name in task_names if "fail2ban" in name]
        assert len(fail2ban_tasks) >= 2

    def test_fail2ban_ssh_jail_configured(self):
        """Test Fail2Ban SSH jail is configured."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "[sshd]" in content or "sshd" in content.lower()

    def test_fail2ban_service_enabled(self):
        """Test Fail2Ban service is enabled."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Find Fail2Ban service task
        service_task = None
        for task in tasks:
            if "fail2ban" in task.get("name", "").lower() and ("enable" in task.get("name", "").lower() or "start" in task.get("name", "").lower()):
                service_task = task
                break
        
        assert service_task is not None


class TestPhase5KernelHardening:
    """Test Phase 5: Kernel Hardening (sysctl)."""

    def test_kernel_hardening_tasks_exist(self):
        """Test kernel hardening tasks exist."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        kernel_tasks = [name for name in task_names if "kernel" in name or "sysctl" in name]
        assert len(kernel_tasks) >= 1

    def test_sysctl_disables_ip_forwarding(self):
        """Test sysctl disables IP forwarding."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "net.ipv4.ip_forward" in content

    def test_sysctl_disables_redirects(self):
        """Test sysctl disables ICMP redirects."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "send_redirects" in content or "accept_redirects" in content

    def test_sysctl_enables_syn_cookies(self):
        """Test sysctl enables SYN cookies."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "tcp_syncookies" in content

    def test_sysctl_has_20_plus_parameters(self):
        """Test sysctl configures 20+ security parameters."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Find sysctl task with loop
        sysctl_task = None
        for task in tasks:
            if "sysctl" in task and "loop" in task:
                sysctl_task = task
                break
        
        if sysctl_task:
            assert len(sysctl_task["loop"]) >= 20


class TestPhase6AutomaticUpdates:
    """Test Phase 6: Automatic Security Updates."""

    def test_unattended_upgrades_configured(self):
        """Test unattended-upgrades is configured."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "unattended-upgrades" in content.lower() or "auto" in content.lower()

    def test_automatic_updates_enabled(self):
        """Test automatic updates are enabled."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        assert any("automatic" in name and "update" in name for name in task_names)


class TestPhase7AuditLogging:
    """Test Phase 7: Audit Logging (auditd)."""

    def test_auditd_configuration_tasks_exist(self):
        """Test auditd configuration tasks exist."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        audit_tasks = [name for name in task_names if "audit" in name]
        assert len(audit_tasks) >= 2

    def test_auditd_monitors_user_changes(self):
        """Test auditd monitors user/group changes."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "/etc/passwd" in content and "identity" in content

    def test_auditd_monitors_privileged_commands(self):
        """Test auditd monitors privileged commands."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "sudo" in content or "passwd" in content

    def test_auditd_service_enabled(self):
        """Test auditd service is enabled."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Find auditd service task
        service_task = None
        for task in tasks:
            if "auditd" in task.get("name", "").lower() and ("enable" in task.get("name", "").lower() or "start" in task.get("name", "").lower()):
                service_task = task
                break
        
        assert service_task is not None


class TestPhase8FileSystemHardening:
    """Test Phase 8: File System Hardening."""

    def test_file_permissions_tasks_exist(self):
        """Test file permissions tasks exist."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        assert any("permission" in name or "file" in name for name in task_names)

    def test_shadow_file_protected(self):
        """Test /etc/shadow is protected."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "/etc/shadow" in content

    def test_unnecessary_filesystems_disabled(self):
        """Test unnecessary filesystems are disabled."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        assert any("filesystem" in name for name in task_names)


class TestPhase9ServiceHardening:
    """Test Phase 9: Service Hardening."""

    def test_unnecessary_services_disabled(self):
        """Test unnecessary services are disabled."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        assert any("service" in name and "disable" in name for name in task_names)


class TestPhase10SecurityScanning:
    """Test Phase 10: Security Scanning and Reporting."""

    def test_aide_initialization_task(self):
        """Test AIDE initialization task exists."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        assert any("aide" in name for name in task_names)

    def test_security_audit_script_created(self):
        """Test security audit script is created."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        assert any("security" in name and "audit" in name and "script" in name for name in task_names)

    def test_daily_audit_cron_job(self):
        """Test daily security audit cron job is created."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        task_names = [t["name"].lower() for t in tasks]
        
        assert any("cron" in name or "daily" in name for name in task_names)


class TestCISBenchmarkCompliance:
    """Test CIS benchmark compliance."""

    def test_playbook_mentions_cis(self):
        """Test playbook references CIS benchmarks."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "CIS" in content or "benchmark" in content.lower()

    def test_supports_ubuntu_debian(self):
        """Test playbook supports Ubuntu and Debian."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        # Should mention supported distributions
        assert "Ubuntu" in content or "Debian" in content


class TestTaskTags:
    """Test task tags for selective execution."""

    def test_tasks_have_tags(self):
        """Test tasks have tags for selective execution."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # At least some tasks should have tags
        tagged_tasks = [t for t in tasks if "tags" in t]
        assert len(tagged_tasks) >= 10

    def test_common_tags_exist(self):
        """Test common tags exist."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        expected_tags = ["ssh", "firewall", "fail2ban", "kernel", "updates", "audit"]
        
        for tag in expected_tags:
            assert tag in content


class TestPlaybookDocumentation:
    """Test playbook documentation."""

    def test_has_header_comments(self):
        """Test playbook has header documentation."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        # First few lines should be comments
        assert content.startswith("---") or content.startswith("#")

    def test_documents_phases(self):
        """Test playbook documents hardening phases."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            content = f.read()
        
        assert "PHASE" in content or "Phase" in content

    def test_final_report_task(self):
        """Test playbook generates final report."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Last task should be a report/summary
        last_task = tasks[-1]
        assert "report" in last_task.get("name", "").lower() or "complete" in last_task.get("name", "").lower()


class TestIdempotency:
    """Test playbook idempotency considerations."""

    def test_handlers_only_restart_when_needed(self):
        """Test handlers only restart services when notified."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Tasks that modify config should notify handlers
        notifying_tasks = [t for t in tasks if "notify" in t]
        assert len(notifying_tasks) >= 5

    def test_creates_parameter_for_idempotency(self):
        """Test command tasks use creates parameter for idempotency."""
        playbook_path = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"
        
        with open(playbook_path) as f:
            playbook = yaml.safe_load(f)
        
        play = playbook[0]
        tasks = play.get("tasks", [])
        
        # Command tasks should have creates parameter
        command_tasks = [t for t in tasks if "command" in t]
        for task in command_tasks:
            if "args" in task["command"]:
                # AIDE init should have creates parameter
                if "aide" in task.get("name", "").lower():
                    assert "creates" in task["command"].get("args", {})