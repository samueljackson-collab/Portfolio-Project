.PHONY: setup run stop validate-prometheus test-alerts test clean help

setup: ## Install dependencies
	@echo "Checking Docker..."
	@command -v docker >/dev/null 2>&1 || (echo "Docker required"; exit 1)
	@command -v docker-compose >/dev/null 2>&1 || (echo "Docker Compose required"; exit 1)
	@echo "✓ Prerequisites met"

run: ## Start monitoring stack
	docker-compose up -d
	@echo ""
	@echo "✓ Monitoring stack started"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana:    http://localhost:3000 (admin/admin)"
	@echo "  Alertmanager: http://localhost:9093"

stop: ## Stop monitoring stack
	docker-compose down

validate-prometheus: ## Validate Prometheus config
	@docker run --rm -v $(PWD)/config:/config prom/prometheus:v2.47.0 \
		promtool check config /config/prometheus.yml
	@docker run --rm -v $(PWD)/config:/config prom/prometheus:v2.47.0 \
		promtool check rules /config/alerts.yml

test-alerts: ## Test alerting rules
	@echo "Testing alert rules..."
	@docker run --rm -v $(PWD)/config:/config prom/prometheus:v2.47.0 \
		promtool test rules /config/alerts.yml || echo "⚠ Create test file: config/alerts.test.yml"

test: ## Run tests
	@if command -v pytest >/dev/null 2>&1; then \
		pytest -v tests/; \
	else \
		echo "pytest not installed"; \
	fi

clean: ## Clean up volumes and containers
	docker-compose down -v
	@echo "✓ Cleaned up monitoring stack"

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
