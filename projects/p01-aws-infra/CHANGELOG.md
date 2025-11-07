# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CloudFormation template for VPC with 3 AZs (public/private subnets)
- Multi-AZ RDS PostgreSQL instance with automated backups
- DR drill automation script (`scripts/dr-drill.sh`)
- Python template validation script
- Pytest test suite for template validation
- Makefile for common operations (setup, validate, test, deploy)
- Complete documentation (README, HANDBOOK, RUNBOOK, PLAYBOOK)
- Architecture and data flow diagrams (Mermaid)
- ADR-0001: Initial technical direction (CloudFormation)

### Security
- Least-privilege IAM roles for CloudFormation execution
- RDS security groups restricted to private subnets
- Secrets Manager integration for database credentials
- CloudWatch Logs export for RDS audit trails

## [0.1.0] - 2024-11-07

### Added
- Initial project structure
- DR drill script for RDS Multi-AZ failover testing
