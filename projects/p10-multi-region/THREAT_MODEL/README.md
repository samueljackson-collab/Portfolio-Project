# Threat Model — P10

## Assets
- DNS records, application traffic, replicated data (DB, S3), Terraform state.

## Entry Points
- Route 53 APIs, application endpoints in both regions, CI pipelines deploying Terraform.

## Threats
- **Misconfiguration:** incorrect failover routing causing split-brain.
- **Data inconsistency:** replication lag leading to stale reads after failover.
- **Credential leakage:** Terraform state containing secrets.

## Mitigations
- Automated policy tests for DNS records.
- Replication health checks with alerts; failover blocked if lag exceeds threshold.
- Store Terraform state in encrypted backend; restrict IAM roles per region.

## Residual Risk
- TTL-based failover cannot instantly shift all clients; some will hit failed region briefly.
