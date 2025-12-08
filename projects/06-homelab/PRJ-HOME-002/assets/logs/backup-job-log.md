# Backup Job Log (Sanitized)

| Date       | Job ID        | Scope                 | Status  | Duration | Notes                                    |
|------------|---------------|-----------------------|---------|----------|------------------------------------------|
| 2025-11-01 | pbs-full-001  | All HA VMs            | Success | 00:27:14 | Verification passed; dedupe ratio 1.8x.  |
| 2025-11-02 | pbs-inc-042   | Daily incrementals    | Success | 00:06:03 | No changes detected on FreeIPA.          |
| 2025-11-03 | pbs-inc-043   | Daily incrementals    | Warning | 00:08:55 | Immich media share temporarily read-only |
| 2025-11-04 | pbs-inc-044   | Daily incrementals    | Success | 00:06:44 | Postgres WAL archive pruned.             |
| 2025-11-05 | pbs-verify-10 | Weekly verification   | Success | 00:12:11 | All chunks validated.                    |

- Logs pulled from PBS and mirrored to TrueNAS `backups/logs/` share for retention.
- Alerting thresholds: job failures page immediately; warnings create tickets for follow-up.
