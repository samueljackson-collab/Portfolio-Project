#!/bin/bash
# Backup Verification Script
set -euo pipefail

echo "Verifying Proxmox backups..."
for node in proxmox-01 proxmox-02 proxmox-03; do
    echo "Checking $node..."
    ssh root@$node "pvesh get /nodes/$node/storage/truenas-nfs/content --content backup"
done
echo "Backup verification complete"
