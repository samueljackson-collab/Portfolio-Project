# Threat Model

Threats:
- Access to billing data by unauthorized users
- Automation mis-tagging resources
- Runaway spend from unbounded services

Mitigations:
- IAM boundaries on CUR bucket
- Dry-run mode on tag enforcer with approvals
- Budget alerts and anomaly detection
