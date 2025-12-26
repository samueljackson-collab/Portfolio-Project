# Proxmox VM Inventory (Sanitized)

| VMID | Name           | Purpose                        | HA Group | Storage | Notes                                  |
|------|----------------|--------------------------------|----------|---------|----------------------------------------|
| 100  | freeipa        | Identity, DNS, RADIUS          | core     | ceph    | First to restore in DR.                |
| 110  | pihole         | DNS filtering, DHCP            | core     | ceph    | Secondary DNS: 192.168.40.36.         |
| 120  | nginx-proxy    | Reverse proxy/TLS termination  | core     | ceph    | Uses NPM config from `configs/nginx-proxy-manager`. |
| 130  | rsyslog        | Centralized logging            | core     | ceph    | Forwards to Loki and TrueNAS archive.  |
| 200  | wikijs         | Documentation portal           | apps     | ceph    | Docker Compose defined in `configs/docker-compose-wikijs.yml`. |
| 210  | homeassistant  | Home automation controller     | apps     | ceph    | MQTT integrated; proxy at `home.example.com`. |
| 220  | immich         | Photo backup                   | apps     | ceph    | Media stored on TrueNAS `pool1/media`. |
| 300  | grafana        | Monitoring dashboards          | infra    | ceph    | Prometheus/Loki stack host.            |
| 310  | pbs            | Proxmox Backup Server          | infra    | lvm     | Backups replicated to TrueNAS weekly.  |
