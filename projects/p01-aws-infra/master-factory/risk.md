# Risk Register

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Misconfigured Route53 failover causing downtime | Medium | High | Automated health checks + DR drill validation with thresholds; manual approval for DNS changes. | Ops Lead |
| Terraform state corruption | Low | High | S3 versioning + DynamoDB locking; restricted IAM on state bucket; periodic state backups. | DevOps |
| RDS backup failure | Medium | High | CloudWatch alarm on snapshot failures; monthly restore tests; SNS alerts. | DBA |
| Security drift (Config/GuardDuty disabled) | Medium | High | Config rules to enforce enablement; CI checks; weekly drift reports. | Security |
| Cost overrun from idle resources | Medium | Medium | Scheduled shutdown for non-prod, tagging, and cost anomaly detection alerts. | FinOps |
