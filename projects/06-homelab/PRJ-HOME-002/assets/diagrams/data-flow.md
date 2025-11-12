# Data Flow

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User as =d External User
    participant CF as  Cloudflare
    participant Router as =% UDM Firewall
    participant Nginx as = Nginx Proxy
    participant Wiki as = Wiki.js VM
    participant DB as = PostgreSQL
    participant NAS as = TrueNAS
    participant Monitor as = Prometheus
    participant PBS as = Backup Server

    Note over User,PBS: External User Access Flow (HTTPS)

    User->>CF: 1. HTTPS Request<br/>wiki.example.com
    CF->>CF: 2. DNS Resolution<br/>Check DDoS rules
    CF->>Router: 3. Forward to Public IP<br/>Port 443
    Router->>Router: 4. Firewall Check<br/>Port forward rule
    Router->>Nginx: 5. Forward to<br/>192.168.40.25:443

    Nginx->>Nginx: 6. SSL Termination<br/>Let's Encrypt Certificate
    Nginx->>Nginx: 7. Route to Backend<br/>Proxy Host Config
    Nginx->>Wiki: 8. HTTP Request<br/>192.168.40.20:3000

    Wiki->>DB: 9. Query User Session<br/>Port 5432
    DB-->>Wiki: 10. Session Data

    Wiki->>DB: 11. Fetch Page Content<br/>SELECT * FROM pages
    DB-->>Wiki: 12. Page Markdown

    Wiki->>NAS: 13. Load Uploaded Images<br/>NFS Mount /mnt/uploads
    NAS-->>Wiki: 14. Image Files

    Wiki->>Wiki: 15. Render HTML<br/>Markdown  HTML
    Wiki-->>Nginx: 16. HTTP Response<br/>200 OK + HTML

    Nginx-->>Router: 17. HTTPS Response<br/>Encrypted
    Router-->>CF: 18. Forward Response
    CF-->>User: 19. Deliver Content<br/>Cached at Edge

    Note over Monitor,PBS: Background Operations (Continuous)

    loop Every 15 seconds
        Monitor->>Wiki: Scrape Metrics<br/>:9100/metrics
        Wiki-->>Monitor: CPU, RAM, Disk I/O
        Monitor->>DB: Scrape Metrics<br/>:9187/metrics
        DB-->>Monitor: Connections, Queries
    end

    loop Every 24 hours (02:00 AM)
        PBS->>Wiki: Snapshot VM<br/>QEMU Guest Agent
        Wiki-->>PBS: Consistent Snapshot
        PBS->>NAS: Store Backup<br/>NFS Mount
        NAS-->>PBS: Backup Confirmation
    end

    Note over User,PBS: Internal User Access Flow (Direct)

    User->>Router: Direct HTTPS<br/>wiki.homelab.local
    Router->>Nginx: Forward to Proxy<br/>Internal DNS
    Note over Nginx,Wiki: Same flow as External<br/>but no Cloudflare
```

## Source File

Original: `data-flow.mmd`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*
