# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Prometheus + Grafana + Alertmanager stack (Docker Compose)
- Alert rules: InstanceDown, HighCPU, HighMemory, DiskSpaceLow
- Node Exporter for system metrics
- Makefile automation (setup, run, validate, test)
- Documentation (README, HANDBOOK)

### Monitoring
- Golden signals tracking: latency, traffic, errors, saturation
- SLO/SLI dashboard templates
- Automated alert routing (Slack/PagerDuty)
