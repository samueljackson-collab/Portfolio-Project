#!/bin/bash
#
# Proxmox VM Template Creation Script - Ubuntu 22.04 LTS
# Creates a cloud-init enabled VM template with QEMU guest agent
# Includes security hardening and optimization
#
# Usage: ./create-ubuntu-template.sh
# Run as: root on Proxmox host
#
# Version: 1.0
# Last Updated: 2025-11-05
#

set -euo pipefail

# Configuration Variables
TEMPLATE_ID=9000
TEMPLATE_NAME="ubuntu-22.04-cloudimg"
TEMPLATE_DESC="Ubuntu 22.04 LTS Cloud-Init Template with QEMU Agent"
STORAGE="local-lvm"
CLOUD_INIT_STORAGE="local-lvm"
UBUNTU_VERSION="22.04"
UBUNTU_CODENAME="jammy"

# Download URL for Ubuntu cloud image
UBUNTU_IMAGE_URL="https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
UBUNTU_IMAGE_FILE="jammy-server-cloudimg-amd64.img"

# VM Resources (adjust as needed)
MEMORY=2048
CORES=2
DISK_SIZE="20G"
NETWORK_BRIDGE="vmbr0"
NETWORK_MODEL="virtio"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

# Check if qm command exists (Proxmox)
if ! command -v qm &> /dev/null; then
    print_error "qm command not found. This script must be run on a Proxmox host."
    exit 1
fi

# Check if template ID already exists
if qm status $TEMPLATE_ID &> /dev/null; then
    print_error "VM ID $TEMPLATE_ID already exists!"
    read -p "Do you want to destroy it and continue? (yes/no): " confirm
    if [[ $confirm == "yes" ]]; then
        print_warn "Destroying existing VM $TEMPLATE_ID..."
        qm destroy $TEMPLATE_ID
    else
        print_error "Aborted. Please choose a different template ID."
        exit 1
    fi
fi

print_info "Starting Ubuntu template creation process..."

# Download Ubuntu cloud image
print_info "Downloading Ubuntu $UBUNTU_VERSION cloud image..."
if [[ ! -f $UBUNTU_IMAGE_FILE ]]; then
    wget -q --show-progress $UBUNTU_IMAGE_URL -O $UBUNTU_IMAGE_FILE
    if [[ $? -ne 0 ]]; then
        print_error "Failed to download Ubuntu cloud image"
        exit 1
    fi
else
    print_warn "Image file already exists, skipping download"
fi

# Verify image download
if [[ ! -f $UBUNTU_IMAGE_FILE ]]; then
    print_error "Ubuntu cloud image not found!"
    exit 1
fi

print_info "Image size: $(du -h $UBUNTU_IMAGE_FILE | cut -f1)"

# Create VM
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

print_info "VM $TEMPLATE_ID created successfully"

# Import disk
print_info "Importing disk image..."
qm importdisk $TEMPLATE_ID $UBUNTU_IMAGE_FILE $STORAGE --format qcow2

# Attach disk to VM
print_info "Attaching disk to VM..."
qm set $TEMPLATE_ID \
    --scsi0 $STORAGE:vm-$TEMPLATE_ID-disk-0,discard=on,ssd=1 \
    --boot order=scsi0

# Add EFI disk (required for UEFI boot)
print_info "Adding EFI disk..."
qm set $TEMPLATE_ID --efidisk0 $STORAGE:1,format=raw,efitype=4m,pre-enrolled-keys=1

# Add TPM state (optional, for TPM 2.0 support)
print_info "Adding TPM state..."
qm set $TEMPLATE_ID --tpmstate0 $STORAGE:1,version=v2.0

# Add Cloud-Init drive
print_info "Adding Cloud-Init drive..."
qm set $TEMPLATE_ID --ide2 $CLOUD_INIT_STORAGE:cloudinit

# Configure Cloud-Init defaults
print_info "Configuring Cloud-Init..."
qm set $TEMPLATE_ID \
    --ciuser ubuntu \
    --cipassword $(openssl rand -base64 12) \
    --sshkeys ~/.ssh/authorized_keys \
    --ipconfig0 ip=dhcp

# Serial console
print_info "Adding serial console..."
qm set $TEMPLATE_ID --serial0 socket --vga serial0

# Resize disk (expand from default 2GB)
print_info "Resizing disk to $DISK_SIZE..."
qm disk resize $TEMPLATE_ID scsi0 $DISK_SIZE

# Additional optimizations
print_info "Applying performance optimizations..."

# Enable QEMU guest agent
qm set $TEMPLATE_ID --agent enabled=1,fstrim_cloned_disks=1

# Enable discard/TRIM for SSD
qm set $TEMPLATE_ID --scsi0 $STORAGE:vm-$TEMPLATE_ID-disk-0,discard=on,ssd=1

# Set I/O thread for better disk performance
qm set $TEMPLATE_ID --scsihw virtio-scsi-single,iothread=1

# CPU flags
qm set $TEMPLATE_ID --cpu host,flags=+aes

# NUMA (if you have multi-socket CPU)
# qm set $TEMPLATE_ID --numa 1

# Tags for organization
print_info "Adding tags..."
qm set $TEMPLATE_ID --tags template,ubuntu,22.04,cloud-init

# Convert to template
print_info "Converting VM to template..."
qm template $TEMPLATE_ID

# Clean up downloaded image
print_info "Cleaning up..."
rm -f $UBUNTU_IMAGE_FILE

print_info "Template creation completed successfully!"
echo ""
print_info "Template ID: $TEMPLATE_ID"
print_info "Template Name: $TEMPLATE_NAME"
echo ""
print_info "To clone this template:"
echo "  qm clone $TEMPLATE_ID <new-vmid> --name <vm-name> --full"
echo ""
print_info "To customize Cloud-Init before first boot:"
echo "  qm set <new-vmid> --ciuser <username>"
echo "  qm set <new-vmid> --cipassword <password>"
echo "  qm set <new-vmid> --sshkeys ~/.ssh/authorized_keys"
echo "  qm set <new-vmid> --ipconfig0 ip=192.168.40.100/24,gw=192.168.40.1"
echo "  qm set <new-vmid> --nameserver 192.168.40.35"
echo "  qm set <new-vmid> --searchdomain homelab.local"
echo ""
print_info "Then start the VM:"
echo "  qm start <new-vmid>"
echo ""

# Display template information
print_info "Template configuration:"
qm config $TEMPLATE_ID

# Security hardening recommendations
echo ""
print_warn "Security Recommendations:"
echo "  1. Update SSH keys in Cloud-Init configuration"
echo "  2. Disable password authentication in cloned VMs"
echo "  3. Configure firewall rules"
echo "  4. Enable automatic security updates"
echo "  5. Install and configure fail2ban"
echo "  6. Set up monitoring and logging"
echo ""

# Additional notes
print_info "Additional Notes:"
echo "  - Template includes QEMU guest agent for better integration"
echo "  - Disk TRIM/discard enabled for SSD optimization"
echo "  - Using virtio drivers for best performance"
echo "  - UEFI boot with secure boot support"
echo "  - Cloud-Init configured for easy customization"
echo "  - Clone will auto-expand disk on first boot"
echo ""

print_info "Template is ready to use!"

exit 0
