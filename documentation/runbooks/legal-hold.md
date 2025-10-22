# Legal Hold Procedure

## Trigger

- Legal, compliance, or executive leadership requests preservation of specific portfolio data sets.

## Steps

1. Create Jira issue `LH-<case-id>`.
2. Disable automated deletions by setting `FEATURE_DATA_PURGE=false` via ConfigMap update.
3. Snapshot Aurora cluster and copy to isolated account using AWS Backup cross-account sharing.
4. Export relevant evidence assets to dedicated S3 bucket `portfolio-legal-hold` with versioning enabled.
5. Document preserved records in [`documentation/security/compliance-register.md`](../security/compliance-register.md).

## Release

- Receive written approval from legal.
- Re-enable purge features and document actions taken.
