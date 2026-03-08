---
title: Restore Test Results
description: Sanitized results from quarterly DR restore tests. - **Date:** 2025-11-01 - **Scope:** Critical services (FreeIPA, Nginx Proxy Manager, Wiki.js) - **Objective:** Validate RTO/RPO alignment and data co
tags: [documentation, portfolio]
path: portfolio/06-homelab/restore-test-results
created: 2026-03-08T22:19:13.057876+00:00
updated: 2026-03-08T22:04:38.349902+00:00
---

# Restore Test Results

Sanitized results from quarterly DR restore tests.

## Test Window
- **Date:** 2025-11-01
- **Scope:** Critical services (FreeIPA, Nginx Proxy Manager, Wiki.js)
- **Objective:** Validate RTO/RPO alignment and data consistency

## Summary
| Service | Backup Source | Restore Target | RTO Target | Actual RTO | Result |
| --- | --- | --- | --- | --- | --- |
| FreeIPA | PBS (daily) | Proxmox node 2 | 60 min | 42 min | ✅ |
| Nginx Proxy Manager | PBS (daily) | Proxmox node 3 | 60 min | 35 min | ✅ |
| Wiki.js | PBS (daily) | Proxmox node 1 | 60 min | 47 min | ✅ |

## Validation Steps
1. Restored VMs from PBS datastore to isolated VLAN.
2. Verified service health via systemd status and HTTP checks.
3. Confirmed application login and data integrity checks.
4. Recorded RTO/RPO timings and anomalies.

## Notes
- DNS cutover was simulated via `/etc/hosts` overrides.
- SSL certificates were validated using staging certs.
- No data loss detected within defined RPO (24 hours).
