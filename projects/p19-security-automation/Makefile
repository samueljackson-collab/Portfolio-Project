.PHONY: setup scan-all scan-cis generate-report test clean help

setup: ## Setup environment
	pip install -r requirements.txt

scan-all: ## Run all security scans
	python scripts/scan_security.py --all

scan-cis: ## Run CIS compliance checks
	python scripts/cis_compliance.py

scan-vulnerabilities: ## Scan for vulnerabilities
	python scripts/vulnerability_scan.py

generate-report: ## Generate compliance report
	python scripts/generate_report.py --output reports/security_report.html

remediate: ## Run automated remediation
	python scripts/auto_remediate.py

test: ## Run tests
	pytest tests/

clean: ## Clean up
	rm -rf reports/ __pycache__

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
