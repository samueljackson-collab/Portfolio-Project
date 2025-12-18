# Troubleshooting Guide

Common failure modes and quick checks for the homelab network.

## Adoption issues
- **Device stuck in Pending:** Confirm DNS resolves `unifi.lab.local` and inform URL is reachable; SSH in and re-run `set-inform`.
- **Wrong VLAN during adoption:** Ensure the switch port is native VLAN 10 (Trusted) until provisioning completes.

## DHCP failures
- **No lease on IoT/Guest:** Verify interface DHCP scopes are enabled and not overlapping; check if switch port tags include the VLAN.
- **Static reservations ignored:** Confirm MAC case matches; ensure reservation is inside the subnet but outside the dynamic pool.

## Wi‑Fi problems
- **Poor coverage on 5 GHz:** Reduce channel width to 40 MHz or lower TX power; realign AP placement per `wifi-layout.md`.
- **Captive portal redirect fails:** Check DNS resolution for guest landing page; ensure firewall rule allows port 443 to portal host.

## Firewall/VPN
- **Inter-VLAN blocks unexpectedly:** Temporarily enable logging on deny rules; validate rule order and interface direction.
- **OpenVPN connects but no routes:** Push `redirect-gateway` or specific routes; verify client firewall allows TAP/TUN traffic.

## IPS performance
- **Suricata drops legitimate traffic:** Add suppression entries for noisy rules; tune to alert-only on LAN while refining policies.

## Controller access
- **MFA/SSO lockout:** Use local break-glass admin created during setup; restrict to TRUST network.
- **Backups failing:** Ensure backup path has write permissions and sufficient disk; test restore in lab quarterly.

