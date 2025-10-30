# Terraform Infrastructure

This directory contains Terraform configurations targeting AWS.
- `modules/vpc`: Reusable VPC module with public/private subnets and supporting resources.
- `envs/prod`: Production environment configuration that consumes the VPC module and defines remote state.

Ensure Terraform 1.6+ is installed and authenticated before running plans.
