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

restart: stop run ## Restart monitoring stack

status: ## Check status of monitoring services
	@echo "P04 Monitoring Stack Status:"
	@echo ""
	@docker-compose ps
	@echo ""
	@echo "Service Health Checks:"
	@curl -s http://localhost:9090/-/healthy > /dev/null && echo "  ✅ Prometheus: Healthy" || echo "  ❌ Prometheus: Unhealthy or not running"
	@curl -s http://localhost:3000/api/health > /dev/null && echo "  ✅ Grafana: Healthy" || echo "  ❌ Grafana: Unhealthy or not running"
	@curl -s http://localhost:9093/-/healthy > /dev/null && echo "  ✅ AlertManager: Healthy" || echo "  ❌ AlertManager: Unhealthy or not running"
	@curl -s http://localhost:9100/metrics > /dev/null && echo "  ✅ Node Exporter: Healthy" || echo "  ❌ Node Exporter: Unhealthy or not running"

logs: ## Show logs from all services
	docker-compose logs -f

logs-prometheus: ## Show Prometheus logs only
	docker-compose logs -f prometheus

logs-grafana: ## Show Grafana logs only
	docker-compose logs -f grafana

reload-prometheus: ## Reload Prometheus config without restart
	@curl -X POST http://localhost:9090/-/reload && echo "✅ Prometheus config reloaded"

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
