# TrueNAS Configuration Summary

Sanitized TrueNAS configuration overview for PRJ-HOME-002 storage services.

## System Profile
- **Appliance:** TrueNAS CORE (virtualized)
- **Primary Pool:** `tank`
- **Cache:** L2ARC enabled for metadata-heavy workloads
- **Scrub Schedule:** Weekly on Sundays at 02:30
- **SMART Tests:** Short daily, long weekly

## Datasets
| Dataset | Purpose | Snapshot Policy | Replication |
| --- | --- | --- | --- |
| `tank/proxmox` | VM backups, templates | Daily (14 days) | Weekly to offsite
| `tank/media` | Immich library | Daily (30 days) | Weekly to offsite
| `tank/docs` | Wiki.js storage | Daily (30 days) | Weekly to offsite
| `tank/iso` | ISO images | Weekly (4 weeks) | Monthly to offsite

## Shares & Services
- **NFS:** `tank/proxmox` exported to Proxmox nodes (read/write).
- **SMB:** `tank/media` shared to admin workstation (read/write).
- **iSCSI:** Dedicated zvol for high-performance VM storage (lab testing only).

## Replication Tasks
- **Target:** `truenas-dr.example.internal`
- **Method:** SSH with key-based auth, encrypted stream
- **Schedule:** Weekly Sundays at 03:00
- **Retention:** 12 weekly snapshots on target

## Alerts & Monitoring
- TrueNAS alerts forwarded to centralized syslog (`192.168.40.30`).
- Prometheus node exporter installed for storage metrics.
