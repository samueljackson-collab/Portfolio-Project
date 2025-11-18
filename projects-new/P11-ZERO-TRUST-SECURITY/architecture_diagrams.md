# Architecture Diagrams

## High-Level Zero-Trust Architecture
```mermaid
flowchart LR
    User --> Ingress
    Ingress --> Frontend
    Frontend -->|mTLS| API
    API -->|mTLS| Payments
    API -->|mTLS| Admin
    subgraph "Control Plane"
      SpireServer
      SpireAgent
    end
    SpireServer -->|issues SVID| SpireAgent
    SpireAgent -->|SVID| Frontend
    SpireAgent -->|SVID| API
    SpireAgent -->|SVID| Payments
    SpireAgent -->|SVID| Admin
    Frontend -->|authz check| OPA
    API -->|authz check| OPA
    Payments -->|authz check| OPA
    Admin -->|authz check| OPA
    EnvoyFront((Envoy)):::proxy
    EnvoyAPI((Envoy)):::proxy
    EnvoyPay((Envoy)):::proxy
    EnvoyAdmin((Envoy)):::proxy
    Frontend --- EnvoyFront
    API --- EnvoyAPI
    Payments --- EnvoyPay
    Admin --- EnvoyAdmin
    EnvoyFront <-->|mTLS| EnvoyAPI
    EnvoyAPI <-->|mTLS| EnvoyPay
    EnvoyAPI <-->|mTLS| EnvoyAdmin
    OPA --> Prometheus
    EnvoyAPI --> Prometheus
    Prometheus --> Grafana
    classDef proxy fill:#f8f8ff,stroke:#333;
```
_Render this Mermaid as a 3000x2000 PNG with transparent background._

## SPIRE Identity Flow
```mermaid
sequenceDiagram
    participant W as Workload Pod
    participant A as SPIRE Agent
    participant S as SPIRE Server
    participant CA as CA
    participant E as Envoy Sidecar
    W->>A: SDS request for identity
    A->>S: Node attestation + CSR
    S->>CA: Sign SVID
    CA-->>S: SVID
    S-->>A: Return SVID bundle
    A-->>W: Deliver SVID via Workload API
    W->>E: Present SVID for mTLS handshake
    E-->>W: mTLS session established
```
_Render this Mermaid as a 2400x1200 PNG._

## Request Authorization Flow
```mermaid
sequenceDiagram
    participant User
    participant FE as Frontend
    participant API
    participant OPA
    User->>FE: HTTPS request
    FE->>API: mTLS request with SVID
    API->>OPA: Input with caller/callee SPIFFE IDs
    OPA-->>API: Allow/Deny
    API-->>FE: Response 200 or 403
    FE-->>User: Result displayed
```
_Render this Mermaid as a 2000x1200 PNG._
