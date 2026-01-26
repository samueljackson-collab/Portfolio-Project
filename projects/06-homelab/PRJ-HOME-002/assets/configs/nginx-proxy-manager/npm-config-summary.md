# Nginx Proxy Manager Configuration Summary

Sanitized configuration overview for Nginx Proxy Manager (NPM). Full proxy host entries are stored in the original NPM backup/export (not committed to this repository).

## Core Settings
- **Base URL:** `https://proxy.example.internal`
- **Admin UI Port:** `81` (restricted to VLAN 40)
- **Default SSL Policy:** Modern TLS (TLS 1.2/1.3, HSTS enabled)
- **Certificate Provider:** Let's Encrypt with DNS-01 challenge
- **Access Lists:** Separate lists for admin-only, internal-only, and public services

## Proxy Host Inventory (Sanitized)
| Hostname | Backend | Port | TLS | Access List | Notes |
| --- | --- | --- | --- | --- | --- |
| `wiki.example.com` | `192.168.40.60` | 3000 | ✅ | `public-services` | Wiki.js
| `ha.example.com` | `192.168.40.61` | 8123 | ✅ | `internal-only` | Home Assistant
| `immich.example.com` | `192.168.40.62` | 2283 | ✅ | `internal-only` | Immich
| `proxmox.example.com` | `192.168.40.10` | 8006 | ✅ | `admin-only` | Proxmox UI
| `grafana.example.com` | `192.168.40.70` | 3000 | ✅ | `admin-only` | Grafana

## Redirects & Security
- Global HTTP → HTTPS redirect enabled.
- Websockets allowed for Home Assistant and Immich.
- Custom headers:
  - `X-Frame-Options: SAMEORIGIN`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`

## Export Notes
- Exported via NPM `Settings → Backup → Download`.
- Sanitized fields: hostnames, upstream IPs, access list names.
- Backup file stored in `assets/configs/nginx-proxy-manager/`.
