# Runbooks — P10

## Runbook: Execute Failover Drill
1. Ensure secondary region stack deployed (`make plan-secondary && make apply-secondary`).
2. Disable primary health check via AWS CLI or inject failure with `scripts/fail_primary.sh`.
3. Run `make failover-drill` to flip Route 53 to secondary.
4. Validate app via `scripts/smoke_secondary.sh`.
5. Record timings and update drill report.
6. Run `make failback` after primary restored.

## Runbook: Replication Health Check
1. Run `python jobs/verify_replication.py --primary primary-bucket --replica secondary-bucket`.
2. Inspect generated `reports/replication-status.json` for mismatches.
3. If drift detected, rerun sync job and re-check.
