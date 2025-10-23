.PHONY: iam-test

iam-test:
	@echo "Running OPA policy tests"
	@if command -v opa >/dev/null 2>&1; then \
		opa test policy-as-code/; \
	else \
		echo "OPA not installed; skipping policy tests"; \
	fi
	@if command -v cfn-lint >/dev/null 2>&1; then \
		cfn-lint policies/**/*.json || true; \
	else \
		echo "cfn-lint not installed; skipping CloudFormation lint"; \
	fi
