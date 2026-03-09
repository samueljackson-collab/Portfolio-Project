###############################################################################
# Security Module - IAM Roles, Security Groups, KMS, and WAF
#
# This module creates security resources including:
# - IAM roles and policies for various AWS services
# - KMS keys for encryption
# - WAF Web ACL for CloudFront/ALB protection
# - Secrets Manager integration
###############################################################################

terraform {
  required_version = ">= 1.4"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

#------------------------------------------------------------------------------
# Data Sources
#------------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

#------------------------------------------------------------------------------
# KMS Key for General Encryption
#------------------------------------------------------------------------------

resource "aws_kms_key" "main" {
  count = var.create_kms_key ? 1 : 0

  description             = "KMS key for ${var.name_prefix} encryption"
  deletion_window_in_days = var.kms_deletion_window_days
  enable_key_rotation     = true
  multi_region            = var.kms_multi_region

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnableRootPermissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowCloudWatchLogs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:*"
          }
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-kms-key"
  })
}

resource "aws_kms_alias" "main" {
  count = var.create_kms_key ? 1 : 0

  name          = "alias/${var.name_prefix}-main"
  target_key_id = aws_kms_key.main[0].key_id
}

#------------------------------------------------------------------------------
# IAM Role for CI/CD Pipeline
#------------------------------------------------------------------------------

resource "aws_iam_role" "cicd" {
  count = var.create_cicd_role ? 1 : 0

  name = "${var.name_prefix}-cicd-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${var.oidc_provider_url}:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "${var.oidc_provider_url}:sub" = var.github_repo_pattern
          }
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "cicd_terraform" {
  count = var.create_cicd_role ? 1 : 0

  name = "${var.name_prefix}-terraform-policy"
  role = aws_iam_role.cicd[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "TerraformStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.terraform_state_bucket}",
          "arn:aws:s3:::${var.terraform_state_bucket}/*"
        ]
      },
      {
        Sid    = "TerraformLockAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${var.terraform_lock_table}"
      },
      {
        Sid    = "EC2FullAccess"
        Effect = "Allow"
        Action = [
          "ec2:*",
          "elasticloadbalancing:*",
          "autoscaling:*"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = data.aws_region.current.name
          }
        }
      },
      {
        Sid    = "RDSFullAccess"
        Effect = "Allow"
        Action = ["rds:*"]
        Resource = "*"
      },
      {
        Sid    = "S3FullAccess"
        Effect = "Allow"
        Action = ["s3:*"]
        Resource = "*"
      },
      {
        Sid    = "CloudFrontFullAccess"
        Effect = "Allow"
        Action = ["cloudfront:*"]
        Resource = "*"
      },
      {
        Sid    = "IAMPassRole"
        Effect = "Allow"
        Action = [
          "iam:PassRole",
          "iam:GetRole",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:GetRolePolicy",
          "iam:CreateInstanceProfile",
          "iam:DeleteInstanceProfile",
          "iam:AddRoleToInstanceProfile",
          "iam:RemoveRoleFromInstanceProfile",
          "iam:GetInstanceProfile"
        ]
        Resource = "*"
      },
      {
        Sid    = "KMSAccess"
        Effect = "Allow"
        Action = [
          "kms:CreateKey",
          "kms:CreateAlias",
          "kms:DeleteAlias",
          "kms:DescribeKey",
          "kms:EnableKey",
          "kms:DisableKey",
          "kms:GetKeyPolicy",
          "kms:PutKeyPolicy",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:ScheduleKeyDeletion"
        ]
        Resource = "*"
      },
      {
        Sid    = "CloudWatchAccess"
        Effect = "Allow"
        Action = [
          "cloudwatch:*",
          "logs:*"
        ]
        Resource = "*"
      }
    ]
  })
}

#------------------------------------------------------------------------------
# IAM Role for Application
#------------------------------------------------------------------------------

resource "aws_iam_role" "application" {
  count = var.create_application_role ? 1 : 0

  name = "${var.name_prefix}-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "app_ssm" {
  count = var.create_application_role ? 1 : 0

  role       = aws_iam_role.application[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "app_cloudwatch" {
  count = var.create_application_role ? 1 : 0

  role       = aws_iam_role.application[0].name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy" "app_secrets" {
  count = var.create_application_role && length(var.secrets_arns) > 0 ? 1 : 0

  name = "${var.name_prefix}-secrets-policy"
  role = aws_iam_role.application[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ]
      Resource = var.secrets_arns
    }]
  })
}

resource "aws_iam_instance_profile" "application" {
  count = var.create_application_role ? 1 : 0

  name = "${var.name_prefix}-app-profile"
  role = aws_iam_role.application[0].name

  tags = var.tags
}

#------------------------------------------------------------------------------
# Secrets Manager Secret (for database credentials)
#------------------------------------------------------------------------------

resource "aws_secretsmanager_secret" "db_credentials" {
  count = var.create_db_secret ? 1 : 0

  name        = "${var.name_prefix}/db-credentials"
  description = "Database credentials for ${var.name_prefix}"
  kms_key_id  = var.create_kms_key ? aws_kms_key.main[0].arn : var.kms_key_arn

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  count = var.create_db_secret ? 1 : 0

  secret_id = aws_secretsmanager_secret.db_credentials[0].id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
    host     = var.db_host
    port     = var.db_port
    dbname   = var.db_name
  })
}

#------------------------------------------------------------------------------
# WAF Web ACL
#------------------------------------------------------------------------------

resource "aws_wafv2_web_acl" "main" {
  count = var.create_waf_acl ? 1 : 0

  name        = "${var.name_prefix}-waf"
  description = "WAF rules for ${var.name_prefix}"
  scope       = var.waf_scope

  default_action {
    allow {}
  }

  # AWS Managed Rules - Common Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.name_prefix}-common-rules"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - Known Bad Inputs
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.name_prefix}-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - SQL Injection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.name_prefix}-sqli"
      sampled_requests_enabled   = true
    }
  }

  # Rate Limiting Rule
  rule {
    name     = "RateLimitRule"
    priority = 4

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.waf_rate_limit
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.name_prefix}-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.name_prefix}-waf"
    sampled_requests_enabled   = true
  }

  tags = var.tags
}

#------------------------------------------------------------------------------
# Security Group - Bastion Host
#------------------------------------------------------------------------------

resource "aws_security_group" "bastion" {
  count = var.create_bastion_sg ? 1 : 0

  name        = "${var.name_prefix}-bastion-sg"
  description = "Security group for bastion host"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from allowed IPs"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.bastion_allowed_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-bastion-sg"
  })
}
