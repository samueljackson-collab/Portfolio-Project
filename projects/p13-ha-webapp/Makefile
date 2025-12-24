.PHONY: setup run test clean help

setup: ## Setup environment
	docker-compose -f docker/docker-compose.yml build

run: ## Run HA stack
	docker-compose -f docker/docker-compose.yml up -d --scale app=3

stop: ## Stop stack
	docker-compose -f docker/docker-compose.yml down

test: ## Run tests
	pytest tests/

test-ha: ## Test high availability
	python tests/test_ha.py

logs: ## Show logs
	docker-compose -f docker/docker-compose.yml logs -f

clean: ## Clean up
	docker-compose -f docker/docker-compose.yml down -v

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
