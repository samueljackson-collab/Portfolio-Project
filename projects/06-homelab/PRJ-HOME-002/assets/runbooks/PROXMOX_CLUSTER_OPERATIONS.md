# Proxmox Cluster Operations Runbook

**Version:** 1.0
**Last Updated:** November 10, 2025
**Maintainer:** Samuel Jackson

---

## Table of Contents

1. [Overview](#overview)
2. [Cluster Management](#cluster-management)
3. [VM Operations](#vm-operations)
4. [High Availability](#high-availability)
5. [Performance Monitoring](#performance-monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Emergency Procedures](#emergency-procedures)

---

## Overview

### Cluster Architecture

- **Nodes:** 3 (proxmox-01, proxmox-02, proxmox-03)
- **IP Addresses:** 192.168.40.10-12
- **Cluster Name:** homelab-cluster
- **Quorum:** 3 votes required (2 for quorum)
- **HA Services:** FreeIPA, Pi-hole, Nginx, Syslog

### Access Points

| Component | URL/IP | Credentials |
|-----------|--------|-------------|
| Node 1 WebGUI | <https://192.168.40.10:8006> | Password Manager |
| Node 2 WebGUI | <https://192.168.40.11:8006> | Password Manager |
| Node 3 WebGUI | <https://192.168.40.12:8006> | Password Manager |
| Cluster View | Any node URL | Same credentials |

### Service Level Objectives

- **Availability:** 99.95% (HA services)
- **RTO:** 1 hour (critical services), 4 hours (standard)
- **RPO:** 24 hours (daily backups)

---

## Cluster Management

### Check Cluster Status

#### Via WebGUI

```
1. Login to any node
2. Navigate to: Datacenter → Summary
3. Verify:
   - All nodes show "online" (green)
   - Quorum: Shows "X/3 nodes online"
   - No warnings or errors
```

#### Via CLI

```bash
# SSH to any node
ssh root@192.168.40.10

# Check cluster status
pvecm status
# Expected output:
# Cluster information
#   Nodes: 3
#   Expected votes: 3
#   Total votes: 3
#   Quorum: 2

# Check node list
pvecm nodes
# All nodes should show "online"

# Check cluster config
cat /etc/pve/corosync.conf
```

### Monitor Cluster Health

#### Daily Health Check

```bash
# On any cluster node
ssh root@192.168.40.10

# 1. Check cluster membership
pvecm status

# 2. Check all VMs running
qm list
# Note any stopped VMs that should be running

# 3. Check resource usage
pvesh get /cluster/resources
# Look for high CPU/RAM usage (>90%)

# 4. Check replication status (if configured)
pvesh get /cluster/replication

# 5. Check for updates
pveversion -v
apt update && apt list --upgradable
```

#### Weekly Health Check

```bash
# Check Ceph cluster health (if using Ceph)
ceph status
# Expected: "HEALTH_OK"

# Check storage usage
pvesm status
# Verify no storage >85% full

# Review system logs
journalctl -p err -since "1 week ago"
```

### Add New Node to Cluster

**Prerequisites:**

- Proxmox VE installed on new node
- Network connectivity to cluster
- Same Proxmox version as existing nodes

**Procedure:**

```bash
# On existing cluster node (e.g., proxmox-01):
ssh root@192.168.40.10

# Get cluster join information
pvecm add <NEW_NODE_IP>
# Copy the displayed join command

# On new node:
ssh root@<NEW_NODE_IP>

# Join cluster (use command from above)
pvecm add 192.168.40.10
# Enter cluster node password when prompted

# Verify on existing node:
pvecm nodes
# New node should appear in list

# Expected time: 5-10 minutes
```

### Remove Node from Cluster

**Use Case:** Decommissioning node, hardware failure

```bash
# On node to be removed, migrate all VMs first
# See VM Operations → Live Migration

# On remaining cluster node:
ssh root@192.168.40.10

# Remove node from cluster
pvecm delnode <NODE_NAME>
# Example: pvecm delnode proxmox-03

# Verify removal
pvecm nodes
# Removed node should not appear

# Clean up on removed node (if accessible):
ssh root@<REMOVED_NODE_IP>
systemctl stop pve-cluster
systemctl stop corosync
pmxcfs -l  # Restart local cluster filesystem
```

---

## VM Operations

### Create New VM

#### Via WebGUI

```
1. Right-click node → Create VM
2. General:
   - Node: Select target node
   - VM ID: Next available (100+)
   - Name: Descriptive name (e.g., web-server-01)
3. OS:
   - ISO: Select from local storage
   - Type: Linux 5.x - 2.6 Kernel
4. System:
   - BIOS: OVMF (UEFI) or SeaBIOS (Legacy)
   - SCSI Controller: VirtIO SCSI
   - Qemu Agent: ✓ (checked)
5. Disks:
   - Storage: ceph-rbd (for HA) or local-lvm
   - Size: As needed (e.g., 32 GB)
   - Cache: No cache
6. CPU:
   - Cores: 2 (minimum)
   - Type: host
7. Memory:
   - Memory: 2048 MB (minimum)
   - Ballooning: Enabled
8. Network:
   - Bridge: vmbr0
   - VLAN Tag: 40 (servers)
   - Model: VirtIO
9. Confirm → Start after created: ✓
```

#### Via CLI

```bash
# SSH to target node
ssh root@192.168.40.10

# Create VM from template (recommended)
qm clone 9000 101 --name web-server-01 --full
# 9000 = template ID, 101 = new VM ID

# Or create from scratch
qm create 101 \
  --name web-server-01 \
  --memory 2048 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0,tag=40 \
  --scsi0 ceph-rbd:32 \
  --boot order=scsi0 \
  --agent 1 \
  --onboot 1

# Start VM
qm start 101
```

### VM Lifecycle Management

#### Start VM

```bash
# Via CLI
ssh root@192.168.40.10
qm start <VMID>

# Via WebGUI
# Select VM → Start
```

#### Stop VM (Graceful Shutdown)

```bash
# Via CLI
qm shutdown <VMID>
# Waits for guest OS to shutdown cleanly

# Force stop after 60 seconds
qm shutdown <VMID> --timeout 60

# Via WebGUI
# Select VM → Shutdown
```

#### Stop VM (Immediate)

```bash
# Via CLI (use only if shutdown hangs)
qm stop <VMID>

# Via WebGUI
# Select VM → Stop
```

#### Restart VM

```bash
# Via CLI
qm reboot <VMID>  # Graceful restart
qm reset <VMID>   # Hard reset

# Via WebGUI
# Select VM → Reboot
```

#### Delete VM

```bash
# Via CLI
# 1. Stop VM first
qm stop <VMID>

# 2. Delete VM and disks
qm destroy <VMID> --purge

# Via WebGUI
# Select VM → More → Remove
# Check "Purge" to delete disks
```

### Live Migration

**Use Case:** Move running VM between nodes without downtime

**Prerequisites:**

- VM disk on shared storage (Ceph)
- Network connectivity between nodes
- Sufficient resources on target node

**Procedure:**

```bash
# Via CLI
ssh root@192.168.40.10

# Check if VM can be migrated
qm migrate <VMID> <TARGET_NODE> --online --check

# Perform migration
qm migrate <VMID> <TARGET_NODE> --online
# Example: qm migrate 101 proxmox-02 --online

# Monitor migration progress
qm status <VMID>

# Via WebGUI
# Select VM → Migrate
# Target node: proxmox-02
# Mode: Online
# Click: Migrate

# Expected downtime: 0 seconds (live)
# Expected time: 1-5 minutes depending on VM memory
```

### Offline Migration

**Use Case:** Move stopped VM or VM on local storage

```bash
# Stop VM first
qm shutdown <VMID>

# Migrate with storage
qm migrate <VMID> <TARGET_NODE> --targetstorage <STORAGE>
# Example: qm migrate 101 proxmox-02 --targetstorage local-lvm

# Expected time: 5-30 minutes depending on disk size
```

### VM Snapshots

#### Create Snapshot

```bash
# Via CLI
ssh root@192.168.40.10

# Create snapshot
qm snapshot <VMID> <SNAPSHOT_NAME> --description "Before update"
# Example: qm snapshot 101 pre-update --description "Before kernel update"

# Include RAM (for running VMs)
qm snapshot <VMID> <SNAPSHOT_NAME> --vmstate

# Via WebGUI
# Select VM → Snapshots → Take Snapshot
```

#### List Snapshots

```bash
# Via CLI
qm listsnapshot <VMID>

# Via WebGUI
# Select VM → Snapshots
```

#### Restore Snapshot

```bash
# Via CLI (stop VM first)
qm stop <VMID>
qm rollback <VMID> <SNAPSHOT_NAME>
qm start <VMID>

# Via WebGUI
# Select VM → Snapshots
# Select snapshot → Rollback
```

#### Delete Snapshot

```bash
# Via CLI
qm delsnapshot <VMID> <SNAPSHOT_NAME>

# Via WebGUI
# Select VM → Snapshots
# Select snapshot → Remove
```

---

## High Availability

### HA Configuration

#### Enable HA for VM

```bash
# Via CLI
ssh root@192.168.40.10

# Add VM to HA
ha-manager add vm:<VMID>
# Example: ha-manager add vm:101

# Set HA policy
ha-manager set vm:<VMID> --state started --max_restart 2 --max_relocate 2

# Via WebGUI
# Datacenter → HA → Add
# Resource: VM ID
# Max restart: 2
# Max relocate: 2
```

#### Check HA Status

```bash
# Via CLI
ha-manager status
# Shows all HA resources and their state

# Check HA configuration
ha-manager config

# Via WebGUI
# Datacenter → HA → Resources
```

#### Disable HA for VM

```bash
# Via CLI
ha-manager remove vm:<VMID>

# Via WebGUI
# Datacenter → HA → Resources
# Select VM → Remove
```

### HA Groups

**Use Case:** Define which nodes can run specific VMs

```bash
# Create HA group
ha-manager groupadd production --nodes "proxmox-01,proxmox-02" --nofailback

# Assign VM to group
ha-manager set vm:<VMID> --group production

# List groups
ha-manager groupconfig
```

### Testing HA Failover

**Scenario:** Simulate node failure

```bash
# On node running HA VM:
ssh root@192.168.40.10

# Simulate crash (use with caution!)
echo b > /proc/sysrq-trigger
# OR stop cluster services:
systemctl stop corosync
systemctl stop pve-cluster

# Expected behavior:
# 1. Cluster detects node failure (30-60 seconds)
# 2. HA manager fences failed node
# 3. VM starts on another node (2-5 minutes)

# Verify on remaining node:
ssh root@192.168.40.11
ha-manager status
qm list  # Check VM location

# Expected total downtime: 2-5 minutes
```

### Watchdog Configuration

**Purpose:** Automatic node fencing on hardware hang

```bash
# Check if watchdog is loaded
lsmod | grep iTCO_wdt

# If not loaded:
modprobe iTCO_wdt
echo "iTCO_wdt" >> /etc/modules

# Configure in cluster config
pvesh set /cluster/ha/groups/<GROUP> --watchdog-action reboot

# Test watchdog (WARNING: This will reboot the node!)
echo 1 > /proc/sys/kernel/sysrq
echo c > /proc/sysrq-trigger
```

---

## Performance Monitoring

### Resource Usage

#### Check Node Resources

```bash
# CPU, memory, disk usage
pvesh get /nodes/<NODE>/status

# Detailed metrics
pvesh get /nodes/<NODE>/rrddata?timeframe=hour

# Via WebGUI
# Select node → Summary
# View graphs for CPU, Memory, Network, Disk
```

#### Check VM Resources

```bash
# All VMs on node
qm list

# Specific VM status
qm status <VMID> --verbose

# VM resource usage
pvesh get /nodes/<NODE>/qemu/<VMID>/rrddata?timeframe=hour
```

### Storage Performance

#### Check Ceph Performance

```bash
# Ceph cluster status
ceph status

# OSD performance
ceph osd perf

# Pool statistics
ceph df

# Slow operations (if any)
ceph health detail
```

#### Storage Latency Test

```bash
# Write test (on VM)
dd if=/dev/zero of=/tmp/test.img bs=1G count=1 oflag=dsync

# Read test
dd if=/tmp/test.img of=/dev/null bs=1G count=1

# IOPS test (requires fio)
fio --name=random-read --ioengine=libaio --rw=randread --bs=4k --size=1G --numjobs=1 --iodepth=32
```

### Network Performance

```bash
# Between nodes (on node 1)
iperf3 -s

# On node 2
iperf3 -c 192.168.40.10

# Expected: 900+ Mbps on 1 Gbps link
# Expected: 9+ Gbps on 10 Gbps link
```

---

## Troubleshooting

### Cluster Issues

#### Node Shows "Unknown" Status

```bash
# On affected node
systemctl status pve-cluster
systemctl status corosync

# If stopped, restart:
systemctl restart pve-cluster
systemctl restart corosync

# Check cluster communication
pvecm status
```

#### Quorum Lost

```bash
# Check quorum status
pvecm status
# If expected_votes != total_votes, quorum may be lost

# On surviving nodes:
pvecm expected 2  # Set to number of surviving nodes
# WARNING: Use only if you understand the implications

# Or reset quorum device
rm /var/lib/corosync/qdisk
systemctl restart corosync
```

#### Split Brain Prevention

```bash
# Ensure proper quorum settings
pvecm status
# Expected votes should be odd number (3, 5, 7)

# Add QDevice for even number of nodes
pvecm qdevice setup <QDEVICE_IP>
```

### VM Issues

#### VM Won't Start

```bash
# Check VM config
qm config <VMID>

# Check for locks
qm unlock <VMID>

# Check disk availability
pvesm list <STORAGE>

# Check logs
journalctl -u qemu-server@<VMID> -n 50
```

#### VM Performance Issues

```bash
# Check CPU steal time (inside VM)
top
# High "st" value = overcommitted host

# Check disk I/O wait (inside VM)
iostat -x 1
# High "await" = slow storage

# Check network (inside VM)
iftop
# Identify bandwidth hogs

# On host:
qm monitor <VMID>
# Type: info status, info blockstats
```

#### VM Disk Full

```bash
# On host, resize disk
qm resize <VMID> scsi0 +10G

# Inside VM, extend filesystem
# For ext4:
df -h  # Note partition (e.g., /dev/sda1)
growpart /dev/sda 1
resize2fs /dev/sda1

# For XFS:
xfs_growfs /
```

### Storage Issues

#### Ceph HEALTH_WARN

```bash
# Check detailed health
ceph health detail

# Common issues:
# 1. Clock skew
systemctl restart chronyd

# 2. OSDs down
ceph osd tree  # Find down OSDs
systemctl start ceph-osd@<OSD_ID>

# 3. PGs inactive
ceph pg stat
ceph pg dump  # Find stuck PGs
```

#### Storage Unavailable

```bash
# Check storage status
pvesm status

# For NFS:
showmount -e <NFS_SERVER_IP>
mount -t nfs <NFS_SERVER>:/path /mnt/test

# For iSCSI:
iscsiadm -m node -l  # Login to targets
iscsiadm -m session  # Show active sessions
```

---

## Emergency Procedures

### Node Failure (Unplanned)

**Scenario:** Node crashes or becomes unresponsive

**Immediate Actions:**

1. **Don't Panic** - HA will handle automatic failover
2. **Verify HA Status** - Check if VMs migrated automatically
3. **Monitor Other Nodes** - Ensure they're handling extra load
4. **Document** - Note time and symptoms

**Detailed Response:**

```bash
# On surviving nodes:
ssh root@192.168.40.11

# Check cluster status
pvecm status
# Note: Missing node will show "offline"

# Check HA resource status
ha-manager status
# HA VMs should be "started" on other nodes

# Check non-HA VMs from failed node
qm list  # Compare with inventory

# Manually start critical non-HA VMs
qm start <VMID>

# Expected total time: 5-10 minutes
```

**Recovery:**

```bash
# Once failed node is back online:
ssh root@192.168.40.10

# Verify cluster rejoined
pvecm status

# Check for any issues
journalctl -p err -since "1 hour ago"

# Rebalance VMs if needed
# (Migrate VMs back to recovered node)
```

### Ceph Failure (Storage Down)

**Scenario:** Ceph cluster unhealthy, VMs can't access storage

**Critical Assessment:**

```bash
# Check Ceph status
ceph status
# Note HEALTH_ERR vs HEALTH_WARN

# Check OSD status
ceph osd tree
# Count: How many OSDs are down?

# Check data availability
ceph pg stat
# Note: Any PGs not "active+clean"?
```

**Response Based on Severity:**

**Scenario A: 1 OSD Down (Minor)**

```bash
# Single OSD failure, data still available (3-way replication)
# Action: Monitor, Ceph will self-heal

# Check recovery progress
ceph -w

# If OSD doesn't recover automatically:
systemctl start ceph-osd@<OSD_ID>

# Expected recovery time: 10-60 minutes
```

**Scenario B: 2+ OSDs Down (Critical)**

```bash
# Data may be unavailable
# Action: Emergency recovery

# 1. Stop all non-critical VMs to reduce I/O
qm list | grep running | grep -v "101\|102\|103" | awk '{print $1}' | xargs -I {} qm stop {}

# 2. Attempt to start down OSDs
for osd in $(ceph osd tree | grep down | awk '{print $1}'); do
  systemctl start ceph-osd@$osd
done

# 3. If OSDs won't start, may need to restore from backup
# See BACKUP_RECOVERY_RUNBOOK.md
```

### Complete Cluster Failure

**Scenario:** All nodes down (power outage, network failure)

**Recovery Procedure:**

```bash
# 1. Power on nodes in order (wait for each to fully boot)
# Node 1 (proxmox-01): Primary
# Node 2 (proxmox-02): Secondary
# Node 3 (proxmox-03): Tertiary

# 2. On first node, verify cluster forms
ssh root@192.168.40.10
pvecm status
# Wait for quorum

# 3. Check Ceph if used
ceph status
# Wait for HEALTH_OK (may take 10-30 minutes)

# 4. Start critical HA services (should auto-start)
ha-manager status

# 5. Start remaining VMs manually or wait for auto-start
qm list
# For each stopped VM that should be running:
qm start <VMID>

# Expected total recovery time: 30-60 minutes
```

---

## Maintenance Windows

### Node Maintenance (Planned)

**Scenario:** Apply updates, hardware maintenance

**Procedure:**

```bash
# 1. Migrate all VMs off node
ssh root@192.168.40.10

# List VMs on this node
qm list

# Migrate each VM
for vmid in $(qm list | grep running | awk '{print $1}'); do
  qm migrate $vmid proxmox-02 --online
done

# 2. Verify no VMs running
qm list

# 3. Put node in maintenance mode (prevents new VMs)
# Via WebGUI: Select node → More → Maintenance

# 4. Perform maintenance (updates, hardware work)
apt update && apt upgrade -y
# Or: shutdown for hardware work

# 5. Reboot if needed
reboot

# 6. After node returns, exit maintenance mode
# Via WebGUI: Select node → More → Exit Maintenance

# 7. Optionally migrate VMs back
# (Or leave them balanced across nodes)

# Expected downtime: 0 for VMs, 15-60 minutes for node
```

---

## Best Practices

### VM Management

- Always use cloud-init templates for new VMs
- Enable QEMU guest agent on all VMs
- Use descriptive VM names (purpose-role-number)
- Set appropriate start order for dependencies
- Enable autostart for critical services

### Storage

- Use Ceph for HA VMs (shared storage)
- Use local storage for non-HA VMs (better performance)
- Monitor storage usage, keep below 80%
- Regular scrubs for data integrity

### Backups

- Daily backups of all production VMs
- Test restore procedures quarterly
- Store backups on separate storage
- Offsite backups for critical data

### Updates

- Review release notes before updating
- Test updates on non-production node first
- Update one node at a time
- Wait 24 hours between node updates

---

## Useful Commands Reference

```bash
# Cluster
pvecm status              # Cluster status
pvecm nodes               # List nodes
pvecm expected <N>        # Set expected votes

# VMs
qm list                   # List all VMs
qm start <VMID>           # Start VM
qm shutdown <VMID>        # Stop VM gracefully
qm stop <VMID>            # Force stop VM
qm status <VMID>          # VM status
qm migrate <VMID> <NODE>  # Migrate VM

# HA
ha-manager status         # HA status
ha-manager add vm:<VMID>  # Add VM to HA
ha-manager remove vm:<VMID>  # Remove from HA

# Storage
pvesm status              # Storage status
pvesm list <STORAGE>      # List storage contents

# Ceph
ceph status               # Cluster health
ceph osd tree             # OSD hierarchy
ceph df                   # Storage usage
ceph health detail        # Detailed health

# Logs
journalctl -u pve-cluster  # Cluster logs
journalctl -u corosync     # Corosync logs
journalctl -u qemu-server@<VMID>  # VM logs
```

---

**End of Runbook**

*Last Reviewed: November 10, 2025*
*Next Review: February 10, 2026 (Quarterly)*
