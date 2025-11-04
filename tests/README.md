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