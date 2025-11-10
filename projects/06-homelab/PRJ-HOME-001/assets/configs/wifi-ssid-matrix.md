# Wi-Fi SSID to VLAN Mapping – PRJ-HOME-001

The UniFi deployment broadcasts four carefully tuned SSIDs across three AP AC Pro access points to align wireless access with wired VLAN segmentation.

| SSID Name | VLAN | Security | Password Type | Band | Max Clients | Purpose | Broadcast | Guest Portal |
|-----------|------|----------|---------------|------|-------------|---------|-----------|--------------|
| Homelab-Trusted | 10 (Trusted) | WPA3-Personal with WPA2 fallback | 32-character passphrase stored in Bitwarden | 2.4 GHz & 5 GHz (band steering enabled) | 20 | Primary personal devices (phones, laptops, workstations) | ✔️ | ❌ |
| Homelab-IoT | 50 (IoT) | WPA2-Personal | 24-character passphrase rotated quarterly | 2.4 GHz only | 30 | Smart home devices requiring legacy compatibility | ✔️ | ❌ |
| Homelab-Guest | 99 (Guest) | WPA2-Personal + captive portal | Human-friendly passphrase paired with QR code | 2.4 GHz & 5 GHz | 10 | Visitor internet access with time-boxed vouchers | ✔️ | ✔️ |
| Homelab-Lab | 100 (Lab) | WPA2-Personal (802.1X lab testing optional) | 28-character passphrase shared with lab notebook | 5 GHz only | 5 | Wireless test workloads and security research rigs | ❌ (hidden) | ❌ |

## Access Point Placement & Channel Plan

| AP | Location | SSIDs Broadcast | 2.4 GHz Channel | 5 GHz Channel | Notes |
|----|----------|-----------------|-----------------|---------------|-------|
| AP #1 | Living Room | All SSIDs | 1 | 36 | Central coverage for common areas; preferred roaming anchor. |
| AP #2 | Bedroom | Homelab-Trusted, Homelab-Guest | 6 | 149 | Reduced SSID set lowers airtime contention near sleeping areas. |
| AP #3 | Office | All SSIDs | 11 | 161 | Prioritizes lab/office devices; closest to Proxmox rack. |

- **Channel Strategy**: Non-overlapping 2.4 GHz channels (1/6/11) prevent co-channel interference. DFS channels avoided to maintain compatibility with IoT hardware.
- **Roaming Enhancements**: 802.11k/v assist client steering, while 802.11r fast roaming is enabled for the trusted SSID to ensure seamless VoIP and video calls.
- **Minimum RSSI**: Clients with RSSI below -70 dBm are steered to nearer APs to maintain throughput and reduce retries.

## Captive Portal (Guest)
- Custom landing page outlines acceptable use policy and emergency contact.
- Voucher system issues **24-hour** credentials with a **5 GB** quota and **10 Mbps** per-client rate limit.
- Client isolation prevents peer-to-peer visibility; guests must rely on internet services or VPNs.

## Troubleshooting Tips
- **IoT devices failing to join**: Force 2.4 GHz only, disable band steering temporarily, and confirm MAC randomization is disabled on device.
- **Poor roaming experience**: Verify 802.11r compatibility on client; older devices may require the feature to be disabled on a per-SSID basis.
- **Hidden lab SSID access**: Manually configure SSID and security parameters on the client; ensure the device supports 5 GHz.
- **Captive portal bypass attempts**: Monitor UniFi insights for anomalous MAC churn or repeated authentication failures; regenerate vouchers if compromised.
