#!/bin/bash
#
# Proxmox VM Template Creation Script - Debian 12 (Bookworm)
# Creates a cloud-init enabled VM template with QEMU guest agent
#
# Usage: ./create-debian-template.sh
# Run as: root on Proxmox host
#
# Version: 1.0
# Last Updated: 2025-11-10
#

set -euo pipefail

TEMPLATE_ID=9001
TEMPLATE_NAME="debian-12-cloudimg"
TEMPLATE_DESC="Debian 12 Cloud-Init Template with QEMU Agent"
STORAGE="local-lvm"
CLOUD_INIT_STORAGE="local-lvm"
DEBIAN_IMAGE_URL="https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2"
DEBIAN_IMAGE_FILE="debian-12-genericcloud-amd64.qcow2"

MEMORY=2048
CORES=2
DISK_SIZE="20G"
NETWORK_BRIDGE="vmbr0"
NETWORK_MODEL="virtio"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [[ $EUID -ne 0 ]]; then
  print_error "This script must be run as root"
  exit 1
fi

if ! command -v qm &> /dev/null; then
  print_error "qm command not found. Run this on a Proxmox host."
  exit 1
fi

if qm status $TEMPLATE_ID &> /dev/null; then
  print_error "VM ID $TEMPLATE_ID already exists!"
  read -r -p "Destroy existing VM and continue? (yes/no): " confirm
  if [[ $confirm == "yes" ]]; then
    print_warn "Destroying existing VM $TEMPLATE_ID..."
    qm destroy $TEMPLATE_ID
  else
    print_error "Aborted. Choose a different template ID."
    exit 1
  fi
fi

print_info "Downloading Debian 12 cloud image..."
if [[ ! -f $DEBIAN_IMAGE_FILE ]]; then
  wget -q --show-progress "$DEBIAN_IMAGE_URL" -O "$DEBIAN_IMAGE_FILE"
else
  print_warn "Image file already exists, skipping download"
fi

if [[ ! -f $DEBIAN_IMAGE_FILE ]]; then
  print_error "Debian cloud image not found!"
  exit 1
fi

print_info "Creating VM $TEMPLATE_ID..."
qm create $TEMPLATE_ID \
  --name $TEMPLATE_NAME \
  --description "$TEMPLATE_DESC" \
  --ostype l26 \
  --memory $MEMORY \
  --cores $CORES \
  --cpu host \
  --sockets 1 \
  --agent 1 \
  --bios ovmf \
  --machine q35 \
  --scsihw virtio-scsi-single \
  --net0 $NETWORK_MODEL,bridge=$NETWORK_BRIDGE

print_info "Importing disk image..."
qm importdisk $TEMPLATE_ID $DEBIAN_IMAGE_FILE $STORAGE --format qcow2

print_info "Attaching disk to VM..."
qm set $TEMPLATE_ID \
  --scsi0 $STORAGE:vm-$TEMPLATE_ID-disk-0,discard=on,ssd=1 \
  --boot order=scsi0

print_info "Adding EFI disk and Cloud-Init drive..."
qm set $TEMPLATE_ID --efidisk0 $STORAGE:1,format=raw,efitype=4m,pre-enrolled-keys=1
qm set $TEMPLATE_ID --ide2 $CLOUD_INIT_STORAGE:cloudinit

print_info "Configuring Cloud-Init defaults..."
qm set $TEMPLATE_ID \
  --ciuser debian \
  --cipassword $(openssl rand -base64 12) \
  --sshkeys ~/.ssh/authorized_keys \
  --ipconfig0 ip=dhcp

print_info "Adding serial console and resizing disk..."
qm set $TEMPLATE_ID --serial0 socket --vga serial0
qm disk resize $TEMPLATE_ID scsi0 $DISK_SIZE

print_info "Converting VM to template..."
qm template $TEMPLATE_ID

print_info "Debian 12 template created successfully: $TEMPLATE_NAME"
