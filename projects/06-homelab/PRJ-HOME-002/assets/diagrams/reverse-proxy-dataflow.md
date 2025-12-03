# Reverse Proxy Data Flow

```mermaid
$(cat projects/06-homelab/PRJ-HOME-002/assets/diagrams/reverse-proxy-dataflow.mmd)
```

**Highlights**
- Nginx Proxy Manager terminates TLS and routes traffic based on SNI to internal services.
- Identity flows back to FreeIPA for Wiki.js and Home Assistant.
- Backups and monitoring traffic remain on the internal network with TrueNAS providing NFS/iSCSI storage.
