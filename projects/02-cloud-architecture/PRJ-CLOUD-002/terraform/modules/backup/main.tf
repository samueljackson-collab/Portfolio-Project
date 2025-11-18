resource "aws_backup_vault" "this" {
  name = "${var.project_name}-${var.environment}-backup"

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-backup"
  })
}

resource "aws_backup_plan" "this" {
  name = "${var.project_name}-${var.environment}-plan"

  rule {
    rule_name         = "daily-rds"
    target_vault_name = aws_backup_vault.this.name
    schedule          = "cron(0 5 * * ? *)"

    lifecycle {
      delete_after = 30
    }
  }

  rule {
    rule_name         = "weekly-rds"
    target_vault_name = aws_backup_vault.this.name
    schedule          = "cron(0 6 ? * SUN *)"

    lifecycle {
      delete_after = 90
    }
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-backup-plan"
  })
}

resource "aws_iam_role" "backup" {
  name_prefix = "${var.project_name}-${var.environment}-backup-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "backup" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}

resource "aws_backup_selection" "rds" {
  name         = "${var.project_name}-${var.environment}-rds"
  plan_id      = aws_backup_plan.this.id
  iam_role_arn = aws_iam_role.backup.arn

  resources = [
    var.rds_instance_arn
  ]

  depends_on = [aws_iam_role_policy_attachment.backup]
}
