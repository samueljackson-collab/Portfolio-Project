---
title: Architecture Overview
description: flowchart TB Client((Users)) --> Route53[Route53] Route53 --> ALB[Public ALB] ALB --> ASG[EC2 Auto Scaling Group] ASG --> RDS[(Amazon RDS)] ASG -->|Artifacts| S3[(S3 Bucket)] ASG -->|Metrics| CloudWat
tags: [documentation, portfolio]
path: portfolio/01-sde-devops/architecture-overview
created: 2026-03-08T22:19:12.914570+00:00
updated: 2026-03-08T22:04:38.142902+00:00
---

```mermaid
flowchart TB
  Client((Users)) --> Route53[Route53]
  Route53 --> ALB[Public ALB]
  ALB --> ASG[EC2 Auto Scaling Group]
  ASG --> RDS[(Amazon RDS)]
  ASG -->|Artifacts| S3[(S3 Bucket)]
  ASG -->|Metrics| CloudWatch[[CloudWatch]]
```
