.PHONY: setup validate-policies test deploy-policies policy-diff simulate clean help

PYTHON := python3
AWS_ACCOUNT_ID ?= $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "123456789012")
POLICY_DIR := policies

setup: ## Install dependencies
	$(PYTHON) -m venv .venv || true
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt || pip install boto3 pytest

validate-policies: ## Validate all IAM policies
	@echo "Validating IAM policies..."
	@for policy in $(POLICY_DIR)/*.json; do \
		echo "Checking $$policy..."; \
		aws iam validate-policy --policy-document file://$$policy || exit 1; \
	done
	@echo "✓ All policies valid"

policy-diff: ## Compare two policies (usage: make policy-diff OLD=old.json NEW=new.json)
	@if [ -z "$(OLD)" ] || [ -z "$(NEW)" ]; then \
		echo "Usage: make policy-diff OLD=policies/old.json NEW=policies/new.json"; \
		exit 1; \
	fi
	$(PYTHON) src/policy_diff.py $(OLD) $(NEW)

simulate: ## Simulate policy action (usage: make simulate POLICY=policies/dev.json ACTION=s3:GetObject RESOURCE=arn:aws:s3:::mybucket/*)
	@if [ -z "$(POLICY)" ] || [ -z "$(ACTION)" ] || [ -z "$(RESOURCE)" ]; then \
		echo "Usage: make simulate POLICY=policies/dev.json ACTION=s3:GetObject RESOURCE=arn:aws:s3:::bucket/*"; \
		exit 1; \
	fi
	@echo "Simulating policy: $(POLICY)"
	@echo "Action: $(ACTION)"
	@echo "Resource: $(RESOURCE)"
	aws iam simulate-custom-policy \
		--policy-input-list file://$(POLICY) \
		--action-names $(ACTION) \
		--resource-arns $(RESOURCE)

deploy-policies: validate-policies ## Deploy IAM policies (dev environment only)
	@echo "⚠️  This would deploy policies to AWS (dry-run mode)"
	@echo "To actually deploy, implement: aws iam create-policy --policy-name X --policy-document file://Y"

test: ## Run tests
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && pytest -v tests/; \
	else \
		pytest -v tests/; \
	fi

clean: ## Clean build artifacts
	rm -rf .venv __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
