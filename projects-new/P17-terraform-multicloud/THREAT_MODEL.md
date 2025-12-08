# Threat Model

Threats:
- State file exposure
- Drift between clouds
- Inconsistent tagging leading to orphaned resources

Mitigations:
- Remote state encryption, IAM-scoped access
- Scheduled `terraform plan` with drift alerts
- Pre-commit hooks enforcing tags
