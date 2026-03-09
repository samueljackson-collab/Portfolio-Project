#!/bin/bash
set -euo pipefail

# Enterprise Portfolio Project Generator
# Aligns the P01–P20 projects with the canonical `projects/` hierarchy.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="${SCRIPT_DIR}/../projects"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Project definitions: "ID" => "Friendly Name:slug"
declare -A PROJECTS=(
    ["P01"]="AWS Infrastructure Automation:aws-infra"
    ["P02"]="IAM Security Hardening:iam-hardening"
    ["P03"]="Hybrid Network Connectivity:hybrid-network"
    ["P04"]="Operational Monitoring Stack:ops-monitoring"
    ["P05"]="Mobile App Manual Testing:mobile-testing"
    ["P06"]="Web App Automated Testing:e2e-testing"
    ["P07"]="International Roaming Simulation:roaming-simulation"
    ["P08"]="Backend API Testing:api-testing"
    ["P09"]="Cloud-Native POC Deployment:cloud-native-poc"
    ["P10"]="Multi-Region Architecture:multi-region"
    ["P11"]="API Gateway & Serverless:serverless"
    ["P12"]="Data Pipeline (Airflow):data-pipeline"
    ["P13"]="High-Availability Web App:ha-webapp"
    ["P14"]="Disaster Recovery:disaster-recovery"
    ["P15"]="Cloud Cost Optimization:cost-optimization"
    ["P16"]="Zero-Trust Cloud Architecture:zero-trust"
    ["P17"]="Terraform Multi-Cloud:terraform-multicloud"
    ["P18"]="CI/CD + Kubernetes:k8s-cicd"
    ["P19"]="Cloud Security Automation:security-automation"
    ["P20"]="Observability Engineering:observability"
)

create_project() {
    local project_id="$1"
    local project_name="$2"
    local project_slug="$3"
    local normalized_id=$(echo "$project_id" | tr '[:upper:]' '[:lower:]')
    local project_dir="${PROJECTS_DIR}/${normalized_id}-${project_slug}"

    if [[ -d "${project_dir}" ]]; then
        echo -e "${YELLOW}Skipping ${project_id} (${project_dir} already exists).${NC}"
        return
    fi

    echo -e "${BLUE}Bootstrapping ${project_id} — ${project_name}${NC}"

    mkdir -p "${project_dir}"/{src,scripts,infra/{terraform,k8s},tests/{unit,integration,e2e}}

    cat > "${project_dir}/README.md" <<EOF
# ${project_id} — ${project_name}

## Overview
Starter documentation for ${project_name}. Customize this README with system-specific context, diagrams, and runbooks. Follow the guidance in [docs/PRJ-MASTER-HANDBOOK](../docs/PRJ-MASTER-HANDBOOK/README.md) for writing standards.

## Getting Started
```bash
make setup
cp .env.example .env
make test
```

## Project Layout
```
${project_id,,}-${project_slug}/
├── README.md
├── HANDBOOK.md
├── RUNBOOK.md
├── PLAYBOOK.md
├── CHANGELOG.md
├── Makefile
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── src/
├── scripts/
├── infra/
│   ├── terraform/
│   └── k8s/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

## Next Steps
- Document the target architecture and trust boundaries.
- Implement automation inside `scripts/` or `infra/`.
- Flesh out the `tests/` suites with unit/integration/e2e coverage.
- Track enhancements in `CHANGELOG.md`.
EOF

    cat > "${project_dir}/HANDBOOK.md" <<EOF
# ${project_name} — Engineering Handbook

## Code Standards
- Follow PEP8 (Python) or the language-specific formatter.
- Require code reviews and CI checks before merging.

## Testing Requirements
- Unit tests live in `tests/unit`.
- Integration tests coordinate with external systems via `tests/integration`.
- End-to-end tests validate user journeys inside `tests/e2e`.

## Security Guidelines
- Never commit secrets; use `.env` + secret stores.
- Enable linting/scanning via `make lint` and CI hooks.
EOF

    cat > "${project_dir}/RUNBOOK.md" <<EOF
# ${project_name} — Runbook

## Deployment Procedures
1. Prepare environment variables using `.env.example`.
2. Run `make setup` and `make test`.
3. Execute the deployment target (documented per project).

## Troubleshooting
- Capture logs under `logs/` and attach to incidents.
- Reference monitoring dashboards noted in the README.

## Incident Response
- Declare incidents in Slack #incidents.
- Follow the escalation matrix defined in docs/PRJ-MASTER-HANDBOOK.
EOF

    cat > "${project_dir}/PLAYBOOK.md" <<EOF
# ${project_name} — Playbook

## Deployment Play
1. Validate infrastructure changes (terraform plan / cfn-lint / sam build).
2. Run smoke tests.
3. Deploy to dev → staging → production.

## Operations Play
- Monitor golden signals (latency, traffic, errors, saturation).
- Trigger rollback if error budgets breach.
EOF

    cat > "${project_dir}/CHANGELOG.md" <<'EOF'
# Changelog

All notable changes will be documented here following [Keep a Changelog](https://keepachangelog.com/) and Semantic Versioning.

## [Unreleased]
- Initial scaffolding.
EOF

    cat > "${project_dir}/Makefile" <<'EOF'
.PHONY: setup test lint run deploy clean help

PYTHON ?= python3
VENV ?= .venv

setup:
$(PYTHON) -m venv $(VENV) || true
. $(VENV)/bin/activate && pip install --upgrade pip
. $(VENV)/bin/activate && pip install -r requirements.txt -r requirements-dev.txt || true

lint:
@echo "Running linters"
@if command -v ruff >/dev/null 2>&1; then ruff check src tests; fi
@if command -v black >/dev/null 2>&1; then black --check src tests; fi

test:
@echo "Running unit tests"
pytest tests

run:
$(PYTHON) src/main.py

deploy:
@echo "Implement project-specific deployment logic"

clean:
rm -rf $(VENV) .pytest_cache __pycache__

help:
@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /'
EOF

    cat > "${project_dir}/requirements.txt" <<'EOF'
boto3>=1.34
requests>=2.32
EOF

    cat > "${project_dir}/requirements-dev.txt" <<'EOF'
pytest>=7.0
pytest-cov>=4.0
black>=24.3
ruff>=0.5
EOF

    cat > "${project_dir}/.env.example" <<EOF
# Environment overrides for ${project_id}
ENVIRONMENT=dev
AWS_REGION=us-east-1
LOG_LEVEL=INFO
METRICS_ENDPOINT=http://localhost:9090/metrics
EOF

    cat > "${project_dir}/.gitignore" <<'EOF'
.venv/
__pycache__/
*.pyc
.env
.env.*
.DS_Store
EOF

    cat > "${project_dir}/src/main.py" <<'EOF'
"""Placeholder application entry point."""


def health_check() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    print(health_check())
EOF

    cat > "${project_dir}/tests/unit/test_main.py" <<'EOF'
from src import main


def test_health_check():
    assert main.health_check()["status"] == "ok"
EOF

    touch "${project_dir}/tests/integration/.gitkeep"
    touch "${project_dir}/tests/e2e/.gitkeep"
    touch "${project_dir}/infra/terraform/main.tf"
    touch "${project_dir}/infra/k8s/README.md"
    touch "${project_dir}/scripts/README.md"

    echo -e "${GREEN}✔ Created ${project_dir}${NC}"
}

for id in "${!PROJECTS[@]}"; do
    IFS=':' read -r name slug <<< "${PROJECTS[$id]}"
    create_project "$id" "$name" "$slug"
done
