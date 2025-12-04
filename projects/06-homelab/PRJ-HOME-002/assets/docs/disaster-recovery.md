# Disaster Recovery Plan

This document captures disaster recovery procedures for PRJ-HOME-002, covering node loss, storage failure, and full-site rebuild.

## Objectives
- **RTO:**
  - P0 services (FreeIPA, Nginx, Pi-hole): 60 minutes
  - P1 services (Wiki.js, Home Assistant, Immich, PostgreSQL): 4 hours
  - P2 services (monitoring, logging): 24 hours
- **RPO:**
  - P0: 24 hours
  - P1: 24 hours
  - P2: 48 hours

## Recovery Tiers
1. **Host Failure (Single Proxmox Node):**
   - Automatic VM evacuation via HA group; live migrate to healthy nodes.
   - Validate quorum and Ceph health (`ceph status`).
   - Confirm networking intact on VLAN 40 bridges.

2. **Storage Failure (Ceph Pool Degraded):**
   - Place pool in `noout` only if performing maintenance; otherwise allow rebalance.
   - Verify replication factor of 3; ensure minimum 2 OSDs remain up before maintenance.
   - Monitor recovery with `ceph -s` and Grafana Ceph dashboards.

3. **Service Failure (VM Corruption):**
   - Restore latest VM backup from Proxmox Backup Server using `backup-config.json` schedule.
   - Use incremental restore to reduce transfer time; prefer restoring to new VM ID to preserve chain.
   - Run post-restore Ansible playbooks: `maintenance-updates.yml`, `deploy-services.yml`.

4. **Site Failure (Datacenter Loss):**
   - Restore TrueNAS replication target (remote NAS) to new hardware.
   - Rebuild Proxmox cluster using `proxmox/cluster.conf` and `network-interfaces` as baseline.
   - Re-import PBS datastore and restore priority services in order: Nginx → FreeIPA → Pi-hole → PostgreSQL → app VMs.

## Backup Validation
- **Daily:** Review PBS dashboard and `assets/logs/backup-rotation.log` for job success.
- **Weekly:** Perform test restore of a non-critical VM (e.g., Wiki.js staging) into isolated VLAN.
- **Quarterly:** Full DR drill using TrueNAS replication target; document timing in `docs/lessons-learned.md`.

## Communication Plan
- Record incidents and remediation steps in the operations log.
- Notify stakeholders via out-of-band channel (Signal/Matrix) if primary services down.
- Track follow-ups in RUNBOOK `PROXMOX_CLUSTER_OPERATIONS.md`.

## Quick Reference Commands
```bash
# Check Proxmox HA status
ha-manager status

# List and verify backups
proxmox-backup-manager status
proxmox-backup-manager prune --dry-run --ns root/pve --all

# Restore VM from PBS
proxmox-backup-client restore vm/110/2024-11-06T02:00:00Z drive-virtio0.raw --target /var/lib/vz/images/210/

# Verify Ceph health
ceph status
ceph osd tree

# Validate TrueNAS replication
ssh truenas "zfs list -t snapshot | grep replication" 
```

## DR Runbook Snippets
- Ensure DNS overrides are ready for emergency cutover (Cloudflare proxied records with low TTL = 60s).
- Keep offline copy of public SSH keys and inventory at `assets/recovery/` with sanitized placeholders.
- Maintain USB installer for Proxmox/TrueNAS in `assets/recovery/disaster-recovery-plan.md` appendix.
