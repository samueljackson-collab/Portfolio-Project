"""
tests/test_configs.py — Multi-OS Lab configuration validation tests
Tests: Vagrantfile syntax, Ansible YAML parsing, benchmark CSV format
"""
import csv
import re
import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_ansible_yaml_files():
    """Return all YAML files under ansible/."""
    return list(PROJECT_ROOT.glob("ansible/**/*.yml"))


# ── Vagrantfile tests ─────────────────────────────────────────────────────────
class TestVagrantfile:
    vagrantfile = PROJECT_ROOT / "vagrant" / "Vagrantfile"

    def test_vagrantfile_exists(self):
        assert self.vagrantfile.exists(), "Vagrantfile must exist at vagrant/Vagrantfile"

    def test_vagrantfile_has_configure_block(self):
        content = self.vagrantfile.read_text()
        assert 'Vagrant.configure("2")' in content

    def test_vagrantfile_defines_three_machines(self):
        content = self.vagrantfile.read_text()
        assert '"ubuntu-22"' in content
        assert '"kali-2024"' in content
        assert '"debian-12"' in content

    def test_vagrantfile_has_private_network_ips(self):
        content = self.vagrantfile.read_text()
        assert "192.168.56.10" in content
        assert "192.168.56.20" in content
        assert "192.168.56.30" in content

    def test_vagrantfile_uses_virtualbox_provider(self):
        content = self.vagrantfile.read_text()
        assert '"virtualbox"' in content

    def test_vagrantfile_has_ansible_provisioner(self):
        content = self.vagrantfile.read_text()
        assert '"ansible"' in content
        assert "ansible/site.yml" in content

    def test_vagrantfile_has_shell_provisioner(self):
        content = self.vagrantfile.read_text()
        assert '"shell"' in content

    def test_vagrantfile_memory_values(self):
        content = self.vagrantfile.read_text()
        assert "2048" in content  # Ubuntu
        assert "4096" in content  # Kali
        assert "1024" in content  # Debian

    def test_vagrantfile_machine_boxes(self):
        content = self.vagrantfile.read_text()
        assert "ubuntu/jammy64" in content
        assert "kalilinux/rolling" in content
        assert "debian/bookworm64" in content


# ── Provisioning script tests ─────────────────────────────────────────────────
class TestProvisioningScripts:
    scripts_dir = PROJECT_ROOT / "scripts"

    def test_ubuntu_script_exists(self):
        assert (self.scripts_dir / "provision-ubuntu.sh").exists()

    def test_kali_script_exists(self):
        assert (self.scripts_dir / "provision-kali.sh").exists()

    def test_debian_script_exists(self):
        assert (self.scripts_dir / "provision-debian.sh").exists()

    def test_ubuntu_script_installs_docker(self):
        content = (self.scripts_dir / "provision-ubuntu.sh").read_text()
        assert "docker" in content.lower()

    def test_ubuntu_script_installs_htop_vim_curl_git(self):
        content = (self.scripts_dir / "provision-ubuntu.sh").read_text()
        for pkg in ["htop", "vim", "curl", "git"]:
            assert pkg in content, f"Expected '{pkg}' in ubuntu provision script"

    def test_kali_script_installs_metasploit(self):
        content = (self.scripts_dir / "provision-kali.sh").read_text()
        assert "metasploit" in content.lower()

    def test_kali_script_installs_wireshark(self):
        content = (self.scripts_dir / "provision-kali.sh").read_text()
        assert "wireshark" in content.lower()

    def test_kali_script_installs_burpsuite(self):
        content = (self.scripts_dir / "provision-kali.sh").read_text()
        assert "burpsuite" in content.lower()

    def test_debian_script_configures_nftables(self):
        content = (self.scripts_dir / "provision-debian.sh").read_text()
        assert "nftables" in content.lower()

    def test_scripts_have_set_euo_pipefail(self):
        """All scripts should use strict error handling."""
        for script in ["provision-ubuntu.sh", "provision-kali.sh", "provision-debian.sh"]:
            content = (self.scripts_dir / script).read_text()
            assert "set -euo pipefail" in content, f"{script} must have 'set -euo pipefail'"

    def test_scripts_have_shebang(self):
        for script in ["provision-ubuntu.sh", "provision-kali.sh", "provision-debian.sh"]:
            content = (self.scripts_dir / script).read_text()
            assert content.startswith("#!/"), f"{script} must start with shebang"


