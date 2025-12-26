# ==============================================================================
# TERRAFORM DATA SOURCES
# ==============================================================================
#
# PURPOSE:
# Data sources allow Terraform to query and use information from external systems:
# - AWS APIs (query existing infrastructure)
# - Other Terraform state files (terraform_remote_state)
# - External programs (external data source)
# - HTTP APIs (http data source)
# - Local files (local_file, template_file)
#
# DATA SOURCES VS RESOURCES:
#
# RESOURCES (resource "aws_vpc" "main"):
# - Create, update, delete infrastructure
# - Terraform manages lifecycle
# - Changes require terraform apply
# - Examples: aws_instance, aws_s3_bucket, aws_rds_instance
# - Use when: You want Terraform to create and manage something
#
# DATA SOURCES (data "aws_ami" "amazon_linux"):
# - Read-only queries to external systems
# - Terraform does NOT manage lifecycle
# - No changes (cannot create, update, or delete)
# - Examples: aws_availability_zones, aws_ami, aws_caller_identity
# - Use when: You need information from AWS without managing the resource
#
# EXAMPLE SHOWING THE DIFFERENCE:
#
# resource "aws_vpc" "main" {
#   # Terraform CREATES this VPC
#   # Terraform OWNS this VPC (updates, deletes)
#   cidr_block = "10.0.0.0/16"
# }
#
# data "aws_vpc" "existing" {
#   # Terraform QUERIES existing VPC (doesn't create)
#   # Terraform does NOT own it (cannot update or delete)
#   filter {
#     name   = "tag:Name"
#     values = ["legacy-vpc"]
#   }
# }
#
# # Use data source to reference existing VPC
# resource "aws_subnet" "new_subnet" {
#   vpc_id = data.aws_vpc.existing.id  # Reference existing VPC
#   # ...
# }
#
# WHY USE DATA SOURCES:
#
# 1. QUERY DYNAMIC INFORMATION:
#    - Latest AMI ID (changes when new version released)
#    - Available availability zones (different per region)
#    - Current AWS account ID (different per account)
#    - IP address of current machine (changes if running from different location)
#
# 2. REFERENCE EXISTING INFRASTRUCTURE:
#    - VPC created manually or by different Terraform config
#    - IAM roles created by security team
#    - KMS keys managed centrally
#    - Route53 zones managed separately
#
# 3. CROSS-STACK REFERENCES:
#    - Network stack (VPC, subnets) managed separately
#    - Application stack references network stack via terraform_remote_state
#    - Database stack references both network and application stacks
#
# 4. ENVIRONMENT-SPECIFIC VALUES:
#    - Different AMIs per region (query latest instead of hardcoding)
#    - Different availability zones per region (query instead of hardcoding)
#
# ==============================================================================

# AVAILABILITY ZONES
#
# Query available availability zones in the current region.
#
# WHY QUERY AZS DYNAMICALLY:
#
# Problem with hardcoding:
# ```hcl
# variable "azs" {
#   default = ["us-east-1a", "us-east-1b", "us-east-1c"]
# }
# ```
# - Only works in us-east-1
# - Breaks if deployed to eu-west-1 (different AZ names)
# - Requires per-region configuration
#
# Solution with data source:
# ```hcl
# data "aws_availability_zones" "available" {
#   state = "available"
# }
#
# locals {
#   azs = slice(data.aws_availability_zones.available.names, 0, var.azs_count)
# }
# ```
# - Works in any region (queries current region's AZs)
# - No hardcoded AZ names
# - Automatically adapts to regional differences
#
# ATTRIBUTES:
# - names: List of AZ names ["us-east-1a", "us-east-1b", ...]
# - zone_ids: List of AZ IDs ["use1-az1", "use1-az2", ...] (stable, don't change)
# - group_name: Region name "us-east-1"
#
# WHY zone_ids EXIST:
# AZ names (us-east-1a) are not consistent across accounts!
# - Your us-east-1a might be my us-east-1b (AWS randomizes mapping)
# - zone_ids are consistent (use1-az1 is always same physical AZ)
# - Use zone_ids for cross-account AZ consistency
#
# FILTERS:
#
# state = "available":
# - Only AZs currently accepting new resources
# - Excludes AZs that are constrained or unavailable
# - Rare, but some AZs are sometimes unavailable (AWS capacity issues)
#
# exclude_names = ["us-east-1e"]:
# - Exclude specific AZs (if you know certain AZ has issues)
# - Example: us-east-1e had historical capacity problems
#
# exclude_zone_ids = ["use1-az3"]:
# - Exclude by zone ID
#
# USAGE:
# See locals.tf where we use this:
# local.azs = slice(data.aws_availability_zones.available.names, 0, var.azs_count)
#
data "aws_availability_zones" "available" {
  state = "available"

  # Optional filters:
  # Uncomment if you want to exclude specific AZs

  # exclude_names = ["us-east-1e"]  # Exclude specific AZ names

  # exclude_zone_ids = ["use1-az3"]  # Exclude specific zone IDs

  # filter {
  #   name   = "opt-in-status"
  #   values = ["opt-in-not-required"]  # Only default AZs (exclude opt-in AZs)
  # }
}

