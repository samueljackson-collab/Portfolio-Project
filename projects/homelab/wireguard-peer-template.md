# WireGuard Peer Template

1. Generate key pair on admin workstation:
   ```bash
   wg genkey | tee sam-admin.key | wg pubkey > sam-admin.pub
   ```
2. Register peer in password manager with expiration review date.
3. Update firewall rule-set to allow UDP/51820 from new peer IP.
4. Append to `/etc/wireguard/wg0.conf` on VPN gateway:
   ```ini
   [Peer]
   # Sam Admin Laptop
   PublicKey = <sam-admin.pub>
   AllowedIPs = 10.10.30.25/32
   PersistentKeepalive = 25
   ```
5. Commit config changes and push to git for approval trail.
6. Distribute `.conf` bundle via secure file share with TTL link.
