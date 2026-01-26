# Disaster Recovery Runbook

Step-by-step guide for restoring core services after a cluster-impacting incident.

## Scope
- Proxmox cluster recovery (node loss, storage failure)
- Core services: FreeIPA, Nginx Proxy Manager, Wiki.js, Home Assistant, Immich
- Backup sources: Proxmox Backup Server, TrueNAS replication target

## Preconditions
- Access to Proxmox host console or IPMI
- PBS datastore accessible (`pbs-core`)
- TrueNAS replication target online (optional)

## 1. Incident Triage
1. Confirm scope: node outage, storage outage, or full site impact.
2. Notify stakeholders and log incident ID in operations tracker.
3. Freeze automation changes (pause Ansible/Terraform pipelines).

## 2. Restore Proxmox Services
1. Power on remaining nodes and confirm quorum.
2. If quorum lost:
   - Boot the most recent node with `pvecm expected 1` (temporary).
   - Restore corosync configuration from `/etc/pve/corosync.conf` backup.
3. Validate storage:
   - Confirm Ceph health (`ceph -s`).
   - Confirm NFS/iSCSI mounts from TrueNAS.

## 3. Restore Critical Services (Priority Order)
1. **FreeIPA**
   - Restore VM from PBS snapshot `daily-core-services`.
   - Validate `ipa-healthcheck` and LDAP auth.
2. **Nginx Proxy Manager**
   - Restore VM from PBS snapshot.
   - Import proxy host config (see `assets/configs/nginx-proxy-manager/npm-config-summary.md`).
   - Confirm TLS certs and DNS resolution.
3. **Wiki.js**
   - Restore VM from PBS snapshot.
   - Validate database connectivity and page integrity.

## 4. Restore Standard Services
1. Home Assistant
2. Immich
3. Monitoring stack (Prometheus/Grafana/Loki)
4. Syslog and NTP services

## 5. Validation Checklist
- [ ] Core services reachable through NPM URLs
- [ ] DNS resolution intact on VLAN 40
- [ ] Backup schedules re-enabled
- [ ] Monitoring dashboards show healthy state

## 6. Post-Recovery Actions
1. Run the platform health-check script (see automation tooling documentation).
2. Document RTO/RPO results in `assets/logs/restore-test-results.md`.
3. Capture incident summary in operations log.
4. Schedule follow-up review for root cause analysis.

## Reference
- Disaster Recovery Plan document
- Detailed recovery procedures documentation
- Backup and restore job logs
