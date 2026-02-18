# Governance

## Roles & RACI
- **Product Owner:** Approves scope, prioritizes backlog.
- **Tech Lead:** Owns architecture decisions and CI/CD quality gates.
- **DevOps:** Maintains Terraform/CloudFormation pipelines and state hygiene.
- **Security:** Reviews guardrails, scans, and incident response readiness.
- **Ops/DBA:** Oversees RDS performance, backups, and DR drill execution.

## Change Control
- All infrastructure changes via PR with linked issue and risk rating.
- Mandatory reviewers: Tech Lead + Security for high/critical changes.
- Emergency changes require postmortem within 48 hours.

## Compliance
- Align with CIS AWS Foundations; document evidence quarterly.
- Track open findings in `reports/p01/findings.csv` with due dates and owners.
- Require tagging standards: `Project=P01`, `Environment`, `Owner`, `CostCenter`.
