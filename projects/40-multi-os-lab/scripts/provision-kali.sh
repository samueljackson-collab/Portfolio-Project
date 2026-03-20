#!/usr/bin/env bash
# provision-kali.sh — Kali Linux 2024 provisioning script
# Updates system and installs: metasploit-framework, burpsuite, wireshark + full toolset
set -euo pipefail

LOG="/var/log/provision-kali.log"
exec > >(tee -a "$LOG") 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Kali Linux 2024 provisioning..."

# ── Update package index ─────────────────────────────────────────────────────
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get full-upgrade -y -qq

# ── Core utilities ────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing core utilities..."
apt-get install -y -qq \
    htop \
    vim \
    curl \
    wget \
    git \
    tmux \
    screen \
    net-tools \
    dnsutils \
    whois \
    jq \
    tree \
    unzip \
    p7zip-full \
    bash-completion \
    zsh \
    zsh-autosuggestions \
    zsh-syntax-highlighting

# ── Metasploit Framework ──────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing Metasploit Framework..."
apt-get install -y -qq metasploit-framework

# Initialise the MSF database
msfdb init 2>/dev/null || true
systemctl enable postgresql 2>/dev/null || true

# ── Burp Suite Community ──────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing Burp Suite Community Edition..."
apt-get install -y -qq burpsuite

# ── Wireshark ─────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing Wireshark..."
echo "wireshark-common wireshark-common/install-setuid boolean true" \
    | debconf-set-selections
apt-get install -y -qq \
    wireshark \
    tshark \
    tcpdump

usermod -aG wireshark vagrant 2>/dev/null || true

# ── Network reconnaissance tools ─────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing network recon tools..."
apt-get install -y -qq \
    nmap \
    masscan \
    nikto \
    dirb \
    gobuster \
    whatweb \
    dnsrecon \
    dnsenum \
    fierce \
    netdiscover \
    arp-scan \
    hping3

# ── Web application testing tools ────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing web app testing tools..."
apt-get install -y -qq \
    sqlmap \
    wfuzz \
    hydra \
    medusa \
    zaproxy

# ── Password auditing tools ───────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing password auditing tools..."
apt-get install -y -qq \
    john \
    hashcat \
    crunch \
    wordlists \
    cewl

# Expand rockyou wordlist
if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
    gunzip -k /usr/share/wordlists/rockyou.txt.gz 2>/dev/null || true
fi

# ── Exploitation tools ────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing exploitation tools..."
apt-get install -y -qq \
    exploitdb \
    searchsploit \
    beef-xss \
    set \
    armitage 2>/dev/null || apt-get install -y -qq exploitdb searchsploit

# ── Forensics tools ───────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing forensics tools..."
apt-get install -y -qq \
    autopsy \
    binwalk \
    foremost \
    volatility3 \
    dc3dd \
    dcfldd \
    exiftool \
    steghide \
    stegcracker

# ── Python 3 and security libraries ──────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing Python security libraries..."
apt-get install -y -qq python3-pip python3-venv
pip3 install --quiet --upgrade pip
pip3 install --quiet \
    impacket \
    scapy \
    pwntools \
    requests \
    beautifulsoup4 \
    paramiko \
    cryptography \
    pycryptodome

# ── Timezone ──────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Setting timezone to UTC..."
timedatectl set-timezone UTC

# ── Motd ─────────────────────────────────────────────────────────────────────
cat > /etc/motd <<'MOTD'
╔══════════════════════════════════════════════════╗
║   Portfolio Lab — Kali Linux 2024.1              ║
║   IP: 192.168.56.20   Role: Security Research     ║
║   Tools: MSF, BurpSuite, Wireshark, 600+ more    ║
╚══════════════════════════════════════════════════╝
MOTD

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Kali provisioning complete."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installed: metasploit burpsuite wireshark nmap sqlmap hydra john hashcat"
