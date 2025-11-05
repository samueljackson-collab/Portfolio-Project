# Test Suite for Portfolio Project

This directory contains comprehensive unit tests for the bash scripts and configuration files in the repository.

## Structure

- tests/scripts/ - Tests for bash scripts
- tests/config/ - Tests for configuration files

## Running Tests

### Run all tests
```bash
python -m pytest tests/
```

### Run tests with verbose output
```bash
python -m pytest tests/ -v
```

### Run specific test file
```bash
python -m pytest tests/scripts/test_verify_pbs_backups.py
```

## Test Categories

### Bash Script Tests
- verify-pbs-backups.sh: Backup verification utility tests
- dr-drill.sh: Disaster recovery drill tests
- fix_unicode_arrows.sh: Unicode arrow replacement tests

### Configuration Tests
- YAML configurations (Prometheus, Alertmanager, Loki, Promtail)
- JSON configurations (Grafana dashboards)
- ArgoCD application manifests

## Requirements

Tests require pytest>=7.2.0 and pyyaml (already in requirements.txt)
# Test Suite Documentation

This directory contains comprehensive tests for the infrastructure code added in this branch.

## Test Coverage

### Bash Scripts (`tests/bash_scripts/`)
- **test_bootstrap_remote_state.py**: Tests for `scripts/bootstrap_remote_state.sh`
  - Script existence and permissions
  - Argument parsing and defaults
  - S3 bucket creation logic
  - DynamoDB table creation logic
  - Error handling
  - Idempotency
  - Region-specific behavior

- **test_deploy_sh.py**: Tests for `scripts/deploy.sh`
  - Terraform command orchestration
  - Workspace management
  - Auto-approve functionality
  - Directory navigation
  - Safety checks

### Terraform Configuration (`tests/terraform/`)
- **test_terraform_syntax.py**: Tests for Terraform files
  - HCL syntax validation
  - Resource definitions
  - Variable declarations
  - Output definitions
  - Backend configuration
  - Security best practices
  - Naming conventions

- **test_github_workflow.py**: Tests for GitHub Actions workflow
  - YAML syntax validation
  - Job structure
  - Terraform steps
  - Security scanning (TFLint, Checkov)
  - OIDC configuration
  - Artifact handling
  - PR commenting

### JSON Configuration (`tests/json_config/`)
- **test_iam_policies.py**: Tests for IAM policy files
  - JSON syntax validation
  - Policy structure
  - Required permissions
  - Security best practices
  - OIDC trust policy
  - Placeholder validation

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test categories:
```bash
# Bash script tests
pytest tests/bash_scripts/

# Terraform tests
pytest tests/terraform/

# JSON config tests
pytest tests/json_config/
```

### Run specific test file:
```bash
pytest tests/bash_scripts/test_bootstrap_remote_state.py -v
```

### Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Test Statistics

| Category | Test Files | Test Cases | Lines of Code |
|----------|------------|------------|---------------|
| Bash Scripts | 2 | ~120 | ~1200 |
| Terraform | 2 | ~70 | ~700 |
| JSON Config | 1 | ~50 | ~500 |
| **Total** | **5** | **~240** | **~2400** |

## Key Testing Principles

1. **Comprehensive Coverage**: Tests cover happy paths, edge cases, and error conditions
2. **Security Focus**: Validates security best practices and configurations
3. **Syntax Validation**: Ensures all configuration files are syntactically correct
4. **Best Practices**: Verifies adherence to coding and infrastructure standards
5. **Documentation**: Tests validate that code is well-documented
6. **Idempotency**: Ensures scripts can be run safely multiple times

## Dependencies

Tests require:
- Python 3.11+
- pytest
- pytest-mock
- pytest-timeout
- PyYAML

Install with:
```bash
pip install -r requirements.txt
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines and provide rapid feedback on code quality and correctness.
Tests require pytest>=7.2.0 and pyyaml (already in requirements.txt)
