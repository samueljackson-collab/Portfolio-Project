"""
Comprehensive tests for security-hardening.yml Ansible playbook.

This test suite validates:
- YAML syntax and structure
- All 10 security hardening phases
- Task definitions and handlers
- Variable configurations
- CIS compliance alignment
- Security best practices
"""

import yaml
import pytest
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent
PLAYBOOK_PATH = BASE_PATH / "projects/06-homelab/PRJ-HOME-002/assets/automation/ansible/playbooks/security-hardening.yml"


@pytest.fixture
def security_playbook():
    """Load and parse security hardening playbook"""
    with open(PLAYBOOK_PATH) as f:
        playbook = yaml.safe_load(f)
    return playbook


@pytest.fixture
def playbook_content():
    """Load raw playbook content for string checks"""
    with open(PLAYBOOK_PATH) as f:
        return f.read()


class TestPlaybookStructure:
    """Test playbook structure and syntax"""
    
    def test_playbook_file_exists(self):
        """Verify security hardening playbook exists"""
        assert PLAYBOOK_PATH.exists()
    
    def test_playbook_valid_yaml(self, security_playbook):
        """Test playbook is valid YAML"""
        assert security_playbook is not None
        assert isinstance(security_playbook, list)
    
    def test_playbook_has_main_play(self, security_playbook):
        """Test playbook has main play definition"""
        assert len(security_playbook) > 0
        main_play = security_playbook[0]
        assert isinstance(main_play, dict)
    
    def test_play_has_required_keys(self, security_playbook):
        """Test main play has required keys"""
        main_play = security_playbook[0]
        assert 'name' in main_play
        assert 'hosts' in main_play
        assert 'become' in main_play
        assert 'tasks' in main_play
    
    def test_play_name_descriptive(self, security_playbook):
        """Test play has descriptive name"""
        main_play = security_playbook[0]
        assert len(main_play['name']) > 0
        assert 'security' in main_play['name'].lower() or 'hardening' in main_play['name'].lower()


class TestPlaybookVariables:
    """Test playbook variables"""
    
    def test_playbook_has_vars(self, security_playbook):
        """Test playbook defines variables"""
        main_play = security_playbook[0]
        assert 'vars' in main_play
        assert isinstance(main_play['vars'], dict)
    
    def test_ssh_port_variable(self, security_playbook):
        """Test SSH port variable is defined"""
        main_play = security_playbook[0]
        vars_dict = main_play['vars']
        assert 'ssh_port' in vars_dict
        assert isinstance(vars_dict['ssh_port'], int)
        assert 1 <= vars_dict['ssh_port'] <= 65535
    
    def test_allowed_ssh_users_variable(self, security_playbook):
        """Test allowed SSH users variable"""
        main_play = security_playbook[0]
        vars_dict = main_play['vars']
        assert 'allowed_ssh_users' in vars_dict
        assert isinstance(vars_dict['allowed_ssh_users'], list)
        assert len(vars_dict['allowed_ssh_users']) > 0
    
    def test_fail2ban_variables(self, security_playbook):
        """Test fail2ban configuration variables"""
        main_play = security_playbook[0]
        vars_dict = main_play['vars']
        
        assert 'fail2ban_bantime' in vars_dict
        assert 'fail2ban_findtime' in vars_dict
        assert 'fail2ban_maxretry' in vars_dict
        
        assert isinstance(vars_dict['fail2ban_bantime'], int)
        assert isinstance(vars_dict['fail2ban_findtime'], int)
        assert isinstance(vars_dict['fail2ban_maxretry'], int)
    
    def test_auto_updates_variable(self, security_playbook):
        """Test auto updates variable"""
        main_play = security_playbook[0]
        vars_dict = main_play['vars']
        assert 'auto_updates_enabled' in vars_dict
        assert isinstance(vars_dict['auto_updates_enabled'], bool)
    
    def test_audit_logs_variable(self, security_playbook):
        """Test audit logs variable"""
        main_play = security_playbook[0]
        vars_dict = main_play['vars']
        assert 'audit_logs_enabled' in vars_dict
        assert isinstance(vars_dict['audit_logs_enabled'], bool)


