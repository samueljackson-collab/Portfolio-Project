# Network Maintenance Runbook

## Overview
**Purpose:** Monthly network maintenance and configuration backup  
**Frequency:** Monthly + as-needed for troubleshooting  
**Estimated Time:** 2-4 hours  
**Risk Level:** Medium

## Prerequisites
- [ ] Backup of current network configuration
- [ ] Maintenance window scheduled (notify household)
- [ ] Access to UDMP admin credentials
- [ ] Secondary internet access available (phone hotspot)

## Monthly Maintenance Checklist

### Step 1: Backup Current Configuration
```bash
# SSH into UDMP
ssh admin@192.168.30.1

# Backup configuration
backup configuration to /data/backups/config-$(date +%Y%m%d).tar.gz

# Download backup to workstation
scp admin@192.168.30.1:/data/backups/config-*.tar.gz ~/network-backups/
```

**Validation:**
- [ ] Backup file created successfully
- [ ] Backup downloaded to local workstation
- [ ] Backup file size > 1MB (sanity check)

### Step 2: Firmware Updates
```bash
# Check for firmware updates
system info
system upgrade check

# If updates available, download and install
system upgrade download
system upgrade install

# Reboot if required
reboot
```

**Expected Downtime:** 5-10 minutes for firmware upgrade

**Validation:**
- [ ] Firmware version updated
- [ ] All devices online after reboot
- [ ] No configuration loss

### Step 3: Review Network Performance
```bash
# Check interface statistics
show interfaces

# Check for errors
show interfaces errors

# Review bandwidth usage
show traffic statistics
```

**Key Metrics to Check:**
- Interface errors < 0.1%
- No CRC errors
- Bandwidth utilization < 70% peak

**Validation:**
- [ ] No excessive errors
- [ ] Bandwidth within normal range
- [ ] All interfaces UP

### Step 4: Wireless Optimization
```bash
# Check for channel congestion
show wireless channels

# Review client connections
show wireless clients

# Check for rogue APs
show wireless rogues
```

**Actions:**
- Change channels if congestion > 50%
- Investigate unrecognized clients
- Disable rogue APs if detected

**Validation:**
- [ ] Channel utilization < 60%
- [ ] All clients recognized
- [ ] No rogue APs detected

### Step 5: Security Audit
```bash
# Review firewall logs
show firewall logs | grep DENY

# Check for failed authentication attempts
show auth-log | grep failed

# Review IPS alerts
show ids-events
```

**Red Flags:**
- > 100 failed auth attempts in 24h
- Repeated connection attempts from single IP
- IPS alerts for known exploits

**Validation:**
- [ ] No suspicious activity
- [ ] Failed attempts within normal range
- [ ] IPS functioning correctly

## Troubleshooting Procedures

### Issue: Internet Connectivity Lost

**Symptoms:** Clients can't access internet, can reach gateway

**Diagnosis:**
```bash
# From UDMP console
ping 1.1.1.1
ping 8.8.8.8
traceroute 1.1.1.1
```

**Solution:**
```bash
# Restart WAN interface
ifconfig eth0 down && ifconfig eth0 up

# Release and renew DHCP (if applicable)
dhclient -r eth0
dhclient eth0

# Check ISP modem status (physical check)
# Reboot ISP modem if necessary
```

**Validation:**
- [ ] Can ping external IPs
- [ ] DNS resolution working
- [ ] Clients can access internet

---

### Issue: High Latency on Network

**Symptoms:** Slow response times, buffering

**Diagnosis:**
```bash
# Check interface utilization
show traffic statistics

# Check for broadcast storms
show interfaces | grep broadcast

# Check CPU utilization on UDMP
top
```

**Solution:**
```bash
# If broadcast storm detected
# Identify source interface and investigate device

# If CPU maxed out
# Check for excessive logging or IPS rules

# Enable QoS if bandwidth saturation
set traffic-control smart-queue enable
```

**Validation:**
- [ ] Latency < 20ms to gateway
- [ ] No broadcast storms
- [ ] CPU utilization < 80%

---

