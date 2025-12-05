# Testing Suite

## Test Categories
- **Unit Tests:** Validate functions/modules for app services and Terraform helpers; enforce coverage thresholds.
- **Integration Tests:** API endpoints via ALB, DB CRUD, Secrets Manager retrieval, and messaging integrations if present.
- **Infrastructure Tests:** terraform fmt/validate, tflint, tfsec, conftest (OPA), infracost guardrails, drift detection.
- **Performance Tests:** Load tests against ALB endpoints; baseline latency and error rates; capacity predictions.
- **Chaos/Resilience:** Task kill, AZ failover simulation, forced DB failover; verify recovery times.
- **Disaster Recovery Drills:** Full restore from snapshot, traffic failover via Route53/ALB weighting, data validation checks.

## Environments & Frequency
- **PR/Feature:** Unit + integration (mocked dependencies), static analysis, IaC validate, dependency scan.
- **Dev/Stage:** Full integration, smoke against deployed stack, limited performance test, drift detection nightly.
- **Prod:** Canary smoke post-deploy; monthly chaos; quarterly DR drill.

## Tooling & Commands
- `make lint` → formatting, linters, security scans.
- `make test` → unit/integration with coverage report; fail if <85% coverage for services.
- `make plan` → terraform plan with cost estimate; block if delta beyond threshold.
- `make smoke ENV=<env>` → hits `/healthz`, DB connectivity, basic CRUD script.
- `make chaos ENV=<env>` → controlled task kill and DB failover tests.

## Acceptance Gates
- PRs must pass lint, unit tests, coverage, IaC validate, and security scans before merge.
- Deployments require green smoke tests and no critical vulnerabilities; prod requires manual approval after plan review.
- DR drills documented with achieved RTO/RPO and gaps; failures must be remediated before next release.

## Reporting
- JUnit/Cobertura outputs uploaded as CI artifacts; coverage trend monitored weekly.
- Test results linked in `REPORTING-PACKAGE.md` and deployment logs; failures trigger incident or bug tickets.
- Chaos/DR outcomes update `OPERATIONS-PACKAGE.md` thresholds and `RISK-REGISTER.md` statuses.
