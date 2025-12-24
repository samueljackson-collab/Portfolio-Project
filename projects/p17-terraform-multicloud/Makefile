.PHONY: setup init plan-aws apply-aws plan-azure apply-azure destroy clean help

setup: ## Install Terraform
	@echo "Install Terraform from https://www.terraform.io/downloads"

init: ## Initialize Terraform
	terraform init

validate: ## Validate Terraform configuration
	terraform validate

plan-aws: init ## Plan AWS infrastructure
	terraform workspace select aws || terraform workspace new aws
	terraform plan -var-file=environments/aws.tfvars

apply-aws: init ## Apply AWS infrastructure
	terraform workspace select aws || terraform workspace new aws
	terraform apply -var-file=environments/aws.tfvars -auto-approve

plan-azure: init ## Plan Azure infrastructure
	terraform workspace select azure || terraform workspace new azure
	terraform plan -var-file=environments/azure.tfvars

apply-azure: init ## Apply Azure infrastructure
	terraform workspace select azure || terraform workspace new azure
	terraform apply -var-file=environments/azure.tfvars -auto-approve

destroy: ## Destroy infrastructure
	terraform destroy -auto-approve

test: ## Run tests
	pytest tests/

clean: ## Clean Terraform files
	rm -rf .terraform terraform.tfstate*

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
