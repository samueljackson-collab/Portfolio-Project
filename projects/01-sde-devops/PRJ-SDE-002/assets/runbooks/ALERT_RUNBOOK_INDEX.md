# Alert Runbook Index

| Alert | Runbook | Notes |
|-------|---------|-------|
| HostDown | [Operational Runbook](./OPERATIONAL_RUNBOOK.md#alert-hostdown) | Verify host reachability, exporter status, and power state. |
| HighCPUUsage | [Operational Runbook](./OPERATIONAL_RUNBOOK.md#alert-highcpuusage) | Use same triage path with CPU-specific checks. |
| BackupJobFailed | [Restore Checklist](../pbs/pbs-restore-checklist.md) | Validate PBS job state, rerun verification script, and confirm retention health. |
| HTTPServiceDown | [Incident Response Playbook](./PRODUCTION_RUNBOOKS_INCIDENT_RESPONSE.md#runbook-service-down) | Includes blackbox probe validation and dependency checks. |
| DiskSpaceWarning | [Operational Runbook](./OPERATIONAL_RUNBOOK.md#alert-diskspacelow) | Expand filesystem, prune logs, or adjust retention based on saturation trend. |

All links reference sanitized documentation within this repository to avoid exposing private runbook URLs.
