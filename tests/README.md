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


## Recent Test Additions

### Modified Script Tests
Comprehensive test coverage for simplified and corrected bash scripts:

- **test_fix_unicode_arrows.py**: Enhanced tests for the simplified unicode arrow replacement script
  - Tests backup file creation and restoration
  - Validates idempotent behavior
  - Tests nested directory processing
  - Edge cases for multiple encoding types
  
- **test_verify_pbs_backups.py**: Tests for simplified PBS backup verification
  - Exit code documentation validation
  - Function structure verification
  - API connectivity handling
  
- **test_deploy.py**: New comprehensive tests for deploy.sh
  - Terraform fmt command correction validation
  - Script structure and organization
  - Error handling verification
  
- **test_bootstrap_remote_state.py**: New comprehensive tests for bootstrap_remote_state.sh
  - Newline at EOF correction validation
  - AWS resource creation logic
  - Output format verification

### Configuration File Tests
Enhanced validation for observability stack configurations:

- **test_yaml_configs.py**: Comprehensive YAML configuration validation
  - Infrastructure alert rules validation (Prometheus)
  - Alert severity and annotation requirements
  - Loki configuration structure tests
  - Promtail and Alertmanager placeholder validation
  
- **test_json_configs.py**: Grafana dashboard validation
  - Dashboard structure and required fields
  - Panel organization and datasource references
  - Template variable validation
  - Time series and stat panel verification

### Test Coverage Statistics
- **Total test classes added**: 24
- **Total test methods added**: 100+
- **Files with enhanced coverage**: 6
- **New test files created**: 2

### Running the New Tests
```bash
# Run all new script tests
pytest tests/scripts/ -v

# Run configuration tests
pytest tests/config/ -v

# Run specific test file
pytest tests/scripts/test_deploy.py -v
pytest tests/scripts/test_bootstrap_remote_state.py -v
```