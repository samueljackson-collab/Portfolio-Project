# Runbook — P03 (Hybrid Network Connectivity Lab)

## Overview

Production operations runbook for hybrid cloud networking infrastructure. This runbook covers VPN tunnel management, connectivity troubleshooting, performance monitoring, and failover procedures for site-to-site connectivity between on-premises and AWS.

**System Components:**
- AWS VPN Gateway and Customer Gateway
- pfSense/WireGuard VPN endpoints
- IPsec tunnels (primary + backup)
- Network monitoring tools (iperf3, mtr)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Tunnel availability** | 99.9% | Both tunnels UP |
| **Primary tunnel uptime** | 99.5% | AWS CloudWatch metrics |
| **Failover time (RTO)** | < 30 seconds | Time to switch to backup tunnel |
| **Latency (RTT)** | < 50ms | Ping on-prem to AWS |
| **Throughput** | > 100 Mbps | iperf3 tests |
| **Packet loss** | < 0.1% | mtr statistics |

---

## Dashboards & Alerts

### Dashboards

#### VPN Tunnel Status Dashboard
```bash
# Check tunnel status (AWS)
aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-xxxxx \
  --query 'VpnConnections[0].VgwTelemetry'

# Check tunnel status (pfSense)
# GUI: VPN → IPsec → Status
# CLI: ipsec status
```

#### Network Performance Dashboard
```bash
# Test latency
ping -c 10 10.0.1.10  # AWS private IP

# Test throughput
iperf3 -c 10.0.1.10 -t 30

# Trace route with MTR
mtr -r -c 100 10.0.1.10
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Both tunnels DOWN | Immediate | Emergency failover to backup WireGuard |
| **P1** | Primary tunnel DOWN | 15 minutes | Investigate and restore |
| **P2** | Latency > 100ms | 1 hour | Check routing, ISP issues |
| **P2** | Packet loss > 1% | 1 hour | MTU/fragmentation investigation |
| **P3** | Throughput < 50 Mbps | 4 hours | Performance optimization |

---

## Standard Operations

### Tunnel Management

#### Check Tunnel Status
```bash
# AWS side
aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-xxxxx

# On-premises (pfSense)
sudo ipsec status
sudo ipsec statusall

# Check tunnel interfaces
ip addr show tun0
```

#### Restart VPN Tunnel
```bash
# Restart specific tunnel (pfSense)
sudo ipsec down vpn-tunnel-1
sleep 5
sudo ipsec up vpn-tunnel-1

# Or restart all IPsec
sudo ipsec restart

# Verify
sudo ipsec status
```

#### Force Failover to Backup Tunnel
```bash
# Disable primary tunnel
sudo ipsec down vpn-tunnel-1

# Verify backup is active
sudo ipsec status | grep vpn-tunnel-2

# Test connectivity
ping -c 5 10.0.1.10

# Re-enable primary after testing
sudo ipsec up vpn-tunnel-1
```

### Performance Testing

#### Latency Test
```bash
# Basic ping test
ping -c 100 10.0.1.10 | tail -1

# MTR (better than traceroute)
mtr -r -c 100 10.0.1.10 > mtr-report.txt

# Expected: < 50ms average
```

#### Throughput Test
```bash
# Start iperf3 server on AWS instance
# SSH to AWS: iperf3 -s

# Run test from on-prem
iperf3 -c 10.0.1.10 -t 60 -i 5

# Expected: > 100 Mbps
# Bi-directional test
iperf3 -c 10.0.1.10 -t 30 --bidir
```

#### Packet Loss Test
```bash
# Extended ping test
ping -c 1000 -i 0.2 10.0.1.10 | grep loss

# Expected: 0% loss or < 0.1%

# MTR for detailed hop analysis
mtr -r -c 1000 10.0.1.10
```

### Network Troubleshooting

#### MTU/Fragmentation Issues
```bash
# Test MTU sizes
ping -M do -s 1400 10.0.1.10  # Should work
ping -M do -s 1450 10.0.1.10  # Might fail if MTU issue

# Find optimal MTU
for mtu in 1500 1450 1400 1350 1300; do
  echo "Testing MTU $mtu"
  ping -M do -s $((mtu-28)) -c 3 10.0.1.10 && echo "MTU $mtu works" && break
done

# Adjust MTU on tunnel interface
sudo ip link set dev tun0 mtu 1400
```

#### Routing Issues
```bash
# Check routing table
ip route show

# Verify VPN routes
ip route | grep 10.0.0.0

# Add static route if missing
sudo ip route add 10.0.0.0/16 dev tun0

# Check AWS route tables
aws ec2 describe-route-tables --route-table-ids rtb-xxxxx
```

---

## Incident Response

### P0: Both Tunnels Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Verify both tunnels are down
sudo ipsec status
aws ec2 describe-vpn-connections --vpn-connection-ids vpn-xxxxx

# 2. Check internet connectivity
ping -c 5 8.8.8.8

# 3. Restart IPsec service
sudo ipsec restart

# 4. Wait 30 seconds for tunnels to establish
sleep 30

# 5. Check status
sudo ipsec status
```

