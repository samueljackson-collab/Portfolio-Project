# PRJ-HOME-001 Lessons Learned

1. **Separate VLANs early**: Standing up VLANs before device adoption avoids re-provisioning cycles and reduces downtime.
2. **Document port profiles**: A small spreadsheet of port → profile mapping prevents accidental untagged traffic leaks when moving equipment.
3. **Backups matter**: Daily encrypted backups saved a rollback when a beta firmware introduced DHCP relay bugs.
4. **Log before drop**: Enabling logging on the first week of firewall rules provided the evidence needed to fine-tune IoT restrictions without blocking legitimate updates.
5. **RF planning beats power**: Lowering transmit power on the LR AP improved roaming and reduced sticky-client issues more than adding another AP.
6. **Captive portal rate limits**: Applying bandwidth limits on the Guest SSID kept livestream events from saturating the WAN uplink.
7. **Out-of-band access**: Keeping management on VLAN 10 with wired access prevented lockout during Wi‑Fi tuning.
