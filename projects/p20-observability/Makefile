.PHONY: setup run stop query-metrics test clean help

setup: ## Setup environment
	docker-compose -f config/docker-compose.yml build

run: ## Run observability stack
	docker-compose -f config/docker-compose.yml up -d

stop: ## Stop observability stack
	docker-compose -f config/docker-compose.yml down

query-metrics: ## Query Prometheus metrics
	curl http://localhost:9090/api/v1/query?query=up

import-dashboards: ## Import Grafana dashboards
	@for dashboard in dashboards/*.json; do \
		echo "Importing $$dashboard..."; \
		curl -X POST -H "Content-Type: application/json" \
			-d @$$dashboard \
			http://admin:admin@localhost:3000/api/dashboards/db; \
	done

test: ## Run tests
	pytest tests/

logs: ## Show logs
	docker-compose -f config/docker-compose.yml logs -f

clean: ## Clean up
	docker-compose -f config/docker-compose.yml down -v

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
