.PHONY: setup build deploy test clean help

SHELL := /bin/bash
STACK_NAME ?= serverless-api
STAGE ?= dev

setup: ## Install SAM CLI
	pip install aws-sam-cli

build: ## Build SAM application
	sam build

deploy-dev: build ## Deploy to dev
	sam deploy --guided --stack-name $(STACK_NAME)-$(STAGE)

test: ## Run tests
	pytest tests/

invoke-local: ## Invoke Lambda locally
	sam local invoke CreateFunction -e events/create.json

clean: ## Clean artifacts
	rm -rf .aws-sam

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
