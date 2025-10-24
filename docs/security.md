# Security Overview

Security is embedded throughout the repository design to reinforce good habits when showcasing projects publicly.

## Defense-in-Depth Controls

1. **Network Segmentation** – Split workloads into public, private, and database subnets. Limit inbound/outbound rules with security groups and network ACLs.
2. **Encryption** – Enforce TLS for inbound traffic, enable encryption at rest for RDS, and use AWS-managed keys for storage services.
3. **Secrets Handling** – Store credentials in GitHub Actions secrets or AWS Secrets Manager. Never commit secrets to version control.
4. **Identity and Access Management** – Use IAM roles with the principle of least privilege. Rotate access keys regularly or adopt OIDC for CI workflows.
5. **Monitoring and Alerting** – Stream CloudTrail logs, configure GuardDuty, and maintain CloudWatch alarms for high-priority events.

## Security Automation in CI

The `security-scan` workflow runs Trivy and Checkov scans on every push, pull request, and weekly schedule. Review findings, prioritize remediation, and document accepted risks in pull request descriptions.

## Reporting Vulnerabilities

If you publish this repository publicly, add a `SECURITY.md` file outlining how others can report vulnerabilities responsibly. Encourage the use of GitHub's private reporting feature.
