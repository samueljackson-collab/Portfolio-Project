# =====================================================
# AWS Secrets Manager Module
# =====================================================
# Creates and manages secrets in AWS Secrets Manager for
# database passwords and other sensitive configuration
#
# Features:
# - Automatic secret rotation (optional)
# - KMS encryption
# - Secret versioning
# - Recovery window for deleted secrets
# - Tags for organization

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# Generate a random password if one is not provided
resource "random_password" "secret_value" {
  count = var.secret_value == null ? 1 : 0

  length  = var.password_length
  special = true
  # Exclude characters that might cause issues in connection strings
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Create the secret
resource "aws_secretsmanager_secret" "this" {
  name        = var.secret_name
  description = var.description

  # Use KMS encryption if key ARN is provided, otherwise use default encryption
  kms_key_id = var.kms_key_id

  # Recovery window for deleted secrets (7-30 days, 0 for immediate deletion)
  recovery_window_in_days = var.recovery_window_in_days

  # Enable or disable automatic rotation
  # Note: Requires Lambda function to implement rotation
  # See: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
  rotation_rules {
    automatically_after_days = var.enable_rotation ? var.rotation_days : 0
  }

  tags = merge(
    var.tags,
    {
      Name        = var.secret_name
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  )
}

# Store the secret value
resource "aws_secretsmanager_secret_version" "this" {
  secret_id = aws_secretsmanager_secret.this.id

  # Use provided secret value or generated random password
  secret_string = var.secret_value != null ? var.secret_value : random_password.secret_value[0].result

  # Lifecycle to prevent replacement on every apply
  lifecycle {
    ignore_changes = [
      secret_string,
    ]
  }
}

# Optional: Create rotation Lambda function if rotation is enabled
# This is a placeholder - implement based on database type
resource "aws_lambda_function" "rotation" {
  count = var.enable_rotation ? 1 : 0

  function_name = "${var.secret_name}-rotation"
  description   = "Rotates ${var.secret_name} secret"
  role          = aws_iam_role.rotation[0].arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30

  # Placeholder code - implement actual rotation logic
  filename         = "${path.module}/lambda/rotation.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/rotation.zip")

  environment {
    variables = {
      SECRET_ARN = aws_secretsmanager_secret.this.arn
    }
  }

  tags = var.tags
}

# IAM role for rotation Lambda
resource "aws_iam_role" "rotation" {
  count = var.enable_rotation ? 1 : 0

  name               = "${var.secret_name}-rotation-role"
  assume_role_policy = data.aws_iam_policy_document.rotation_assume[0].json

  tags = var.tags
}

# IAM policy for Lambda to assume role
data "aws_iam_policy_document" "rotation_assume" {
  count = var.enable_rotation ? 1 : 0

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# IAM policy for rotation Lambda
resource "aws_iam_role_policy" "rotation" {
  count = var.enable_rotation ? 1 : 0

  name   = "${var.secret_name}-rotation-policy"
  role   = aws_iam_role.rotation[0].id
  policy = data.aws_iam_policy_document.rotation[0].json
}

data "aws_iam_policy_document" "rotation" {
  count = var.enable_rotation ? 1 : 0

  # Allow Lambda to update the secret
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetSecretValue",
      "secretsmanager:PutSecretValue",
      "secretsmanager:UpdateSecretVersionStage"
    ]
    resources = [aws_secretsmanager_secret.this.arn]
  }

  # Allow Lambda to generate random passwords
  statement {
    effect    = "Allow"
    actions   = ["secretsmanager:GetRandomPassword"]
    resources = ["*"]
  }

  # CloudWatch Logs permissions
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  # VPC permissions if Lambda is in VPC
  dynamic "statement" {
    for_each = var.vpc_config != null ? [1] : []
    content {
      effect = "Allow"
      actions = [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ]
      resources = ["*"]
    }
  }
}

# Attach Lambda to VPC if configuration is provided
resource "aws_lambda_function" "rotation_vpc" {
  count = var.enable_rotation && var.vpc_config != null ? 1 : 0

  function_name = "${var.secret_name}-rotation"
  description   = "Rotates ${var.secret_name} secret"
  role          = aws_iam_role.rotation[0].arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30

  filename         = "${path.module}/lambda/rotation.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/rotation.zip")

  vpc_config {
    subnet_ids         = var.vpc_config.subnet_ids
    security_group_ids = var.vpc_config.security_group_ids
  }

  environment {
    variables = {
      SECRET_ARN = aws_secretsmanager_secret.this.arn
    }
  }

  tags = var.tags
}

# Permission for Secrets Manager to invoke rotation Lambda
resource "aws_lambda_permission" "rotation" {
  count = var.enable_rotation ? 1 : 0

  statement_id  = "AllowExecutionFromSecretsManager"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rotation[0].function_name
  principal     = "secretsmanager.amazonaws.com"
}

# Resource policy to allow application to read the secret
resource "aws_secretsmanager_secret_policy" "this" {
  count = length(var.allowed_iam_arns) > 0 ? 1 : 0

  secret_arn = aws_secretsmanager_secret.this.arn
  policy     = data.aws_iam_policy_document.secret_policy[0].json
}

data "aws_iam_policy_document" "secret_policy" {
  count = length(var.allowed_iam_arns) > 0 ? 1 : 0

  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = var.allowed_iam_arns
    }

    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]

    resources = [aws_secretsmanager_secret.this.arn]
  }
}
