.PHONY: setup generate-certs deploy-policies test clean help

setup: ## Setup environment
	pip install -r requirements.txt

generate-certs: ## Generate mTLS certificates
	bash scripts/generate_certs.sh

deploy-policies: ## Deploy security policies
	python scripts/deploy_policies.py

verify-mtls: ## Verify mTLS configuration
	bash scripts/verify_mtls.sh

test: ## Run tests
	pytest tests/

clean: ## Clean up
	rm -rf certs/ __pycache__

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
