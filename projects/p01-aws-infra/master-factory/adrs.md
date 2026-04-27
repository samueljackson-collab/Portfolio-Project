# Architecture Decision Records

## ADR-001: Terraform + CloudFormation Hybrid
- **Context:** Existing VPC/RDS stack uses CloudFormation; new modules leverage Terraform.
- **Decision:** Keep CloudFormation for stack stability but wrap with Terraform outputs and remote state to orchestrate dependencies.
- **Consequences:** Mixed IaC requires consistent tagging and state documentation; CI must run both `terraform plan` and `cfn-lint`.

## ADR-002: DR Failover Regions
- **Context:** Need active/passive resilience.
- **Decision:** Use primary region `us-east-1` with secondary `us-west-2` for Route53 failover and cross-region snapshots.
- **Consequences:** Increased snapshot and data transfer cost; requires cross-region KMS keys and health check alarms.

## ADR-003: Security Baseline Enforcement
- **Context:** Compliance requires continuous guardrails.
- **Decision:** Enable Config and GuardDuty in all deployed regions, enforce via CI checks and periodic reports.
- **Consequences:** Additional per-account costs; ensures audit readiness and early drift detection.
