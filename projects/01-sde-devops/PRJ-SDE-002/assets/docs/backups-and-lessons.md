# Backup Operations, Retention, and Lessons Learned

## Proxmox Backup Server (PBS) Jobs
- **Nightly VM backups (02:00 UTC):** Incremental, verified with checksum comparison and restore simulation using a disposable VM ID.
- **Weekly config snapshots (Sundays):** Captures `/etc` for Prometheus, Grafana, Loki, Alertmanager, and Promtail.
- **Monthly restoration drill:** Full restore rehearsal into an isolated network to validate boot, metrics ingestion, and alert clearance.

### Retention Strategy
- Daily: keep 7
- Weekly: keep 4
- Monthly: keep 3
- Auto-pruning is validated with the `pbs-retention-report.json` artifact.

### Evidence Artifacts
- [`pbs-job-manifest.yml`](../pbs/pbs-job-manifest.yml) — declarative job schedule with labels and retention.
- [`pbs-retention-report.json`](../pbs/pbs-retention-report.json) — sanitized sample report showing retention compliance.
- [`pbs-restore-checklist.md`](../pbs/pbs-restore-checklist.md) — step-by-step validation procedure.

## Lessons Learned
1. **Verify after every run:** Automated verification caught intermittent snapshot corruption caused by transient storage latency.
2. **Track retention drift:** Surfacing retention status in Grafana prevents silent storage overrun.
3. **Practice restores:** Monthly drills shortened recovery from 45 minutes to 18 minutes by rehearsing networking and credential steps.
4. **Keep configs versioned:** Prometheus/Alertmanager/Loki/Promtail configs now live in git to make rollback trivial and auditable.

## Sanitization and Sharing
All PBS artifacts remove real hostnames, datastore IDs, and user names. Timestamps, job IDs, and sizes are sample values intended for portfolio demonstration only.
