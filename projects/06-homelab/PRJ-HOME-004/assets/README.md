# PRJ-HOME-004 Assets

This directory contains all supporting materials for the Homelab Enterprise Infrastructure Program (v6.0).

## Directory Structure

### `/diagrams`
Mermaid architecture and process diagrams visualizing the homelab infrastructure:
- `architecture-overview.mermaid` - Complete system architecture
- `firewall-policy.mermaid` - Network segmentation and firewall rules
- `backup-strategy.mermaid` - 3-2-1 backup implementation
- `risk-assessment-matrix.mermaid` - Risk probability/impact quadrant
- `implementation-timeline.mermaid` - Project Gantt chart

### `/configs`
Configuration files and templates for infrastructure components:
- Proxmox host and VM configurations
- TrueNAS ZFS dataset definitions
- UniFi network and firewall rules
- WireGuard VPN peer configurations
- Nginx Proxy Manager host definitions
- Docker Compose files for services
- Monitoring stack configurations (Prometheus, Grafana, Loki)

### `/documentation`
Additional technical documentation:
- Operational runbooks
- Disaster recovery procedures
- Security policies and hardening guides
- Change management templates
- Incident response procedures

### `/evidence`
Performance benchmarks, test results, and validation artifacts:
- System performance metrics
- Security scan reports
- Backup verification logs
- Disaster recovery test results
- Uptime and availability reports

## Usage

These assets are referenced throughout the main project README and demonstrate the comprehensive, enterprise-grade approach to homelab infrastructure.

For the complete proposal and implementation plan, see [../README.md](../README.md).
