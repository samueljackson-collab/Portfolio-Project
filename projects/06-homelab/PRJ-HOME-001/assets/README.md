# PRJ-HOME-001 Network Infrastructure Assets

## Overview
This directory contains comprehensive documentation, sanitized exports, and configuration artifacts for the homelab network infrastructure build.

## Directory Structure

```
assets/
├── diagrams/          # Network topology diagrams (Mermaid format)
│   ├── physical-topology.mermaid
│   ├── logical-vlan-map.mermaid
│   └── wifi-topology.mermaid
├── configs/           # Network configuration documentation
│   ├── firewall-rules.md
│   ├── wifi-ssid-matrix.md
│   ├── ip-addressing-scheme.md
│   └── vlan-firewall-dhcp.md
├── network-exports/   # Sanitized controller exports
│   └── unifi-controller-export-sanitized.json
├── docs/              # Guides and checklists
│   ├── installation-guide.md
│   ├── configuration-guide.md
│   ├── troubleshooting-guide.md
│   ├── lessons-learned.md
│   └── verification-checklist.md
├── photos/            # Sanitized photo references
│   └── README.md
└── runbooks/          # Deployment and operational procedures
    └── network-deployment-runbook.md
```

## Generated Artifacts

### Diagrams
- **physical-topology.mermaid**: Complete physical network layout showing all equipment, cable runs, and connections.
- **logical-vlan-map.mermaid**: Logical network segmentation with VLAN architecture and firewall rules.
- **wifi-topology.mermaid**: Wi-Fi coverage, AP placement, and SSID-to-VLAN mapping.

### Configuration Documentation
- **firewall-rules.md**: Comprehensive firewall rule set with maintenance procedures.
- **wifi-ssid-matrix.md**: Wireless network configuration with SSID mappings and troubleshooting.
- **ip-addressing-scheme.md**: Complete IP addressing plan with static assignments and DHCP pools.
- **vlan-firewall-dhcp.md**: Combined VLAN, DHCP, and firewall validation matrix with change control steps.

### Controller Export
- **network-exports/unifi-controller-export-sanitized.json**: Sanitized UniFi Network controller backup with VLANs, DHCP scopes, Wi-Fi profiles, firewall policies, and reservations.

### Guides and Checklists
- **installation-guide.md**: Step-by-step rack, controller, and AP installation procedure.
- **configuration-guide.md**: Switch/SSID/firewall configuration with monitoring and backup settings.
- **troubleshooting-guide.md**: Triage flow for adoption, DHCP, Wi-Fi, and VPN issues.
- **lessons-learned.md**: Operational learnings from deploying and operating the network.
- **verification-checklist.md**: End-to-end validation list for audits and change windows.

### Photos
- **photos/README.md**: Sanitized photo inventory (rack, cabling, AP mounts, lab bench).

### Runbooks
- **network-deployment-runbook.md**: Step-by-step deployment guide with validation procedures.

## Status
- ✅ Physical topology diagram
- ✅ Logical VLAN map
- ✅ Wi-Fi topology diagram
- ✅ Configuration documentation
- ✅ Deployment runbook
- ✅ Sanitized UniFi export
- ✅ Guides, checklists, and photo inventory
