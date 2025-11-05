# Network Topology Documentation

## Overview

This document describes the home network architecture with VLANs, firewall rules, and security measures.

## VLAN Architecture

| VLAN | Name | Subnet | Purpose |
|------|------|--------|---------|
| 10 | Trusted | 10.0.10.0/24 | Admin, workstations, servers |
| 20 | IoT | 10.0.20.0/24 | Smart home devices |
| 30 | Guest | 10.0.30.0/24 | Guest Wi-Fi |

## Security Measures

- Network segmentation via VLANs
- Firewall rules (default deny)
- WPA3 Wi-Fi security
- VPN-only remote access

**Last Updated**: November 2025