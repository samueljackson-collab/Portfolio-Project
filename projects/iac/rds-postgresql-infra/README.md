# RDS PostgreSQL Database Infrastructure

## Overview
Terraform module for provisioning a secure, highly-available Amazon RDS PostgreSQL cluster supporting transactional workloads.

## Features
- Multi-AZ deployment with automatic failover.
- Parameter groups tuned for FastAPI workload (connection limits, logging).
- Encrypted at rest with KMS, encrypted in transit using TLS enforcement.
- Automated backups, snapshot retention policies, and cross-region replica support.
- Integration with IAM authentication and Secrets Manager rotation.

## Usage
1. Configure remote state backend (S3 + DynamoDB) as per portfolio standards.
2. Copy `terraform.tfvars.example`, specify VPC subnets, security groups, instance class, storage.
3. Run `terraform init`, `terraform plan`, `terraform apply`.
4. Outputs provide connection strings, security group IDs, monitoring endpoints.

## Operations
- CloudWatch alarms for CPU, storage, connections; integrates with PagerDuty.
- Performance Insights enabled for query tuning.
- Runbook covers failover, snapshot restore, and point-in-time recovery.

## Compliance
- Aligns with CIS benchmarks for database encryption, auditing, and logging.
- Audit logs exported to CloudWatch Logs → centralized SIEM.