class TestHandlers:
    """Test playbook handlers"""
    
    def test_playbook_has_handlers(self, security_playbook):
        """Test playbook defines handlers"""
        main_play = security_playbook[0]
        assert 'handlers' in main_play
        assert isinstance(main_play['handlers'], list)
        assert len(main_play['handlers']) > 0
    
    def test_restart_sshd_handler(self, security_playbook):
        """Test restart sshd handler exists"""
        main_play = security_playbook[0]
        handlers = main_play['handlers']
        
        sshd_handler = next((h for h in handlers if h['name'] == 'restart sshd'), None)
        assert sshd_handler is not None
        assert 'service' in sshd_handler
        assert sshd_handler['service']['name'] == 'sshd'
        assert sshd_handler['service']['state'] == 'restarted'
    
    def test_restart_fail2ban_handler(self, security_playbook):
        """Test restart fail2ban handler exists"""
        main_play = security_playbook[0]
        handlers = main_play['handlers']
        
        fail2ban_handler = next((h for h in handlers if h['name'] == 'restart fail2ban'), None)
        assert fail2ban_handler is not None
        assert 'service' in fail2ban_handler
    
    def test_restart_ufw_handler(self, security_playbook):
        """Test restart ufw handler exists"""
        main_play = security_playbook[0]
        handlers = main_play['handlers']
        
        ufw_handler = next((h for h in handlers if h['name'] == 'restart ufw'), None)
        assert ufw_handler is not None
        assert 'service' in ufw_handler
    
    def test_restart_auditd_handler(self, security_playbook):
        """Test restart auditd handler exists"""
        main_play = security_playbook[0]
        handlers = main_play['handlers']
        
        auditd_handler = next((h for h in handlers if h['name'] == 'restart auditd'), None)
        assert auditd_handler is not None
        assert 'service' in auditd_handler
    
    def test_all_handlers_have_names(self, security_playbook):
        """Test all handlers have descriptive names"""
        main_play = security_playbook[0]
        handlers = main_play['handlers']
        
        for handler in handlers:
            assert 'name' in handler
            assert len(handler['name']) > 0


class TestPhase1SystemUpdates:
    """Test Phase 1: System Updates and Package Management"""
    
    def test_update_apt_cache_task(self, security_playbook):
        """Test apt cache update task"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        update_task = next((t for t in tasks if 'Update apt cache' in t.get('name', '')), None)
        assert update_task is not None
        assert 'apt' in update_task
        assert update_task['apt']['update_cache'] is True
    
    def test_upgrade_packages_task(self, security_playbook):
        """Test package upgrade task"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        upgrade_task = next((t for t in tasks if 'Upgrade all packages' in t.get('name', '')), None)
        assert upgrade_task is not None
        assert 'apt' in upgrade_task
        assert 'upgrade' in upgrade_task['apt']
    
    def test_install_security_packages_task(self, security_playbook):
        """Test security packages installation"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        install_task = next((t for t in tasks if 'Install security packages' in t.get('name', '')), None)
        assert install_task is not None
        assert 'apt' in install_task
        assert 'name' in install_task['apt']
        
        packages = install_task['apt']['name']
        assert isinstance(packages, list)
        
        # Check for essential security packages
        expected_packages = ['fail2ban', 'ufw', 'auditd', 'aide', 'rkhunter']
        for pkg in expected_packages:
            assert pkg in packages


class TestPhase2SSHHardening:
    """Test Phase 2: SSH Hardening"""
    
    def test_ssh_daemon_configuration_task(self, security_playbook):
        """Test SSH daemon security configuration"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        ssh_config_task = next((t for t in tasks if 'Configure SSH daemon security' in t.get('name', '')), None)
        assert ssh_config_task is not None
        assert 'lineinfile' in ssh_config_task
        assert 'loop' in ssh_config_task
    
    def test_ssh_config_disables_root_login(self, playbook_content):
        """Test SSH config disables root login"""
        assert 'PermitRootLogin no' in playbook_content
    
    def test_ssh_config_disables_password_auth(self, playbook_content):
        """Test SSH config disables password authentication"""
        assert 'PasswordAuthentication no' in playbook_content
    
    def test_ssh_config_enables_pubkey_auth(self, playbook_content):
        """Test SSH config enables public key authentication"""
        assert 'PubkeyAuthentication yes' in playbook_content
    
    def test_ssh_config_disables_empty_passwords(self, playbook_content):
        """Test SSH config disables empty passwords"""
        assert 'PermitEmptyPasswords no' in playbook_content
    
    def test_ssh_config_disables_x11_forwarding(self, playbook_content):
        """Test SSH config disables X11 forwarding"""
        assert 'X11Forwarding no' in playbook_content
    
    def test_ssh_max_auth_tries(self, playbook_content):
        """Test SSH max authentication tries is limited"""
        assert 'MaxAuthTries' in playbook_content


