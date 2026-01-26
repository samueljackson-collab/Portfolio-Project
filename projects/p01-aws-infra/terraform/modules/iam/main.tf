# CloudFormation Execution Role (for deploying stacks)
resource "aws_iam_role" "cloudformation_execution" {
  name = "${var.environment}-cfn-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "cloudformation.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.environment}-cfn-execution-role"
  }
}

resource "aws_iam_role_policy" "cloudformation_execution" {
  name = "${var.environment}-cfn-execution-policy"
  role = aws_iam_role.cloudformation_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "rds:*",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:GetRole",
          "iam:PassRole",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

# Application Role (example for EC2 instances or Lambda)
resource "aws_iam_role" "application" {
  name = "${var.environment}-application-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ec2.amazonaws.com",
            "lambda.amazonaws.com"
          ]
        }
      }
    ]
  })

  tags = {
    Name = "${var.environment}-application-role"
  }
}

# Least-privilege policy for application access to RDS
resource "aws_iam_role_policy" "application_rds" {
  name = "${var.environment}-application-rds-policy"
  role = aws_iam_role.application.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = ["us-east-1", "us-west-2"]
          }
        }
      }
    ]
  })
}

# Least-privilege policy for CloudWatch Logs
resource "aws_iam_role_policy" "application_logs" {
  name = "${var.environment}-application-logs-policy"
  role = aws_iam_role.application.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/${var.environment}/*"
      }
    ]
  })
}

# Instance Profile for EC2
resource "aws_iam_instance_profile" "application" {
  name = "${var.environment}-application-instance-profile"
  role = aws_iam_role.application.name
}
