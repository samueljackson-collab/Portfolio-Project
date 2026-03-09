---
title: PBS Backup Verification & Lessons Learned
description: - **Scope:** `pbs-demo` datastore, jobs `nightly-vm-backup`, `weekly-synthetic-full` - **Method:** `verify-pbs-backups.sh --datastore pbs-demo --hours 48` - **Result:** 100% of backups validated; aver
tags: [documentation, portfolio]
path: portfolio/01-sde-devops/pbs-report
created: 2026-03-08T22:19:12.893836+00:00
updated: 2026-03-08T22:04:38.210902+00:00
---

# PBS Backup Verification & Lessons Learned

## Verification Summary
- **Scope:** `pbs-demo` datastore, jobs `nightly-vm-backup`, `weekly-synthetic-full`
- **Method:** `verify-pbs-backups.sh --datastore pbs-demo --hours 48`
- **Result:** 100% of backups validated; average verify duration 9m; dedup ratio ~2.7x (sanitized sample).

## Findings
1. **Retention drift prevented:** Dry-run prune with `pbs-retention-policy.yaml` flagged two snapshots outside policy; pruning avoided capacity alarm.
2. **Exporters matter:** Missing PBS exporter metrics delayed alerting. Added scrape target and runbook entry.
3. **Network throttling:** Bandwidth cap of 200 Mbps kept backup windows predictable without starving tenant workloads.

## Next Actions
- Add quarterly restore test to staging Proxmox cluster using latest synthetic full.
- Track datastore growth in Grafana with 30-day projection panel (see `backup-capacity-forecast` panel in dashboards).
- Review alert receivers quarterly to ensure backup paging goes to on-call alias.

## Sanitization Notes
All hostnames, datastore names, and URLs are placeholders. Replace with environment-specific values before deployment.
