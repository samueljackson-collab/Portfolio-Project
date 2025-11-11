# SNS Topic Module for Security Alerts

resource "aws_sns_topic" "security_alerts" {
  name              = var.topic_name
  display_name      = var.display_name
  kms_master_key_id = var.kms_key_id

  tags = merge(
    var.tags,
    {
      Name      = var.topic_name
      ManagedBy = "Terraform"
    }
  )
}

# SNS Topic Policy
resource "aws_sns_topic_policy" "security_alerts" {
  arn    = aws_sns_topic.security_alerts.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    sid    = "AllowOpenSearchPublish"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["es.amazonaws.com"]
    }

    actions = [
      "SNS:Publish"
    ]

    resources = [
      aws_sns_topic.security_alerts.arn
    ]
  }

  statement {
    sid    = "AllowAccountAccess"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions = [
      "SNS:Subscribe",
      "SNS:Publish",
      "SNS:Receive"
    ]

    resources = [
      aws_sns_topic.security_alerts.arn
    ]
  }
}

# Email Subscriptions
resource "aws_sns_topic_subscription" "email" {
  for_each = toset(var.email_addresses)

  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = each.value
}

# Slack Webhook Subscription (via Lambda)
resource "aws_sns_topic_subscription" "slack" {
  count = var.slack_webhook_url != null ? 1 : 0

  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.slack_forwarder[0].arn
}

# Lambda function to forward to Slack
resource "aws_lambda_function" "slack_forwarder" {
  count = var.slack_webhook_url != null ? 1 : 0

  function_name = "${var.topic_name}-slack-forwarder"
  role          = aws_iam_role.slack_forwarder[0].arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 10

  filename         = data.archive_file.slack_forwarder[0].output_path
  source_code_hash = data.archive_file.slack_forwarder[0].output_base64sha256

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }

  tags = var.tags
}

# Lambda code
data "archive_file" "slack_forwarder" {
  count = var.slack_webhook_url != null ? 1 : 0

  type        = "zip"
  output_path = "${path.module}/slack_forwarder.zip"

  source {
    content = <<-EOF
import json
import urllib3
import os

http = urllib3.PoolManager()

def handler(event, context):
    webhook_url = os.environ['SLACK_WEBHOOK_URL']

    for record in event['Records']:
        sns_message = record['Sns']['Message']
        subject = record['Sns'].get('Subject', 'Security Alert')

        payload = {
            'text': f'*{subject}*',
            'blocks': [
                {
                    'type': 'header',
                    'text': {
                        'type': 'plain_text',
                        'text': subject
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': sns_message
                    }
                }
            ]
        }

        encoded_data = json.dumps(payload).encode('utf-8')
        resp = http.request('POST', webhook_url, body=encoded_data)

        print(f'Slack response: {resp.status}')

    return {'statusCode': 200}
EOF
    filename = "index.py"
  }
}

# IAM role for Lambda
resource "aws_iam_role" "slack_forwarder" {
  count = var.slack_webhook_url != null ? 1 : 0

  name               = "${var.topic_name}-slack-forwarder-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume[0].json

  tags = var.tags
}

data "aws_iam_policy_document" "lambda_assume" {
  count = var.slack_webhook_url != null ? 1 : 0

  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  count = var.slack_webhook_url != null ? 1 : 0

  role       = aws_iam_role.slack_forwarder[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Permission for SNS to invoke Lambda
resource "aws_lambda_permission" "sns_invoke" {
  count = var.slack_webhook_url != null ? 1 : 0

  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slack_forwarder[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.security_alerts.arn
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
