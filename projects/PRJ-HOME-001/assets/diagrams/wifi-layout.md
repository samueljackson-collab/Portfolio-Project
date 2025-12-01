# Wi‑Fi Layout and Channel Plan

## Access Point Placement
- **AP-Office (U6 Pro):** Mounted central to work area, ceiling height 9ft; primary coverage for Trusted/IoT.
- **AP-Living (U6 Pro):** Mounted near living space hallway, ceiling height 8ft; extends Guest coverage to entryway.

## SSIDs
- `Homelab-Secure` — VLAN 10, WPA3-Enterprise, band steering on, fast roaming enabled.
- `Homelab-IoT` — VLAN 20, WPA2-PSK, client isolation on, schedule 06:00–23:00.
- `Homelab-Guest` — VLAN 30, open with captive portal, bandwidth limits 20/5 Mbps.

## Channel/Power Plan
| AP        | Band | Channel | Width | TX Power |
|-----------|------|---------|-------|----------|
| AP-Office | 2.4G | 1       | 20MHz | Medium   |
| AP-Office | 5G   | 36      | 80MHz | Medium   |
| AP-Living | 2.4G | 6       | 20MHz | Low      |
| AP-Living | 5G   | 149     | 80MHz | Medium   |

- DFS channels avoided for stability in residential area.
- Reduce width to 40MHz on 5G if interference detected.

## Roaming & QoS
- 802.11r fast transition enabled on Secure; disabled on Guest.
- Smart Queues enabled on WAN for fair-sharing guest devices.
- Voice/video devices pinned to Trusted or IoT SSID depending on security needs.

