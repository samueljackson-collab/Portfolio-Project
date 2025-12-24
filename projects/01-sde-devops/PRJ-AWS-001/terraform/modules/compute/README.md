# Compute Module

Implements the application tier:
- Public Application Load Balancer spanning the public subnets.
- Target group with HTTP health checks and listener forwarding.
- EC2 Auto Scaling Group using launch templates, detailed monitoring, and target-tracking policies.

Tune capacity, AMI, user data, and health-check paths via module variables.
