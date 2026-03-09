#!/bin/bash
# Resource Usage Report for Proxmox Cluster
# Produces a CSV summary of CPU, memory, storage usage per node

set -euo pipefail

OUTPUT=${OUTPUT:-"/var/log/homelab/resource-usage.csv"}
NODES=(proxmox-01 proxmox-02 proxmox-03)

mkdir -p $(dirname "$OUTPUT")

echo "timestamp,node,cpu_load,memory_used_mb,memory_total_mb,storage_used_gb,storage_total_gb" > "$OUTPUT"

for node in "${NODES[@]}"; do
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  cpu_load=$(uptime | awk -F'load average: ' '{print $2}' | cut -d',' -f1)
  mem_used=$(free -m | awk '/Mem:/ {print $3}')
  mem_total=$(free -m | awk '/Mem:/ {print $2}')
  storage_used=$(df -BG / | awk 'NR==2 {print $3}' | tr -d 'G')
  storage_total=$(df -BG / | awk 'NR==2 {print $2}' | tr -d 'G')
  echo "${timestamp},${node},${cpu_load},${mem_used},${mem_total},${storage_used},${storage_total}" >> "$OUTPUT"
done

cat "$OUTPUT"
