.PHONY: setup deploy-primary deploy-secondary deploy-all test-failover clean help

SHELL := /bin/bash
PRIMARY_REGION ?= us-east-1
SECONDARY_REGION ?= us-west-2
STACK_NAME ?= multi-region-app

setup: ## Install dependencies
	@echo "Installing AWS CLI and dependencies..."
	pip install --upgrade awscli boto3 pyyaml

deploy-primary: ## Deploy to primary region
	@echo "Deploying to primary region: $(PRIMARY_REGION)"
	aws cloudformation deploy \
		--stack-name $(STACK_NAME)-primary \
		--template-file infra/primary-region.yaml \
		--region $(PRIMARY_REGION) \
		--capabilities CAPABILITY_IAM

deploy-secondary: ## Deploy to secondary region
	@echo "Deploying to secondary region: $(SECONDARY_REGION)"
	aws cloudformation deploy \
		--stack-name $(STACK_NAME)-secondary \
		--template-file infra/secondary-region.yaml \
		--region $(SECONDARY_REGION) \
		--capabilities CAPABILITY_IAM

deploy-all: deploy-primary deploy-secondary ## Deploy to both regions
	@echo "Configuring Route 53 failover..."
	aws cloudformation deploy \
		--stack-name $(STACK_NAME)-route53 \
		--template-file infra/route53-failover.yaml \
		--region us-east-1 \
		--capabilities CAPABILITY_IAM

test-failover: ## Test failover mechanism
	@echo "Testing failover..."
	python3 scripts/test_failover.py

check-health: ## Check Route 53 health checks
	@echo "Checking health check status..."
	python3 scripts/check_health.py

simulate-outage: ## Simulate primary region outage
	@echo "⚠️  Simulating primary region outage..."
	python3 scripts/simulate_outage.py --region $(PRIMARY_REGION)

clean: ## Delete all stacks
	@echo "Deleting stacks..."
	aws cloudformation delete-stack --stack-name $(STACK_NAME)-route53 --region us-east-1
	aws cloudformation delete-stack --stack-name $(STACK_NAME)-primary --region $(PRIMARY_REGION)
	aws cloudformation delete-stack --stack-name $(STACK_NAME)-secondary --region $(SECONDARY_REGION)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
