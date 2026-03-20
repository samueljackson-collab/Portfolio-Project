#!/usr/bin/env bash
# provision-debian.sh — Debian 12 (Bookworm) minimal server provisioning script
# Objective: lean, secure, production-ready baseline
set -euo pipefail

LOG="/var/log/provision-debian.log"
exec > >(tee -a "$LOG") 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Debian 12 (Bookworm) provisioning..."

# ── Update package index ─────────────────────────────────────────────────────
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq

# ── Minimal server utilities ──────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing minimal server utilities..."
apt-get install -y -qq \
    vim-tiny \
    curl \
    wget \
    git \
    htop \
    net-tools \
    dnsutils \
    tcpdump \
    nmap \
    unzip \
    jq \
    logrotate \
    rsyslog \
    bash-completion \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# ── Python 3 ─────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing Python 3 (minimal)..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv

pip3 install --quiet --upgrade pip
pip3 install --quiet pyyaml requests

# ── Security baseline ─────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing security baseline packages..."
apt-get install -y -qq \
    nftables \
    fail2ban \
    apt-listchanges \
    debsums \
    rkhunter \
    lynis

# ── nftables firewall configuration ──────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Configuring nftables firewall..."
cat > /etc/nftables.conf <<'NFTCONF'
#!/usr/sbin/nft -f
# Debian 12 minimal server firewall — provisioned by provision-debian.sh

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;

        # Allow established/related
        ct state established,related accept

        # Allow loopback
        iifname "lo" accept

        # Allow ICMP ping
        ip protocol icmp icmp type echo-request accept
        ip6 nexthdr icmpv6 accept

        # Allow SSH
        tcp dport 22 accept

        # Allow lab network
        ip saddr 192.168.56.0/24 accept
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}
NFTCONF

systemctl enable nftables
systemctl start nftables

# ── SSH hardening ─────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hardening SSH..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
cat >> /etc/ssh/sshd_config <<'SSHCONF'

# Hardening additions — provisioned by provision-debian.sh
Protocol 2
MaxAuthTries 3
LoginGraceTime 30
PermitRootLogin no
PasswordAuthentication yes
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
UseDNS no
SSHCONF
systemctl restart sshd

# ── Fail2ban configuration ────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Configuring fail2ban..."
cat > /etc/fail2ban/jail.local <<'F2BCONF'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5
backend  = systemd

[sshd]
enabled  = true
port     = ssh
filter   = sshd
maxretry = 3
bantime  = 7200
F2BCONF
systemctl enable fail2ban
systemctl start fail2ban

# ── Unattended upgrades ───────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Configuring unattended security upgrades..."
apt-get install -y -qq unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<'UUCONF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
UUCONF

# ── Timezone and NTP ──────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Setting timezone to UTC and configuring NTP..."
timedatectl set-timezone UTC
apt-get install -y -qq chrony
cat > /etc/chrony/chrony.conf <<'CHRONCONF'
pool 2.debian.pool.ntp.org iburst
driftfile /var/lib/chrony/drift
makestep 1.0 3
rtcsync
logdir /var/log/chrony
CHRONCONF
systemctl enable chrony
systemctl start chrony

# ── System tuning ─────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Applying sysctl hardening..."
cat > /etc/sysctl.d/99-hardening.conf <<'SYSCTL'
# Network hardening
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.tcp_syncookies = 1
net.ipv6.conf.all.accept_redirects = 0
# Kernel hardening
kernel.randomize_va_space = 2
kernel.dmesg_restrict = 1
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
SYSCTL
sysctl -p /etc/sysctl.d/99-hardening.conf 2>/dev/null || true

# ── Motd ─────────────────────────────────────────────────────────────────────
cat > /etc/motd <<'MOTD'
╔══════════════════════════════════════════════════╗
║   Portfolio Lab — Debian 12 (Bookworm)           ║
║   IP: 192.168.56.30   Role: Stable Server         ║
║   Managed by Vagrant + Ansible                    ║
╚══════════════════════════════════════════════════╝
MOTD

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Debian 12 provisioning complete."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Baseline: nftables fail2ban chrony unattended-upgrades sysctl-hardening"
