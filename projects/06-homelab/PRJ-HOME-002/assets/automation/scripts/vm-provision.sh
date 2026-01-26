#!/bin/bash
# VM Provisioning Script for Proxmox
# Creates a VM from template and applies cloud-init settings

set -euo pipefail

VMID=${VMID:-110}
NAME=${NAME:-"app-server"}
TEMPLATE=${TEMPLATE:-"ubuntu-22.04-cloudimg"}
NODE=${NODE:-"proxmox-01"}
MEMORY=${MEMORY:-4096}
CORES=${CORES:-2}
STORAGE=${STORAGE:-"local-lvm"}
BRIDGE=${BRIDGE:-"vmbr0"}
VLAN=${VLAN:-40}
IPCONFIG=${IPCONFIG:-"ip=dhcp"}

qm clone ${TEMPLATE} ${VMID} --name ${NAME} --target ${NODE} --full
qm set ${VMID} --memory ${MEMORY} --cores ${CORES}
qm set ${VMID} --scsihw virtio-scsi-single --scsi0 ${STORAGE}:vm-${VMID}-disk-0
qm set ${VMID} --net0 virtio,bridge=${BRIDGE},tag=${VLAN}
qm set ${VMID} --ipconfig0 ${IPCONFIG}
qm set ${VMID} --agent 1
qm start ${VMID}

echo "Provisioned VM ${NAME} (${VMID}) on ${NODE}"
