.PHONY: setup test run-simulation clean help

SHELL := /bin/bash
PYTHON := python3
VENV := .venv
SCENARIO ?= international_roaming

setup: ## Install dependencies and setup database
	$(PYTHON) -m venv $(VENV) || true
	. $(VENV)/bin/activate && pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -r requirements.txt
	@echo "Initializing subscriber database..."
	. $(VENV)/bin/activate && $(PYTHON) src/init_db.py

test: ## Run all tests
	@echo "Running roaming simulation tests..."
	@if [ -f $(VENV)/bin/activate ]; then \
		. $(VENV)/bin/activate && pytest -v tests/; \
	else \
		pytest -v tests/; \
	fi

test-coverage: ## Run tests with coverage report
	@if [ -f $(VENV)/bin/activate ]; then \
		. $(VENV)/bin/activate && pytest --cov=src --cov-report=html --cov-report=term tests/; \
	else \
		pytest --cov=src --cov-report=html --cov-report=term tests/; \
	fi

run-simulation: ## Run roaming simulation
	@echo "Running roaming simulation: $(SCENARIO)..."
	@if [ -f $(VENV)/bin/activate ]; then \
		. $(VENV)/bin/activate && $(PYTHON) src/simulator.py --scenario $(SCENARIO); \
	else \
		$(PYTHON) src/simulator.py --scenario $(SCENARIO); \
	fi

run-all-scenarios: ## Run all test scenarios
	@echo "Running all roaming scenarios..."
	@for scenario in international_roaming failed_auth no_roaming_agreement network_selection; do \
		echo "=== Running scenario: $$scenario ==="; \
		make run-simulation SCENARIO=$$scenario; \
	done

init-db: ## Initialize subscriber database
	@echo "Initializing database..."
	@if [ -f $(VENV)/bin/activate ]; then \
		. $(VENV)/bin/activate && $(PYTHON) src/init_db.py; \
	else \
		$(PYTHON) src/init_db.py; \
	fi

clean: ## Clean build artifacts and logs
	rm -rf $(VENV) __pycache__ .pytest_cache htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf logs/*.log data/*.db
	mkdir -p logs data

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
