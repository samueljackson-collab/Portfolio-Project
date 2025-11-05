# Service Architecture Documentation

## Overview

Proxmox host running multiple services with Nginx reverse proxy.

## Services

- **Wiki.js** (10.0.10.30) - Documentation
- **Home Assistant** (10.0.10.31) - Smart home
- **Immich** (10.0.10.32) - Photo backup
- **Nginx Proxy** (10.0.10.40) - Reverse proxy

## Storage

- TrueNAS NFS mounts for shared storage
- ZFS snapshots for backups

**Last Updated**: November 2025