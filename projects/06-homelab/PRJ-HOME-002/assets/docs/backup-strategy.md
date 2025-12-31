# Backup Strategy

This document summarizes the backup approach for PRJ-HOME-002, aligning with the 3-2-1 rule and PBS verification settings.

## Targets & Cadence
- **Proxmox Backup Server (Primary):** Daily incremental backups of all VMs and containers with weekly fulls.
- **TrueNAS (Secondary):** Weekly ZFS snapshots replicated to offsite storage; NFS share hosts PBS datastore copies.
- **Offsite rsync (Tertiary):** Weekly sync of PBS datastore to encrypted remote storage.

## Retention
- **PBS:** 7 daily, 4 weekly, 12 monthly (configured in `assets/proxmox/backup-config.json`).
- **TrueNAS:** Daily snapshots retained for 14 days; weekly snapshots retained for 12 weeks.
- **Logs:** Retention defined in `assets/docs/logging-and-retention.md` to align with incident response requirements.

## Verification & Testing
- Nightly verification tasks enabled in PBS to validate chunk integrity.
- Quarterly restore tests logged in `assets/logs/backup-job-log.md` with RTO/RPO measurements.
- Application-level checks (Wiki.js, Home Assistant, Immich) triggered after restore to confirm data completeness.

## Responsibilities
- **Backup Operator:** Owns PBS job scheduling and verification review.
- **Storage Admin:** Maintains TrueNAS snapshot replication health and available capacity.
- **Service Owners:** Validate restored application functionality and update runbooks if drift is detected.
