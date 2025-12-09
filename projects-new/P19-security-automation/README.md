# P19 – Security Automation

CIS compliance scanner with remediation playbooks and GuardDuty integration.

## Quick start
- Stack: Python, boto3, AWS Config rules, GuardDuty webhooks.
- Flow: Scheduler runs scans, pushes findings to Security Hub, and triggers remediation lambdas or SSM automations.
- Run: make lint then pytest tests
- Operate: Update control baselines monthly, rotate webhook secrets, and monitor remediation success metrics.
