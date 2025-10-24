# Secure Cloud Network (VPC) Infrastructure

## Overview
Terraform configurations to build a foundational AWS VPC aligned with zero trust principles. Supports multi-account landing zone with shared services.

## Components
- VPC with public, private application, and private data subnets across three AZs.
- NAT gateways, transit gateway attachments, and centralized egress via firewall appliances.
- Network ACLs, security groups, and AWS Network Firewall policies enforcing least-privilege flows.
- VPC endpoints for AWS services (S3, DynamoDB, Secrets Manager) to avoid public internet exposure.
- Flow logs and traffic mirroring for security analytics.

## Usage
1. Configure `terraform.tfvars` with CIDR ranges, account IDs, firewall settings.
2. Initialize and apply module per environment (dev/staging/prod) using Terraform workspaces.
3. Outputs provide subnet IDs, route table IDs, security groups for consumption by other modules.

## Security & Compliance
- Integrates with AWS Control Tower guardrails.
- Uses AWS Config rules to monitor drift.
- Tags resources for cost allocation and compliance reporting.

## Operations
- Change management via network change requests (NCR) documented in `docs/ncr/`.
- Runbook covers network troubleshooting, VPN setup, and cross-region replication.

