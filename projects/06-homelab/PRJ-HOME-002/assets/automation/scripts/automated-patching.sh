#!/bin/bash
# Automated Patching for Homelab Hosts
# Applies security updates and reboots if required

set -euo pipefail

HOSTS=(proxmox-01 proxmox-02 proxmox-03 truenas-01)
LOG_FILE=${LOG_FILE:-"/var/log/homelab/patching.log"}

mkdir -p $(dirname "$LOG_FILE")

echo "[$(date -u)] Starting automated patching" | tee -a "$LOG_FILE"

for host in "${HOSTS[@]}"; do
  echo "[$(date -u)] Patching ${host}" | tee -a "$LOG_FILE"
  ssh "${host}" "sudo apt-get update && sudo apt-get -y upgrade" | tee -a "$LOG_FILE" || true
  ssh "${host}" "if [ -f /var/run/reboot-required ]; then sudo reboot; fi" | tee -a "$LOG_FILE" || true
  echo "[$(date -u)] Completed ${host}" | tee -a "$LOG_FILE"
  echo "---" | tee -a "$LOG_FILE"
done

echo "[$(date -u)] Patching completed" | tee -a "$LOG_FILE"
