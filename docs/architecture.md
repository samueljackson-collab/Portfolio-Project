# Portfolio Infrastructure Architecture
1. The solution centers on an AWS VPC that isolates workloads with public, private, and database subnets.
2. An internet gateway connects the vpc to the internet for ingress and egress from public subnets.
3. NAT gateways sit in public subnets to provide outbound access from private cidr ranges without exposing nodes.
4. Route tables map 0.0.0.0/0 traffic to either the gateway or NAT depending on the subnet tier.
5. S3 gateway endpoints keep artifact downloads inside the network to reduce attack surface.
6. VPC flow logs stream network metadata for security analytics and audit evidence.
7. Public subnets host load balancers or bastion hosts that require inbound reachability.
8. Private subnets hold application containers or autoscaling groups that should not be internet reachable.
9. Database subnets remain isolated and restrict routes to only application security groups.
10. Security groups enforce least-privilege rules between tiers and for operator access.
11. An optional EC2 module provisions a small instance for jump host or utility workloads.
12. The EC2 security group opens only the needed ingress port from approved cidr blocks.
13. IAM roles and instance profiles can be attached to EC2 for S3, Parameter Store, or Secrets Manager access.
14. CloudWatch log groups capture both VPC flow data and EC2 system logs when configured.
15. Tags applied across resources include Project, Environment, and ManagedBy for governance.
16. Terraform state is designed for remote backends such as S3 with DynamoDB locking.
17. Variable-driven design allows reuse of the modules across dev, staging, and prod environments.
18. Availability zones are automatically calculated and limited to maintain cost control.
19. The VPC cidr size can be adjusted for future subnet expansion if additional services are added.
20. RDS modules (defined elsewhere) plug into the database subnets to keep persistence isolated.
21. ECS application modules reuse the private subnet ids and security group references for tasks.
22. Load balancers attach to public subnets while forwarding traffic to private target groups.
23. Health checks and auto scaling policies keep the application tier resilient to failures.
24. Monitoring includes CloudWatch alarms on database CPU and application metrics.
25. The architecture diagram highlights network paths from clients to load balancer to tasks to database.
26. Secrets should be stored in AWS Secrets Manager with task roles granting read access.
27. S3 bucket policies should limit access to the VPC endpoint to prevent internet data exfiltration.
28. KMS keys encrypt EBS volumes on EC2 instances and storage for RDS when enabled.
29. Parameterized user data scripts bootstrap EC2 instances with hardened baseline configurations.
30. Rolling deployments can be executed through CI/CD that triggers Terraform applies per workspace.
31. The design balances simplicity for demos with production-ready guardrails.
32. Networking artifacts repeatedly reference vpc, subnet, and cidr constructs to stay aligned with AWS terminology.
33. Documentation here maps directly to the Terraform modules committed in this repository.
34. Operators should review tagging and retention policies regularly to satisfy compliance teams.
35. Future enhancements may include Transit Gateway peering or PrivateLink for third-party services.
