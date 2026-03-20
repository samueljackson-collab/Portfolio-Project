#!/usr/bin/env bash
# provision-ubuntu.sh — Ubuntu 22.04 LTS provisioning script
# Installs baseline tools: htop, vim, curl, git, docker, nmap, python3
set -euo pipefail

LOG="/var/log/provision-ubuntu.log"
exec > >(tee -a "$LOG") 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Ubuntu 22.04 provisioning..."

# ── Update package index ─────────────────────────────────────────────────────
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq

# ── Core utilities ────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing core utilities..."
apt-get install -y -qq \
    htop \
    vim \
    curl \
    wget \
    git \
    nmap \
    net-tools \
    dnsutils \
    tcpdump \
    unzip \
    jq \
    tree \
    tmux \
    bash-completion

# ── Python 3 ─────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing Python 3..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

pip3 install --quiet --upgrade pip
pip3 install --quiet \
    requests \
    pyyaml \
    rich \
    pytest

# ── Docker CE ─────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing Docker CE..."
apt-get install -y -qq \
    ca-certificates \
    gnupg \
    lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -qq
apt-get install -y -qq \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Add vagrant user to docker group
usermod -aG docker vagrant
systemctl enable docker
systemctl start docker

# ── Security tools ────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing security utilities..."
apt-get install -y -qq \
    fail2ban \
    ufw \
    auditd \
    lynis \
    chkrootkit

# ── Firewall baseline ─────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Configuring UFW baseline rules..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment "SSH"
ufw allow from 192.168.56.0/24 comment "Lab private network"
ufw --force enable

# ── SSH hardening ─────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hardening SSH configuration..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
cat >> /etc/ssh/sshd_config <<'SSHCONF'

# Hardening additions — provisioned by provision-ubuntu.sh
Protocol 2
MaxAuthTries 3
LoginGraceTime 30
PermitRootLogin no
PasswordAuthentication yes
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
SSHCONF
systemctl restart sshd

# ── Timezone and NTP ──────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Setting timezone to UTC..."
timedatectl set-timezone UTC
apt-get install -y -qq chrony
systemctl enable chrony
systemctl start chrony

# ── Motd ─────────────────────────────────────────────────────────────────────
cat > /etc/motd <<'MOTD'
╔══════════════════════════════════════════════════╗
║   Portfolio Lab — Ubuntu 22.04 LTS               ║
║   IP: 192.168.56.10   Role: General Purpose       ║
║   Managed by Vagrant + Ansible                    ║
╚══════════════════════════════════════════════════╝
MOTD

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ubuntu provisioning complete."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installed: htop vim curl git docker nmap python3"
