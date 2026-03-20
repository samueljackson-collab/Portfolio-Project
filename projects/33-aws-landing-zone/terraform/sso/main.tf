terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
  }
  required_version = ">= 1.5"
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------
# Data sources — look up the IAM Identity Center instance and account IDs
# ---------------------------------------------------------------------------

data "aws_ssoadmin_instances" "main" {}

locals {
  sso_instance_arn = tolist(data.aws_ssoadmin_instances.main.arns)[0]
  identity_store_id = tolist(data.aws_ssoadmin_instances.main.identity_store_ids)[0]
}

# ---------------------------------------------------------------------------
# Permission Sets
# ---------------------------------------------------------------------------

resource "aws_ssoadmin_permission_set" "administrator_access" {
  name             = "AdministratorAccess"
  description      = "Full administrator access — for break-glass and platform team"
  instance_arn     = local.sso_instance_arn
  session_duration = "PT4H"

  tags = {
    ManagedBy = "terraform"
    Scope     = "full-admin"
  }
}

resource "aws_ssoadmin_managed_policy_attachment" "administrator_access" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.administrator_access.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# ---------------------------------------------------------------------------

resource "aws_ssoadmin_permission_set" "read_only_access" {
  name             = "ReadOnlyAccess"
  description      = "Read-only visibility across all services — for auditors and stakeholders"
  instance_arn     = local.sso_instance_arn
  session_duration = "PT8H"

  tags = {
    ManagedBy = "terraform"
    Scope     = "read-only"
  }
}

resource "aws_ssoadmin_managed_policy_attachment" "read_only_access" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.read_only_access.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# ---------------------------------------------------------------------------

resource "aws_ssoadmin_permission_set" "devops_access" {
  name             = "DevOpsAccess"
  description      = "EC2, ECS, EKS, Lambda, S3, RDS, CloudWatch — for DevOps/platform engineers"
  instance_arn     = local.sso_instance_arn
  session_duration = "PT8H"

  tags = {
    ManagedBy = "terraform"
    Scope     = "devops"
  }
}

resource "aws_ssoadmin_permission_set_inline_policy" "devops_access" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.devops_access.arn
  inline_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DevOpsComputeAccess"
        Effect = "Allow"
        Action = [
          "ec2:*",
          "ecs:*",
          "eks:*",
          "lambda:*",
          "ecr:*",
          "autoscaling:*",
          "elasticloadbalancing:*",
        ]
        Resource = "*"
      },
      {
        Sid    = "DevOpsStorageAccess"
        Effect = "Allow"
        Action = [
          "s3:*",
          "rds:*",
          "elasticache:*",
          "dynamodb:*",
        ]
        Resource = "*"
      },
      {
        Sid    = "DevOpsObservabilityAccess"
        Effect = "Allow"
        Action = [
          "cloudwatch:*",
          "logs:*",
          "xray:*",
          "sns:*",
          "sqs:*",
        ]
        Resource = "*"
      },
      {
        Sid    = "DevOpsCICDAccess"
        Effect = "Allow"
        Action = [
          "codepipeline:*",
          "codebuild:*",
          "codedeploy:*",
          "codestar-connections:*",
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyIAMWrite"
        Effect = "Deny"
        Action = [
          "iam:CreateUser",
          "iam:DeleteUser",
          "iam:AttachUserPolicy",
          "iam:CreateAccessKey",
          "organizations:*",
        ]
        Resource = "*"
      },
    ]
  })
}

# ---------------------------------------------------------------------------

resource "aws_ssoadmin_permission_set" "security_audit_access" {
  name             = "SecurityAuditAccess"
  description      = "Security audit tools: GuardDuty, SecurityHub, Config, CloudTrail, IAM read"
  instance_arn     = local.sso_instance_arn
  session_duration = "PT4H"

  tags = {
    ManagedBy = "terraform"
    Scope     = "security-audit"
  }
}

resource "aws_ssoadmin_managed_policy_attachment" "security_audit_access" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.security_audit_access.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}

resource "aws_ssoadmin_permission_set_inline_policy" "security_audit_access" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.security_audit_access.arn
  inline_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "SecurityToolsReadAccess"
        Effect = "Allow"
        Action = [
          "guardduty:Get*",
          "guardduty:List*",
          "securityhub:Get*",
          "securityhub:List*",
          "securityhub:Describe*",
          "config:Get*",
          "config:List*",
          "config:Describe*",
          "cloudtrail:Get*",
          "cloudtrail:List*",
          "cloudtrail:Describe*",
          "access-analyzer:Get*",
          "access-analyzer:List*",
          "inspector2:Get*",
          "inspector2:List*",
        ]
        Resource = "*"
      },
    ]
  })
}

# ---------------------------------------------------------------------------
# Account assignments
# ---------------------------------------------------------------------------

# AdministratorAccess → management account (platform team group)
resource "aws_ssoadmin_account_assignment" "admin_management" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.administrator_access.arn

  principal_type = "GROUP"
  principal_id   = var.platform_team_group_id

  target_type = "AWS_ACCOUNT"
  target_id   = var.management_account_id
}

# AdministratorAccess → shared-services account (platform team)
resource "aws_ssoadmin_account_assignment" "admin_shared_services" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.administrator_access.arn

  principal_type = "GROUP"
  principal_id   = var.platform_team_group_id

  target_type = "AWS_ACCOUNT"
  target_id   = var.shared_services_account_id
}

# ReadOnlyAccess → security-audit account (auditor group)
resource "aws_ssoadmin_account_assignment" "readonly_security_audit" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.read_only_access.arn

  principal_type = "GROUP"
  principal_id   = var.auditor_group_id

  target_type = "AWS_ACCOUNT"
  target_id   = var.security_audit_account_id
}

# ReadOnlyAccess → log-archive account (auditor group)
resource "aws_ssoadmin_account_assignment" "readonly_log_archive" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.read_only_access.arn

  principal_type = "GROUP"
  principal_id   = var.auditor_group_id

  target_type = "AWS_ACCOUNT"
  target_id   = var.log_archive_account_id
}

# DevOpsAccess → shared-services account (devops team group)
resource "aws_ssoadmin_account_assignment" "devops_shared_services" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.devops_access.arn

  principal_type = "GROUP"
  principal_id   = var.devops_team_group_id

  target_type = "AWS_ACCOUNT"
  target_id   = var.shared_services_account_id
}

# DevOpsAccess → sandbox-dev account (devops team group)
resource "aws_ssoadmin_account_assignment" "devops_sandbox" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.devops_access.arn

  principal_type = "GROUP"
  principal_id   = var.devops_team_group_id

  target_type = "AWS_ACCOUNT"
  target_id   = var.sandbox_dev_account_id
}

# SecurityAuditAccess → security-audit account (security team)
resource "aws_ssoadmin_account_assignment" "security_audit_assignment" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.security_audit_access.arn

  principal_type = "GROUP"
  principal_id   = var.security_team_group_id

  target_type = "AWS_ACCOUNT"
  target_id   = var.security_audit_account_id
}
