.PHONY: setup validate test lint test-unit test-integration terraform-init terraform-plan terraform-apply 	cfn-changeset cfn-apply deploy-dev deploy-stage deploy-prod clean help

SHELL := /bin/bash
PYTHON := python3
STACK_NAME ?= my-infra-stack
ENVIRONMENT ?= dev
AWS_REGION ?= us-east-1
TEMPLATE := infra/vpc-rds.yaml
RDS_TEMPLATE := infra/rds.yaml
PARAMS ?= params/$(ENVIRONMENT).json
TF_DIR := terraform
STATE_BUCKET ?= p01-aws-infra-tf-state
LOCK_TABLE ?= p01-aws-infra-tf-locks
CHANGE_SET_NAME ?= $(STACK_NAME)-$(shell date +%Y%m%d-%H%M%S)

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

test: test-unit test-integration ## Run all tests

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && pytest -v tests/unit; \
	else \
		pytest -v tests/unit; \
	fi

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && pytest -v tests/integration; \
	else \
		pytest -v tests/integration; \
	fi

lint: ## Lint markdown files
	@echo "Linting markdown..."
	@if command -v markdownlint >/dev/null 2>&1; then \
		markdownlint *.md docs/**/*.md || true; \
	else \
		echo "⚠ markdownlint not installed (npm install -g markdownlint-cli)"; \
	fi

cfn-changeset: validate ## Create CloudFormation change set for the RDS stack
	@echo "Creating change set for stack: $(STACK_NAME) using $(RDS_TEMPLATE)..."
	aws cloudformation create-change-set \
		--stack-name $(STACK_NAME) \
		--change-set-name $(CHANGE_SET_NAME) \
		--template-body file://$(RDS_TEMPLATE) \
		--capabilities CAPABILITY_IAM \
		--region $(AWS_REGION)
	aws cloudformation describe-change-set --stack-name $(STACK_NAME) --change-set-name $(CHANGE_SET_NAME) --region $(AWS_REGION)

cfn-apply: ## Execute a previously created CloudFormation change set
	@echo "Executing change set $(CHANGE_SET_NAME) for stack $(STACK_NAME)..."
	aws cloudformation execute-change-set \
		--stack-name $(STACK_NAME) \
		--change-set-name $(CHANGE_SET_NAME) \
		--region $(AWS_REGION)

terraform-init: ## Initialize Terraform with remote state backend
	@echo "Initializing Terraform backend..."
	@if [ -z "$(STATE_BUCKET)" ] || [ -z "$(LOCK_TABLE)" ]; then \
		echo "STATE_BUCKET and LOCK_TABLE are required"; exit 1; \
	fi
	terraform -chdir=$(TF_DIR) init -input=false \
		-backend-config="bucket=$(STATE_BUCKET)" \
		-backend-config="key=p01-aws-infra/terraform.tfstate" \
		-backend-config="region=$(AWS_REGION)" \
		-backend-config="dynamodb_table=$(LOCK_TABLE)" \
		-backend-config="encrypt=true"

terraform-plan: terraform-init ## Generate Terraform plan
	terraform -chdir=$(TF_DIR) plan -input=false -out=plan.out

terraform-apply: terraform-plan ## Apply Terraform plan (requires confirmation)
	@read -p "Apply Terraform plan to $(ENVIRONMENT)? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		terraform -chdir=$(TF_DIR) apply -input=false plan.out; \
	else \
		echo "Terraform apply cancelled"; \
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
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "[36m%-20s[0m %s
", $$1, $$2}'

.DEFAULT_GOAL := help
