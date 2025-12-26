locals {
  tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      Tier        = "application"
    }
  )
  create_instance_profile = var.create_instance_profile && var.iam_instance_profile == null
  log_group_name          = var.cloudwatch_log_group_name != null ? var.cloudwatch_log_group_name : "/${var.project_name}/${var.environment}/app"
  instance_profile_name   = var.iam_instance_profile != null ? var.iam_instance_profile : local.create_instance_profile ? aws_iam_instance_profile.app[0].name : null
  user_data_base64 = var.user_data_base64 != null ? var.user_data_base64 : base64encode(
    templatefile("${path.module}/user-data.sh", {
      log_group_name = local.log_group_name
      app_log_path   = var.app_log_path
    })
  )
}

data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect = "Allow"

    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app" {
  count              = local.create_instance_profile ? 1 : 0
  name               = "${var.project_name}-${var.environment}-app-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-app-role" })
}

resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {
  count      = local.create_instance_profile ? 1 : 0
  role       = aws_iam_role.app[0].name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  count      = local.create_instance_profile ? 1 : 0
  role       = aws_iam_role.app[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  count      = local.create_instance_profile ? 1 : 0
  role       = aws_iam_role.app[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "app" {
  count = local.create_instance_profile ? 1 : 0
  name  = "${var.project_name}-${var.environment}-app-profile"
  role  = aws_iam_role.app[0].name

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-app-profile" })
}

resource "aws_cloudwatch_log_group" "app" {
  name              = local.log_group_name
  retention_in_days = var.cloudwatch_log_retention_days
  kms_key_id        = null

  tags = merge(local.tags, { Name = local.log_group_name })
}

resource "aws_lb" "app" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  idle_timeout = 60

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-alb" })
}

resource "aws_lb_target_group" "app" {
  name        = "${var.project_name}-${var.environment}-tg"
  port        = var.app_port
  protocol    = "HTTP"
  target_type = "instance"
  vpc_id      = var.vpc_id

  health_check {
    enabled             = true
    path                = var.health_check_path
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    unhealthy_threshold = 3
    healthy_threshold   = 2
  }

  tags = merge(local.tags, { Name = "${var.project_name}-${var.environment}-tg" })
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-${var.environment}-lt-"
  image_id      = var.ami_id
  instance_type = var.instance_type
  key_name      = var.ssh_key_name

  update_default_version = true

  vpc_security_group_ids = [var.app_security_group_id]
  user_data              = local.user_data_base64

  dynamic "iam_instance_profile" {
    for_each = local.instance_profile_name == null ? [] : [local.instance_profile_name]
    content {
      name = iam_instance_profile.value
    }
  }

  block_device_mappings {
    device_name = var.root_volume_device
    ebs {
      volume_size           = var.root_volume_size
      volume_type           = var.root_volume_type
      delete_on_termination = true
      encrypted             = true
    }
  }

  monitoring {
    enabled = var.enable_detailed_monitoring
  }

  tag_specifications {
    resource_type = "instance"
    tags          = merge(local.tags, { Role = "app" })
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "app" {
  name                      = "${var.project_name}-${var.environment}-asg"
  desired_capacity          = var.desired_capacity
  min_size                  = var.min_size
  max_size                  = var.max_size
  vpc_zone_identifier       = var.private_app_subnet_ids
  health_check_type         = "EC2"
  health_check_grace_period = 120

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  target_group_arns = [aws_lb_target_group.app.arn]

  tag {
    key                 = "Name"
    value               = "${var.project_name}-${var.environment}-app"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_policy" "cpu_target" {
  name                   = "${var.project_name}-${var.environment}-cpu-policy"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = var.target_cpu_utilization
  }
}