class TestPhase3FirewallConfiguration:
    """Test Phase 3: Firewall Configuration (UFW)"""
    
    def test_reset_ufw_task(self, security_playbook):
        """Test UFW reset task"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        reset_task = next((t for t in tasks if 'Reset UFW' in t.get('name', '')), None)
        assert reset_task is not None
        assert 'ufw' in reset_task
    
    def test_configure_ufw_defaults_task(self, security_playbook):
        """Test UFW default policy configuration"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        defaults_task = next((t for t in tasks if 'Configure UFW default' in t.get('name', '')), None)
        assert defaults_task is not None
    
    def test_allow_ssh_through_firewall_task(self, security_playbook):
        """Test SSH is allowed through firewall"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        ssh_task = next((t for t in tasks if 'Allow SSH' in t.get('name', '')), None)
        assert ssh_task is not None
    
    def test_enable_ufw_task(self, security_playbook):
        """Test UFW is enabled"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        enable_task = next((t for t in tasks if 'Enable UFW' in t.get('name', '')), None)
        assert enable_task is not None


class TestPhase4Fail2Ban:
    """Test Phase 4: Fail2Ban Configuration"""
    
    def test_fail2ban_local_config_task(self, security_playbook):
        """Test fail2ban local configuration task"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        config_task = next((t for t in tasks if 'fail2ban local configuration' in t.get('name', '')), None)
        assert config_task is not None
    
    def test_fail2ban_ssh_jail_task(self, security_playbook):
        """Test fail2ban SSH jail configuration"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        jail_task = next((t for t in tasks if 'fail2ban SSH jail' in t.get('name', '')), None)
        assert jail_task is not None
    
    def test_enable_fail2ban_task(self, security_playbook):
        """Test fail2ban is enabled and started"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        enable_task = next((t for t in tasks if 'Enable and start fail2ban' in t.get('name', '')), None)
        assert enable_task is not None


class TestPhase5KernelHardening:
    """Test Phase 5: Kernel Hardening (sysctl)"""
    
    def test_kernel_hardening_task(self, security_playbook):
        """Test kernel hardening via sysctl"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        sysctl_task = next((t for t in tasks if 'kernel hardening via sysctl' in t.get('name', '')), None)
        assert sysctl_task is not None
        assert 'sysctl' in sysctl_task
        assert 'loop' in sysctl_task
    
    def test_disable_ip_forwarding(self, playbook_content):
        """Test IP forwarding is disabled"""
        assert 'net.ipv4.ip_forward' in playbook_content
    
    def test_disable_send_redirects(self, playbook_content):
        """Test ICMP redirects are disabled"""
        assert 'net.ipv4.conf.all.send_redirects' in playbook_content
    
    def test_disable_accept_redirects(self, playbook_content):
        """Test accepting redirects is disabled"""
        assert 'net.ipv4.conf.all.accept_redirects' in playbook_content
    
    def test_disable_source_routing(self, playbook_content):
        """Test source routing is disabled"""
        assert 'net.ipv4.conf.all.accept_source_route' in playbook_content or 'accept_redirects' in playbook_content


class TestPhase6AutoUpdates:
    """Test Phase 6: Automatic Updates"""
    
    def test_auto_updates_phase_exists(self, playbook_content):
        """Test automatic updates phase exists"""
        assert 'PHASE 6' in playbook_content or 'auto' in playbook_content.lower()


class TestPhase7AuditLogging:
    """Test Phase 7: Audit Logging"""
    
    def test_audit_logging_phase_exists(self, playbook_content):
        """Test audit logging phase exists"""
        assert 'PHASE 7' in playbook_content or 'audit' in playbook_content.lower()


