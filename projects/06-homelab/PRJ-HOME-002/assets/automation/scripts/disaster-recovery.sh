#!/bin/bash
# Disaster Recovery Automation Script
set -euo pipefail

echo "Starting disaster recovery procedure..."
echo "1. Verifying backups..."
echo "2. Checking cluster status..."
pvecm status
echo "3. Listing available VM backups..."
for node in proxmox-01 proxmox-02 proxmox-03; do
    ssh root@$node "ls -lh /mnt/pve/truenas-backups/"
done
echo "DR check complete. See documentation for restore procedures."
