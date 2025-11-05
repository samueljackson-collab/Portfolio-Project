#!/bin/bash
#
# FreeIPA Server Installation Script
# Centralized Identity Management and RADIUS Authentication
# Version: 1.0
# Last Updated: 2025-11-05
#

set -euo pipefail

# Configuration Variables
DOMAIN="homelab.local"
REALM="HOMELAB.LOCAL"
HOSTNAME="freeipa.homelab.local"
IP_ADDRESS="192.168.40.25"
DS_PASSWORD="YourDirectoryManagerPassword"
ADMIN_PASSWORD="YourAdminPassword"
FORWARDER1="192.168.40.35"  # Pi-hole
FORWARDER2="192.168.1.1"    # pfSense

# Install FreeIPA server packages
apt-get update
apt-get install -y freeipa-server freeipa-server-dns freeipa-server-trust-ad

# Set hostname
hostnamectl set-hostname $HOSTNAME
echo "$IP_ADDRESS $HOSTNAME freeipa" >> /etc/hosts

# Install FreeIPA server with integrated DNS
ipa-server-install \
    --realm=$REALM \
    --domain=$DOMAIN \
    --hostname=$HOSTNAME \
    --ip-address=$IP_ADDRESS \
    --ds-password=$DS_PASSWORD \
    --admin-password=$ADMIN_PASSWORD \
    --mkhomedir \
    --setup-dns \
    --forwarder=$FORWARDER1 \
    --forwarder=$FORWARDER2 \
    --no-reverse \
    --unattended

# Install RADIUS support for wireless 802.1X
apt-get install -y freeradius freeipa-server-freeradius

# Configure FreeRadius with FreeIPA
ipa-advise config-server-for-smart-card-auth > /tmp/freeradius-setup.sh
chmod +x /tmp/freeradius-setup.sh

# Enable and start services
systemctl enable ipa
systemctl enable freeradius
systemctl start freeradius

echo "FreeIPA installation complete!"
echo "Access web UI: https://$HOSTNAME"
echo "Admin user: admin"
echo "Kerberos realm: $REALM"
