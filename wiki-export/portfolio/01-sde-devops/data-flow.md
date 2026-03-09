---
title: Data Flow
description: sequenceDiagram participant U as User participant R as Route53 participant L as ALB participant A as App EC2 participant D as RDS participant S as S3 U->>R: DNS query R->>L: ALB DNS U->>L: HTTPS reque
tags: [documentation, portfolio]
path: portfolio/01-sde-devops/data-flow
created: 2026-03-08T22:19:12.915514+00:00
updated: 2026-03-08T22:04:38.143902+00:00
---

```mermaid
sequenceDiagram
  participant U as User
  participant R as Route53
  participant L as ALB
  participant A as App EC2
  participant D as RDS
  participant S as S3

  U->>R: DNS query
  R->>L: ALB DNS
  U->>L: HTTPS request
  L->>A: Forward request
  A->>D: SQL query
  D-->>A: Result set
  A->>S: Fetch artifacts
  S-->>A: Object
  A-->>L: HTTP response
  L-->>U: Response
```
