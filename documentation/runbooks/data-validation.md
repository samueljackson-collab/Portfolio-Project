# Data Validation Runbook

Use this runbook after deployments to verify that the database and evidence stores contain expected content.

## Preconditions

- Deployment succeeded and smoke tests passed.
- Access to the `PortfolioPlatformAdmin` IAM role.

## Steps

1. **Check portfolio entries**
   ```bash
   psql "$(aws rds generate-db-auth-token --hostname ${DB_HOST} --port 5432 --region us-west-2 --username portfolio_app)" \
     -d portfolio -c "SELECT count(*) FROM portfolio_entry;"
   ```
2. **Verify evidence bucket**
   ```bash
   aws s3 ls s3://portfolio-${PORTFOLIO_ENV}-evidence/ --recursive | head
   ```
3. **Confirm export jobs**
   ```bash
   curl -H "Authorization: Bearer ${TOKEN}" https://api.${PORTFOLIO_ENV}.portfolio.example.com/api/v1/jobs?status=completed
   ```
4. Record results in [`documentation/security/compliance-register.md`](../security/compliance-register.md).

## Rollback Criteria

- Missing portfolio entries: rollback application deployment.
- Evidence bucket empty: rerun background sync job via `kubectl create job --from=cronjob/portfolio-reindex manual-reindex`.
- Export jobs failing: follow [`documentation/runbooks/incident-response.md`](./incident-response.md).
