###############################################################################
# Compute Module - EC2, ASG, Launch Templates, ALB
#
# This module creates compute resources including Auto Scaling Groups,
# Launch Templates, Application Load Balancers, and associated target groups.
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

data "aws_ssm_parameter" "amazon_linux_ami" {
  name = var.ami_ssm_parameter
}

#------------------------------------------------------------------------------
# IAM Role for EC2 Instances
#------------------------------------------------------------------------------

resource "aws_iam_role" "instance" {
  name = "${var.name_prefix}-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {
  role       = aws_iam_role.instance.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_instance_profile" "instance" {
  name = "${var.name_prefix}-instance-profile"
  role = aws_iam_role.instance.name

  tags = var.tags
}

#------------------------------------------------------------------------------
# Security Group for Application Instances
#------------------------------------------------------------------------------

resource "aws_security_group" "app" {
  name        = "${var.name_prefix}-app-sg"
  description = "Security group for application instances"
  vpc_id      = var.vpc_id

  # Allow HTTP from ALB
  ingress {
    description     = "HTTP from ALB"
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-app-sg"
  })
}

#------------------------------------------------------------------------------
# Security Group for ALB
#------------------------------------------------------------------------------

resource "aws_security_group" "alb" {
  name        = "${var.name_prefix}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  # Allow HTTP
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Allow HTTPS
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-alb-sg"
  })
}

#------------------------------------------------------------------------------
# Launch Template
#------------------------------------------------------------------------------

resource "aws_launch_template" "app" {
  name_prefix   = "${var.name_prefix}-app-"
  image_id      = data.aws_ssm_parameter.amazon_linux_ami.value
  instance_type = var.instance_type

  iam_instance_profile {
    name = aws_iam_instance_profile.instance.name
  }

  vpc_security_group_ids = [aws_security_group.app.id]

  monitoring {
    enabled = var.enable_detailed_monitoring
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"  # IMDSv2 required
    http_put_response_hop_limit = 1
  }

  user_data = base64encode(var.user_data != "" ? var.user_data : <<-EOF
    #!/bin/bash
    set -euo pipefail

    # Update system packages
    dnf update -y

    # Install and configure nginx
    dnf install -y nginx amazon-cloudwatch-agent

    # Configure nginx
    cat > /usr/share/nginx/html/index.html <<'HTML'
    <!DOCTYPE html>
    <html>
    <head><title>${var.name_prefix}</title></head>
    <body>
    <h1>Welcome to ${var.name_prefix}</h1>
    <p>Instance: $(hostname)</p>
    </body>
    </html>
    HTML

    # Health check endpoint
    cat > /usr/share/nginx/html/healthz <<'HTML'
    OK
    HTML

    # Start nginx
    systemctl enable nginx --now

    # Configure CloudWatch Agent
    /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
      -a fetch-config \
      -m ec2 \
      -s \
      -c ssm:${var.cloudwatch_agent_config_ssm_parameter}
  EOF
  )

  tag_specifications {
    resource_type = "instance"

    tags = merge(var.tags, {
      Name = "${var.name_prefix}-app"
    })
  }

  tag_specifications {
    resource_type = "volume"

    tags = merge(var.tags, {
      Name = "${var.name_prefix}-app-volume"
    })
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = var.tags
}

#------------------------------------------------------------------------------
# Application Load Balancer
#------------------------------------------------------------------------------

resource "aws_lb" "app" {
  name               = "${var.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.enable_deletion_protection

  access_logs {
    bucket  = var.alb_access_logs_bucket
    prefix  = "${var.name_prefix}-alb"
    enabled = var.alb_access_logs_bucket != ""
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-alb"
  })
}

#------------------------------------------------------------------------------
# ALB Target Group
#------------------------------------------------------------------------------

resource "aws_lb_target_group" "app" {
  name     = "${var.name_prefix}-app-tg"
  port     = var.app_port
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = var.health_check_path
    matcher             = "200-399"
  }

  deregistration_delay = 60

  stickiness {
    type            = "lb_cookie"
    enabled         = var.enable_stickiness
    cookie_duration = 86400
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-app-tg"
  })
}

#------------------------------------------------------------------------------
# ALB Listeners
#------------------------------------------------------------------------------

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = var.acm_certificate_arn != "" ? "redirect" : "forward"

    dynamic "redirect" {
      for_each = var.acm_certificate_arn != "" ? [1] : []
      content {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }

    dynamic "forward" {
      for_each = var.acm_certificate_arn == "" ? [1] : []
      content {
        target_group {
          arn = aws_lb_target_group.app.arn
        }
      }
    }
  }

  tags = var.tags
}

resource "aws_lb_listener" "https" {
  count = var.acm_certificate_arn != "" ? 1 : 0

  load_balancer_arn = aws_lb.app.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }

  tags = var.tags
}

#------------------------------------------------------------------------------
# Auto Scaling Group
#------------------------------------------------------------------------------

resource "aws_autoscaling_group" "app" {
  name                      = "${var.name_prefix}-app-asg"
  min_size                  = var.min_size
  max_size                  = var.max_size
  desired_capacity          = var.desired_capacity
  vpc_zone_identifier       = var.private_subnet_ids
  health_check_type         = "ELB"
  health_check_grace_period = var.health_check_grace_period
  target_group_arns         = [aws_lb_target_group.app.arn]

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
    }
  }

  dynamic "tag" {
    for_each = merge(var.tags, {
      Name = "${var.name_prefix}-app"
    })
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

#------------------------------------------------------------------------------
# Auto Scaling Policies
#------------------------------------------------------------------------------

resource "aws_autoscaling_policy" "scale_up" {
  name                   = "${var.name_prefix}-scale-up"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = var.target_cpu_utilization
  }
}

resource "aws_autoscaling_policy" "scale_on_requests" {
  count = var.enable_request_based_scaling ? 1 : 0

  name                   = "${var.name_prefix}-scale-requests"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.app.arn_suffix}/${aws_lb_target_group.app.arn_suffix}"
    }
    target_value = var.target_requests_per_instance
  }
}
