# ==============================================================================
# TERRAFORM AND PROVIDER VERSION CONSTRAINTS
# ==============================================================================
#
# PURPOSE:
# This file defines version constraints for:
# 1. Terraform CLI itself (the terraform binary)
# 2. Provider plugins (AWS, random, etc.)
# 3. Required provider configurations
#
# WHY VERSION CONSTRAINTS MATTER:
#
# WITHOUT VERSION CONSTRAINTS:
# - Team members might use different Terraform versions (inconsistent behavior)
# - Provider updates could introduce breaking changes unexpectedly
# - Deployments could fail in CI/CD due to version mismatches
# - Difficult to reproduce issues (works on my machine, fails in CI)
# - No guarantee infrastructure code works after 6 months
#
# WITH VERSION CONSTRAINTS:
# - Consistent behavior across team and environments
# - Explicit upgrade decisions (controlled, tested, documented)
# - CI/CD uses same versions as local development
# - Infrastructure code remains functional over time
# - Easier troubleshooting (everyone on same versions)
#
# VERSION CONSTRAINT PHILOSOPHY:
#
# TOO STRICT (exact version):
# terraform {
#   required_version = "= 1.6.0"  # Only 1.6.0, nothing else
# }
#
# Pros:
# - Maximum consistency
# - No surprises from version changes
#
# Cons:
# - Cannot get bug fixes (stuck on 1.6.0 even if 1.6.1 fixes critical bug)
# - Manual version bumps required frequently
# - Blocks adoption of new features
# - Annoying for developers (must match exact version)
#
# TOO LOOSE (no constraints):
# terraform {
#   # No required_version specified
# }
#
# Pros:
# - No friction for developers
# - Automatically get latest features
#
# Cons:
# - Breaking changes break your code unexpectedly
# - Different developers use different versions
# - CI/CD might use different version than local
# - Infrastructure drift over time
#
# RECOMMENDED (balanced constraints):
# terraform {
#   required_version = ">= 1.6.0, < 2.0.0"
# }
#
# Pros:
# - Get patch releases automatically (1.6.1, 1.6.2, etc.)
# - Get minor releases automatically (1.7.0, 1.8.0, etc.)
# - Blocked from major version (2.0.0) which may have breaking changes
# - Flexibility with safety
#
# Cons:
# - Minor releases occasionally have breaking changes (rare but happens)
# - Still need to test before upgrading
#
# SEMANTIC VERSIONING:
# Terraform follows semantic versioning (semver): MAJOR.MINOR.PATCH
#
# MAJOR version (1.x.x → 2.x.x):
# - Breaking changes expected
# - Requires code updates
# - Examples: HCL syntax changes, resource behavior changes
# - Timeline: Years between major versions
#
# MINOR version (1.6.x → 1.7.x):
# - New features added
# - Should be backward compatible
# - Rarely breaks existing code
# - Examples: New functions, new resource types, new features
# - Timeline: Every few months
#
# PATCH version (1.6.0 → 1.6.1):
# - Bug fixes only
# - No new features
# - Always backward compatible
# - Examples: Fix crash, fix incorrect behavior
# - Timeline: As needed (days to weeks)
#
# TERRAFORM VERSION UPGRADE STRATEGY:
#
# PATCH RELEASES (1.6.0 → 1.6.1):
# - Upgrade immediately (bug fixes, no breaking changes)
# - No testing required (low risk)
# - Update terraform version in CI/CD
#
# MINOR RELEASES (1.6.0 → 1.7.0):
# - Review changelog first
# - Test in dev environment
# - Update version constraint: >= 1.7.0, < 2.0.0
# - Rollout: dev → staging → prod
# - Timeline: Within 1-2 months of release
#
# MAJOR RELEASES (1.x.x → 2.0.0):
# - Read upgrade guide thoroughly
# - Expect code changes required
# - Test extensively in isolated environment
# - Update version constraint: >= 2.0.0, < 3.0.0
# - Timeline: Plan for several weeks/months
# - May require infrastructure refactoring
#
# ==============================================================================

