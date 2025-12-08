# Architecture

Stack: Python, boto3, AWS Config rules, GuardDuty webhooks.

Data/Control flow: Scheduler runs scans, pushes findings to Security Hub, and triggers remediation lambdas or SSM automations.

Dependencies:
- Python, boto3, AWS Config rules, GuardDuty webhooks.
- Env/config: see README for required secrets and endpoints.
