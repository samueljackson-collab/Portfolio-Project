.PHONY: setup build run test test-coverage clean help

SHELL := /bin/bash
PYTHON := python3
DOCKER := docker
COMPOSE := docker-compose
IMAGE_NAME := cloud-native-poc
CONTAINER_NAME := poc-app

setup: ## Install dependencies
	$(PYTHON) -m venv .venv || true
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt

build: ## Build Docker image
	$(DOCKER) build -t $(IMAGE_NAME):latest -f docker/Dockerfile .

run: ## Run application locally
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000; \
	else \
		uvicorn src.main:app --reload --host 0.0.0.0 --port 8000; \
	fi

run-docker: build ## Run in Docker container
	$(DOCKER) run -d --name $(CONTAINER_NAME) \
		-p 8000:8000 \
		-v $(PWD)/data:/app/data \
		$(IMAGE_NAME):latest

run-compose: ## Run with Docker Compose
	$(COMPOSE) -f docker/docker-compose.yml up -d

stop: ## Stop Docker containers
	$(DOCKER) stop $(CONTAINER_NAME) || true
	$(DOCKER) rm $(CONTAINER_NAME) || true

stop-compose: ## Stop Docker Compose
	$(COMPOSE) -f docker/docker-compose.yml down

test: ## Run tests
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && pytest -v tests/; \
	else \
		pytest -v tests/; \
	fi

test-coverage: ## Run tests with coverage
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate && pytest --cov=src --cov-report=html --cov-report=term tests/; \
	else \
		pytest --cov=src --cov-report=html --cov-report=term tests/; \
	fi

test-docker: build ## Run tests in Docker
	$(DOCKER) run --rm $(IMAGE_NAME):latest pytest tests/

logs: ## Show Docker logs
	$(DOCKER) logs -f $(CONTAINER_NAME)

health-check: ## Check application health
	@curl -f http://localhost:8000/health || echo "Health check failed"
	@curl -f http://localhost:8000/ready || echo "Ready check failed"

clean: ## Clean artifacts and containers
	rm -rf .venv __pycache__ .pytest_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	$(DOCKER) stop $(CONTAINER_NAME) || true
	$(DOCKER) rm $(CONTAINER_NAME) || true
	$(COMPOSE) -f docker/docker-compose.yml down || true

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
