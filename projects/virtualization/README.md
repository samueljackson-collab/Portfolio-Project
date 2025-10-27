# Virtualization & Core Services Stack

## Overview
Proxmox VE cluster paired with TrueNAS storage hosting core home services behind a reverse proxy. The stack powers knowledge management (Wiki.js), automation (Home Assistant), media (Immich), and supporting services with RBAC and TLS enforced end-to-end.

## Current Deliverables
- Narrative of the virtualization layout, including node roles and storage pools.
- Service catalog summarizing each VM/container, its purpose, and dependency chain.
- Reverse proxy routing matrix documenting hostnames, certificates, and backend targets.

## Upcoming Artifacts
- Detailed topology diagrams of Proxmox clusters, TrueNAS datasets, and backup flows.
- Deployment runbooks for adding nodes, expanding storage, and patching services safely.
- Performance baselines gathered from monitoring dashboards to validate resource sizing.

Ping me if you want any of the drafts before they land in the repo.
