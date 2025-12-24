.PHONY: setup test-connectivity test benchmark latency-test clean help

REMOTE_IP ?= 10.0.1.10
PING_COUNT ?= 10

setup: ## Install dependencies
	@echo "Installing network testing tools..."
	@command -v ping >/dev/null 2>&1 || (echo "ping required"; exit 1)
	@command -v iperf3 >/dev/null 2>&1 || echo "⚠ iperf3 recommended: apt install iperf3"
	@command -v mtr >/dev/null 2>&1 || echo "⚠ mtr recommended: apt install mtr"
	chmod +x scripts/*.sh

test-connectivity: ## Test VPN tunnel connectivity
	./scripts/test_connectivity.sh $(REMOTE_IP)

test: ## Run unit tests
	@if command -v pytest >/dev/null 2>&1; then \
		pytest -v tests/; \
	else \
		echo "pytest not installed: pip install pytest"; \
	fi

benchmark: ## Benchmark network throughput (requires iperf3 server on remote)
	@if command -v iperf3 >/dev/null 2>&1; then \
		echo "Running iperf3 benchmark to $(REMOTE_IP)..."; \
		iperf3 -c $(REMOTE_IP) -t 10 -P 4; \
	else \
		echo "iperf3 not installed"; \
		exit 1; \
	fi

latency-test: ## Run latency analysis with mtr
	@if command -v mtr >/dev/null 2>&1; then \
		echo "Running mtr latency test to $(REMOTE_IP)..."; \
		mtr -r -c 50 $(REMOTE_IP); \
	else \
		echo "mtr not installed"; \
		exit 1; \
	fi

clean: ## Clean temporary files
	rm -f *.log

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