terraform {
  # TERRAFORM CLI VERSION
  #
  # Requires Terraform 1.6.0 or newer, but blocks Terraform 2.0.0 and above.
  #
  # WHY 1.6.0 AS MINIMUM:
  # - Testing: HCL functions and validation rules (1.6.0+)
  # - S3 backend: Server-side encryption improvements (1.5.0+)
  # - Performance: State locking improvements (1.5.0+)
  # - Language features: Optional attributes, type constraints (1.3.0+)
  #
  # WHAT BREAKS IF USING OLDER VERSIONS:
  # - 1.5.x: Missing some validation rules, slightly different behavior
  # - 1.4.x: Cannot use some variable validation patterns
  # - 1.3.x: Cannot use optional() in variable types
  # - 1.2.x and older: Significant language limitations, not recommended
  #
  # WHY BLOCK 2.0.0:
  # - Terraform 2.0.0 will likely have breaking changes
  # - This code may require updates to work with Terraform 2.0
  # - Explicit decision required to upgrade to 2.0 (not automatic)
  #
  # UPGRADE PATH:
  # When Terraform 2.0.0 is released:
  # 1. Read the Terraform 2.0 upgrade guide
  # 2. Test infrastructure code in isolated environment
  # 3. Make required code changes
  # 4. Update this constraint to: >= 2.0.0, < 3.0.0
  # 5. Test thoroughly before production rollout
  #
  # CHECKING TERRAFORM VERSION:
  # ```bash
  # terraform version
  # # Terraform v1.6.5
  # # on linux_amd64
  # ```
  #
  # INSTALLING SPECIFIC VERSION:
  # Option 1 - tfenv (Terraform version manager):
  # ```bash
  # tfenv install 1.6.5
  # tfenv use 1.6.5
  # ```
  #
  # Option 2 - Official downloads:
  # ```bash
  # wget https://releases.hashicorp.com/terraform/1.6.5/terraform_1.6.5_linux_amd64.zip
  # unzip terraform_1.6.5_linux_amd64.zip
  # sudo mv terraform /usr/local/bin/
  # ```
  #
  # Option 3 - Homebrew (macOS):
  # ```bash
  # brew install terraform@1.6
  # ```
  #
  # CI/CD CONFIGURATION:
  # Ensure CI/CD uses compatible Terraform version:
  #
  # GitHub Actions:
  # ```yaml
  # - uses: hashicorp/setup-terraform@v2
  #   with:
  #     terraform_version: 1.6.5
  # ```
  #
  # GitLab CI:
  # ```yaml
  # image:
  #   name: hashicorp/terraform:1.6.5
  # ```
  #
  # Docker:
  # ```dockerfile
  # FROM hashicorp/terraform:1.6.5
  # ```
  #
  required_version = ">= 1.6.0, < 2.0.0"

  # REQUIRED PROVIDERS
  #
  # Providers are plugins that Terraform uses to interact with APIs.
  # Each provider has its own version, independent of Terraform CLI version.
  #
  # PROVIDER VERSIONING STRATEGY:
  #
  # Similar to Terraform CLI, use optimistic constraints:
  # - Allow patch releases (bug fixes)
  # - Allow minor releases (new features, usually compatible)
  # - Block major releases (likely breaking changes)
  #
  # Example: ~> 5.0 means >= 5.0.0 and < 6.0.0
  #
  # WHY USE ~> (pessimistic constraint):
  # - Automatically get new features in 5.x releases
  # - Blocked from 6.0 which might break your code
  # - Balance between stability and staying current
  #
  # ALTERNATIVE CONSTRAINTS:
  # = 5.0.0    → Exact version only (too strict)
  # >= 5.0.0   → Any version 5.0.0 or higher (too loose, allows 10.0.0)
  # ~> 5.0.0   → Any 5.0.x (patch releases only, blocks 5.1.0)
  # ~> 5.0     → Any 5.x (minor + patch releases, blocks 6.0.0) ← RECOMMENDED
  #
  required_providers {
    # AWS PROVIDER
    #
    # Interacts with AWS APIs to manage resources (EC2, RDS, S3, etc.)
    #
    # VERSION: ~> 5.0
    # Allows: 5.0.0, 5.1.0, 5.50.0, etc.
    # Blocks: 6.0.0 and above
    #
    # WHY AWS PROVIDER 5.0+:
    # - Improved resource import (aws_s3_bucket split into modular resources)
    # - Better error messages and validation
    # - Support for newest AWS services and features
    # - Performance improvements (faster planning and applying)
    # - Bug fixes from 4.x releases
    #
    # WHAT CHANGED IN 5.0:
    # - S3 bucket resource refactored (aws_s3_bucket now minimal, features split)
    # - Some deprecated attributes removed
    # - Improved defaults for security (e.g., S3 public access block enabled)
    # - Better Terraform state handling
    #
    # If upgrading from 4.x to 5.x:
    # - Review upgrade guide: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/guides/version-5-upgrade
    # - S3 buckets require refactoring (most common breaking change)
    # - Test in non-production first
    #
    # PROVIDER SOURCE:
    # hashicorp/aws = registry.terraform.io/hashicorp/aws
    # - Registry: Terraform Registry (public)
    # - Namespace: hashicorp (publisher)
    # - Provider: aws (name)
    #
    # PROVIDER AUTHENTICATION:
    # AWS provider supports multiple authentication methods:
    # 1. Environment variables (recommended for local):
    #    export AWS_ACCESS_KEY_ID="..."
    #    export AWS_SECRET_ACCESS_KEY="..."
    #    export AWS_REGION="us-east-1"
    #
    # 2. AWS credentials file (~/.aws/credentials):
    #    [default]
    #    aws_access_key_id = ...
    #    aws_secret_access_key = ...
    #
    # 3. IAM role (recommended for EC2/ECS/Lambda):
    #    Instance profile automatically provides credentials
    #
    # 4. AWS SSO (recommended for humans):
    #    aws sso login --profile my-profile
    #    export AWS_PROFILE=my-profile
    #
    # DO NOT HARDCODE CREDENTIALS IN TERRAFORM FILES!
    # Never:
    # provider "aws" {
    #   access_key = "AKIAIOSFODNN7EXAMPLE"  # ❌ NEVER DO THIS
    #   secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # ❌ NEVER
    # }
    #
    # CHECKING PROVIDER VERSION:
    # ```bash
    # terraform version
    # # Provider Registry: registry.terraform.io
    # # - hashicorp/aws: 5.30.0
    # ```
    #
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    # RANDOM PROVIDER
    #
    # Generates random values (IDs, passwords, pet names, etc.)
    #
    # USE CASES IN THIS PROJECT:
    # - Random suffixes for globally-unique resource names (S3 buckets, IAM roles)
    # - Generate unique identifiers for tagging
    # - Create random passwords for initial setup (stored in Secrets Manager)
    #
    # WHY RANDOM PROVIDER:
    # Some AWS resources require globally unique names:
    # - S3 bucket names (unique across ALL AWS accounts worldwide)
    # - IAM role names (unique within account, but conflicts possible)
    # - CloudFront distribution CNAMEs
    #
    # Adding random suffix prevents naming conflicts:
    # - myapp-prod-static-assets → exists, cannot create
    # - myapp-prod-static-assets-a3b4c5d6 → unique, works
    #
    # RANDOM PROVIDER RESOURCES:
    # - random_id: Random bytes encoded as base64, hex, etc.
    # - random_string: Random string with customizable character set
    # - random_password: Random password (marked sensitive in state)
    # - random_pet: Random pet name (e.g., "heroic-llama")
    # - random_integer: Random number in specified range
    # - random_shuffle: Shuffle a list
    # - random_uuid: Random UUID (globally unique identifier)
    #
    # EXAMPLE USAGE:
    # ```hcl
    # resource "random_id" "bucket_suffix" {
    #   byte_length = 4  # 8 hex characters
    # }
    #
    # resource "aws_s3_bucket" "static_assets" {
    #   bucket = "${var.project_name}-${var.environment}-static-assets-${random_id.bucket_suffix.hex}"
    #   # Results in: myapp-prod-static-assets-a3b4c5d6
    # }
    # ```
    #
    # STATE HANDLING:
    # Random provider values are stored in Terraform state.
    # - First apply: Generate random value, store in state
    # - Subsequent applies: Use value from state (doesn't regenerate)
    # - Destroy: Value removed from state
    # - Recreate: New random value generated
    #
    # This ensures random values are stable (don't change on every apply).
    #
    # RANDOM PASSWORDS:
    # ```hcl
    # resource "random_password" "db_master_password" {
    #   length  = 32
    #   special = true
    # }
    #
    # resource "aws_db_instance" "main" {
    #   password = random_password.db_master_password.result
    #   # ...
    # }
    #
    # # Store in Secrets Manager for retrieval
    # resource "aws_secretsmanager_secret_version" "db_password" {
    #   secret_id     = aws_secretsmanager_secret.db_password.id
    #   secret_string = random_password.db_master_password.result
    # }
    # ```
    #
    # VERSION: ~> 3.0
    # - Stable provider, infrequent updates
    # - 3.x has been stable for years
    # - Unlikely to have breaking changes
    # - Pessimistic constraint provides safety
    #
    # SECURITY NOTE:
    # Random passwords generated by random_password are stored in Terraform state.
    # - Ensure state is encrypted (S3 backend with encryption)
    # - Restrict access to state files (IAM policies)
    # - Rotate passwords regularly (create new random_password, update resources)
    # - Consider AWS Secrets Manager rotation for production passwords
    #
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }

    # NULL PROVIDER
    #
    # Provides null_resource for running arbitrary local commands and triggers.
    #
    # USE CASES:
    # - Running local scripts during Terraform apply (e.g., database migrations)
    # - Triggering actions based on resource changes
    # - Waiting for external conditions (polling an API until ready)
    # - Running commands that don't fit into specific providers
    #
    # null_resource is a "fake" resource that doesn't manage real infrastructure
    # but can run provisioners (local-exec, remote-exec).
    #
    # EXAMPLE (run database migrations after RDS creation):
    # ```hcl
    # resource "null_resource" "db_migrations" {
    #   triggers = {
    #     db_endpoint = aws_db_instance.main.endpoint  # Re-run if endpoint changes
    #   }
    #
    #   provisioner "local-exec" {
    #     command = <<EOF
    #       PGPASSWORD=${random_password.db_password.result} psql \
    #         -h ${aws_db_instance.main.address} \
    #         -U ${var.db_username} \
    #         -d ${var.db_name} \
    #         -f migrations/001_initial_schema.sql
    #     EOF
    #   }
    #
    #   depends_on = [aws_db_instance.main]
    # }
    # ```
    #
    # TRIGGERS:
    # - Map of key-value pairs
    # - When any value changes, null_resource is destroyed and recreated
    # - Causes provisioners to run again
    # - Useful for re-running scripts when dependencies change
    #
    # ALTERNATIVES TO NULL RESOURCE:
    # - Use native resources when possible (better state management)
    # - Consider Terraform Cloud/Enterprise for workflows
    # - External scripts via CI/CD instead of Terraform
    # - Configuration management tools (Ansible, Chef) for complex provisioning
    #
    # WHEN TO USE:
    # ✅ One-time setup tasks (create database schema, upload initial data)
    # ✅ Waiting for external API (poll until resource ready)
    # ✅ Cleanup tasks (delete S3 objects before destroying bucket)
    #
    # WHEN NOT TO USE:
    # ❌ Ongoing configuration management (use Ansible, not Terraform)
    # ❌ Deployment of application code (use CI/CD, not Terraform)
    # ❌ Complex orchestration (use Step Functions, Airflow, etc.)
    #
    # VERSION: ~> 3.0
    # - Stable provider, minimal changes
    # - Simple functionality, low risk of breaking changes
    #
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }

    # ADDITIONAL PROVIDERS (for advanced scenarios)
    #
    # Uncomment and configure as needed:

    # # TLS PROVIDER
    # # Generate TLS certificates and keys
    # # Use case: Self-signed certs for testing, private CAs
    # tls = {
    #   source  = "hashicorp/tls"
    #   version = "~> 4.0"
    # }

    # # TIME PROVIDER
    # # Time-based resources (delays, sleep, rotating resources)
    # # Use case: Wait 5 minutes for DNS propagation before validation
    # time = {
    #   source  = "hashicorp/time"
    #   version = "~> 0.9"
    # }

    # # EXTERNAL PROVIDER
    # # Run external programs and use their output
    # # Use case: Query existing infrastructure not managed by Terraform
    # external = {
    #   source  = "hashicorp/external"
    #   version = "~> 2.0"
    # }

    # # HTTP PROVIDER
    # # Fetch data from HTTP APIs
    # # Use case: Get latest AMI version from vendor API
    # http = {
    #   source  = "hashicorp/http"
    #   version = "~> 3.0"
    # }
  }

  # TERRAFORM STATE BACKEND (OPTIONAL BUT RECOMMENDED)
  #
  # Commenting out here because backend configuration is typically in backend.tf
  # (separate file for better organization).
  #
  # However, it's valid to include backend configuration in versions.tf:
  #
  # backend "s3" {
  #   bucket         = "my-terraform-state"
  #   key            = "multi-tier-app/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
  #
  # See backend.tf for detailed backend configuration.
}

# PROVIDER CONFIGURATION BLOCKS
#
# The required_providers block above specifies which providers to download.
# The provider blocks below configure those providers.
#
# PATTERN:
# required_providers { aws = {...} }  → Download AWS provider
# provider "aws" {...}                → Configure AWS provider
#
# MULTIPLE CONFIGURATIONS (ALIASES):
# You can have multiple configurations of the same provider:
# - Different regions (us-east-1 for main resources, us-east-1 for ACM certs)
# - Different accounts (cross-account resource management)
# - Different authentication (different IAM roles)
#
# Example:
# provider "aws" {
#   region = var.aws_region  # Default provider
# }
#
# provider "aws" {
#   alias  = "us-east-1"  # Named provider alias
#   region = "us-east-1"  # Always us-east-1
# }
#
# resource "aws_acm_certificate" "cdn" {
#   provider = aws.us-east-1  # Use us-east-1 provider (required for CloudFront)
#   # ...
# }
#
# This is defined in a separate file (provider.tf) for better organization.
