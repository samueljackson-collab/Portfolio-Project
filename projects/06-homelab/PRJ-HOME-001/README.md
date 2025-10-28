# PRJ-HOME-001: Homelab & Secure Network Build

**Status:** 🟢 Completed (Documentation Pending)
**Category:** Homelab & Infrastructure
**Technologies:** UniFi, VLANs, pfSense/OPNsense, Networking

---

## Overview

Designed and implemented a secure home network from the ground up, including physical cabling, network segmentation, and enterprise-grade Wi-Fi management.

## Project Goals

- Learn enterprise networking concepts hands-on
- Create isolated network segments for different use cases
- Implement security best practices at the network layer
- Build a foundation for virtualization and service hosting

## Implementation Summary

### Physical Infrastructure
- Rack-mounted networking equipment
- Structured cabling (Cat6/Cat6a)
- Patch panels and cable management
- UPS for power reliability

### Network Segmentation
- **Trusted VLAN** - Personal devices, trusted computers
- **IoT VLAN** - Smart home devices (isolated from trusted network)
- **Guest VLAN** - Visitor access with internet-only connectivity
- **Lab VLAN** - Experimental systems and testing

### Security Features
- Inter-VLAN firewall rules
- Device isolation within IoT network
- WPA3 encryption on all SSIDs
- Guest network portal with time-based access
- VPN for secure remote access

### Hardware
- UniFi Dream Machine or USG (Unified Security Gateway)
- UniFi Switches (PoE for access points)
- UniFi Access Points (mesh-capable, VLAN-aware)
- NAS for centralized storage

## Skills Demonstrated

- Network design and planning
- VLAN configuration and routing
- Firewall rule creation
- Wi-Fi management and optimization
- Physical infrastructure setup
- Network security best practices

## Documentation Status

📝 **Pending:** Network diagrams, configuration exports, and detailed setup guides are being created and will be added to the `assets/` directory.

## Future Enhancements

- Network monitoring with Prometheus and Grafana
- NetFlow analysis for traffic insights
- IDS/IPS integration
- Automated configuration backups

---

**Last Updated:** October 28, 2025
