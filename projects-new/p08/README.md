# P08 API Testing Harness

Composable API testing stack with contract tests, synthetic data, and CI-friendly Docker/Kubernetes manifests. Provides full operational collateral to ship and support API quality gates in production-like environments.

## Quick start
```sh
docker compose -f docker/docker-compose.yml up --build
pytest docker/tests --maxfail=1
```

## Contents
- ARCHITECTURE: components and data flow
- TESTING: strategy, cases, and fixtures
- REPORT_TEMPLATES: incident and postmortem templates
- PLAYBOOK: rollout and triage guidance
- RUNBOOKS: checklists for common operational tasks
- SOP: recurring operational routines
- METRICS: SLI/SLO catalog
- ADRS: key architectural decisions
- THREAT_MODEL: security analysis
- RISK_REGISTER: tracked delivery/operational risks
- docker/: runnable producer/consumer mocks and test jobs
- k8s/: manifests for CI smoke tests
