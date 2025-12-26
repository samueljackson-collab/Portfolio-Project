# PRJ-HOME-001 Network Infrastructure Assets

## Overview
This directory contains comprehensive documentation and configuration artifacts for the homelab network infrastructure build.

## Directory Structure

```
assets/
├── diagrams/          # Network topology diagrams (Mermaid + SVG exports)
│   ├── physical-topology.mermaid / physical-topology.svg
│   └── logical-vlan-map.mermaid / logical-vlan-map.svg
├── configs/           # Network configuration documentation and monitoring evidence
│   ├── firewall-rules.md
│   ├── firewall-rules-matrix.md
│   ├── wifi-ssid-matrix.md
│   ├── ip-addressing-scheme.md
│   └── monitoring-observations.md
├── screenshots/       # Sanitized UniFi + Proxmox dashboards (placeholder)
└── runbooks/          # Deployment and operational procedures
    └── network-deployment-runbook.md
```

## Generated Artifacts

### Diagrams
- **physical-topology.mermaid/.svg**: Complete physical network layout showing all equipment, cable runs, and connections
- **logical-vlan-map.mermaid/.svg**: Logical network segmentation with VLAN architecture and firewall rules

### Configuration Documentation
- **firewall-rules.md**: Comprehensive firewall rule set with maintenance procedures
- **wifi-ssid-matrix.md**: Wireless network configuration with SSID mappings and troubleshooting
- **ip-addressing-scheme.md**: Complete IP addressing plan with static assignments and DHCP pools
- **monitoring-observations.md**: Prometheus/Grafana/Loki evidence with sanitized metrics and log lines

### Screenshots
- Pending sanitized UniFi and Proxmox dashboards (stored externally to avoid binary assets in repo).

### Runbooks
- **network-deployment-runbook.md**: Step-by-step deployment guide with validation procedures

## Usage

### Viewing Mermaid Diagrams
Mermaid diagrams can be viewed using:
- GitHub (renders automatically in markdown)
- VS Code with Mermaid extension
- Online: https://mermaid.live/

### Implementation
Follow the network-deployment-runbook.md for complete deployment procedures.

## Status
- ✅ Physical topology diagram
- ✅ Logical VLAN map
- ⚠️ Sanitized dashboard screenshots stored externally (not committed as binaries)
- ✅ Monitoring evidence excerpts (Prometheus/Grafana/Loki)
- 📝 Configuration documentation (in progress)
- 📝 Deployment runbook (in progress)
