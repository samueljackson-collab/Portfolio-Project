# TrueNAS Backup Policies

## Objectives
- **RPO:** 24 hours for critical services, 72 hours for standard workloads
- **RTO:** 4 hours for core services, 24 hours for non-critical workloads
- **Retention:** 30 daily, 12 monthly, 3 yearly snapshots

## Backup Targets
- **Proxmox Backup Server (PBS):** Primary daily backups
- **TrueNAS ZFS Snapshots:** Hourly/daily snapshots for fast restores
- **Offsite Sync:** Weekly rsync to remote NAS (encrypted)

## Backup Schedule
| Workload | Frequency | Retention | Destination |
| --- | --- | --- | --- |
| Core services (FreeIPA, DNS, NTP) | Daily | 30 days | PBS + ZFS snapshot |
| Application VMs (Wiki.js, Immich) | Daily | 30 days | PBS + ZFS snapshot |
| Bulk media | Weekly | 12 weeks | ZFS snapshot + offsite |
| Configuration exports | Daily | 90 days | ZFS snapshot + offsite |

## Verification
- PBS verification job runs nightly at 02:00
- ZFS snapshot integrity validated weekly
- Quarterly restore test documented in `assets/recovery/recovery-procedures/`
