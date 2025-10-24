resource "aws_launch_template" "backend" {
  name_prefix   = "${var.project}-${var.environment}-lt"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  user_data = base64encode(<<EOT
#!/bin/bash
echo "Starting portfolio backend"
EOT
  )

  vpc_security_group_ids = var.security_group_ids

  tag_specifications {
    resource_type = "instance"
    tags = merge(var.common_tags, {
      Name = "${var.project}-${var.environment}-backend"
    })
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_lb" "app" {
  name               = "${var.project}-${var.environment}-alb"
  load_balancer_type = "application"
  subnets            = var.subnet_ids

  security_groups = var.security_group_ids

  tags = merge(var.common_tags, {
    Name = "${var.project}-${var.environment}-alb"
  })
}

resource "aws_lb_target_group" "app" {
  name     = "${var.project}-${var.environment}-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }

  tags = var.common_tags
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_autoscaling_group" "backend" {
  name                = "${var.project}-${var.environment}-asg"
  min_size            = var.min_size
  max_size            = var.max_size
  desired_capacity    = var.min_size
  health_check_type   = "EC2"
  vpc_zone_identifier = var.subnet_ids

  launch_template {
    id      = aws_launch_template.backend.id
    version = "$Latest"
  }

  target_group_arns = [aws_lb_target_group.app.arn]

  tag {
    key                 = "Name"
    value               = "${var.project}-${var.environment}-backend"
    propagate_at_launch = true
  }
}
