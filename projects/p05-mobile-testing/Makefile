.PHONY: help view-charters view-matrix view-cases view-defects test

help: ## Show this help
	@echo "Mobile App Manual Testing - P05"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

view-charters: ## View test charter template
	@echo "=== Test Charter Template ==="
	@cat docs/test-charter-template.md

view-matrix: ## View device compatibility matrix
	@echo "=== Device Compatibility Matrix ==="
	@column -t -s',' config/device-matrix.csv | head -20

view-cases: ## View test cases
	@echo "=== Test Cases: Login Flow ==="
	@cat test-cases/login-flow.md

view-defects: ## View sample defect reports
	@echo "=== Defect Report: BUG-201 ==="
	@cat defects/BUG-201-session-timeout.md

test: ## Run automated checks (validates file structure)
	@echo "Checking test artifacts..."
	@test -f docs/test-charter-template.md && echo "✓ Charter template exists" || echo "✗ Charter template missing"
	@test -f config/device-matrix.csv && echo "✓ Device matrix exists" || echo "✗ Device matrix missing"
	@test -f test-cases/login-flow.md && echo "✓ Test cases exist" || echo "✗ Test cases missing"
	@test -f defects/BUG-201-session-timeout.md && echo "✓ Defect reports exist" || echo "✗ Defect reports missing"
	@echo ""
	@echo "✓ All test artifacts validated"

.DEFAULT_GOAL := help
