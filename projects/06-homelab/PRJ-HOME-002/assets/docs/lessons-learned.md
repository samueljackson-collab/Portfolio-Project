# Lessons Learned

Notes captured during the build-out and steady-state operation of PRJ-HOME-002.

## Architecture
- **Ceph + TrueNAS balance**: Keeping performance workloads on Ceph and archival data on TrueNAS avoided contention and improved backup throughput.
- **Dedicated management VLAN**: Isolating Proxmox API and hypervisor management reduced noise on the storage network and simplified firewall policies.

## Operations
- **Immutable templates**: Standardizing on a single hardened cloud-init template cut onboarding time for new services by 30% and reduced configuration drift.
- **Runbooks as code**: Treating runbooks in `assets/runbooks/` as versioned code improved review quality and ensured reproducible maintenance windows.
- **Alert tuning**: Initial monitoring generated noisy alerts; adjusting Prometheus thresholds and using Alertmanager inhibition rules stabilized on-call load.

## Security & Compliance
- **Centralized CA**: Having FreeIPA issue certificates for internal services simplified TLS for Nginx Proxy Manager and prevented mismatched SAN errors.
- **Audit trails**: Shipping Proxmox and TrueNAS logs to Rsyslog with retention enforced in `assets/docs/logging-and-retention.md` provided clear incident timelines.

## Reliability
- **PBS verification**: Enabling backup verification in `assets/proxmox/backup-config.json` surfaced early media errors and prevented failed restores.
- **DR drills**: Practicing quarterly restore scenarios reduced the recovery timeline below the 1-hour RTO target and highlighted documentation gaps quickly.
