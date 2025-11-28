# Project 4: DevSecOps Pipeline

Security-first CI pipeline with SBOM generation, container scanning, and policy checks.

## Contents
- GitHub Actions workflow [`pipelines/github-actions.yaml`](pipelines/github-actions.yaml) orchestrating build, security scanning, and deployment gates.
- Kyverno policy enforcing signed images in [`manifests/policy-engine.yaml`](manifests/policy-engine.yaml).
- Prometheus alert rules watching for critical CVEs in [`monitoring/security-alerts.yml`](monitoring/security-alerts.yml).
- Tests validating workflow coverage in [`tests/test_pipeline_config.py`](tests/test_pipeline_config.py).
- Operational guidance in [`RUNBOOK.md`](RUNBOOK.md) and design notes in [`wiki/overview.md`](wiki/overview.md).
