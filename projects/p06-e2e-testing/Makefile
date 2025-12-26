.PHONY: setup install test test-headed test-debug test-ui report clean help

SHELL := /bin/bash
NODE := node
NPM := npm
BROWSER ?= chromium
WORKERS ?= 4

setup: ## Install dependencies and browsers
	@echo "Installing Node.js dependencies..."
	$(NPM) install
	@echo "Installing Playwright browsers..."
	npx playwright install --with-deps

install: setup ## Alias for setup

test: ## Run all tests headless
	@echo "Running Playwright tests..."
	npx playwright test --workers=$(WORKERS)

test-headed: ## Run tests in headed mode (visible browser)
	@echo "Running tests in headed mode..."
	npx playwright test --headed --workers=1

test-debug: ## Run tests in debug mode
	@echo "Running tests in debug mode..."
	npx playwright test --debug

test-ui: ## Run tests with UI mode
	@echo "Opening Playwright UI mode..."
	npx playwright test --ui

test-chromium: ## Run tests on Chromium only
	npx playwright test --project=chromium

test-firefox: ## Run tests on Firefox only
	npx playwright test --project=firefox

test-webkit: ## Run tests on WebKit only
	npx playwright test --project=webkit

report: ## Open HTML test report
	@echo "Opening test report..."
	npx playwright show-report reports/playwright-html

trace: ## Show trace viewer (specify TRACE_FILE)
	@if [ -z "$(TRACE_FILE)" ]; then \
		echo "Usage: make trace TRACE_FILE=path/to/trace.zip"; \
	else \
		npx playwright show-trace $(TRACE_FILE); \
	fi

update-snapshots: ## Update visual regression snapshots
	@echo "Updating snapshots..."
	npx playwright test --update-snapshots

lint: ## Lint test files
	@echo "Linting TypeScript files..."
	@if command -v eslint >/dev/null 2>&1; then \
		npx eslint tests/**/*.ts; \
	else \
		echo "⚠ ESLint not configured"; \
	fi

clean: ## Clean test artifacts and reports
	rm -rf reports test-results playwright-report .playwright
	rm -rf node_modules package-lock.json
	find . -type f -name "*.zip" -delete

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
