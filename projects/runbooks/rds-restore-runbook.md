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
  --db-snapshot-identifier <SNAPSHOT_ID> \
  --db-subnet-group-name <SUBNET_GROUP> \
  --engine postgres \
  --db-instance-class db.t3.medium \
  --no-multi-az
```

2) Wait for the instance to be available:
```bash
aws rds wait db-instance-available --db-instance-identifier <NEW_INSTANCE_ID>
```

3) Validate:
- Run basic queries against critical tables
- Run app smoke tests against restored DB
- Check for data consistency and row counts

## Rollback
If the restore is not valid:
1) Re-point application to previous DB (if available)
2) Delete restored DB instance:
```bash
aws rds delete-db-instance --db-instance-identifier <NEW_INSTANCE_ID> --skip-final-snapshot
```

## Post-incident
- Document root cause
- Update alerts and remediation steps
- Run disaster recovery drill to verify process
