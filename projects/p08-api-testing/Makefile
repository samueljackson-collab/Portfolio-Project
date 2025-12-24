.PHONY: setup test test-verbose test-ci report clean help

SHELL := /bin/bash
NODE := node
NPM := npm
COLLECTION := collections/api-tests.json
ENV_FILE := collections/environment.dev.json
REPORT_DIR := reports

setup: ## Install dependencies
	@echo "Installing Newman and reporters..."
	$(NPM) install -g newman newman-reporter-htmlextra
	mkdir -p $(REPORT_DIR)

test: ## Run API tests
	@echo "Running API tests with Newman..."
	newman run $(COLLECTION) \
		-e $(ENV_FILE) \
		--bail \
		--color on

test-verbose: ## Run tests with verbose output
	@echo "Running API tests (verbose)..."
	newman run $(COLLECTION) \
		-e $(ENV_FILE) \
		--verbose \
		--color on

test-ci: ## Run tests for CI/CD (with reports)
	@echo "Running API tests for CI..."
	newman run $(COLLECTION) \
		-e $(ENV_FILE) \
		--reporters cli,json,htmlextra \
		--reporter-json-export $(REPORT_DIR)/newman-report.json \
		--reporter-htmlextra-export $(REPORT_DIR)/newman-report.html \
		--bail

test-folder: ## Run specific folder (use FOLDER=name)
	@if [ -z "$(FOLDER)" ]; then \
		echo "Usage: make test-folder FOLDER='Folder Name'"; \
	else \
		newman run $(COLLECTION) \
			-e $(ENV_FILE) \
			--folder "$(FOLDER)"; \
	fi

test-staging: ## Run tests against staging
	@echo "Running tests against staging environment..."
	newman run $(COLLECTION) \
		-e collections/environment.staging.json \
		--bail

test-prod: ## Run smoke tests against production
	@echo "⚠️  Running smoke tests against PRODUCTION"
	newman run $(COLLECTION) \
		-e collections/environment.prod.json \
		--folder "Smoke Tests"

report: ## Open HTML test report
	@if [ -f $(REPORT_DIR)/newman-report.html ]; then \
		open $(REPORT_DIR)/newman-report.html || xdg-open $(REPORT_DIR)/newman-report.html; \
	else \
		echo "No report found. Run 'make test-ci' first."; \
	fi

validate-collection: ## Validate Postman collection format
	@echo "Validating collection format..."
	@$(NODE) -e "JSON.parse(require('fs').readFileSync('$(COLLECTION)', 'utf8'))" && echo "✓ Collection is valid JSON"

clean: ## Clean reports and artifacts
	rm -rf $(REPORT_DIR)/*
	mkdir -p $(REPORT_DIR)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
