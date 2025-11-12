.PHONY: setup run test clean help

setup: ## Setup Airflow with Docker
	docker-compose -f docker/docker-compose.yml up airflow-init

run: ## Start Airflow
	docker-compose -f docker/docker-compose.yml up -d

stop: ## Stop Airflow
	docker-compose -f docker/docker-compose.yml down

test: ## Test DAGs
	pytest tests/

test-dags: ## Validate DAG integrity
	python dags/validate_dags.py

clean: ## Clean up
	docker-compose -f docker/docker-compose.yml down -v

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
