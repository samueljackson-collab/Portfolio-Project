# Homelab Network Lessons Learned

1. **Color-coded cabling accelerates troubleshooting**
   - Bundling by VLAN color made it obvious when IoT ports were mislabeled; include color legend in rack door.
2. **DHCP guard prevents rogue leases**
   - Guest devices with USB Ethernet adapters occasionally exposed ICS DHCP; enabling guard eliminated random 169.* addresses.
3. **Keep management DHCP off**
   - A firmware upgrade briefly enabled DHCP on mgmt; static-only policy avoided IP conflicts with the gateway.
4. **RF planning matters more than power**
   - Lowering AP power reduced roaming flaps and improved throughput; start at medium, adjust after site survey.
5. **Backups before change windows**
   - Exporting config before firewall edits allowed rapid rollback when a typo blocked IoT → cloud traffic.
6. **Document per-port intent**
   - Adding switch port notes (e.g., "Port 17 = IoT camera") reduced ambiguity during weekend maintenance.
7. **Guest portal rate limits keep WAN happy**
   - 10/2 Mbps cap prevented overnight sync jobs from saturating upstream while still usable for browsing.
