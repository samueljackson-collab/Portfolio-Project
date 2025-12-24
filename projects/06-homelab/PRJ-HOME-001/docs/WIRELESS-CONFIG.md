# Wireless Configuration (UniFi) – PRJ-HOME-001

Comprehensive UniFi wireless configuration for the homelab deployment, including SSID security, radio and advanced tuning, AP-specific parameters, channel planning, site survey outcomes, and guest network enforcement.

## Controller Context
- **Controller:** UniFi Network 7.5.187 (self-hosted)
- **Management IPs:** UniFi Switch `192.168.1.2`, Controller VM `192.168.40.30`
- **APs:** 2× U6 Pro (Living Room `192.168.1.3`, Office `192.168.1.4`)

## SSID Profiles (Security & Advanced Settings)

| SSID | VLAN / Subnet | Security | Radio Profile | Advanced | Client Stats (last 30 days) |
|------|---------------|----------|----------------|----------|-----------------------------|
| **Homelab-Secure** | VLAN 10 / `192.168.1.0/24` | WPA3-Enterprise (SAE transition **off**), RADIUS `192.168.40.25:1812`, shared secret `<REDACTED>` | 2.4 GHz **on** (20 MHz), 5 GHz **on** (80 MHz), band steering **Prefer 5 GHz** | 802.11r Fast Roaming **Adaptive**, 802.11k/v **on**, PMF **Required**, Minimum RSSI `-67 dBm`, DTIM `3`, Multicast Enhancement **on** | Peak clients: **18**, Avg RSSI: **-62 dBm**, 95th percentile throughput: **420 Mbps down / 320 Mbps up**, Roam success: **99.7%** |
| **Homelab-IoT** | VLAN 20 / `192.168.20.0/24` | WPA2-PSK (AES), passphrase `<REDACTED>`, PMF **Optional** | 2.4 GHz **on** (20 MHz), 5 GHz **off** | Client Isolation **on**, Minimum RSSI `-75 dBm`, DTIM `2`, Schedule **05:00–00:00**, Block LAN to WLAN **on**, IGMP Snooping **on** | Peak clients: **27**, Avg RSSI: **-68 dBm**, 95th percentile throughput: **95 Mbps down / 45 Mbps up**, Retry rate: **6%** |
| **Homelab-Guest** | VLAN 30 / `192.168.30.0/24` | Open + UniFi Hotspot captive portal (voucher), PMF **Optional** | 2.4 GHz **on** (20 MHz), 5 GHz **on** (80 MHz) | Guest Policies **on**, Client Isolation **on**, Rate Limit **10/5 Mbps** (User Group: `Guest-Limit`), Session Timeout **8 hours**, Walled Garden: `10.0.0.0/8`, `192.168.0.0/16`, DNS redirect to `192.168.30.1` | Peak clients: **12**, Avg RSSI: **-64 dBm**, 95th percentile throughput: **85 Mbps down / 20 Mbps up**, Captive portal success: **99.1%** |

## AP-Specific Details

| AP | Location | IP / MAC | 2.4 GHz | 5 GHz | Power | Min RSSI | Notable Settings |
|----|----------|----------|---------|-------|-------|----------|------------------|
| **U6 Pro – Living Room** | Main floor, ceiling mount | `192.168.1.3` / `fc:ec:da:aa:bb:01` | Ch **1**, 20 MHz | Ch **36**, 80 MHz | 2.4 GHz: **17 dBm**, 5 GHz: **18 dBm** | `-67 dBm` | DFS **off**, Airtime Fairness **on**, Load Balancing **on** (20 client threshold), LED **off** |
| **U6 Pro – Office** | Upstairs office, ceiling mount | `192.168.1.4` / `fc:ec:da:aa:bb:02` | Ch **6**, 20 MHz | Ch **149**, 80 MHz | 2.4 GHz: **17 dBm**, 5 GHz: **19 dBm** | `-67 dBm` | DFS **off**, Airtime Fairness **on**, Load Balancing **on** (20 client threshold), LED **off** |

## Channel Plan

| Band | AP (Living Room) | AP (Office) | Notes |
|------|------------------|-------------|-------|
| **2.4 GHz** | Channel **1**, 20 MHz, EIRP **17 dBm** | Channel **6**, 20 MHz, EIRP **17 dBm** | Channels 1/6 chosen to avoid overlap; Channel 11 reserved for contingency. |
| **5 GHz** | Channel **36**, 80 MHz, EIRP **18 dBm** | Channel **149**, 80 MHz, EIRP **19 dBm** | DFS channels disabled to avoid radar events; 80 MHz width used for higher throughput with only two APs present. |

## Site Survey Summary (Post-Deployment)
- **Methodology:** Ekahau walk with Sidekick 2; validation survey after channel/power tuning.
- **Coverage Targets:** Achieved `-65 dBm` or better for 92% of active floor area; IoT SSIDs maintain `-70 dBm` on critical sensors.
- **SNR:** Median **27 dB** (2.4 GHz) and **31 dB** (5 GHz); dead zones limited to garage corner (mitigated by 5 GHz roaming preference).
- **Roaming:** 802.11k/v/r enabled; average roam time **42 ms** between APs with no session drops on WPA3 clients.
- **Interference:** 2.4 GHz utilization peaks at **42%** during evening; 5 GHz remains below **28%**. No DFS hit events recorded.
- **Actions Taken:** Reduced 5 GHz power on Living Room AP to balance cell overlap; set minimum RSSI to `-67 dBm` to discourage sticky clients; locked IoT SSID to 2.4 GHz for legacy compatibility.

## Guest Network Policies (UniFi)
- **Network / VLAN:** Guest network bound to VLAN **30** (`192.168.30.0/24`), DHCP served by pfSense at `192.168.30.1`.
- **Captive Portal:** UniFi Hotspot with voucher authentication (8-hour validity, 4-device limit per voucher); custom terms-of-service page and walled garden for `github.com`, `speedtest.net`, and internal DNS.
- **Firewall Rules:** Default **Guest Control** rules plus explicit deny to RFC1918 ranges; allow **80/443/123/853** to internet; drop inter-guest traffic and multicast except mDNS reflector disabled.
- **Bandwidth & QoS:** User Group `Guest-Limit` enforcing **10 Mbps down / 5 Mbps up** and **1 Mbps/1 Mbps per-station burst**; Smart Queues enabled at gateway for fairness.
- **Logging & Monitoring:** Portal auth logs exported to syslog (`192.168.40.30`); anomaly detection alerts enabled for repeated auth failures; guest clients tagged for traffic analytics.

---

**Change Control:** All settings applied and backed up via UniFi site export (`assets/unifi/unifi-config.json`) and pfSense guest firewall ruleset snapshots.
