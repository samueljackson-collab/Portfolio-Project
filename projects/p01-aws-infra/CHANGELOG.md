# Changelog

All notable changes to the P01 AWS Infrastructure Automation project.

## [Unreleased]

### Added
- Complete Terraform alternative implementation with modular structure
  - VPC module with 3-AZ deployment, NAT gateways, and VPC Flow Logs
  - RDS module with Multi-AZ PostgreSQL, enhanced monitoring, and CloudWatch alarms
  - IAM module with least-privilege roles and instance profiles
- Comprehensive integration test suite
  - VPC connectivity tests validating subnets, routing, and security
  - RDS configuration tests for Multi-AZ, encryption, and backups
  - RDS failover tests (manual execution for destructive testing)
- DR drill automation script (`src/dr_drill.py`)
  - Automated RDS failover initiation and monitoring
  - CloudWatch metrics collection during failover
  - JSON report generation with detailed results
- Grafana dashboard for AWS infrastructure metrics
  - VPC network monitoring
  - RDS performance metrics
  - NAT gateway usage tracking
- Architecture Decision Records (ADRs)
  - CloudFormation vs Terraform strategy
  - State management approach
  - Multi-AZ deployment rationale
  - Database engine selection
  - VPC Flow Logs enablement
- Comprehensive threat model with STRIDE analysis

### Changed
- Enhanced documentation with Terraform deployment instructions
- Updated Makefile with Terraform targets

## [1.0.0] - 2024-12-10

### Added
- Initial CloudFormation template for VPC and RDS deployment
- Basic validation scripts
- Project structure with documentation framework