# CURRENT AWS CALLER IDENTITY
#
# Query information about the AWS identity making Terraform API calls.
#
# ATTRIBUTES:
# - account_id: AWS account ID (12 digits)
# - arn: ARN of the calling identity (user or role)
# - user_id: Unique identifier for the calling identity
#
# USE CASES:
#
# 1. ACCOUNT ID IN RESOURCE NAMES OR ARNS:
#    Many resources require or benefit from including account ID:
#
#    S3 bucket name (must be globally unique):
#    resource "aws_s3_bucket" "example" {
#      bucket = "${var.project_name}-${data.aws_caller_identity.current.account_id}-logs"
#      # Results in: myapp-123456789012-logs (unique across all AWS accounts)
#    }
#
#    IAM policy with ARN:
#    data "aws_iam_policy_document" "example" {
#      statement {
#        principals {
#           type        = "AWS"
#          identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
#        }
#      }
#    }
#
# 2. CROSS-ACCOUNT ACCESS:
#    Verify you're operating in correct account:
#
#    resource "aws_s3_bucket_policy" "example" {
#      # Only allow access from specific account
#      condition {
#        test     = "StringEquals"
#        variable = "aws:PrincipalAccount"
#        values   = [data.aws_caller_identity.current.account_id]
#      }
#    }
#
# 3. TAGGING:
#    Include account ID in tags for multi-account organizations:
#
#    tags = {
#      AccountID = data.aws_caller_identity.current.account_id
#    }
#
# 4. CONDITIONAL LOGIC:
#    Different behavior based on account:
#
#    locals {
#      is_production_account = data.aws_caller_identity.current.account_id == "123456789012"
#      enable_advanced_features = local.is_production_account
#    }
#
# 5. DEBUGGING:
#    Print account info for verification:
#
#    output "current_account_id" {
#      value = data.aws_caller_identity.current.account_id
#    }
#    # Outputs: current_account_id = "123456789012"
#
# NO AUTHENTICATION REQUIRED:
# This data source uses the same AWS credentials as Terraform itself.
# If Terraform can authenticate to AWS, this data source will work.
#
# EXAMPLES OF WHAT YOU'LL SEE:
#
# IAM user:
# - account_id: "123456789012"
# - arn: "arn:aws:iam::123456789012:user/john"
# - user_id: "AIDAI..." (unique ID)
#
# IAM role (EC2 instance profile):
# - account_id: "123456789012"
# - arn: "arn:aws:sts::123456789012:assumed-role/TerraformRole/i-1234567890abcdef0"
# - user_id: "AROAI..." (unique ID)
#
# IAM role (AssumeRole):
# - account_id: "123456789012"
# - arn: "arn:aws:sts::123456789012:assumed-role/AdminRole/session-name"
# - user_id: "AROAI..."
#
# AWS SSO:
# - account_id: "123456789012"
# - arn: "arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_Admin_.../john@example.com"
# - user_id: "AROAI..."
#
data "aws_caller_identity" "current" {}

