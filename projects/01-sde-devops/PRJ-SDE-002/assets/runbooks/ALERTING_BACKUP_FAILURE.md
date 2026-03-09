# Runbook: Backup Job / Retention Failures (PBS)

**Alert Names:** `PBSBackupFailure`, `PBSRetentionDrift`, `PBSRepositoryCapacityRisk`  
**Severity:** Warning → escalates to Critical if consecutive failures > 3 or capacity risk > 85%  
**Dashboards:** Grafana "Backup & PBS Health"  
**Related Files:** `assets/pbs/pbs-jobs.yaml`, `assets/pbs/pbs-retention-policy.yaml`, `scripts/verify-pbs-backups.sh`

---

## When This Fires
- Backup task fails or completes with errors for two consecutive runs.
- Prune/retention task cannot enforce the configured keep policy.
- PBS datastore capacity projects <14 days remaining based on ingest rate.

## Immediate Actions
1. **Acknowledge in Alertmanager** to suppress duplicates (link from alert).
2. **Open Grafana dashboard** → Backup panel → filter datastore to `pbs-demo` to confirm scope.
3. **Check last job logs** on PBS UI (sanitized host placeholder: `https://pbs.example.internal:8007`).
4. **Run verification script** from the Prometheus host:
   ```bash
   ./scripts/verify-pbs-backups.sh --datastore pbs-demo --hours 24
   ```
5. **Validate retention config** matches repo policy:
   ```bash
   cat assets/pbs/pbs-retention-policy.yaml
   ```

## Diagnosis Checklist
- [ ] Network reachability between Proxmox and PBS (`ping pbs.example.internal`).
- [ ] Datastore free space >20% (`proxmox-backup-manager status`).
- [ ] Task log shows throttling or checksum errors.
- [ ] Recent Proxmox updates changed backup schedule owners/permissions.

## Resolution Paths
- **Space pressure:** Increase datastore size or temporarily reduce retention (e.g., keep-last 7 → 5) and schedule manual prune.
- **Checksum errors:** Re-run job with `--verify` and check storage backend SMART/health.
- **Scheduling drift:** Re-apply sanitized job config from `pbs-jobs.yaml` and restart scheduler.
- **Exporter metrics missing:** Restart pbs-exporter and ensure Prometheus scrape target matches placeholders.

## Verification
- [ ] Last backup task status is `OK` for two consecutive runs.
- [ ] Retention task enforces policy without `incomplete` flag.
- [ ] Alert resolved automatically in Alertmanager.
- [ ] Incident summary posted to #homelab-alerts with impact and actions.

## Preventative Follow-ups
- Add restore test to CI monthly using latest snapshot.
- Track datastore growth rate in Grafana; adjust retention when 30-day trend exceeds capacity forecast.
- Ensure `verify-pbs-backups.sh` is scheduled and alerting wired to backup receiver.
