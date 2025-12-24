#!/bin/bash
# TrueNAS ZFS Dataset Creation Script
# This script sets up the storage architecture for the homelab
# Run on TrueNAS CORE 13.x

set -euo pipefail

POOL_NAME="tank"
COMPRESSION="zstd"
ATIME="off"
RECORDSIZE_DEFAULT="128k"

echo "Creating ZFS datasets for homelab infrastructure..."

# Parent dataset for application data
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=${RECORDSIZE_DEFAULT} \
           ${POOL_NAME}/homelab

# Proxmox VM/CT backups
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=1M \
           -o quota=500G \
           ${POOL_NAME}/homelab/backups

# Immich photo storage
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=1M \
           -o quota=2T \
           ${POOL_NAME}/homelab/media

# Application configurations
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=128k \
           -o quota=10G \
           ${POOL_NAME}/homelab/configs

# PostgreSQL databases (Immich, Wiki.js, etc.)
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=8k \
           -o quota=50G \
           ${POOL_NAME}/homelab/databases

# Prometheus time-series data
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=16k \
           -o quota=100G \
           ${POOL_NAME}/homelab/prometheus

# Loki log aggregation
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=128k \
           -o quota=50G \
           ${POOL_NAME}/homelab/loki

# Grafana dashboards and metadata
zfs create -o compression=${COMPRESSION} \
           -o atime=${ATIME} \
           -o recordsize=128k \
           -o quota=5G \
           ${POOL_NAME}/homelab/grafana

echo "Dataset creation complete."
echo ""
echo "Created datasets:"
zfs list -r ${POOL_NAME}/homelab
