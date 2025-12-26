# PBS Job & Retention Summary (Sanitized)

**Stack:** PRJ-SDE-002 Observability & Backups
**Date:** 2025-11-14
**Sources:** PBS UI export (sanitized), `pbs-job-plan.yaml`

## Job Health
- ✅ All three jobs completed within 18 minutes of start time.
- ✅ No failed chunks; deduplication ratio averaged **2.4x** across datasets.
- ✅ Incremental backups reduced network utilization by ~42% compared to fulls.

## Retention Outcomes
| Job | Policy | Oldest Restore Point | Expected Footprint |
| --- | ------ | ------------------- | ------------------ |
| nightly-hv-snapshots | 3 last / 7 daily / 4 weekly | 28 days | ~1.2 TB
| k8s-control-plane | 3 last / 14 daily / 6 weekly | 60 days | ~850 GB
| observability-stack | 5 last / 14 daily / 8 weekly | 90 days | ~640 GB

## Notable Actions
- Adjusted staggered start times to avoid NFS saturation from `k8s-control-plane` and `observability-stack`.
- Enabled encryption-at-rest on the datastore; keys are stored in a password manager, not in Git.
- Verified restore of Grafana and Prometheus volumes to a sandbox VM; dashboards and TSDB contents survived WAL replay.

## Follow-ups
- Monitor datastore capacity weekly; target <75% utilization.
- Evaluate object storage tiering for archives older than 90 days.
- Automate restore tests quarterly via Ansible playbook (placeholder tasks in `scripts/verify-pbs-backups.sh`).

**Sanitization:** Hostnames, IPs, usernames, and tokens removed; schedule and retention values kept intact for reproducibility.
