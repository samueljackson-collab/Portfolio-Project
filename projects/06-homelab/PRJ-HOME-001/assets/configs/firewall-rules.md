# Firewall Rules Documentation

## Inter-VLAN Rules

### IoT to Trusted - BLOCKED
- Prevents IoT devices from accessing trusted network
- Action: DROP

### Guest to Internal - BLOCKED  
- Isolates guest network from internal networks
- Action: DROP

## IoT Restrictions

- Allow HTTPS (port 443) for updates
- Allow NTP (port 123) for time sync
- Block all other traffic

**Last Updated**: November 2025