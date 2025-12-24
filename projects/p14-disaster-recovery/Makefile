.PHONY: setup backup-all restore dr-drill clean help

setup: ## Setup DR environment
	pip install -r requirements.txt

backup-all: ## Run all backups
	bash scripts/backup_database.sh
	bash scripts/backup_files.sh
	bash scripts/backup_config.sh

restore: ## Restore from backup
	bash scripts/restore.sh

dr-drill: ## Run DR drill
	python scripts/dr_drill.py

test: ## Run tests
	pytest tests/

clean: ## Clean up
	rm -rf backups/ logs/

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
