# Security Module

Creates layered security controls for the three-tier stack:

- Application Load Balancer security group exposing HTTP/HTTPS.
- Application tier security group receiving traffic only from the ALB and optionally bastion CIDRs for SSH.
- Database tier security group restricted to the application tier on configurable port.

Customize ingress CIDRs, listener ports, and tagging via module variables.
