# Alert Runbooks (Condensed)

This quick reference links alert names to first-response steps. Full operational guidance remains in `OPERATIONAL_RUNBOOK.md`.

## HostDown (Critical)
- **Trigger:** `up == 0` for 2 minutes (any exporter target).
- **Dashboard:** `infrastructure-overview.json` → `Exporter Uptime` panel.
- **First steps:**
  1. Confirm synthetic probe status on the blackbox panel (rules out DNS/firewall).
  2. `ping <instance>` then `nc -zv <instance> 9100` from the Prometheus node.
  3. If reachable, restart exporter: `sudo systemctl restart node_exporter`.
- **Escalation:** Page on-call if outage >5 minutes.

## HighErrorRate (Critical)
- **Trigger:** `rate(http_requests_total{status=~"5.."}[5m])` exceeds 5% of traffic for 10 minutes.
- **Dashboard:** `application-metrics.json` → `Error Budget` + `Latency Heatmap` panels.
- **First steps:**
  1. Check recent deploy annotations in Grafana for correlating changes.
  2. Inspect service logs via `LogErrorRate` panel (Loki) filtered on `app="demo-api"`.
  3. Enable circuit breaker/rollback the latest release if error budget burn >1%/min.
- **Escalation:** Engage service owner if errors persist beyond 15 minutes.

## BackupJobFailed (Critical)
- **Trigger:** `proxmox_backup_job_last_status != 0` at job completion.
- **Dashboard:** `pbs-backups.json` → `Job Duration` and `Dedup Ratio` panels.
- **First steps:**
  1. Re-run `scripts/verify-pbs-backups.sh` in dry-run mode to confirm scope.
  2. Verify datastore free space and NFS connectivity; look for IO wait spikes on Prometheus disk panels.
  3. Retry the failed job with throttled bandwidth to avoid saturating the datastore.
- **Escalation:** Notify storage owner if two consecutive runs fail.

## LogErrorRate (Warning)
- **Trigger:** Loki error logs above 10/min with severity label `ERROR` for 10 minutes.
- **Dashboard:** `alert-operations.json` → `Log Noise` panel.
- **First steps:**
  1. Filter logs by `app` and `pod` labels to isolate noisy components.
  2. If noise comes from probes, adjust sampling in Promtail pipelines.
  3. Open a follow-up ticket for noisy-but-benign errors.

## DataStaleness (Warning)
- **Trigger:** Prometheus `up` scrape age >5 minutes for any monitored job.
- **Dashboard:** `infrastructure-overview.json` → `Scrape Freshness` panel.
- **First steps:**
  1. Check Prometheus TSDB headroom; run `promtool tsdb analyze` if ingestion stalls.
  2. Validate time sync on exporters (`timedatectl status`).
  3. Reduce scrape interval temporarily for flapping targets to confirm stability.