# LATEST AMAZON LINUX 2023 AMI
#
# Query the latest Amazon Linux 2023 AMI ID for EC2 instances.
#
# WHY QUERY AMI DYNAMICALLY:
#
# Problem with hardcoding:
# ```hcl
# resource "aws_instance" "web" {
#   ami = "ami-0abcdef1234567890"  # Hardcoded AMI ID
# }
# ```
# - AMI IDs are region-specific (different ID per region)
# - AMI IDs change when new version released
# - Requires manual updates (check for new AMI every month)
# - Might use outdated AMI with security vulnerabilities
#
# Solution with data source:
# ```hcl
# data "aws_ami" "amazon_linux_2023" {
#   most_recent = true
#   owners      = ["amazon"]
#   filter {
#     name   = "name"
#     values = ["al2023-ami-*-x86_64"]
#   }
# }
#
# resource "aws_instance" "web" {
#   ami = data.aws_ami.amazon_linux_2023.id  # Always latest AMI
# }
# ```
# - Works in any region (queries region-specific AMI)
# - Always uses latest AMI (automatic security updates)
# - No manual updates needed
#
# FILTERS:
#
# most_recent = true:
# - Returns only the newest AMI matching filters
# - Without this, might get old AMI version
#
# owners = ["amazon"]:
# - Only AMIs owned by Amazon (official AMIs)
# - Prevents accidental use of community/marketplace AMIs
# - Other owner options:
#   - ["self"]: Your own AMIs
#   - ["aws-marketplace"]: AWS Marketplace AMIs
#   - ["123456789012"]: Specific account ID
#
# filter name = "name":
# - Match AMI name pattern
# - al2023-ami-*-x86_64: Amazon Linux 2023 for x86_64
# - al2023-ami-*-arm64: Amazon Linux 2023 for ARM (Graviton)
# - Wildcard (*) matches any version number
#
# filter virtualization-type = "hvm":
# - Hardware Virtual Machine (modern virtualization)
# - Alternative: "paravirtual" (legacy, not recommended)
# - All modern instance types require HVM
#
# filter root-device-type = "ebs":
# - Root volume is EBS (Elastic Block Store)
# - Alternative: "instance-store" (ephemeral, loses data on stop)
# - EBS is recommended (persistent storage)
#
# COMMON AMI PATTERNS:
#
# Amazon Linux 2023 (recommended for new projects):
# filter {
#   name   = "name"
#   values = ["al2023-ami-*-x86_64"]
# }
#
# Amazon Linux 2 (stable, long-term support):
# filter {
#   name   = "name"
#   values = ["amzn2-ami-hvm-*-x86_64-gp2"]
# }
#
# Ubuntu 22.04 LTS:
# data "aws_ami" "ubuntu" {
#   owners      = ["099720109477"]  # Canonical's AWS account ID
#   most_recent = true
#   filter {
#     name   = "name"
#     values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
#   }
# }
#
# Red Hat Enterprise Linux 9:
# data "aws_ami" "rhel" {
#   owners      = ["309956199498"]  # Red Hat's AWS account ID
#   most_recent = true
#   filter {
#     name   = "name"
#     values = ["RHEL-9*_HVM-*-x86_64-*"]
#   }
# }
#
# Windows Server 2022:
# data "aws_ami" "windows" {
#   owners      = ["amazon"]
#   most_recent = true
#   filter {
#     name   = "name"
#     values = ["Windows_Server-2022-English-Full-Base-*"]
#   }
# }
#
# ATTRIBUTES:
# - id: AMI ID (ami-0abcdef1234567890)
# - name: AMI name (al2023-ami-2023.3.20240108.0-kernel-6.1-x86_64)
# - description: AMI description
# - creation_date: When AMI was created (ISO 8601 format)
# - architecture: x86_64 or arm64
# - image_location: S3 bucket location of AMI
# - root_device_name: /dev/xvda or /dev/sda1
# - virtualization_type: hvm or paravirtual
#
# USAGE:
# resource "aws_launch_template" "web" {
#   image_id = data.aws_ami.amazon_linux_2023.id
#   # ...
# }
#
# AMI VERSIONING:
# Amazon releases new AMIs regularly (monthly security updates).
# Using this data source ensures you always get latest security patches.
#
# CAVEATS:
# - AMI ID changes on every terraform plan (new AMI released)
# - Might trigger instance replacement if using in aws_instance directly
# - For production, consider pinning to specific AMI version (stability)
# - Or use launch templates with update strategy (rolling updates)
#
# PINNING TO SPECIFIC VERSION (stability):
# filter {
#   name   = "name"
#   values = ["al2023-ami-2023.3.20240108.0-kernel-6.1-x86_64"]  # Exact version
# }
#
# BALANCE (security + stability):
# Use data source in launch template, not directly in instance:
# - Launch template can be updated without replacing instances
# - Auto Scaling Group can roll out new AMI gradually
# - Instances stay on same AMI until ASG refresh triggered
#
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  # Optional: Filter by specific kernel version
  # filter {
  #   name   = "name"
  #   values = ["al2023-ami-*-kernel-6.1-x86_64"]
  # }

  # Optional: Filter by architecture (if you want ARM)
  # filter {
  #   name   = "architecture"
  #   values = ["arm64"]  # For Graviton instances
  # }
}