# ── Ansible YAML tests ────────────────────────────────────────────────────────
class TestAnsibleYaml:
    ansible_dir = PROJECT_ROOT / "ansible"

    def test_site_yml_exists(self):
        assert (self.ansible_dir / "site.yml").exists()

    def test_site_yml_parses(self):
        content = (self.ansible_dir / "site.yml").read_text()
        parsed = yaml.safe_load(content)
        assert parsed is not None
        assert isinstance(parsed, list)

    def test_site_yml_has_play_for_all(self):
        content = (self.ansible_dir / "site.yml").read_text()
        parsed = yaml.safe_load(content)
        hosts = [play.get("hosts") for play in parsed if isinstance(play, dict)]
        assert "all" in hosts

    def test_common_role_tasks_exist(self):
        tasks_file = self.ansible_dir / "roles" / "common" / "tasks" / "main.yml"
        assert tasks_file.exists()

    def test_ubuntu_baseline_tasks_exist(self):
        tasks_file = self.ansible_dir / "roles" / "ubuntu-baseline" / "tasks" / "main.yml"
        assert tasks_file.exists()

    def test_kali_setup_tasks_exist(self):
        tasks_file = self.ansible_dir / "roles" / "kali-setup" / "tasks" / "main.yml"
        assert tasks_file.exists()

    @pytest.mark.parametrize("yaml_file", get_ansible_yaml_files())
    def test_ansible_yaml_parses_without_error(self, yaml_file):
        content = yaml_file.read_text()
        try:
            parsed = yaml.safe_load(content)
            assert parsed is not None, f"{yaml_file} must not be empty"
        except yaml.YAMLError as exc:
            pytest.fail(f"YAML parse error in {yaml_file}: {exc}")

    def test_common_tasks_set_hostname(self):
        content = (self.ansible_dir / "roles" / "common" / "tasks" / "main.yml").read_text()
        assert "hostname" in content.lower()

    def test_common_tasks_configure_ntp(self):
        content = (self.ansible_dir / "roles" / "common" / "tasks" / "main.yml").read_text()
        assert "chrony" in content.lower()

    def test_ubuntu_baseline_tasks_configure_ufw(self):
        content = (self.ansible_dir / "roles" / "ubuntu-baseline" / "tasks" / "main.yml").read_text()
        assert "ufw" in content.lower()

    def test_ubuntu_baseline_tasks_configure_fail2ban(self):
        content = (self.ansible_dir / "roles" / "ubuntu-baseline" / "tasks" / "main.yml").read_text()
        assert "fail2ban" in content.lower()

    def test_kali_tasks_configure_metasploit(self):
        content = (self.ansible_dir / "roles" / "kali-setup" / "tasks" / "main.yml").read_text()
        assert "metasploit" in content.lower() or "msfdb" in content.lower()


# ── Benchmark CSV tests ───────────────────────────────────────────────────────
class TestBenchmarkCsv:
    csv_file = PROJECT_ROOT / "benchmarks" / "benchmark_results.csv"

    REQUIRED_COLUMNS = {"os", "test", "metric", "value", "unit", "timestamp"}
    EXPECTED_OS = {"Ubuntu 22.04 LTS", "Kali Linux 2024.1", "Debian 12 Bookworm"}
    EXPECTED_TESTS = {"boot_time", "memory_idle", "disk_write", "disk_read", "cpu_sysbench"}

    def test_csv_exists(self):
        assert self.csv_file.exists()

    def test_csv_has_correct_columns(self):
        with self.csv_file.open() as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == self.REQUIRED_COLUMNS

    def test_csv_has_all_three_os(self):
        with self.csv_file.open() as f:
            reader = csv.DictReader(f)
            os_set = {row["os"] for row in reader}
        assert self.EXPECTED_OS.issubset(os_set), \
            f"Missing OS entries. Found: {os_set}"

    def test_csv_has_required_tests(self):
        with self.csv_file.open() as f:
            reader = csv.DictReader(f)
            test_set = {row["test"] for row in reader}
        assert self.EXPECTED_TESTS.issubset(test_set), \
            f"Missing tests. Found: {test_set}"

    def test_csv_values_are_numeric(self):
        with self.csv_file.open() as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    float(row["value"])
                except ValueError:
                    pytest.fail(f"Row {i+2}: 'value' column is not numeric: {row['value']!r}")

    def test_csv_timestamps_are_iso_format(self):
        ts_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        with self.csv_file.open() as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                assert ts_pattern.match(row["timestamp"]), \
                    f"Row {i+2}: timestamp not ISO format: {row['timestamp']!r}"

    def test_csv_has_minimum_row_count(self):
        with self.csv_file.open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 15, f"Expected at least 15 benchmark rows, got {len(rows)}"

    def test_csv_boot_time_values_are_positive(self):
        with self.csv_file.open() as f:
            reader = csv.DictReader(f)
            boot_times = [float(row["value"]) for row in reader if row["test"] == "boot_time"]
        assert all(v > 0 for v in boot_times), "All boot times must be positive"
        assert len(boot_times) == 3, f"Expected 3 boot time rows, got {len(boot_times)}"


# ── Demo output tests ─────────────────────────────────────────────────────────
class TestDemoOutput:
    demo_dir = PROJECT_ROOT / "demo_output"

    def test_os_comparison_txt_exists(self):
        assert (self.demo_dir / "os_comparison.txt").exists()

    def test_lab_inventory_txt_exists(self):
        assert (self.demo_dir / "lab_inventory.txt").exists()

    def test_os_comparison_has_all_three_os(self):
        content = (self.demo_dir / "os_comparison.txt").read_text()
        assert "Ubuntu" in content
        assert "Kali" in content
        assert "Debian" in content

    def test_os_comparison_has_feature_matrix(self):
        content = (self.demo_dir / "os_comparison.txt").read_text()
        assert "FEATURE MATRIX" in content.upper()

    def test_os_comparison_has_benchmark_chart(self):
        content = (self.demo_dir / "os_comparison.txt").read_text()
        assert "BENCHMARK" in content.upper()

    def test_lab_inventory_has_vagrant_status(self):
        content = (self.demo_dir / "lab_inventory.txt").read_text()
        assert "running" in content.lower()
        assert "ubuntu-22" in content

    def test_lab_inventory_has_ansible_inventory(self):
        content = (self.demo_dir / "lab_inventory.txt").read_text()
        assert "192.168.56.10" in content
        assert "192.168.56.20" in content
        assert "192.168.56.30" in content
