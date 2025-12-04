# Lessons Learned

Key takeaways from building and operating the secure homelab network.

1. **Adoption before segmentation** — Keep devices on a trusted flat network until controller adoption completes; moving too early caused stuck provisioning.
2. **Default deny saves cleanup time** — Starting with deny-all inter-VLAN rules reduced troubleshooting later versus relaxing permissive defaults.
3. **Channel planning matters** — Explicit 20 MHz on 2.4 GHz and non-overlapping 80 MHz on 5 GHz eliminated roaming flaps and retry storms.
4. **Document MAC/IP mappings** — Maintaining a single source of truth for static reservations prevented duplicate leases after restores.
5. **Backups are brittle if untested** — Quarterly restore tests surfaced path/permission issues early; copies are stored offline and in cloud storage.
6. **Inline IPS needs sizing** — Suricata in inline mode added latency on small hardware; enabling only on WAN/DMZ kept throughput acceptable.
7. **Guest isolation simplicity** — Using UniFi client isolation plus pfSense deny rules was faster than per-device ACLs for casual guests.

