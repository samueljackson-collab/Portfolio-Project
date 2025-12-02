# Disaster Recovery Playbook

This playbook aligns with the broader disaster recovery plan in `assets/recovery/disaster-recovery-plan.md` and focuses on executable steps for the virtualization platform and core services.

## Objectives
- **RTO:** 1 hour for P0 services (FreeIPA, Pi-hole, Nginx Proxy Manager, Syslog)
- **RPO:** 24 hours for P0/P1 workloads
- **Scope:** Proxmox cluster, TrueNAS storage, PBS backups, and application containers

## Recovery Scenarios
1. **Single Node Failure**
   - Confirm quorum and HA status: `pvecm status` and `ha-manager status`.
   - Evacuate workloads if not already migrated: `ha-manager migrate <vmid> <target-node>`.
   - Replace failed node, reapply `assets/proxmox/network-interfaces`, and rejoin the cluster.
2. **Storage Pool Degradation**
   - Check Ceph health: `ceph health detail`.
   - If OSD failed, replace disk and run `ceph-volume lvm activate --all` followed by `ceph osd crush reweight` after rebuild.
   - Validate PBS backups remain intact; prepare TrueNAS NFS/iSCSI as temporary datastore if needed.
3. **Control Plane Loss (2+ nodes)**
   - Promote surviving node by re-establishing quorum via `pvecm expected 1` (temporary) and isolate failed hardware.
   - Restore from PBS using latest verified snapshots; prioritize P0 VMs.
   - Rehydrate monitoring targets and proxy entries using `assets/configs/nginx-proxy-manager/proxy-hosts.yml`.
4. **Full Site Rebuild**
   - Deploy fresh Proxmox cluster and TrueNAS per `assets/docs/deployment.md`.
   - Import PBS datastore, restore VMs starting with FreeIPA and DNS, then proxy and application stack.
   - Apply Ansible roles to reconfigure services and validate DNS/HTTPS endpoints.

## Evidence & Testing
- **Quarterly DR Tests:** Results logged in `assets/logs/backup-job-log.md` with pass/fail outcomes.
- **Restore Drills:** Documented in `assets/recovery/recovery-procedures/` with timestamps and observed RTO/RPO.
- **Configuration Integrity:** Hash and version references recorded in `assets/proxmox/backup-config.json` and monitoring dashboards.

## Communication & Access
- Status updates via internal chat channel and status page served through Nginx.
- Access restored using break-glass credentials stored offline; rotate credentials after DR completion.
- Provide stakeholders with service availability ETA and restoration order.
