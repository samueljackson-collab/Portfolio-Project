# Backup Recovery

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
flowchart TB
    subgraph Daily["< Nightly Backup Jobs (02:00 AM)"]
        direction LR
        Job1["Job 1: Wiki.js VM<br/>02:00 AM<br/>Full + Incremental"]
        Job2["Job 2: Home Assistant<br/>02:15 AM<br/>Full + Incremental"]
        Job3["Job 3: Immich VM<br/>02:30 AM<br/>Full + Incremental"]
        Job4["Job 4: PostgreSQL VM<br/>02:45 AM<br/>Full + Incremental"]
        Job5["Job 5: All Containers<br/>03:00 AM<br/>Weekly Full Only"]
    end

    subgraph PBS["= Proxmox Backup Server"]
        direction TB
        Scheduler["Backup Scheduler<br/>Job Definitions"]
        Dedup["Deduplication Engine<br/>Content-Defined Chunking"]
        Compress["Compression<br/>Zstandard"]
        Encrypt["Encryption<br/>AES-256-GCM"]
        Datastore["Datastore: homelab-backups<br/>Retention: 7 daily, 4 weekly, 3 monthly"]
    end

    subgraph Storage["= Storage Backends"]
        direction LR
        Local["Local SSD<br/>4TB External<br/>Fast tier"]
        NFS["TrueNAS NFS Mount<br/>/mnt/backup/pbs<br/>Capacity tier"]
    end

    subgraph Verify[" Verification & Testing"]
        direction TB
        AutoVerify["Auto-Verify<br/>Nightly after backups"]
        ManualTest["Monthly Restore Test<br/>First Sunday"]
        Script["verify-pbs-backups.sh<br/>Health checks<br/>Email alerts"]
    end

    subgraph Recovery["= Recovery Scenarios"]
        direction TB
        Scenario1["Scenario 1: File Recovery<br/>Mount snapshot, copy files<br/>Time: 5 minutes"]
        Scenario2["Scenario 2: Full VM Restore<br/>Restore to same ID<br/>Time: 15-30 minutes"]
        Scenario3["Scenario 3: Clone to Test<br/>Restore to new ID<br/>Time: 15-30 minutes"]
        Scenario4["Scenario 4: Disaster Recovery<br/>New Proxmox host<br/>Time: 2-4 hours"]
    end

    Job1 & Job2 & Job3 & Job4 & Job5 --> Scheduler
    Scheduler --> Dedup
    Dedup --> Compress
    Compress --> Encrypt
    Encrypt --> Datastore

    Datastore -->|Hot Data<br/>Recent Backups| Local
    Datastore -->|Cold Data<br/>Archive| NFS

    Datastore --> AutoVerify
    AutoVerify --> Script
    Script -->|Monthly| ManualTest

    ManualTest --> Scenario1
    ManualTest --> Scenario2
    ManualTest --> Scenario3

    Datastore -.->|Disaster Event| Scenario4

    style Daily fill:#e3f2fd
    style PBS fill:#fff3e0
    style Storage fill:#e8f5e9
    style Verify fill:#f3e5f5
    style Recovery fill:#ffebee
```

## Source File

Original: `backup-recovery.mmd`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*
