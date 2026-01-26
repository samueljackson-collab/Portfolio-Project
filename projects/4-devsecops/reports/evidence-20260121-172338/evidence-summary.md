# Evidence Summary

## CI workflow (from .github/workflows/ci.yml)
- Pip upgrade: `ci-pip-upgrade.txt`
- Dependency install: `ci-deps-install.txt`
- Tool install: `ci-tools-install.txt`
- Black format check: `ci-black.txt`
- Flake8 linting: `ci-flake8.txt`
- Pytest run + coverage: `ci-pytest.txt` (coverage.xml captured in this folder)
- Docker build: `ci-docker-build.txt`

## Security scans
- SAST (Bandit): `bandit-stdout.txt`, `bandit-stderr.txt`
- SAST (Semgrep): `semgrep-stdout.txt`, `semgrep-stderr.txt`
- Dependency scan (pip-audit): `pip-audit-stdout.txt`, `pip-audit-stderr.txt`
- Container scan (Trivy): `trivy-image-stdout.txt`, `trivy-image-stderr.txt`
- DAST (OWASP ZAP baseline): `zap-stdout.txt`, `zap-stderr.txt`

## Policy gate outcomes (OPA)
- Kubernetes policy input: `policy-input-kubernetes.json`
- Terraform policy input: `policy-input-terraform.json`
- OPA evaluation logs: `opa-kubernetes-stdout.txt`, `opa-kubernetes-stderr.txt`, `opa-terraform-stdout.txt`, `opa-terraform-stderr.txt`

## Vulnerability summary chart
- `vulnerability-summary.md`
- `vulnerability-summary.csv`
