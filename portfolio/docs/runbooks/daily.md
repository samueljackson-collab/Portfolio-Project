# Daily Operations Runbook

1. **Check CI Pipelines**
   - Review the latest GitHub Actions runs for lint/test/build stages.
   - Investigate failures immediately and triage to the appropriate owner.
2. **Monitor Service Health**
   - Load observability dashboards (`docs/observability/*.json`) into Grafana or the preferred tool.
   - Verify request latency, error rates, and infrastructure metrics.
3. **Validate Backups**
   - Confirm that the nightly database backup completed successfully.
   - Ensure content export artifacts exist and are timestamped.
