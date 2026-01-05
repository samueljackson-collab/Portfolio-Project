# Architecture

Stack: Python, boto3, AWS Config rules, GuardDuty webhooks.

Data/Control flow: Scheduler runs scans, pushes findings to Security Hub, and triggers remediation lambdas or SSM automations.

Dependencies:
- Python 3.9+ runtime with `boto3`, `requests` for webhook handling.
- AWS Config service enabled with managed/custom rules for compliance checks.
- GuardDuty active with EventBridge integration for real-time threat alerts.
- IAM roles for Lambda execution with permissions for Security Hub, Config, SSM.
- Env/config: see README for required secrets and endpoints.
