SHELL := /bin/bash

.PHONY: help setup dev stop backend frontend monitoring infra fmt lint test ci security package

help:
@echo "Available targets:"
@echo "  setup      Install tooling"
@echo "  dev        Start docker-compose stack"
@echo "  stop       Stop docker-compose stack"
@echo "  backend    Run backend tests"
@echo "  frontend   Run frontend tests"
@echo "  monitoring Run monitoring service locally"
@echo "  infra      Validate Terraform modules"
@echo "  fmt        Run formatters"
@echo "  lint       Run linters"
@echo "  test       Run all tests"
@echo "  ci         Run lint, test, security"
@echo "  security   Run security scanners"
@echo "  package    Build distribution artifacts"

setup:
pip install -r requirements.txt
npm install
pre-commit install

dev:
docker-compose up --build

stop:
docker-compose down

backend:
cd backend && pytest

frontend:
cd frontend && npm install && npm run test

monitoring:
cd monitoring && uvicorn app.main:app --reload --port 9100

infra:
cd infra && terraform init -backend=false && terraform validate

fmt:
ruff format .
prettier --write frontend/src

lint:
ruff .
npm run lint

security:
pip install pip-audit && pip-audit
npm audit --audit-level=high || true
cd infra && tfsec .

test: backend frontend

ci: fmt lint test security

package:
./scripts/package_zip.sh

