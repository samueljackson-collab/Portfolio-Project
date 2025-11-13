# PRJ-HOME-003: Multi-OS Lab - Operations Runbook

**Version:** 0.1 (Draft)
**Last Updated:** November 10, 2025
**Maintainer:** Samuel Jackson
**Project Status:** 🔵 Planned

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Lab Environment Setup](#lab-environment-setup)
4. [Operating Systems](#operating-systems)
5. [Common Operations](#common-operations)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Overview

### Purpose
This runbook provides operational procedures for managing a multi-OS lab environment featuring Kali Linux, Slackware-based SlackoPuppy, and Ubuntu for comparative analysis and security testing.

### Scope
- **Operating Systems:** Kali Linux, SlackoPuppy, Ubuntu
- **Environment:** Virtual machines on Proxmox cluster
- **Use Cases:** Comparative OS analysis, security testing, tool evaluation
- **Status:** Project in planning phase

### Service Level Objectives
- **Availability:** 95% (lab/testing environment)
- **RTO:** 24 hours (low priority)
- **RPO:** 7 days (weekly snapshots)
- **Priority:** P3 (Non-production)

---

## Quick Reference

### Lab VM Information

> **Note:** This section will be populated when VMs are deployed.

| VM | OS | IP Address | VM ID | Purpose | Status |
|----|----|-----------:|-------|---------|--------|
| kali-lab | Kali Linux | TBD | TBD | Security testing | Planned |
| slacko-lab | SlackoPuppy | TBD | TBD | Lightweight OS testing | Planned |
| ubuntu-lab | Ubuntu 24.04 | TBD | TBD | Baseline comparison | Planned |

### Access Points

```bash
# SSH access (to be configured)
ssh user@<VM_IP>

# Console access via Proxmox
# https://192.168.40.10:8006
# Select VM → Console
```

### Resource Allocation (Planned)

| VM | vCPUs | RAM | Disk | Storage |
|----|------:|----:|-----:|---------|
| kali-lab | 2-4 | 4 GB | 50 GB | local-lvm or ceph-rbd |
| slacko-lab | 1-2 | 1 GB | 10 GB | local-lvm |
| ubuntu-lab | 2 | 2 GB | 20 GB | local-lvm |

---

## Lab Environment Setup

### Phase 1: Planning (Current)

**Objectives:**
- Define lab goals and use cases
- Select OS versions
- Plan network configuration
- Identify required tools and software

**Decisions to Make:**
- [ ] Network segmentation (separate VLAN? Lab VLAN 100?)
- [ ] Internet access requirements
- [ ] Shared storage needs
- [ ] Snapshot frequency
- [ ] Resource allocation

### Phase 2: Deployment (Upcoming)

**Prerequisites:**
- Proxmox cluster operational (PRJ-HOME-002)
- Network infrastructure ready (PRJ-HOME-001)
- ISO images downloaded
- Resource availability confirmed

**Deployment Steps:**

#### 1. Download ISO Images
```bash
# SSH to Proxmox node
ssh root@192.168.40.10

# Download Kali Linux
cd /var/lib/vz/template/iso
wget https://cdimage.kali.org/kali-2025.1/kali-linux-2025.1-installer-amd64.iso

# Download Ubuntu
wget https://releases.ubuntu.com/24.04/ubuntu-24.04-live-server-amd64.iso

# SlackoPuppy (Puppy Linux based on Slackware)
wget <SLACKOPUPPY_ISO_URL>

# Verify checksums
sha256sum *.iso
```

#### 2. Create VMs
```bash
# Create Kali Linux VM
qm create 201 \
  --name kali-lab \
  --memory 4096 \
  --cores 4 \
  --net0 virtio,bridge=vmbr0,tag=100 \
  --scsi0 local-lvm:50 \
  --ide2 local:iso/kali-linux-2025.1-installer-amd64.iso,media=cdrom \
  --boot order=scsi0 \
  --agent 1 \
  --ostype l26

# Create SlackoPuppy VM
qm create 202 \
  --name slacko-lab \
  --memory 1024 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0,tag=100 \
  --scsi0 local-lvm:10 \
  --ide2 local:iso/slackopuppy.iso,media=cdrom \
  --boot order=scsi0 \
  --ostype l26

# Create Ubuntu VM
qm create 203 \
  --name ubuntu-lab \
  --memory 2048 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0,tag=100 \
  --scsi0 local-lvm:20 \
  --ide2 local:iso/ubuntu-24.04-live-server-amd64.iso,media=cdrom \
  --boot order=scsi0 \
  --agent 1 \
  --ostype l26

# Start VMs for installation
qm start 201
qm start 202
qm start 203
```

#### 3. OS Installation
```
# Via Proxmox console:
# Select VM → Console
# Follow OS-specific installation procedures

# Kali Linux:
# - Graphical Install
# - Hostname: kali-lab
# - Domain: homelab.local
# - Default user + sudo access
# - Install desktop environment

# SlackoPuppy:
# - Boot to live environment
# - Install to disk if needed
# - Configure persistence

# Ubuntu:
# - Install Ubuntu Server
# - Hostname: ubuntu-lab
# - Install OpenSSH server
# - Minimal installation
```

#### 4. Post-Installation Configuration
```bash
# For each VM, configure:
# - Static IP or DHCP reservation
# - SSH access
# - QEMU guest agent
# - Updates/security patches
# - Basic tools

# Example (Ubuntu):
ssh user@<UBUNTU_IP>
sudo apt update && sudo apt upgrade -y
sudo apt install qemu-guest-agent -y
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent
```

#### 5. Create Initial Snapshots
```bash
# On Proxmox host
ssh root@192.168.40.10

# Create "clean install" snapshots
qm snapshot 201 clean-install --description "Fresh Kali installation"
qm snapshot 202 clean-install --description "Fresh SlackoPuppy installation"
qm snapshot 203 clean-install --description "Fresh Ubuntu installation"
```

### Phase 3: Configuration (Future)

**Setup Tasks:**
- Configure networking
- Install comparative analysis tools
- Set up shared storage (if needed)
- Configure backup schedule
- Document baseline configurations

---

## Operating Systems

### Kali Linux (VM ID: 201)

**Purpose:** Security testing, penetration testing, forensics

**Key Features:**
- Pre-installed security tools
- Rolling release updates
- Multiple desktop environments available

**Common Tools to Install/Configure:**
```bash
# Update all tools
sudo apt update && sudo apt full-upgrade -y

# Key tools (should be pre-installed):
# - nmap (network scanning)
# - metasploit (exploitation framework)
# - wireshark (packet analysis)
# - burpsuite (web app testing)
# - john (password cracking)
# - aircrack-ng (wireless testing)

# Verify tools
which nmap metasploit wireshark burpsuite john aircrack-ng
```

**Maintenance:**
```bash
# Regular updates
sudo apt update && sudo apt full-upgrade -y

# Clean up
sudo apt autoremove -y
sudo apt autoclean
```

### SlackoPuppy (VM ID: 202)

**Purpose:** Lightweight OS testing, resource efficiency analysis

**Key Features:**
- Slackware-based Puppy Linux
- Minimal resource requirements
- Fast boot time
- Portable/live USB capability

**Configuration Notes:**
- Runs primarily in RAM
- Persistent storage configuration needed
- Package management via slapt-get or manual

**Maintenance:**
```bash
# Updates (if applicable)
# SlackoPuppy uses Puppy Package Manager (PPM)
# Or: slapt-get if configured

# Check system info
uname -a
cat /etc/slackware-version  # If available
```

### Ubuntu 24.04 LTS (VM ID: 203)

**Purpose:** Baseline comparison, general-purpose server testing

**Key Features:**
- Long-term support (until 2029)
- Stable and well-documented
- Standard package management (apt)
- Wide software availability

**Common Setup:**
```bash
# Install essential tools
sudo apt update
sudo apt install -y \
  vim \
  tmux \
  htop \
  net-tools \
  curl \
  wget \
  git \
  build-essential

# Enable firewall
sudo ufw enable
sudo ufw allow 22/tcp  # SSH
```

**Maintenance:**
```bash
# Regular updates
sudo apt update && sudo apt upgrade -y

# Security updates only
sudo apt update && sudo apt upgrade -y --security

# Check for reboot requirement
[ -f /var/run/reboot-required ] && echo "Reboot required" || echo "No reboot needed"
```

---

## Common Operations

### Starting Lab VMs

```bash
# SSH to Proxmox node
ssh root@192.168.40.10

# Start all lab VMs
qm start 201  # Kali
qm start 202  # SlackoPuppy
qm start 203  # Ubuntu

# Or start all at once
for vmid in 201 202 203; do qm start $vmid; done

# Verify all running
qm list | grep -E "201|202|203"
```

### Stopping Lab VMs

```bash
# Graceful shutdown
qm shutdown 201
qm shutdown 202
qm shutdown 203

# Or shutdown all
for vmid in 201 202 203; do qm shutdown $vmid; done

# Force stop (if needed)
qm stop 201
```

### Taking Snapshots Before Testing

```bash
# Take snapshots before major testing
qm snapshot 201 before-test-$(date +%Y%m%d) --description "Before security testing"
qm snapshot 202 before-test-$(date +%Y%m%d) --description "Before performance testing"
qm snapshot 203 before-test-$(date +%Y%m%d) --description "Before baseline testing"
```

### Restoring from Snapshot

```bash
# List snapshots
qm listsnapshot 201

# Stop VM
qm stop 201

# Rollback to snapshot
qm rollback 201 <SNAPSHOT_NAME>

# Start VM
qm start 201
```

### Cloning Lab VM

```bash
# Clone VM for different test scenario
qm clone 201 211 --name kali-lab-clone --full

# Start clone
qm start 211
```

---

## Comparative Analysis

### System Resource Comparison

**Objective:** Compare resource usage across different OS

**Procedure:**
```bash
# On each VM, collect metrics:

# 1. Boot time
systemd-analyze  # Linux systemd-based systems

# 2. Memory usage
free -h

# 3. Disk usage
df -h

# 4. Process count
ps aux | wc -l

# 5. Installed packages
# Ubuntu: dpkg -l | wc -l
# Kali: dpkg -l | wc -l
# SlackoPuppy: ls /var/log/packages | wc -l

# 6. Network performance
# Install iperf3 on all VMs
# From one VM: iperf3 -s
# From another: iperf3 -c <SERVER_IP>
```

**Documentation:**
Create comparison table in lab notes:
```
| Metric | Kali | SlackoPuppy | Ubuntu | Winner |
|--------|------|-------------|--------|--------|
| Boot Time | X sec | Y sec | Z sec | ? |
| RAM Usage (Idle) | X MB | Y MB | Z MB | ? |
| Disk Usage (Fresh) | X GB | Y GB | Z GB | ? |
| Package Count | X | Y | Z | ? |
| Network Throughput | X Mbps | Y Mbps | Z Mbps | ? |
```

### Security Tool Comparison

**Objective:** Evaluate security tools across platforms

**Test Cases:**
1. Port scanning speed (nmap)
2. Password cracking speed (john)
3. Network sniffing capabilities (tcpdump/wireshark)
4. Exploit framework availability
5. Forensics tool compatibility

### Package Management Comparison

**Objective:** Compare package management systems

**Comparison Points:**
- Install speed
- Update speed
- Dependency resolution
- Repository size
- Package availability

---

## Troubleshooting

### VM Won't Start

```bash
# Check VM status
qm status <VMID>

# Check for locks
qm unlock <VMID>

# Check VM configuration
qm config <VMID>

# Check logs
journalctl -u qemu-server@<VMID> -n 50

# Try starting with verbose output
qm start <VMID> --verbose
```

### Network Connectivity Issues

```bash
# Inside VM:
# Check IP address
ip addr show

# Check routing
ip route show

# Test connectivity
ping 192.168.40.1  # Gateway
ping 8.8.8.8       # Internet

# Check DNS
nslookup google.com

# If DHCP not working:
# Set static IP (example for Ubuntu):
sudo nano /etc/netplan/50-cloud-init.yaml
# Apply: sudo netplan apply
```

### Performance Issues

```bash
# Check CPU/Memory on host
ssh root@192.168.40.10
qm status <VMID> --verbose

# Check inside VM
top  # or htop
df -h
iostat -x 1  # If sysstat installed

# Adjust resources if needed
qm set <VMID> --memory 8192  # Increase RAM
qm set <VMID> --cores 4       # Add CPU cores
```

---

## Maintenance

### Weekly Maintenance

```bash
# Take weekly snapshots
qm snapshot 201 weekly-$(date +%Y%m%d)
qm snapshot 202 weekly-$(date +%Y%m%d)
qm snapshot 203 weekly-$(date +%Y%m%d)

# Update all VMs
# Kali:
ssh user@<KALI_IP>
sudo apt update && sudo apt full-upgrade -y

# Ubuntu:
ssh user@<UBUNTU_IP>
sudo apt update && sudo apt upgrade -y

# SlackoPuppy:
# Manual updates as needed
```

### Monthly Maintenance

```bash
# Clean up old snapshots (keep last 4 weeks)
qm delsnapshot 201 <OLD_SNAPSHOT_NAME>

# Review disk usage
qm status 201 --verbose | grep disk

# Resize disk if needed
qm resize 201 scsi0 +10G
```

### Backup Strategy

**Frequency:** Weekly (low priority)
**Method:** Proxmox vzdump to TrueNAS
**Retention:** 4 weekly backups

```bash
# Manual backup
vzdump 201 202 203 --storage truenas-nfs --mode snapshot --compress zstd

# Automated backup (configured in Proxmox)
# Datacenter → Backup → Add
# VMs: 201,202,203
# Storage: truenas-nfs
# Schedule: Sunday 4:00 AM
```

---

## Project Milestones

### Phase 1: Planning ✅
- [x] Define project scope
- [x] Create initial runbook
- [ ] Finalize OS versions
- [ ] Plan network configuration

### Phase 2: Deployment (Upcoming)
- [ ] Download ISO images
- [ ] Create VMs
- [ ] Install operating systems
- [ ] Configure networking
- [ ] Take initial snapshots

### Phase 3: Configuration
- [ ] Install analysis tools
- [ ] Configure shared storage (if needed)
- [ ] Set up automated backups
- [ ] Document baseline configurations

### Phase 4: Testing & Analysis
- [ ] Perform comparative analysis
- [ ] Document findings
- [ ] Create comparison reports
- [ ] Identify use cases for each OS

---

## Future Enhancements

**Potential Additions:**
- [ ] Add more OS variants (Arch, Fedora, OpenBSD)
- [ ] Automated testing framework
- [ ] Performance benchmarking suite
- [ ] Integration with monitoring tools (Grafana)
- [ ] Automated comparative reports
- [ ] Container comparison (Docker, Podman, LXC)

---

## Notes and Documentation

### Lab Notes Location
- **Path:** `/opt/lab-notes/PRJ-HOME-003/`
- **Format:** Markdown files
- **Backup:** Included in VM backups

### Test Results
- Store test results in: `assets/test-results/`
- Include: screenshots, benchmark outputs, comparison tables

### Useful Commands Reference

```bash
# Kali Linux specific
kali-tweaks               # Configuration tool
msfconsole                # Metasploit
burpsuite                 # Web app testing

# Ubuntu specific
landscape-sysinfo         # System information
ubuntu-security-status    # Security updates

# SlackoPuppy specific
puppy-package-manager     # Install software
```

---

## Related Documentation

### Project Documentation
- **Project README:** `/projects/06-homelab/PRJ-HOME-003/README.md`
- **PRJ-HOME-002 RUNBOOK:** For Proxmox operations
- **PRJ-HOME-001 RUNBOOK:** For network configuration

### External Resources
- [Kali Linux Documentation](https://www.kali.org/docs/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Puppy Linux Forum](https://forum.puppylinux.com/)
- [SlackoPuppy Specific Docs](http://murga-linux.com/puppy/)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2025-11-10 | Initial draft runbook (project in planning) | Samuel Jackson |

---

**Project Status:** 🔵 Planned
**Next Milestone:** Phase 2 - Deployment
**Review Date:** TBD (when project moves to active phase)

---

> **Note:** This runbook is a living document and will be updated as the project progresses through planning, deployment, and operational phases. Sections marked as "TBD" or "Planned" will be filled in during project execution.

*Last Updated: November 10, 2025*
