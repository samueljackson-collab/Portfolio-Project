#!/bin/bash
# TrueNAS ZFS Pool Configuration Script
# Creates pool + datasets for homelab infrastructure

set -euo pipefail

POOL_NAME=${POOL_NAME:-tank}
DISKS=(/dev/sdb /dev/sdc /dev/sdd /dev/sde)

echo "Creating ZFS pool ${POOL_NAME}..."
zpool create -f -o ashift=12 ${POOL_NAME} raidz2 ${DISKS[@]}

zfs set compression=lz4 ${POOL_NAME}
zfs set atime=off ${POOL_NAME}

DATASETS=(
  "homelab"
  "homelab/backups"
  "homelab/media"
  "homelab/configs"
  "homelab/databases"
  "homelab/monitoring"
  "homelab/virtualization"
)

for dataset in "${DATASETS[@]}"; do
  echo "Creating dataset ${POOL_NAME}/${dataset}..."
  zfs create ${POOL_NAME}/${dataset}
  zfs set compression=lz4 ${POOL_NAME}/${dataset}
  zfs set recordsize=128K ${POOL_NAME}/${dataset}
  zfs set atime=off ${POOL_NAME}/${dataset}
done

echo "ZFS pool and datasets created successfully."
