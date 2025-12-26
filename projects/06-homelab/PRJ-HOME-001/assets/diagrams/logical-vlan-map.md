# Logical Vlan Map

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
flowchart TB
    %% =============================================
    %% Internet Connection
    %% =============================================
    Internet((Internet))

    %% =============================================
    %% Management Zone (VLAN 1)
    %% =============================================
    subgraph ManagementZone[Management Zone - Highest Trust]
        VLAN1[VLAN 1 - Management<br/>192.168.1.0/24<br/>Network Equipment Only]
        
        subgraph VLAN1_Devices[Devices]
            UDMP_MGMT[UDMP: 192.168.1.1]
            USW24_MGMT[Switch 24: 192.168.1.2]
            USW8_MGMT[Switch 8: 192.168.1.3]
            AP1_MGMT[AP #1: 192.168.1.10]
            AP2_MGMT[AP #2: 192.168.1.11]
            AP3_MGMT[AP #3: 192.168.1.12]
        end
    end

    %% =============================================
    %% Trusted Zone (VLAN 10)
    %% =============================================
    subgraph TrustedZone[Trusted Zone - High Trust]
        VLAN10[VLAN 10 - Trusted<br/>192.168.10.0/24<br/>Personal & Work Devices]
        
        subgraph VLAN10_Devices[Devices]
            Proxmox_Trusted[Proxmox: 192.168.10.10]
            TrueNAS_Trusted[TrueNAS: 192.168.10.5]
            Desktop_Trusted[Desktop: 192.168.10.20]
            PiHole_Trusted[Pi-hole: 192.168.10.2]
            Laptop1_Trusted[MacBook: 192.168.10.21]
            Laptop2_Trusted[ThinkPad: 192.168.10.22]
        end
    end

    %% =============================================
    %% Isolated Zones
    %% =============================================
    subgraph IsolatedZones[Isolated Zones - Restricted Access]
        %% IoT Zone (VLAN 50)
        subgraph IoTZone[IoT Zone - No Internal Access]
            VLAN50[VLAN 50 - IoT<br/>192.168.50.0/24<br/>Smart Home Devices]
            
            subgraph VLAN50_Devices[Devices]
                SmartTV_IoT[Smart TV: 192.168.50.10]
                Thermostat_IoT[Thermostat: 192.168.50.11]
                SmartLock_IoT[Smart Lock: 192.168.50.12]
                HueBulbs_IoT[Hue Bulbs: 192.168.50.20-29]
                WyzeCam_IoT[Wyze Cams: 192.168.50.30-31]
            end
        end

        %% Guest Zone (VLAN 99)
        subgraph GuestZone[Guest Zone - Internet Only]
            VLAN99[VLAN 99 - Guest<br/>192.168.99.0/24<br/>Visitor Access]
            
            subgraph VLAN99_Devices[Devices]
                GuestPhone[Guest Phone: DHCP]
                GuestLaptop[Guest Laptop: DHCP]
            end
        end

        %% Lab Zone (VLAN 100)
        subgraph LabZone[Lab Zone - Testing & Research]
            VLAN100[VLAN 100 - Lab<br/>192.168.100.0/24<br/>Experimental Systems]
            
            subgraph VLAN100_Devices[Devices]
                Kali_Lab[Kali Linux: 192.168.100.10]
                Metasploitable_Lab[Metasploitable: 192.168.100.11]
                UbuntuTest_Lab[Ubuntu Test: 192.168.100.12]
            end
        end
    end

    %% =============================================
    %% Firewall Rules - ALLOW Connections (Green)
    %% =============================================
    
    %% Internet Access
    Internet -->|NAT/Firewall| VLAN1
    VLAN1 -->|Internet Access| Internet
    
    VLAN10 -->|Internet Access| Internet
    VLAN50 -->|HTTP/HTTPS/DNS Only| Internet
    VLAN99 -->|Internet Access<br/>Rate Limited| Internet
    VLAN100 -->|Internet Access<br/>With Restrictions| Internet

    %% Management Access
    VLAN10 -.->|ALLOW: TCP 22,443,8443| VLAN1
    
    %% Trusted to IoT Control
    VLAN10 -.->|ALLOW: mDNS UDP 5353| VLAN50
    VLAN10 -.->|ALLOW: HTTP/HTTPS to specific IPs| VLAN50
    
    %% Trusted to Lab Access
    VLAN10 -.->|ALLOW: All Traffic| VLAN100
    
    %% Lab to Trusted (Restricted)
    VLAN100 -.->|ALLOW: TCP 8080,8443 only| VLAN10

    %% =============================================
    %% Firewall Rules - DENY Connections (Red)
    %% =============================================
    
    %% IoT Isolation
    VLAN50 -.-x|DENY: All Internal Traffic| VLAN1
    VLAN50 -.-x|DENY: All Internal Traffic| VLAN10
    VLAN50 -.-x|DENY: All Internal Traffic| VLAN99
    VLAN50 -.-x|DENY: All Internal Traffic| VLAN100

    %% Guest Isolation
    VLAN99 -.-x|DENY: All Internal Networks| VLAN1
    VLAN99 -.-x|DENY: All Internal Networks| VLAN10
    VLAN99 -.-x|DENY: All Internal Networks| VLAN50
    VLAN99 -.-x|DENY: All Internal Networks| VLAN100

    %% Lab Isolation
    VLAN100 -.-x|DENY: Management Access| VLAN1
    VLAN100 -.-x|DENY: IoT Access| VLAN50
    VLAN100 -.-x|DENY: Guest Access| VLAN99

    %% =============================================
    %% Styling and Colors
    %% =============================================
    classDef internet fill:#ffebee,stroke:#c62828
    classDef management fill:#f3e5f5,stroke:#7b1fa2
    classDef trusted fill:#e8f5e8,stroke:#2e7d32
    classDef iot fill:#fff3e0,stroke:#ef6c00
    classDef guest fill:#f5f5f5,stroke:#9e9e9e
    classDef lab fill:#e0f2f1,stroke:#00695c
    
    class Internet internet
    class ManagementZone management
    class TrustedZone trusted
    class IoTZone iot
    class GuestZone guest
    class LabZone lab

    %% =============================================
    %% Legend
    %% =============================================
    
    subgraph Legend[Firewall Rules Legend]
        AllowSolid[Solid Green Line: ALLOW Traffic]
        AllowDashed[Dashed Green Line: ALLOW with Restrictions]
        DenyDashed[Dashed Red Line: DENY Traffic]
        TrustLevels[Trust Levels: Management > Trusted > Lab > IoT = Guest]
    end
```

## Source File

Original: `logical-vlan-map.mermaid`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*
