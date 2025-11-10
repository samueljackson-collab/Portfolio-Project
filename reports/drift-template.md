## Drift Detected: PRJ-SDE-001 RDS Module

**Environment:** See issue title for target environment.
**Detection Timestamp:** Workflow run timestamp (UTC).

### Summary
Terraform drift detection identified changes in the managed RDS resources. Review the attached `plan.out` artifact in the GitHub Actions run for exact details.

### Required Actions
1. Inspect the drift plan and confirm whether console changes were intentional.
2. If drift is legitimate, update Terraform configuration and open a PR.
3. If drift is unintended, run `terraform apply` to reconcile the state.
4. Document remediation steps in the change log and close this issue when resolved.

### Contacts
- Platform Engineering: platform@your-org.com
- On-call Rotation: PagerDuty schedule `Platform-DB`

### Attachments
- Terraform plan artifact (see workflow run)
- CloudWatch alarm snapshots if triggered
