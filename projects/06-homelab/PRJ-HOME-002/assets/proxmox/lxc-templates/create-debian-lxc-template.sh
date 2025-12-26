#!/bin/bash
#
# Proxmox LXC Template Fetch Script - Debian 12
# Downloads and prepares a Debian LXC template for container deployments.
#
# Usage: ./create-debian-lxc-template.sh
# Run as: root on Proxmox host
#
# Version: 1.0
# Last Updated: 2025-11-10
#

set -euo pipefail

TEMPLATE_STORAGE="local"
TEMPLATE_NAME="debian-12-standard_12.0-1_amd64.tar.zst"

if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] This script must be run as root"
  exit 1
fi

if ! command -v pveam &> /dev/null; then
  echo "[ERROR] pveam command not found. Run this on a Proxmox host."
  exit 1
fi

echo "[INFO] Updating template list..."
pveam update

echo "[INFO] Downloading Debian LXC template to ${TEMPLATE_STORAGE}..."
pveam download ${TEMPLATE_STORAGE} ${TEMPLATE_NAME}

echo "[INFO] Template available at /var/lib/vz/template/cache/${TEMPLATE_NAME}"
