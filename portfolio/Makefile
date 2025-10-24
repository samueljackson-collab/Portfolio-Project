.PHONY: dev test fmt lint build up down setup-py setup-node migrate

PYTHON ?= python3
PIP ?= pip
COMPOSE ?= docker compose

setup-py:
	$(PIP) install -r requirements.txt

setup-node:
	cd projects/frontend && npm install

dev:
	$(COMPOSE) -f docker-compose.yml up --build

up:
	$(COMPOSE) -f docker-compose.yml up -d

down:
	$(COMPOSE) -f docker-compose.yml down -v

test:
	pytest --cov=projects/backend/app --cov-report=term-missing projects/backend/app/tests
	cd projects/frontend && npm run test

lint:
	ruff check projects/backend/app
	black --check projects/backend/app
	isort --check-only projects/backend/app
	bandit -c bandit.yaml -r projects/backend/app
	cd projects/frontend && npm run lint
	cd projects/frontend && npm run format:check
	@if command -v terraform >/dev/null 2>&1; then \
		cd projects/infra/terraform && terraform fmt -check; \
	else \
		echo "Terraform not installed, skipping terraform fmt"; \
	fi
	@if command -v tflint >/dev/null 2>&1; then \
		tflint projects/infra/terraform/envs/prod; \
	else \
		echo "tflint not installed, skipping"; \
	fi
	@if command -v tfsec >/dev/null 2>&1; then \
		tfsec projects/infra/terraform; \
	else \
		echo "tfsec not installed, skipping"; \
	fi
	@if command -v npm >/dev/null 2>&1; then \
		npm audit --audit-level=moderate || true; \
	fi
	@if command -v trivy >/dev/null 2>&1; then \
		trivy fs --exit-code 0 --no-progress . || true; \
	else \
		echo "trivy not installed, skipping"; \
	fi

fmt:
	black projects/backend/app
	isort projects/backend/app
	ruff check --fix projects/backend/app
	cd projects/frontend && npm run format
	@if command -v terraform >/dev/null 2>&1; then \
		cd projects/infra/terraform && terraform fmt; \
	else \
		echo "Terraform not installed, skipping terraform fmt"; \
	fi

build:
	cd projects/frontend && npm run build
	cd projects/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

migrate:
	cd projects/backend && alembic upgrade head
