# Testing Suite

## Scope
Covers unit, integration, infrastructure, security, performance, and disaster-recovery validation for PRJ-SDE-001. Designed to be automated in CI/CD with clear entry/exit criteria and rollback triggers.

## Test Matrix
| Layer | Objective | Tools | Frequency | Exit Criteria |
| --- | --- | --- | --- | --- |
| Unit | Validate app logic, handlers, utilities | pytest/jest, coverage | On every PR | ≥90% line coverage; zero critical defects |
| Contract | Verify API schemas and DB migrations | schemathesis, prisma migrate dry-run | On PR and nightly | All contracts validated; no incompatible changes |
| Integration | Exercise service-to-service and DB flows | docker-compose, localstack, testcontainers | On PR merges | CRUD flows succeed; idempotent migrations |
| Infrastructure | Assert Terraform correctness | terraform fmt/validate/plan, tflint, terratest | On PR and pre-prod | Plan clean; terratest suite green |
| Security | Detect vulnerabilities/secrets | trivy, grype, gitleaks, tfsec/OPA | On PR and weekly | No critical/high findings; waivers documented |
| Performance | Baseline latency and throughput | k6, artillery, locust | Pre-release | p95 latency < 250ms at target RPS; error rate <0.1% |
| DR/Resilience | Validate backup/restore and failover | aws rds restore, route53 failover drills, chaos experiments | Quarterly | RTO ≤ 60 min; RPO ≤ 5 min; alarms trigger |

## Pipelines & Commands
- **Static checks:** `make lint` → runs `terraform fmt`, `tflint`, `tfsec`, `hadolint`, `pre-commit` hooks.
- **Unit/Integration:** `make test` → language-specific tests plus docker-compose integration against ephemeral DB.
- **Infrastructure tests:** `make terratest` → Go-based tests validating VPC, RDS, and ECS resources in sandbox.
- **Performance:** `make load-test` → execute k6 scripts with environment-specific targets; publish HTML and JSON.
- **Security scans:** `make security-scan` → trivy filesystem/image scan + gitleaks secrets scan.
- **DR drill:** `make dr-drill` → scripted restore from latest snapshot, ALB/Route53 failover, data integrity checks.

## Data & Environments
- **Test data:** Generated fixtures in `code-examples/fixtures`; sanitized datasets for integration and performance.
- **Environments:**
  - **dev:** fast feedback; feature branches auto-deploy.
  - **stage:** pre-prod parity; load and failover tests.
  - **prod:** manual approval; limited to smoke tests and canary deploys.

## Reporting
- JUnit/XML and coverage reports uploaded as CI artifacts.
- Terraform plan summaries commented on PRs with estimated monthly cost deltas.
- Load test results and DR drill outcomes stored in `reports/` with timestamps.
- Failing tests auto-create tickets with owner, SLA, and next action.