# CURRENT AWS REGION
#
# Query the current AWS region.
#
# While we have var.aws_region, this data source provides the ACTUAL region
# being used (useful for validation, multi-region setups, debugging).
#
# USE CASES:
#
# 1. VALIDATION:
#    Ensure provider region matches variable:
#
#    locals {
#      region_mismatch = var.aws_region != data.aws_region.current.name
#    }
#
#    # Can add validation or output warning
#
# 2. DYNAMIC REGION-SPECIFIC CONFIGURATION:
#    Different settings based on region:
#
#    locals {
#      is_us_east_1 = data.aws_region.current.name == "us-east-1"
#      # CloudFront certificates must be in us-east-1
#      acm_region = local.is_us_east_1 ? "us-east-1" : data.aws_region.current.name
#    }
#
# 3. MULTI-REGION DEPLOYMENTS:
#    Building resources in multiple regions:
#
#    provider "aws" {
#      alias  = "us-west-2"
#      region = "us-west-2"
#    }
#
#    data "aws_region" "us_west_2" {
#      provider = aws.us-west-2
#    }
#
# 4. TAGGING:
#    Include region in resource tags:
#
#    tags = {
#      Region = data.aws_region.current.name
#    }
#
# ATTRIBUTES:
# - name: Region name (us-east-1, eu-west-1, etc.)
# - description: Region description ("US East (N. Virginia)", etc.)
# - endpoint: EC2 endpoint for region (ec2.us-east-1.amazonaws.com)
#
data "aws_region" "current" {}

# EXISTING ROUTE53 ZONE (OPTIONAL)
#
# Query existing Route53 hosted zone if you have a domain managed separately.
#
# SCENARIO:
# - Domain registered outside Terraform (manual, different team, etc.)
# - Route53 hosted zone already exists
# - Terraform needs to create DNS records in this zone
#
# EXAMPLE:
# ```hcl
# data "aws_route53_zone" "main" {
#   name         = "example.com."  # Note trailing dot!
#   private_zone = false
# }
#
# resource "aws_route53_record" "www" {
#   zone_id = data.aws_route53_zone.main.zone_id  # Reference existing zone
#   name    = "www.example.com"
#   type    = "A"
#   alias {
#     name                   = module.alb.alb_dns_name
#     zone_id                = module.alb.alb_zone_id
#     evaluate_target_health = true
#   }
# }
# ```
#
# Uncomment if you have existing Route53 zone:
#
# data "aws_route53_zone" "main" {
#   name         = "${var.domain_name}."  # Trailing dot is important!
#   private_zone = false
#
#   # Optional filters:
#   # vpc_id = "vpc-12345678"  # For private hosted zones
#   # tags = {
#     # Environment = var.environment
#   # }
# }

# KMS KEY FOR ENCRYPTION (OPTIONAL)
#
# Query existing KMS key for encrypting resources (RDS, S3, etc.).
#
# SCENARIO:
# - Security team manages KMS keys centrally
# - Keys created outside Terraform (compliance requirement)
# - Terraform resources use these keys for encryption
#
# EXAMPLE:
# ```hcl
# data "aws_kms_key" "rds" {
#   key_id = "alias/rds-encryption-key"  # Reference by alias
# }
#
# resource "aws_db_instance" "main" {
#   kms_key_id = data.aws_kms_key.rds.arn
#   # ...
# }
# ```
#
# Uncomment if you have existing KMS keys:
#
# data "aws_kms_key" "rds_encryption" {
#   key_id = "alias/${var.project_name}-rds-encryption"
# }
#
# data "aws_kms_key" "s3_encryption" {
#   key_id = "alias/${var.project_name}-s3-encryption"
# }

# EXISTING VPC (FOR DEPLOYING INTO EXISTING NETWORK)
#
# Query existing VPC if deploying application into pre-existing network.
#
# SCENARIO:
# - Network layer (VPC, subnets, routing) managed separately
# - Application layer (ALB, ASG, RDS) managed by this Terraform config
# - Application needs to reference existing VPC and subnets
#
# EXAMPLE:
# ```hcl
# data "aws_vpc" "main" {
#   filter {
#     name   = "tag:Name"
#     values = ["${var.project_name}-${var.environment}-vpc"]
#   }
# }
#
# data "aws_subnets" "private" {
#   filter {
#     name   = "vpc-id"
#     values = [data.aws_vpc.main.id]
#   }
#   filter {
#     name   = "tag:Type"
#     values = ["private"]
#   }
# }
#
# # Use existing VPC and subnets
# resource "aws_security_group" "app" {
#   vpc_id = data.aws_vpc.main.id
#   # ...
# }
#
# resource "aws_autoscaling_group" "app" {
#   vpc_zone_identifier = data.aws_subnets.private.ids
#   # ...
# }
# ```
#
# Uncomment if deploying into existing VPC:
#
# data "aws_vpc" "existing" {
#   filter {
#     name   = "tag:Name"
#     values = ["${var.project_name}-${var.environment}-vpc"]
#   }
#
#   # Alternative: Reference by ID
#   # id = var.vpc_id
# }
#
# data "aws_subnets" "private" {
#   filter {
#     name   = "vpc-id"
#     values = [data.aws_vpc.existing.id]
#   }
#   filter {
#     name   = "tag:Tier"
#     values = ["private"]
#   }
# }
#
# data "aws_subnets" "public" {
#   filter {
#     name   = "vpc-id"
#     values = [data.aws_vpc.existing.id]
#   }
#   filter {
#     name   = "tag:Tier"
#     values = ["public"]
#   }
# }

