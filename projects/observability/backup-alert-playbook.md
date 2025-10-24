# Backup Alert Playbook — `BackupJobFailed`

## Trigger
Prometheus alert fires when Borg backup job exits non-zero or reports duration exceeding 2× rolling average.

## Severity Levels
- **SEV2:** Backup failed for primary Proxmox cluster.
- **SEV3:** Backup warning for secondary services (Wiki.js, Immich).

## Response Steps
1. **Acknowledge Alert** in OpsGenie and record incident number in ticketing system.
2. **Check Job Logs**
   ```bash
   kubectl logs job/borg-backup-$(date +%Y%m%d) -n platform
   ```
3. **Validate Storage Target** — ensure Borg repository reachable and has free space.
4. **Re-run Job** if failure due to transient network issue:
   ```bash
   kubectl create job --from=cronjob/borg-backup manual-borg-$(date +%s)
   ```
5. **Escalate to Storage On-Call** if failure repeats or repository reports corruption.
6. **Post-Incident** — document root cause, attach log excerpts, update knowledge base.

## Communication Template
> Backup job for `<cluster>` failed at `<time>`. Initial findings: `<summary>`. Retrying job now and monitoring results.

## Preventive Actions
- Rotate Borg repo keys annually and store in sealed secrets.
- Run monthly restore drill to ensure data integrity.
