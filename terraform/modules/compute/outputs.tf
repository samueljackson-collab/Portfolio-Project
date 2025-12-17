/**
 * Compute module outputs
 *
 * This file documents every output the compute module will expose once resources are wired in.
 * Each output pairs a structured placeholder payload (fields set to null so the file is syntactically valid
 * even before resources exist) with a rich example payload that illustrates the expected shape.
 */

locals {
 compute_output_examples = {
    alb = {
      arn                 = "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/example-alb/50dc6c495c0c9188"
      dns_name            = "example-alb-1234567890.us-east-1.elb.amazonaws.com"
      zone_id             = "Z35SXDOTRQ7X7K"
      listeners           = [{ port = 80, protocol = "HTTP" }, { port = 443, protocol = "HTTPS", certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc" }]
      access_logs_bucket  = "example-alb-logs"
      waf_web_acl_arn     = "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/example/1234abcd-12ab-34cd-56ef-1234567890ab"
      ipv6_enabled        = true
    }

    target_groups = {
      default = {
        arn               = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/example/73e2d6bc24d8a067"
        name              = "example"
        port              = 80
        protocol          = "HTTP"
        health_check_path = "/health"
        target_type       = "instance"
      }
      blue = {
        arn               = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/example-blue/73e2d6bc24d8a067"
        name              = "example-blue"
        port              = 8080
        protocol          = "HTTP"
        health_check_path = "/healthz"
        target_type       = "instance"
      }
    }

    autoscaling_group = {
      name                      = "example-asg"
      arn                       = "arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:uuid:autoScalingGroupName/example-asg"
      min_size                  = 2
      max_size                  = 6
      desired_capacity          = 3
      launch_template_id        = "lt-0abcd1234efgh5678"
      launch_template_version   = "$Latest"
      capacity_rebalance        = true
      health_check_type         = "EC2"
      health_check_grace_period = 300
    }

    iam = {
      instance_profile_arn = "arn:aws:iam::123456789012:instance-profile/example-profile"
      role_arn             = "arn:aws:iam::123456789012:role/example-role"
      policies             = [
        "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM",
        "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
      ]
    }

    security_groups = {
      alb       = { id = "sg-0a1b2c3d4e5f6g7h8", name = "example-alb-sg", description = "ALB ingress" }
      instances = { id = "sg-1a2b3c4d5e6f7g8h9", name = "example-ec2-sg", description = "Instance ingress/egress" }
      rds       = { id = "sg-2a3b4c5d6e7f8g9h0", name = "example-rds-sg", description = "DB access" }
    }

    scaling_policies = {
      scale_out = {
        name         = "cpu-scale-out"
        policy_type  = "TargetTrackingScaling"
        metric       = "ASGAverageCPUUtilization"
        target_value = 65
        cooldown     = 300
      }
      scale_in = {
        name         = "cpu-scale-in"
        policy_type  = "TargetTrackingScaling"
        metric       = "ASGAverageCPUUtilization"
        target_value = 35
        cooldown     = 300
      }
    }

    alarms = {
      high_cpu = {
        name           = "cpu-too-high"
        metric_name    = "CPUUtilization"
        namespace      = "AWS/EC2"
        threshold      = 80
        comparison     = "GreaterThanOrEqualToThreshold"
        evaluation     = 3
        period_seconds = 60
        sns_topic_arns = ["arn:aws:sns:us-east-1:123456789012:alerts"]
      }
      unhealthy_host = {
        name           = "alb-unhealthy-hosts"
        metric_name    = "UnHealthyHostCount"
        namespace      = "AWS/ApplicationELB"
        threshold      = 1
        comparison     = "GreaterThanOrEqualToThreshold"
        evaluation     = 2
        period_seconds = 60
        sns_topic_arns = ["arn:aws:sns:us-east-1:123456789012:alerts"]
      }
    }

    instance_configuration = {
      ami_id              = "ami-0abcdef1234567890"
      instance_type       = "t3.micro"
      user_data_sha       = "a8f5f167f44f4964e6c998dee827110c"
      key_name            = "example-key"
      root_volume         = { size = 20, type = "gp3", encrypted = true }
      additional_volumes  = [{ size = 100, type = "gp3", encrypted = true, device_name = "/dev/sdh" }]
      iam_instance_profile = "example-profile"
    }

    network = {
      vpc_id               = "vpc-0abc1234def567890"
      public_subnet_ids    = ["subnet-0a1b2c3d", "subnet-0d4c3b2a"]
      private_subnet_ids   = ["subnet-12345678", "subnet-87654321"]
      availability_zones   = ["us-east-1a", "us-east-1b"]
      alb_security_group   = "sg-0a1b2c3d4e5f6g7h8"
      asg_security_group   = "sg-1a2b3c4d5e6f7g8h9"
      rds_security_group   = "sg-2a3b4c5d6e7f8g9h0"
    }

    operational_summary = {
      service_url              = "https://example-alb-1234567890.us-east-1.elb.amazonaws.com"
      dashboards               = ["https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=example"]
      runbooks                 = ["https://example.com/runbooks/compute"]
      deployment_strategy      = "Rolling update via ASG launch template"
      blue_green_ready         = true
      maintenance_windows      = [{ day = "sunday", start_utc = "02:00", duration_minutes = 60 }]
      owner_contacts           = ["devops@example.com", "oncall@example.com"]
      cost_center              = "CC-1234"
    }

    aggregate = {
      alb = {
        arn      = "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/example-alb/50dc6c495c0c9188"
        dns_name = "example-alb-1234567890.us-east-1.elb.amazonaws.com"
      }
      autoscaling_group = {
        name     = "example-asg"
        arn      = "arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:uuid:autoScalingGroupName/example-asg"
        min_size = 2
        max_size = 6
      }
      network = {
        vpc_id           = "vpc-0abc1234def567890"
        public_subnets   = ["subnet-0a1b2c3d", "subnet-0d4c3b2a"]
        private_subnets  = ["subnet-12345678", "subnet-87654321"]
        availability_zones = ["us-east-1a", "us-east-1b"]
      }
      operations = {
        service_url = "https://example-alb-1234567890.us-east-1.elb.amazonaws.com"
        runbook     = "https://example.com/runbooks/compute"
        dashboard   = "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=example"
        contacts    = ["devops@example.com", "oncall@example.com"]
      }
    }
  }

  compute_outputs = {
    alb = {
      description = "Application Load Balancer attributes including DNS endpoints, listener ports, and logging destinations."
      values      = {
        arn                = null
        dns_name           = null
        zone_id            = null
        listeners          = []
        access_logs_bucket = null
        waf_web_acl_arn    = null
        ipv6_enabled       = null
      }
      example = local.compute_output_examples.alb
      notes   = "Populate from aws_lb and aws_lb_listener resources when wiring in the ALB."
    }

    target_groups = {
      description = "Target group metadata keyed by lifecycle (e.g., default, blue/green) for routing and health checks."
      values      = {}
      example     = local.compute_output_examples.target_groups
      notes       = "Expect to surface ARNs, names, ports, protocols, health checks, and target types for each group."
    }

    autoscaling_group = {
      description = "Auto Scaling Group identity and capacity settings used for the compute fleet."
      values      = {
        name                      = null
        arn                       = null
        min_size                  = null
        max_size                  = null
        desired_capacity          = null
        launch_template_id        = null
        launch_template_version   = null
        capacity_rebalance        = null
        health_check_type         = null
        health_check_grace_period = null
      }
      example = local.compute_output_examples.autoscaling_group
      notes   = "Attach real values from aws_autoscaling_group and aws_launch_template resources."
    }

    iam = {
      description = "IAM surfaces required for instances, including instance profile, role, and attached policies."
      values      = {
        instance_profile_arn = null
        role_arn             = null
        policies             = []
      }
      example = local.compute_output_examples.iam
      notes   = "Expose ARNs so downstream modules (e.g., CI/CD) can reuse the same execution role."
    }

    security_groups = {
      description = "Security group identifiers for the ALB, compute instances, and data plane dependencies."
      values      = {}
      example     = local.compute_output_examples.security_groups
      notes       = "Return ids, names, and descriptions to simplify cross-module references and documentation."
    }

    scaling_policies = {
      description = "Scaling policies tied to the Auto Scaling Group, covering target-tracking rules for CPU, ALB request counts, or custom metrics."
      values      = {}
      example     = local.compute_output_examples.scaling_policies
      notes       = "Surface policy names, types, tracked metrics, target values, and cooldowns."
    }

    alarms = {
      description = "CloudWatch alarms used for compute health and capacity guardrails."
      values      = {}
      example     = local.compute_output_examples.alarms
      notes       = "Include thresholds, evaluation periods, and notification topics so operators know how incidents are raised."
    }

    instance_configuration = {
      description = "Per-instance configuration details from the launch template, including AMI, instance type, and storage."
      values      = {
        ami_id               = null
        instance_type        = null
        user_data_sha        = null
        key_name             = null
        root_volume          = null
        additional_volumes   = []
        iam_instance_profile = null
      }
      example = local.compute_output_examples.instance_configuration
      notes   = "Useful for audits and troubleshooting when correlating running instances with launch configuration."
    }

    network = {
      description = "Network and placement details for the compute stack, including VPC and subnet selections."
      values      = {
        vpc_id             = null
        public_subnet_ids  = []
        private_subnet_ids = []
        availability_zones = []
        alb_security_group = null
        asg_security_group = null
        rds_security_group = null
      }
      example = local.compute_output_examples.network
      notes   = "Enables consumers to attach additional resources (e.g., cache clusters) into the same network segments."
    }

    operational_summary = {
      description = "Human-friendly operational references such as service URLs, dashboards, and runbooks."
      values      = {
        service_url         = null
        dashboards          = []
        runbooks            = []
        deployment_strategy = null
        blue_green_ready    = null
        maintenance_windows = []
        owner_contacts      = []
        cost_center         = null
      }
      example = local.compute_output_examples.operational_summary
      notes   = "Keep this section updated so on-call engineers have a quick snapshot of where to start."
    }

    aggregate_summary = {
      description = "Condensed, automation-friendly view that surfaces the most referenced identifiers across the compute stack."
      values      = {
        alb = {
          arn      = null
          dns_name = null
        }
        autoscaling_group = {
          name     = null
          arn      = null
          min_size = null
          max_size = null
        }
        network = {
          vpc_id              = null
          public_subnets      = []
          private_subnets     = []
          availability_zones  = []
        }
        operations = {
          service_url = null
          runbook     = null
          dashboard   = null
          contacts    = []
        }
      }
      example = local.compute_output_examples.aggregate
      notes   = "Use this for dashboards or cross-module references that only need the most important identifiers."
    }
  }
}

output "alb" {
  description = <<-EOT
    Application Load Balancer endpoints and metadata. Provide the ARN, DNS name, listeners, and
    logging/WAF integrations so downstream services (like DNS or monitoring modules) can stitch
    together the full ingress path.

    Example shape:
    ${jsonencode(local.compute_output_examples.alb)}
  EOT
  value = local.compute_outputs.alb
}

output "target_groups" {
  description = <<-EOT
    Target groups attached to the ALB or other load balancers. Expose identifiers, ports, protocols,
    and health check paths for each group (blue/green or default) to enable traffic shifting and
    observability mappings.

    Example shape:
    ${jsonencode(local.compute_output_examples.target_groups)}
  EOT
  value = local.compute_outputs.target_groups
}

output "autoscaling_group" {
  description = <<-EOT
    Auto Scaling Group identifiers and capacity settings. Downstream modules can reference the ASG
    ARN for scaling policies or attach lifecycle hooks.

    Example shape:
    ${jsonencode(local.compute_output_examples.autoscaling_group)}
  EOT
  value = local.compute_outputs.autoscaling_group
}

output "iam" {
  description = <<-EOT
    IAM primitives that back the compute instances. Useful for delegating permissions to other
    infrastructure (e.g., log shippers, backup agents) without recreating roles.

    Example shape:
    ${jsonencode(local.compute_output_examples.iam)}
  EOT
  value = local.compute_outputs.iam
}

output "security_groups" {
  description = <<-EOT
    Security group identifiers for all compute-adjacent resources. Keeping these surfaced helps
    network modules and service teams grant the correct ingress/egress permissions.

    Example shape:
    ${jsonencode(local.compute_output_examples.security_groups)}
  EOT
  value = local.compute_outputs.security_groups
}

output "scaling_policies" {
  description = <<-EOT
    Scaling policies applied to the ASG. Exposing policy names, metrics, and targets helps correlate
    CloudWatch alarms and autoscaling activity during incident reviews.

    Example shape:
    ${jsonencode(local.compute_output_examples.scaling_policies)}
  EOT
  value = local.compute_outputs.scaling_policies
}

output "alarms" {
  description = <<-EOT
    CloudWatch alarms associated with the compute stack. Include thresholds and notification topics
    so alert routing remains transparent.

    Example shape:
    ${jsonencode(local.compute_output_examples.alarms)}
  EOT
  value = local.compute_outputs.alarms
}

output "instance_configuration" {
  description = <<-EOT
    Launch template or configuration settings applied to instances. This output captures AMI ID,
    instance type, user data checksum, SSH key, and storage layout so operations has a single source
    of truth for the fleet baseline.

    Example shape:
    ${jsonencode(local.compute_output_examples.instance_configuration)}
  EOT
  value = local.compute_outputs.instance_configuration
}

output "network" {
  description = <<-EOT
    Network placement for compute resources. Expose VPC and subnet IDs, availability zones, and
    security group references to simplify cross-service integrations.

    Example shape:
    ${jsonencode(local.compute_output_examples.network)}
  EOT
  value = local.compute_outputs.network
}

output "operational_summary" {
  description = <<-EOT
    Human-centric operational references that complement the infrastructure outputs: primary service
    URL, dashboards, runbooks, deployment approach, and contact details.

    Example shape:
    ${jsonencode(local.compute_output_examples.operational_summary)}
  EOT
  value = local.compute_outputs.operational_summary
}

output "aggregate_summary" {
  description = <<-EOT
    Compact output that bubbles up the most commonly referenced identifiers across the module: key
    ALB attributes, ASG handles, network placement, and operational contact points. Intended for
    downstream automation, dashboards, or documentation generators that prefer a concise payload.

    Example shape:
    ${jsonencode(local.compute_output_examples.aggregate)}
  EOT
  value = local.compute_outputs.aggregate_summary
}
