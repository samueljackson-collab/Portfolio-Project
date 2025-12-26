.PHONY: setup cluster-create deploy test clean help

CLUSTER_NAME ?= dev
NAMESPACE ?= default

setup: ## Install kind and kubectl
	@echo "Install kind: https://kind.sigs.k8s.io/docs/user/quick-start/"
	@echo "Install kubectl: https://kubernetes.io/docs/tasks/tools/"

cluster-create: ## Create kind cluster
	kind create cluster --name $(CLUSTER_NAME) --config manifests/kind-config.yaml

cluster-delete: ## Delete kind cluster
	kind delete cluster --name $(CLUSTER_NAME)

deploy: ## Deploy to Kubernetes
	kubectl apply -f manifests/deployment.yaml
	kubectl apply -f manifests/service.yaml
	kubectl rollout status deployment/app -n $(NAMESPACE)

rollout-restart: ## Restart deployment
	kubectl rollout restart deployment/app -n $(NAMESPACE)

rollout-undo: ## Undo last rollout
	kubectl rollout undo deployment/app -n $(NAMESPACE)

test: ## Run tests
	pytest tests/

test-cluster: ## Test cluster connectivity
	kubectl cluster-info
	kubectl get nodes

logs: ## Show pod logs
	kubectl logs -l app=myapp -n $(NAMESPACE) --tail=50

clean: cluster-delete ## Clean up
	rm -rf __pycache__ .pytest_cache

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
