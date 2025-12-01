# Verification Checklist

Use this list to confirm the network is configured and hardened as intended.

## Core network
- [ ] WAN online with public IP; DNS resolution works from TRUST.
- [ ] Each VLAN gateway reachable from a host on that VLAN.
- [ ] DHCP leases issued per VLAN with correct DNS/NTP options.
- [ ] Inter-VLAN default deny enforced; logged drops appear for unauthorized flows.

## Wireless
- [ ] `Homelab-Secure` broadcasting WPA3; RADIUS auth succeeds with MFA.
- [ ] `Homelab-IoT` on VLAN 20 with client isolation; sample IoT device gets expected IP.
- [ ] `Homelab-Guest` captive portal loads; guest cannot reach TRUST/SERVERS networks.
- [ ] AP channels/power match `wifi-layout.md` and avoid overlap.

## Security
- [ ] Suricata inline on WAN/DMZ with ET rules updating; no excessive false positives after suppression list applied.
- [ ] Firewall has anti-spoof/bogon enabled on all internal VLANs.
- [ ] Admin access to pfSense and UniFi restricted to TRUST and VPN subnets; MFA enforced on controller.
- [ ] Backups for pfSense/UniFi stored and restore tested in lab.

## Services
- [ ] Proxmox/TrueNAS reachable on VLAN 40; management UI restricted via firewall aliases.
- [ ] DNS overrides for lab services resolve correctly on TRUST and SERVERS.
- [ ] VPN clients receive routes to TRUST + SERVERS and can reach monitoring targets.

