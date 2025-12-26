.PHONY: help install test test-coverage lint format clean build deploy local samlocal destroy

# Default target
help:
	@echo "P11 Serverless API Gateway - Available targets:"
	@echo "  install          - Install dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  lint             - Run linting checks (flake8, pylint)"
	@echo "  format           - Format code with black and isort"
	@echo "  clean            - Remove build artifacts and cache"
	@echo "  build            - Build SAM application"
	@echo "  local            - Run Lambda locally with SAM"
	@echo "  deploy           - Deploy to AWS"
	@echo "  destroy          - Delete CloudFormation stack"

# Install dependencies
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

# Run all tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-coverage:
	pytest tests/ -v --tb=short --cov=lambda_handlers --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

# Lint code
lint:
	flake8 lambda_handlers tests --max-line-length=120 --ignore=E203,W503
	pylint lambda_handlers --disable=all --enable=E,F

# Format code
format:
	black lambda_handlers tests --line-length=120
	isort lambda_handlers tests --profile=black

# Clean build artifacts
clean:
	rm -rf .pytest_cache __pycache__ htmlcov .coverage
	rm -rf lambda_handlers/__pycache__ tests/__pycache__
	rm -rf .aws-sam build
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Build SAM application
build:
	sam build

# Run Lambda locally
local: build
	sam local start-api --port 3000 --parameter-overrides Environment=dev

# Deploy to AWS (requires AWS credentials configured)
deploy: test
	@if [ -z "$(ENVIRONMENT)" ]; then \
		echo "ERROR: ENVIRONMENT variable not set"; \
		echo "Usage: make deploy ENVIRONMENT=dev [AWS_REGION=us-east-1] [STACK_NAME=serverless-api-gateway]"; \
		exit 1; \
	fi
	@echo "Deploying to $(ENVIRONMENT) environment..."
	sam build
	sam deploy \
		--template-file .aws-sam/build/template.yaml \
		--stack-name $(STACK_NAME:=serverless-api-gateway-$(ENVIRONMENT)) \
		--region $(AWS_REGION:=us-east-1) \
		--parameter-overrides Environment=$(ENVIRONMENT) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset
	@echo "Stack outputs:"
	aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME:=serverless-api-gateway-$(ENVIRONMENT)) \
		--region $(AWS_REGION:=us-east-1) \
		--query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
		--output table

# Run SAM local tests
samlocal: build
	sam local invoke CreateItemFunction --event events/create_event.json
	sam local invoke ReadItemFunction --event events/read_event.json
	sam local invoke UpdateItemFunction --event events/update_event.json
	sam local invoke DeleteItemFunction --event events/delete_event.json

# Destroy CloudFormation stack
destroy:
	@if [ -z "$(ENVIRONMENT)" ]; then \
		echo "ERROR: ENVIRONMENT variable not set"; \
		echo "Usage: make destroy ENVIRONMENT=dev [AWS_REGION=us-east-1] [STACK_NAME=serverless-api-gateway]"; \
		exit 1; \
	fi
	@echo "WARNING: This will delete the stack and all resources"
	@echo "Stack: $(STACK_NAME:=serverless-api-gateway-$(ENVIRONMENT))"
	@read -p "Type 'yes' to confirm deletion: " confirm && \
	if [ "$$confirm" = "yes" ]; then \
		aws cloudformation delete-stack \
			--stack-name $(STACK_NAME:=serverless-api-gateway-$(ENVIRONMENT)) \
			--region $(AWS_REGION:=us-east-1); \
		echo "Stack deletion initiated"; \
	else \
		echo "Deletion cancelled"; \
	fi

# Install and run all checks
check: install lint test-coverage
	@echo "All checks passed!"

# Quick test for development
test-quick:
	pytest tests/ -v --tb=short -x

# Watch tests (requires pytest-watch)
test-watch:
	ptw tests/

# View SAM stack outputs
outputs:
	@if [ -z "$(ENVIRONMENT)" ]; then \
		echo "ERROR: ENVIRONMENT variable not set"; \
		echo "Usage: make outputs ENVIRONMENT=dev [AWS_REGION=us-east-1] [STACK_NAME=serverless-api-gateway]"; \
		exit 1; \
	fi
	aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME:=serverless-api-gateway-$(ENVIRONMENT)) \
		--region $(AWS_REGION:=us-east-1) \
		--query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
		--output table

# Get API endpoint
endpoint:
	@if [ -z "$(ENVIRONMENT)" ]; then \
		echo "ERROR: ENVIRONMENT variable not set"; \
		echo "Usage: make endpoint ENVIRONMENT=dev [AWS_REGION=us-east-1] [STACK_NAME=serverless-api-gateway]"; \
		exit 1; \
	fi
	@aws cloudformation describe-stacks \
		--stack-name $(STACK_NAME:=serverless-api-gateway-$(ENVIRONMENT)) \
		--region $(AWS_REGION:=us-east-1) \
		--query 'Stacks[0].Outputs[?OutputKey==`ItemsApiEndpoint`].OutputValue' \
		--output text
