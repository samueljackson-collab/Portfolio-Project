# Disaster Recovery Runbook

This runbook outlines the steps to restore the Portfolio API platform following a catastrophic event.

## Recovery Time & Point Objectives

- **RTO:** 2 hours for API availability.
- **RPO:** 15 minutes for portfolio data.

## Recovery Steps

1. **Assess Incident**
   - Gather context from Alertmanager and PagerDuty.
   - Open an incident in Jira using the template `INC-DR`.
2. **Restore Database**
   - Select latest snapshot:
     ```bash
     aws rds describe-db-cluster-snapshots --db-cluster-identifier portfolio-${PORTFOLIO_ENV}-aurora --query 'DBClusterSnapshots[0].DBClusterSnapshotArn' --output text
     ```
   - Restore to new cluster and promote.
3. **Rehydrate S3 Evidence**
   - Use AWS Backup vault recovery point.
   - Validate checksums with `scripts/compliance-scan.sh --image ghcr.io/sams-jackson/portfolio-api:${TAG}`.
4. **Redeploy Application**
   - Run `./scripts/deploy.sh --env ${PORTFOLIO_ENV}`.
   - Execute [`documentation/runbooks/data-validation.md`](./data-validation.md).
5. **Post-Incident Review**
   - Document findings in `documentation/security/post-incident-reviews/`.

## Encryption Controls

- KMS keys rotate annually (AWS-managed alias `alias/portfolio`).
- TLS certificates managed via ACM with automatic renewal.
