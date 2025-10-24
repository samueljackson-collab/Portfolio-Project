# Architecture Guide

This document provides a detailed walkthrough of the reference AWS multi-tier architecture described in the GitHub repository setup guide. It explains the major components, networking layout, availability zones, and data flows for recruiters or reviewers who want a deeper understanding of the infrastructure story behind the portfolio project.

## Layers

1. **Networking** – A /16 VPC carved into public, private, and database subnets across two availability zones. Routing tables, NAT gateways, and security groups enforce least-privilege communication paths.
2. **Delivery** – Amazon Route 53 maps the friendly domain to CloudFront, which terminates TLS and caches static assets close to end users.
3. **Application** – Application Load Balancers distribute requests to auto-scaling groups of EC2 instances that host the web and API tiers. Lifecycle hooks and health checks keep deployments resilient.
4. **Data** – A Multi-AZ Amazon RDS PostgreSQL cluster handles transactional storage with automatic failover. Encrypted snapshots provide disaster recovery coverage.
5. **Observability and Operations** – CloudWatch metrics, logs, alarms, and dashboards deliver actionable insights. AWS Backup and AWS Config enforce compliance and retention requirements.

## Diagrams

- `docs/images/architecture.png` – High-level system diagram referenced in the main README.
- `docs/images/networking.png` – Optional supplemental diagram that zooms into the VPC layout.

Use diagramming tools such as Excalidraw, draw.io, or Lucidchart to export updated PNG diagrams into the `docs/images/` folder.
