.PHONY: setup analyze-costs generate-report clean help

setup: ## Setup environment
	pip install -r requirements.txt

analyze-costs: ## Analyze AWS costs
	python scripts/analyze_costs.py

generate-report: ## Generate cost report
	python scripts/generate_report.py

run-queries: ## Run CUR queries
	python scripts/run_athena_queries.py

test: ## Run tests
	pytest tests/

clean: ## Clean up
	rm -rf reports/ __pycache__

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
