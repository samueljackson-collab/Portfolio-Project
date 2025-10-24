variable "project_name" {
  type        = string
  description = "Project identifier"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID hosting the compute tier"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs for the auto scaling group"
}

variable "alb_target_group_arn" {
  type        = string
  description = "ARN of the target group for the load balancer"
}

variable "alb_security_group_id" {
  type        = string
  description = "Security group ID for the load balancer"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "desired_capacity" {
  type        = number
  description = "Desired capacity for the auto scaling group"
  default     = 2
}

variable "min_size" {
  type        = number
  description = "Minimum size for the auto scaling group"
  default     = 2
}

variable "max_size" {
  type        = number
  description = "Maximum size for the auto scaling group"
  default     = 4
}

variable "ami_id" {
  type        = string
  description = "Optional AMI override for the application instances"
  default     = ""
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
}

data "aws_ami" "amazon_linux" {
  most_recent = true

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  owners = ["137112412989"] # Amazon
}

locals {
  name_prefix      = lower("${var.project_name}-${var.environment}")
  sanitized_prefix = replace(local.name_prefix, "_", "-")

  common_tags = merge({
    Project     = var.project_name
    Environment = var.environment
  }, var.tags)

  user_data = base64encode(templatefile("${path.module}/templates/userdata.sh.tpl", {
    project_name = var.project_name
    environment  = var.environment
    region       = var.aws_region
  }))
}

resource "aws_security_group" "app" {
  name        = "${local.sanitized_prefix}-app-sg"
  description = "Allow HTTP from the load balancer"
  vpc_id      = var.vpc_id

  ingress {
    description      = "Allow HTTP from ALB"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    security_groups  = [var.alb_security_group_id]
  }

  egress {
    description = "Allow outbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-app-sg"
  })
}

resource "aws_launch_template" "app" {
  name_prefix   = "${local.sanitized_prefix}-lt-"
  image_id      = var.ami_id != "" ? var.ami_id : data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  user_data     = local.user_data

  vpc_security_group_ids = [aws_security_group.app.id]

  tag_specifications {
    resource_type = "instance"

    tags = merge(local.common_tags, {
      Name = "${local.name_prefix}-app"
    })
  }

  tag_specifications {
    resource_type = "volume"

    tags = merge(local.common_tags, {
      Name = "${local.name_prefix}-app"
    })
  }

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-lt"
  })
}

resource "aws_autoscaling_group" "app" {
  name                      = replace("${local.name_prefix}-asg", "_", "-")
  desired_capacity          = var.desired_capacity
  min_size                  = var.min_size
  max_size                  = var.max_size
  vpc_zone_identifier       = var.subnet_ids
  health_check_type         = "ELB"
  health_check_grace_period = 120
  target_group_arns         = [var.alb_target_group_arn]
  capacity_rebalance        = true

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${local.name_prefix}-app"
    propagate_at_launch = true
  }

  dynamic "tag" {
    for_each = local.common_tags

    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_launch_template.app]
}

output "asg_name" {
  value = aws_autoscaling_group.app.name
}

output "instance_security_group_id" {
  value = aws_security_group.app.id
}