**If Still Down:**
```bash
# Emergency: Establish WireGuard tunnel
sudo systemctl start wg-quick@wg0

# Test connectivity
ping -c 5 10.0.1.10

# Notify team
echo "VPN tunnels down, WireGuard backup active" | \
  mail -s "P0: VPN Outage" ops-team@company.com
```

**Investigation:**
```bash
# Check IPsec logs
sudo tail -100 /var/log/ipsec.log

# Check system logs
sudo journalctl -u ipsec -n 100

# Check AWS VPN status
aws ec2 describe-vpn-connections --vpn-connection-ids vpn-xxxxx

# Common issues:
# - Pre-shared key mismatch
# - Phase 1/2 parameter mismatch
# - Security group blocking UDP 500/4500
```

### P1: Primary Tunnel Down

**Investigation:**
```bash
# Check tunnel telemetry
aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-xxxxx \
  --query 'VpnConnections[0].VgwTelemetry[0]'

# Check logs
sudo grep "vpn-tunnel-1" /var/log/ipsec.log | tail -50

# Test tunnel endpoint reachability
ping -c 5 <AWS-VPN-ENDPOINT-IP>
```

**Remediation:**
```bash
# Restart tunnel
sudo ipsec down vpn-tunnel-1
sudo ipsec up vpn-tunnel-1

# Check Phase 1/2 parameters match
sudo ipsec statusall | grep vpn-tunnel-1

# Verify pre-shared key
# Check: /etc/ipsec.secrets
```

### P2: High Latency

**Investigation:**
```bash
# Detailed latency analysis
mtr -r -c 100 10.0.1.10 > latency-report.txt

# Check for congestion
iperf3 -c 10.0.1.10 -t 30 --get-server-output

# Check ISP issues
mtr -r -c 100 8.8.8.8
```

**Mitigation:**
```bash
# Check local network congestion
iftop -i eth0

# Verify QoS settings (if configured)
tc -s qdisc show dev eth0

# Contact ISP if external issue
# Document evidence: mtr reports, timestamps
```

---

## Troubleshooting

### Common Issues

#### Issue: Tunnel connects but no traffic flows

**Diagnosis:**
```bash
# Check routing
ip route | grep 10.0.0.0

# Check firewall rules
sudo iptables -L -n -v | grep 10.0

# Check security groups (AWS)
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Verify NAT traversal
sudo tcpdump -i eth0 udp port 4500
```

**Solution:**
```bash
# Add routing if missing
sudo ip route add 10.0.0.0/16 dev tun0

# Allow traffic in firewall
sudo iptables -A FORWARD -s 192.168.1.0/24 -d 10.0.0.0/16 -j ACCEPT
sudo iptables -A FORWARD -s 10.0.0.0/16 -d 192.168.1.0/24 -j ACCEPT

# Update AWS security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol all \
  --cidr 192.168.1.0/24
```

---

#### Issue: Tunnel flapping (UP/DOWN repeatedly)

**Diagnosis:**
```bash
# Monitor tunnel state
watch -n 1 'sudo ipsec status'

# Check DPD (Dead Peer Detection) settings
sudo ipsec statusall | grep -i dpd

# Check for NAT issues
sudo tcpdump -i eth0 -n esp or udp port 500 or udp port 4500
```

**Solution:**
```bash
# Adjust DPD timers in ipsec.conf
# dpddelay=30s
# dpdtimeout=120s
# dpdaction=restart

sudo ipsec reload
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check tunnel status
make test-connectivity

# Check latency
ping -c 10 10.0.1.10
```

### Weekly Tasks
```bash
# Performance benchmark
make benchmark

# Review logs
sudo grep ERROR /var/log/ipsec.log

# Update MTR reports
mtr -r -c 100 10.0.1.10 > reports/mtr-$(date +%Y%m%d).txt
```

### Monthly Tasks
```bash
# Failover drill
# Disable primary, verify backup takes over
sudo ipsec down vpn-tunnel-1
# Test connectivity, then restore
sudo ipsec up vpn-tunnel-1

# Review and rotate pre-shared keys (quarterly)
# Update both AWS and on-prem configurations

# Update firmware (pfSense/router)
# Schedule during maintenance window
```

---

## Quick Reference

### Common Commands
```bash
# Check status
sudo ipsec status
aws ec2 describe-vpn-connections --vpn-connection-ids vpn-xxxxx

# Restart tunnel
sudo ipsec restart

# Test connectivity
make test-connectivity

# Benchmark
make benchmark
```

### Emergency Response
```bash
# P0: Both tunnels down
sudo ipsec restart && sleep 30 && sudo ipsec status

# P1: Start WireGuard backup
sudo systemctl start wg-quick@wg0

# P2: Force tunnel restart
sudo ipsec down vpn-tunnel-1 && sudo ipsec up vpn-tunnel-1
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Network Engineering Team
- **Review Schedule:** Quarterly
- **Feedback:** Submit PR with updates