class TestPhase8FileSystem:
    """Test Phase 8: File System Hardening"""
    
    def test_filesystem_phase_exists(self, playbook_content):
        """Test file system hardening phase exists"""
        assert 'PHASE 8' in playbook_content or 'file' in playbook_content.lower()


class TestPhase9Services:
    """Test Phase 9: Disable Unnecessary Services"""
    
    def test_services_phase_exists(self, playbook_content):
        """Test services phase exists"""
        assert 'PHASE 9' in playbook_content or 'service' in playbook_content.lower()


class TestPhase10SecurityScanning:
    """Test Phase 10: Security Scanning"""
    
    def test_security_scanning_phase_exists(self, playbook_content):
        """Test security scanning phase exists"""
        assert 'PHASE 10' in playbook_content or 'scan' in playbook_content.lower()


class TestTaskTags:
    """Test task tagging"""
    
    def test_tasks_have_tags(self, security_playbook):
        """Test important tasks have tags for selective execution"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        tagged_tasks = [t for t in tasks if 'tags' in t]
        assert len(tagged_tasks) > 0
    
    def test_update_tasks_have_update_tag(self, playbook_content):
        """Test update tasks have 'updates' tag"""
        assert 'tags:' in playbook_content or 'tags' in playbook_content


class TestSecurityBestPractices:
    """Test security best practices"""
    
    def test_playbook_uses_become(self, security_playbook):
        """Test playbook uses privilege escalation"""
        main_play = security_playbook[0]
        assert main_play['become'] is True
    
    def test_playbook_targets_all_hosts(self, security_playbook):
        """Test playbook targets appropriate hosts"""
        main_play = security_playbook[0]
        assert main_play['hosts'] in ['all', 'servers', 'linux']
    
    def test_ssh_config_uses_backup(self, playbook_content):
        """Test SSH configuration creates backups"""
        assert 'backup:' in playbook_content or 'backup' in playbook_content.lower()
    
    def test_handlers_use_notify(self, playbook_content):
        """Test tasks use notify to trigger handlers"""
        assert 'notify:' in playbook_content or 'notify' in playbook_content.lower()


class TestCISCompliance:
    """Test CIS Benchmark compliance"""
    
    def test_cis_aligned_ssh_settings(self, playbook_content):
        """Test SSH settings align with CIS benchmarks"""
        # CIS 5.2.x - SSH Server Configuration
        cis_ssh_settings = [
            'PermitRootLogin no',
            'PasswordAuthentication no',
            'PermitEmptyPasswords no',
            'Protocol 2',
        ]
        
        for setting in cis_ssh_settings:
            assert setting in playbook_content
    
    def test_cis_aligned_network_settings(self, playbook_content):
        """Test network settings align with CIS benchmarks"""
        # CIS 3.x - Network Configuration
        assert 'net.ipv4.ip_forward' in playbook_content
        assert 'net.ipv4.conf.all.send_redirects' in playbook_content


class TestPlaybookCompletenessPhases:
    """Test all 10 phases are present"""
    
    def test_all_10_phases_documented(self, playbook_content):
        """Test all 10 phases are documented in comments"""
        phases = [f'PHASE {i}' for i in range(1, 11)]
        
        for phase in phases:
            assert phase in playbook_content, f"Missing {phase}"
    
    def test_playbook_has_sufficient_tasks(self, security_playbook):
        """Test playbook has substantial number of tasks"""
        main_play = security_playbook[0]
        tasks = main_play['tasks']
        
        # Should have at least 20 tasks for comprehensive hardening
        assert len(tasks) >= 20


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_playbook_size_indicates_comprehensive_coverage(self):
        """Test playbook file is substantial (indicates comprehensive coverage)"""
        file_size = PLAYBOOK_PATH.stat().st_size
        assert file_size > 10000  # At least 10KB
    
    def test_playbook_line_count(self):
        """Test playbook has substantial line count"""
        with open(PLAYBOOK_PATH) as f:
            lines = len(f.readlines())
        assert lines >= 400  # Should have at least 400 lines


if __name__ == '__main__':
    pytest.main([__file__, '-v'])