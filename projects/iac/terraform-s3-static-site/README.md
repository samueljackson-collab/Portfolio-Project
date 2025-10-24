# Terraform S3 Static Website Bucket

## Overview
Infrastructure-as-code module that provisions a secure S3 bucket backed by CloudFront for hosting static frontend assets. Includes logging, encryption, and CI/CD integration.

## Features
- Private S3 bucket with CloudFront Origin Access Control (OAC) to prevent direct access.
- Managed certificates via AWS Certificate Manager for custom domains.
- Versioning, lifecycle policies, and access logging shipped to centralized log bucket.
- Terraform variables for environment tagging, WAF association, and caching policies.

## Usage
1. Initialize Terraform: `terraform init`.
2. Copy `terraform.tfvars.example` to `terraform.tfvars` and set domain, ACM ARN, log bucket, etc.
3. Plan changes: `terraform plan` (state stored remotely via S3/DynamoDB as defined in backend configuration).
4. Apply: `terraform apply` with approval workflow.
5. Upload assets via CI/CD (GitHub Actions) using `aws s3 sync` + `aws cloudfront create-invalidation`.

## Security
- Server-side encryption with AWS KMS CMK.
- Public access block enabled; only CloudFront accesses bucket.
- Optional WAF ACL to mitigate OWASP Top 10 and rate-based attacks.

## Compliance & Documentation
- Terraform docs generated via `terraform-docs` and stored in `docs/`.
- Sentinel policies enforce tagging, logging, encryption.
- Runbook describes DR steps for failover to secondary region bucket.