# TERRAFORM REMOTE STATE (FOR CROSS-STACK REFERENCES)
#
# Query outputs from another Terraform configuration (state file).
#
# SCENARIO:
# - Infrastructure split into multiple Terraform configs (layered approach)
# - Network layer: VPC, subnets, routing
# - Security layer: IAM roles, KMS keys, security groups
# - Application layer: ALB, ASG, RDS
# - Each layer has separate state file
# - Application layer needs outputs from network layer
#
# EXAMPLE:
# ```hcl
# # In network/ Terraform config:
# output "vpc_id" {
#   value = aws_vpc.main.id
# }
# output "private_subnet_ids" {
#   value = aws_subnet.private[*].id
# }
#
# # In application/ Terraform config:
# data "terraform_remote_state" "network" {
#   backend = "s3"
#   config = {
#     bucket = "myapp-terraform-state"
#     key    = "network/${var.environment}/terraform.tfstate"
#     region = "us-east-1"
#   }
# }
#
# resource "aws_security_group" "app" {
#   vpc_id = data.terraform_remote_state.network.outputs.vpc_id  # From network layer
# }
#
# resource "aws_autoscaling_group" "app" {
#   vpc_zone_identifier = data.terraform_remote_state.network.outputs.private_subnet_ids
# }
# ```
#
# Uncomment if using layered Terraform approach:
#
# data "terraform_remote_state" "network" {
#   backend = "s3"
#   config = {
#     bucket = var.state_bucket
#     key    = "network/${var.environment}/terraform.tfstate"
#     region = var.aws_region
#   }
# }
#
# data "terraform_remote_state" "security" {
#   backend = "s3"
#   config = {
#     bucket = var.state_bucket
#     key    = "security/${var.environment}/terraform.tfstate"
#     region = var.aws_region
#   }
# }

# DATA SOURCE BEST PRACTICES:
#
# 1. ALWAYS FILTER PRECISELY:
#    Don't rely on defaults or assumptions:
#    ❌ Bad:
#    data "aws_ami" "app" {
#      owners = ["amazon"]
#      # Might return unexpected AMI
#    }
#    ✅ Good:
#    data "aws_ami" "app" {
#      owners      = ["amazon"]
#      most_recent = true
#      filter {
#        name   = "name"
#        values = ["al2023-ami-*-x86_64"]
#      }
#      filter {
#        name   = "virtualization-type"
#        values = ["hvm"]
#      }
#    }
#
# 2. HANDLE MISSING DATA:
#    Data source fails if no matching resource found:
#    data "aws_vpc" "main" {
#      filter {
#        name   = "tag:Name"
#        values = ["nonexistent-vpc"]  # ❌ Errors if VPC doesn't exist
#      }
#    }
#
#    Solution: Use count to make data source optional:
#    data "aws_vpc" "main" {
#      count = var.use_existing_vpc ? 1 : 0
#      filter {
#        name   = "tag:Name"
#        values = [var.existing_vpc_name]
#      }
#    }
#
# 3. COMMENT DATA SOURCE DEPENDENCIES:
#    Explain why data source is needed:
#    # Query latest AMI for Auto Scaling launch template
#    # Ensures instances use up-to-date security patches
#    data "aws_ami" "app" {
#      # ...
#    }
#
# 4. VALIDATE DATA SOURCE RESULTS:
#    Use outputs to verify data source returned expected value:
#    output "ami_id" {
#      value = data.aws_ami.amazon_linux_2023.id
#      description = "Verify correct AMI is selected"
#    }
#
# The data sources defined here provide foundation for the infrastructure.
# Additional data sources can be added as needed for specific modules.
