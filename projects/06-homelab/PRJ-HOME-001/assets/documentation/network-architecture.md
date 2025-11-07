# Network Architecture

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        ISP[ISP Connection]
    end

    subgraph Security["🔒 Security Layer"]
        PF[pfSense Firewall<br/>192.168.1.1<br/>WAN: DHCP]
        IPS1[Suricata IPS<br/>WAN Interface]
        IPS2[Suricata IPS<br/>DMZ Interface]
        VPN[OpenVPN Server<br/>Port 1194]
    end

    subgraph Core["⚙️ Core Network"]
        SW[UniFi Switch 24 POE<br/>192.168.1.2]
        AP1[U6 Pro - Living Room<br/>192.168.1.3<br/>2.4GHz: Ch1 | 5GHz: Ch36]
        AP2[U6 Pro - Office<br/>192.168.1.4<br/>2.4GHz: Ch6 | 5GHz: Ch149]
    end

    subgraph VLAN10["VLAN 10 - Trusted (High Trust)<br/>192.168.1.0/24"]
        SSID1[📶 Homelab-Secure<br/>WPA3 Enterprise<br/>Band Steering ON]
        WS[Workstation<br/>192.168.1.10]
        LAP[Laptop<br/>192.168.1.11]
    end

    subgraph VLAN20["VLAN 20 - IoT (Medium Trust)<br/>192.168.20.0/24"]
        SSID2[📶 Homelab-IoT<br/>WPA2 PSK<br/>Client Isolation ON]
        IOT1[Smart Lights]
        IOT2[Cameras]
        IOT3[Thermostats]
    end

    subgraph VLAN30["VLAN 30 - Guest (Low Trust)<br/>192.168.30.0/24"]
        SSID3[📶 Homelab-Guest<br/>Open + Captive Portal<br/>10/5 Mbps Limit]
        GUEST[Guest Devices<br/>Internet Only]
    end

    subgraph VLAN40["VLAN 40 - Servers (High Trust)<br/>192.168.40.0/24"]
        PX1[Proxmox-01<br/>192.168.40.10]
        PX2[Proxmox-02<br/>192.168.40.11]
        PX3[Proxmox-03<br/>192.168.40.12]
        TN[TrueNAS<br/>192.168.40.20]
        RADIUS[RADIUS/FreeIPA<br/>192.168.40.25]
        SYSLOG[Syslog Server<br/>192.168.40.30]
    end

    subgraph VLAN50["VLAN 50 - DMZ (Low Trust)<br/>192.168.50.0/24"]
        WEB[Web Server<br/>192.168.50.10<br/>HTTP:80 HTTPS:443]
    end

    subgraph Services["🛠️ Network Services"]
        DHCP[DHCP Server<br/>Per VLAN]
        DNS[DNS Resolver<br/>Unbound<br/>homelab.local]
        TS[Traffic Shaping<br/>VoIP: 20%<br/>Default: 60%<br/>Bulk: 20%]
    end

    %% Internet Connections
    ISP -->|WAN| PF
    PF -->|Protected| IPS1
    
    %% Core Network Connections
    PF -->|Port 1| SW
    SW -->|Port 2 PoE| AP1
    SW -->|Port 3 PoE| AP2
    
    %% VLAN 10 Connections
    SW -->|VLAN 10| SSID1
    AP1 -.->|Broadcast| SSID1
    AP2 -.->|Broadcast| SSID1
    SW -->|Port 8| WS
    SSID1 --> LAP
    
    %% VLAN 20 Connections
    SW -->|VLAN 20| SSID2
    AP1 -.->|Broadcast| SSID2
    AP2 -.->|Broadcast| SSID2
    SSID2 --> IOT1
    SSID2 --> IOT2
    SSID2 --> IOT3
    
    %% VLAN 30 Connections
    SW -->|VLAN 30| SSID3
    AP1 -.->|Broadcast| SSID3
    AP2 -.->|Broadcast| SSID3
    SSID3 --> GUEST
    
    %% VLAN 40 Server Connections
    SW -->|Port 4<br/>VLAN 40| PX1
    SW -->|Port 5<br/>VLAN 40| PX2
    SW -->|Port 6<br/>VLAN 40| PX3
    SW -->|Port 7<br/>VLAN 40| TN
    PX1 -.->|VM| RADIUS
    PX2 -.->|VM| SYSLOG
    
    %% VLAN 50 DMZ Connections
    SW -->|VLAN 50| WEB
    IPS2 -->|Monitor| WEB
    ISP -.->|Port Forward<br/>80/443| WEB
    
    %% Service Connections
    PF --> DHCP
    PF --> DNS
    PF --> TS
    DHCP -.->|Assign IPs| VLAN10
    DHCP -.->|Assign IPs| VLAN20
    DHCP -.->|Assign IPs| VLAN30
    DHCP -.->|Assign IPs| VLAN40
    DHCP -.->|Assign IPs| VLAN50
    DNS -.->|Resolve| VLAN10
    DNS -.->|Resolve| VLAN20
    DNS -.->|Resolve| VLAN30
    DNS -.->|Resolve| VLAN40
    
    %% VPN Access
    ISP -.->|Remote Access| VPN
    VPN -.->|Tunnel| VLAN10
    VPN -.->|Tunnel| VLAN40
    
    %% Authentication
    SSID1 -.->|802.1X| RADIUS
    
    %% Logging
    PF -.->|Logs| SYSLOG
    SW -.->|Logs| SYSLOG
    AP1 -.->|Logs| SYSLOG
    AP2 -.->|Logs| SYSLOG

    %% Firewall Rules Indicators
    classDef highTrust fill:#90EE90,stroke:#006400,stroke-width:3px
    classDef mediumTrust fill:#FFD700,stroke:#FF8C00,stroke-width:2px
    classDef lowTrust fill:#FFB6C1,stroke:#DC143C,stroke-width:2px
    classDef security fill:#87CEEB,stroke:#00008B,stroke-width:3px
    classDef core fill:#DDA0DD,stroke:#8B008B,stroke-width:2px
    
    class VLAN10,WS,LAP,SSID1,PX1,PX2,PX3,TN,RADIUS,SYSLOG,VLAN40 highTrust
    class VLAN20,IOT1,IOT2,IOT3,SSID2 mediumTrust
    class VLAN30,GUEST,SSID3,VLAN50,WEB lowTrust
    class PF,IPS1,IPS2,VPN security
    class SW,AP1,AP2 core

    %% Security Zones Legend
    note1[Security Zones:<br/>🟢 High Trust - Full Access<br/>🟡 Medium Trust - Restricted<br/>🔴 Low Trust - Isolated]
    
    style note1 fill:#F0F8FF,stroke:#4169E1,stroke-width:2px
```

## Source File

Original: `network-architecture.mermaid`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*
