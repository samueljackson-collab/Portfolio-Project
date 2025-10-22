# Data Retention Runbook

This runbook outlines the operational steps to enforce the data retention policy defined in [`security/policies/data-retention.md`](../../security/policies/data-retention.md).

## Monthly Tasks

1. Run Athena query `queries/data_retention.sql` to identify records exceeding retention windows.
2. Export results to CSV and attach to Jira ticket `DATA-RET-<month>`.
3. Trigger purge workflow via `/api/v1/exports` with `delete_after_export=true`.
4. Confirm deletions by running `SELECT * FROM portfolio_entry WHERE deleted_at IS NOT NULL`.

## Quarterly Audit

- Review purge logs stored in `documentation/security/compliance-register.md`.
- Validate S3 lifecycle rules for evidence buckets.
- Report findings during Security & Compliance review.
