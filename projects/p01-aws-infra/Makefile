.PHONY: setup validate test lint run deploy-dev deploy-stage deploy-prod changeset clean help

SHELL := /bin/bash
PYTHON := python3
STACK_NAME ?= my-infra-stack
ENVIRONMENT ?= dev
AWS_REGION ?= us-east-1
TEMPLATE := infra/vpc-rds.yaml
PARAMS ?= params/$(ENVIRONMENT).json

setup: ## Install dependencies
	$(PYTHON) -m venv .venv || true
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt || pip install pyyaml pytest boto3

validate: ## Validate CloudFormation templates
	@echo "Validating CloudFormation templates..."
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && $(PYTHON) src/validate_template.py; \
	else \
		$(PYTHON) src/validate_template.py; \
	fi

test: ## Run unit tests
	@echo "Running tests..."
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && pytest -v tests/; \
	else \
		pytest -v tests/; \
	fi

lint: ## Lint markdown files
	@echo "Linting markdown..."
	@if command -v markdownlint >/dev/null 2>&1; then \
		markdownlint *.md docs/**/*.md || true; \
	else \
		echo "⚠ markdownlint not installed (npm install -g markdownlint-cli)"; \
	fi

changeset: validate ## Create CloudFormation change set
	@echo "Creating change set for stack: $(STACK_NAME)..."
	@if [ -f "$(PARAMS)" ]; then \
		aws cloudformation create-change-set \
			--stack-name $(STACK_NAME) \
			--change-set-name $(STACK_NAME)-$(shell date +%Y%m%d-%H%M%S) \
			--template-body file://$(TEMPLATE) \
			--parameters file://$(PARAMS) \
			--capabilities CAPABILITY_IAM \
			--region $(AWS_REGION); \
	else \
		aws cloudformation create-change-set \
			--stack-name $(STACK_NAME) \
			--change-set-name $(STACK_NAME)-$(shell date +%Y%m%d-%H%M%S) \
			--template-body file://$(TEMPLATE) \
			--capabilities CAPABILITY_IAM \
			--region $(AWS_REGION); \
	fi

deploy-dev: ENVIRONMENT=dev
deploy-dev: validate ## Deploy stack to dev environment
	@echo "Deploying stack to DEV: $(STACK_NAME)..."
	aws cloudformation deploy \
		--stack-name $(STACK_NAME) \
		--template-file $(TEMPLATE) \
		--parameter-overrides Environment=dev \
		--capabilities CAPABILITY_IAM \
		--region $(AWS_REGION) \
		--no-fail-on-empty-changeset

deploy-stage: ENVIRONMENT=stage
deploy-stage: validate ## Deploy stack to staging environment
	@echo "Deploying stack to STAGE: $(STACK_NAME)..."
	aws cloudformation deploy \
		--stack-name $(STACK_NAME) \
		--template-file $(TEMPLATE) \
		--parameter-overrides Environment=stage \
		--capabilities CAPABILITY_IAM \
		--region $(AWS_REGION) \
		--no-fail-on-empty-changeset

deploy-prod: ENVIRONMENT=prod
deploy-prod: validate ## Deploy stack to production (USE WITH CAUTION)
	@echo "⚠️  WARNING: Deploying to PRODUCTION"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		aws cloudformation deploy \
			--stack-name $(STACK_NAME) \
			--template-file $(TEMPLATE) \
			--parameter-overrides Environment=prod \
			--capabilities CAPABILITY_IAM \
			--region $(AWS_REGION) \
			--no-fail-on-empty-changeset; \
	else \
		echo "Deployment cancelled"; \
	fi

clean: ## Clean build artifacts
	rm -rf .venv __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
