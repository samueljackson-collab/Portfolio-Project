---
title: Sam Jackson's Portfolio Wiki
description: Comprehensive documentation for infrastructure, security, and DevOps projects
published: true
date: 2025-11-07
tags: [portfolio, documentation, wiki]
---

# Welcome to Sam Jackson's Enterprise Portfolio Wiki

> **Building reliable systems, documenting clearly, and sharing what I learn.**

This wiki contains complete documentation for all portfolio projects, including implementation guides, operational runbooks, process playbooks, and reference handbooks.

## 🎯 Quick Navigation

### 📁 Projects by Category

#### Homelab & Infrastructure
- [PRJ-HOME-001: Homelab & Secure Network Build](/projects/homelab/prj-home-001/overview) - pfSense, UniFi, VLANs, IPS, VPN
- [PRJ-HOME-002: Virtualization & Core Services](/projects/homelab/prj-home-002/overview) - Proxmox, TrueNAS, reverse proxy, TLS

#### System Development & DevOps
- [PRJ-SDE-001: Full-Stack Database Infrastructure](/projects/sde-devops/prj-sde-001/overview) - Terraform, AWS VPC, RDS, ECS, ALB
- [PRJ-SDE-002: Observability & Backups Stack](/projects/sde-devops/prj-sde-002/overview) - Prometheus, Grafana, Loki, Alertmanager, PBS

#### Cybersecurity
- [PRJ-CYB-BLUE-001: AWS SIEM Pipeline](/projects/cybersecurity/prj-cyb-blue-001/overview) - OpenSearch, Kinesis, GuardDuty, Lambda

#### Cloud Architecture
- [PRJ-CLOUD-001: AWS Landing Zone](/projects/cloud-architecture/prj-cloud-001/overview) - Organizations, SSO, Control Tower *(In Progress)*

### 📖 Operational Documentation

#### Runbooks (Incident Response)
Operational procedures for specific incidents and alerts:

**Infrastructure**
- [Host Down Response](/runbooks/infrastructure/host-down) - When a server becomes unreachable
- [High CPU Usage](/runbooks/infrastructure/high-cpu) - CPU >80% troubleshooting
- [Disk Space Low](/runbooks/infrastructure/disk-space-low) - Disk usage >90%
- [Memory Exhaustion](/runbooks/infrastructure/memory-exhaustion) - OOM conditions

**Database**
- [Database Connection Failure](/runbooks/database/connection-failure) - Cannot connect to database
- [Slow Query Performance](/runbooks/database/slow-queries) - Query performance degradation
- [Backup Job Failure](/runbooks/database/backup-failure) - Backup jobs not completing
- [Replication Lag](/runbooks/database/replication-lag) - Master-replica sync issues

**Networking**
- [Network Connectivity Issues](/runbooks/networking/connectivity-issues) - General network troubleshooting
- [VPN Connection Failure](/runbooks/networking/vpn-failure) - OpenVPN not connecting
- [VLAN Misconfiguration](/runbooks/networking/vlan-issues) - Inter-VLAN communication problems
- [DNS Resolution Failure](/runbooks/networking/dns-failure) - DNS not resolving

**Security**
- [IPS Alert Response](/runbooks/security/ips-alert-response) - Suricata/IPS alerts
- [Unauthorized Access Attempt](/runbooks/security/unauthorized-access) - Failed login attempts
- [Certificate Expiration](/runbooks/security/cert-expiration) - SSL/TLS certificate renewal
- [Security Scan Findings](/runbooks/security/scan-findings) - Vulnerability scan remediation

**Monitoring**
- [Prometheus Scrape Failures](/runbooks/monitoring/scrape-failures) - Exporters not responding
- [Grafana Dashboard Issues](/runbooks/monitoring/dashboard-issues) - Dashboards not loading
- [Alert Storm Management](/runbooks/monitoring/alert-storm) - Too many alerts firing
- [Log Ingestion Failure](/runbooks/monitoring/log-ingestion-failure) - Loki not receiving logs

#### Playbooks (Process Workflows)
End-to-end process workflows for common scenarios:

- [Disaster Recovery Playbook](/playbooks/disaster-recovery) - Complete DR procedures
- [Deployment Playbook](/playbooks/deployment) - Application deployment workflow
- [Incident Response Playbook](/playbooks/incident-response) - Security incident handling
- [Change Management Playbook](/playbooks/change-management) - Production change process
- [Backup & Recovery Playbook](/playbooks/backup-recovery) - Data protection procedures
- [Infrastructure Provisioning Playbook](/playbooks/infrastructure-provisioning) - New infrastructure setup
- [Security Hardening Playbook](/playbooks/security-hardening) - System hardening procedures
- [Performance Tuning Playbook](/playbooks/performance-tuning) - Optimization workflows

#### Handbooks (Reference Guides)
Comprehensive reference documentation and standards:

- [Engineer's Handbook](/handbooks/engineers-handbook) - Standards, quality gates, best practices
- [Operations Handbook](/handbooks/operations-handbook) - Day-to-day operational procedures
- [Security Handbook](/handbooks/security-handbook) - Security standards and compliance
- [Monitoring Handbook](/handbooks/monitoring-handbook) - Observability best practices
- [Database Handbook](/handbooks/database-handbook) - Database administration guide
- [Network Engineering Handbook](/handbooks/network-handbook) - Networking reference

## 🚀 Getting Started

New to this wiki? Start here:

1. [**Quick Start Guide**](/getting-started) - Learn how to navigate and use this wiki
2. [**Project Index**](/projects/index) - Browse all projects by category
3. [**Common Runbooks**](/runbooks/index) - Most frequently used procedures
4. [**Glossary**](/glossary) - Technical terms and acronyms

## 📊 Project Status Overview

| Category | Completed | In Progress | Planned |
|----------|-----------|-------------|---------|
| **Homelab** | 2 | 0 | 1 |
| **SDE/DevOps** | 2 | 0 | 0 |
| **Cybersecurity** | 1 | 0 | 2 |
| **Cloud Architecture** | 0 | 1 | 1 |
| **QA/Testing** | 0 | 0 | 2 |
| **Web/Data** | 0 | 1 | 0 |
| **AI/ML** | 0 | 0 | 1 |

## 🔍 Search Tips

Use the search bar (top right) to quickly find:
- `runbook:` - Find operational procedures
- `playbook:` - Find process workflows
- `alert:` - Find alert-related documentation
- `terraform` - Find IaC-related content
- `security` - Find security documentation

## 📚 Documentation Philosophy

This wiki follows these principles:

- **Completeness**: Every project has implementation guide, runbooks, and operational docs
- **Clarity**: Step-by-step instructions with expected outcomes
- **Maintainability**: Living documentation updated with lessons learned
- **Searchability**: Consistent structure and tagging for easy discovery
- **Actionability**: Runbooks provide immediate action steps, not just theory

## 🤝 Connect

**Author**: Sam Jackson
**GitHub**: [@samueljackson-collab](https://github.com/samueljackson-collab)
**LinkedIn**: [sams-jackson](https://www.linkedin.com/in/sams-jackson)

---

**Last Updated**: November 7, 2025
**Wiki Version**: 1.0
**Total Pages**: 100+ documents covering infrastructure, security, and operations
