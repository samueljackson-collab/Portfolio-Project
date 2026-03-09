---
title: Changelog
description: All notable changes to this project will be documented in this file. - Prometheus + Grafana + Alertmanager stack (Docker Compose) - Alert rules: InstanceDown, HighCPU, HighMemory, DiskSpaceLow - Node 
tags: [documentation, grafana, monitoring, observability, portfolio]
path: portfolio/p04-ops-monitoring/changelog
created: 2026-03-08T22:19:13.511814+00:00
updated: 2026-03-08T22:04:38.899902+00:00
---

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
