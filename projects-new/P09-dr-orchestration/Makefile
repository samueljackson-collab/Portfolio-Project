.PHONY: help install test test-unit test-integration test-e2e lint format clean build deploy

help:
	@echo "Available targets:"
	@echo "  install           - Install dependencies"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests"
	@echo "  test-integration  - Run integration tests"
	@echo "  test-e2e          - Run end-to-end tests"
	@echo "  lint              - Run linters"
	@echo "  format            - Format code"
	@echo "  clean             - Clean build artifacts"
	@echo "  build             - Build Docker image"
	@echo "  deploy            - Deploy application (ENV=dev|staging|prod)"

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install -r requirements-dev.txt

test: test-unit test-integration

test-unit:
	. venv/bin/activate && pytest tests/unit -v --cov=src --cov-report=term-missing

test-integration:
	. venv/bin/activate && pytest tests/integration -v

test-e2e:
	. venv/bin/activate && pytest tests/e2e -v

lint:
	. venv/bin/activate && flake8 src tests
	. venv/bin/activate && pylint src
	. venv/bin/activate && mypy src

format:
	. venv/bin/activate && black src tests
	. venv/bin/activate && isort src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .coverage htmlcov

build:
	docker build -t ${PROJECT_SLUG}:latest .

deploy:
	@if [ -z "$(ENV)" ]; then \
		echo "Error: ENV not set. Usage: make deploy ENV=dev|staging|prod"; \
		exit 1; \
	fi
	@echo "Deploying to $(ENV)..."
	./scripts/deploy.sh $(ENV)