### Issue: Client Can't Connect to Wi-Fi

**Symptoms:** Single client unable to connect, others OK

**Diagnosis:**
```bash
# Check if client is blocked
show wireless block-list

# Check DHCP pool exhaustion
show dhcp leases VLAN-ID

# Review authentication logs
show auth-log | grep <client-MAC>
```

**Solution:**
```bash
# If client blocked, unblock
wireless unblock-client <MAC-address>

# If DHCP pool full, expand or clean old leases
delete dhcp lease <old-MAC>

# If password issue, verify correct SSID password
```

**Validation:**
- [ ] Client successfully connects
- [ ] Client receives IP address
- [ ] Client can reach gateway

---

## VLAN Configuration Changes

### Adding a New VLAN

**Example:** Add VLAN 60 for Lab Network

**Procedure:**
```bash
# Create VLAN on UDMP
configure
set interfaces ethernet vlan 60 address 192.168.60.1/24
set service dhcp-server shared-network-name VLAN60 subnet 192.168.60.0/24 \
    default-router 192.168.60.1 \
    dns-server 192.168.10.2 \
    lease 86400 \
    range 0 start 192.168.60.100 stop 192.168.60.200
commit
save
```

**Switch Configuration:**
```bash
# SSH into UniFi switch
ssh admin@192.168.30.2

# Add VLAN to trunk ports
configure
set interfaces ethernet eth1 vif 60
commit
save
```

**Validation:**
- [ ] VLAN created on all switches
- [ ] DHCP serving addresses
- [ ] Firewall rules applied
- [ ] Test client connectivity

---

## Firewall Rule Management

### Adding a New Allow Rule

**Example:** Allow VLAN 10 to access VLAN 60 on port 8080

```bash
configure
set firewall name VLAN10_TO_VLAN60 rule 100 action accept
set firewall name VLAN10_TO_VLAN60 rule 100 protocol tcp
set firewall name VLAN10_TO_VLAN60 rule 100 destination address 192.168.60.0/24
set firewall name VLAN10_TO_VLAN60 rule 100 destination port 8080
set firewall name VLAN10_TO_VLAN60 rule 100 description "Allow access to Lab Web Service"
commit
save
```

**Testing:**
```bash
# From VLAN 10 client
curl http://192.168.60.50:8080

# Check firewall counters
show firewall name VLAN10_TO_VLAN60 statistics
```

**Validation:**
- [ ] Rule added successfully
- [ ] Traffic passes as expected
- [ ] Rule counters incrementing
- [ ] Documentation updated

---

## Configuration Rollback Procedure

**If changes cause issues:**

```bash
# Restore from backup
restore configuration from /data/backups/config-YYYYMMDD.tar.gz
commit
save
reboot
```

**Validation:**
- [ ] Configuration restored
- [ ] Network functioning as before
- [ ] Document what went wrong

---

## Post-Maintenance Validation

### Connectivity Tests
- [ ] Can ping gateway from all VLANs
- [ ] Can ping 1.1.1.1 (internet) from trusted VLAN
- [ ] DNS resolution working
- [ ] All services accessible

### Performance Tests
- [ ] Speedtest.net shows expected ISP speeds
- [ ] Latency to gateway < 5ms
- [ ] Wi-Fi signal strength adequate in all areas

### Security Validation
- [ ] Guest VLAN isolated from internal networks
- [ ] IoT VLAN can't access trusted VLAN
- [ ] VPN connectivity working

### Monitoring
- [ ] Prometheus scraping network metrics
- [ ] Grafana dashboards showing data
- [ ] Alerts not firing

---

## Documentation Updates
- [ ] Update network diagram if topology changed
- [ ] Update firewall policy matrix if rules changed
- [ ] Update this runbook with any new procedures
- [ ] Update IP address scheme if new devices added

---

## Sign-Off
- [ ] All maintenance tasks completed
- [ ] All validation checks passed
- [ ] Household notified maintenance complete
- [ ] Next maintenance scheduled

**Performed by:** _________________  
**Date:** _________________  
**Next Maintenance Due:** _________________
