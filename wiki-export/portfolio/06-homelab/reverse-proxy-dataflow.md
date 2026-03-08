---
title: Reverse Proxy Data Flow
description: $(cat projects/06-homelab/PRJ-HOME-002/assets/diagrams/reverse-proxy-dataflow.mmd) **Highlights** - Nginx Proxy Manager terminates TLS and routes traffic based on SNI to internal services. - Identity 
tags: [documentation, portfolio]
path: portfolio/06-homelab/reverse-proxy-dataflow
created: 2026-03-08T22:19:13.025632+00:00
updated: 2026-03-08T22:04:38.340902+00:00
---

# Reverse Proxy Data Flow

```mermaid
$(cat projects/06-homelab/PRJ-HOME-002/assets/diagrams/reverse-proxy-dataflow.mmd)
```

**Highlights**
- Nginx Proxy Manager terminates TLS and routes traffic based on SNI to internal services.
- Identity flows back to FreeIPA for Wiki.js and Home Assistant.
- Backups and monitoring traffic remain on the internal network with TrueNAS providing NFS/iSCSI storage.
