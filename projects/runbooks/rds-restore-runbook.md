# RDS Restore Runbook - PRJ-SDE-001

## Overview
Purpose: Restore PostgreSQL RDS from snapshot to recover from data corruption or accidental deletion.
Estimated time: 30–60 minutes
Risk: High

## Prerequisites
- AWS CLI configured with appropriate permissions
- Snapshot identifier available
- Maintenance window scheduled
- Communication with stakeholders

## Pre-flight checks
- [ ] Confirm snapshot exists:
  aws rds describe-db-snapshots --db-snapshot-identifier <SNAPSHOT_ID>
- [ ] Confirm subnet group exists and is healthy
- [ ] Ensure backups and final-state snapshots are available

## Procedure

1) Restore DB from snapshot:
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier restored-db-$(date +%s) \
  --db-snapshot-identifier <SNAPSHOT_ID>
```
