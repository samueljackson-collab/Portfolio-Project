#!/bin/bash
# Proxmox Backup Automation
# Triggers PBS backups for critical VMs and logs results

set -euo pipefail

PBS_STORAGE=${PBS_STORAGE:-"proxmox-backup"}
LOG_FILE=${LOG_FILE:-"/var/log/homelab/backup-run.log"}
VM_IDS=(100 101 102 110)

mkdir -p $(dirname "$LOG_FILE")

echo "[$(date -u)] Starting backup run" | tee -a "$LOG_FILE"

for vmid in "${VM_IDS[@]}"; do
  echo "[$(date -u)] Backing up VM ${vmid}" | tee -a "$LOG_FILE"
  vzdump ${vmid} --storage ${PBS_STORAGE} --mode snapshot --compress zstd --remove 0 | tee -a "$LOG_FILE"
  echo "[$(date -u)] Completed VM ${vmid}" | tee -a "$LOG_FILE"
  echo "---" | tee -a "$LOG_FILE"
done

echo "[$(date -u)] Backup run finished" | tee -a "$LOG_FILE"
