# Physical Topology

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
flowchart TD
    %% =============================================
    %% Internet/ISP Layer
    %% =============================================
    Internet[Internet<br/>ISP Connection]
    
    ISP_Modem[ISP Modem<br/>Bridge Mode<br/>Public IP: Dynamic]

    %% =============================================
    %% Edge/Gateway Layer
    %% =============================================
    UDMP[UniFi Dream Machine Pro<br/>192.168.1.1<br/>Router/Firewall/VPN/Controller]

    %% =============================================
    %% Core Switching Layer
    %% =============================================
    USW24[UniFi Switch 24 PoE<br/>192.168.1.2<br/>95W PoE Budget]
    
    USW8[UniFi Switch 8 PoE<br/>192.168.1.3<br/>Secondary Location]

    %% =============================================
    %% Access Layer - Rack Devices (VLAN 10)
    %% =============================================
    subgraph Rack[Network Rack - 12U Wall Mount]
        Proxmox[Proxmox Server<br/>Port 5<br/>VLAN 10<br/>192.168.10.10]
        TrueNAS[TrueNAS Server<br/>Port 6<br/>VLAN 10<br/>192.168.10.5]
        Desktop[Desktop Workstation<br/>Port 7<br/>VLAN 10<br/>192.168.10.20]
        Printer[Network Printer<br/>Port 8<br/>VLAN 10<br/>192.168.10.30]
    end

    %% =============================================
    %% Access Layer - Living Room
    %% =============================================
    subgraph LivingRoom[Living Room]
        SmartTV[Smart TV<br/>Port 9<br/>VLAN 50<br/>192.168.50.10]
        AP1[UniFi AP AC Pro #1<br/>Port 15<br/>PoE ⚡<br/>Living Room]
    end

    %% =============================================
    %% Access Layer - Bedroom
    %% =============================================
    subgraph Bedroom[Bedroom]
        AP2[UniFi AP AC Pro #2<br/>Port 16<br/>PoE ⚡<br/>Bedroom]
    end

    %% =============================================
    %% Access Layer - Office
    %% =============================================
    subgraph Office[Office]
        AP3[UniFi AP AC Pro #3<br/>Port 17<br/>PoE ⚡<br/>Office]
    end

    %% =============================================
    %% Wireless Clients by VLAN
    %% =============================================
    subgraph WirelessClients[Wireless Clients]
        subgraph VLAN10_Clients[VLAN 10 - Trusted]
            Laptop1[MacBook Pro<br/>VLAN 10]
            Laptop2[ThinkPad<br/>VLAN 10]
            Phone1[iPhone 14<br/>VLAN 10]
            Phone2[Android Phone<br/>VLAN 10]
        end
        
        subgraph VLAN50_Clients[VLAN 50 - IoT]
            SmartSpeaker1[Amazon Echo<br/>VLAN 50]
            SmartSpeaker2[Google Home<br/>VLAN 50]
            IoT_Phone[iPhone - IoT Control<br/>VLAN 50]
        end
        
        subgraph VLAN99_Clients[VLAN 99 - Guest]
            GuestPhone1[Guest Phone<br/>VLAN 99]
            GuestLaptop1[Guest Laptop<br/>VLAN 99]
        end
        
        subgraph VLAN100_Clients[VLAN 100 - Lab]
            TestLaptop[Kali Linux Laptop<br/>VLAN 100]
        end
    end

    %% =============================================
    %% Physical Connections
    %% =============================================
    
    %% Internet to Gateway
    Internet -->|Coaxial/Fiber| ISP_Modem
    ISP_Modem -->|WAN Port<br/>Cat6a| UDMP
    
    %% Gateway to Core Switching
    UDMP -->|LAN1 Port 1<br/>Cat6a| USW24
    USW24 -->|Port 24<br/>Cat6a| USW8
    
    %% Core Switch to Rack Devices
    USW24 -->|Port 5<br/>Cat6a| Proxmox
    USW24 -->|Port 6<br/>Cat6a| TrueNAS
    USW24 -->|Port 7<br/>Cat6a| Desktop
    USW24 -->|Port 8<br/>Cat6a| Printer
    
    %% Core Switch to Living Room
    USW24 -->|Port 9<br/>Cat6a| SmartTV
    USW24 -->|Port 15<br/>Cat6a + PoE ⚡| AP1
    
    %% Core Switch to Bedroom & Office
    USW24 -->|Port 16<br/>Cat6a + PoE ⚡| AP2
    USW24 -->|Port 17<br/>Cat6a + PoE ⚡| AP3
    
    %% Access Points to Wireless Clients
    AP1 -->|Wi-Fi 5 GHz| Laptop1
    AP1 -->|Wi-Fi 2.4 GHz| SmartSpeaker1
    AP1 -->|Wi-Fi 2.4/5 GHz| GuestPhone1
    AP1 -->|Wi-Fi 5 GHz| TestLaptop
    
    AP2 -->|Wi-Fi 5 GHz| Laptop2
    AP2 -->|Wi-Fi 2.4 GHz| SmartSpeaker2
    AP2 -->|Wi-Fi 2.4/5 GHz| GuestLaptop1
    
    AP3 -->|Wi-Fi 5 GHz| Phone1
    AP3 -->|Wi-Fi 5 GHz| Phone2
    AP3 -->|Wi-Fi 2.4 GHz| IoT_Phone

    %% =============================================
    %% Styling and Colors
    %% =============================================
    classDef internet fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef gateway fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef switching fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef servers fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef iot fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef wireless fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef trustedClients fill:#e8f5e8,stroke:#2e7d32
    classDef iotClients fill:#fff3e0,stroke:#ef6c00
    classDef guestClients fill:#f5f5f5,stroke:#9e9e9e
    classDef labClients fill:#e0f2f1,stroke:#00695c
    
    class Internet,ISP_Modem internet
    class UDMP gateway
    class USW24,USW8 switching
    class Proxmox,TrueNAS,Desktop,Printer servers
    class SmartTV iot
    class AP1,AP2,AP3 wireless
    class VLAN10_Clients trustedClients
    class VLAN50_Clients iotClients
    class VLAN99_Clients guestClients
    class VLAN100_Clients labClients

    %% =============================================
    %% Legend and Notes
    %% =============================================
    
    subgraph Legend[Physical Topology Legend]
        Direction[Flow: Top to Bottom]
        CableType[Solid Lines: Cat6/Cat6a Ethernet]
        PoEMarker[PoE ⚡: Power over Ethernet]
        WirelessDashed[Dashed Lines: Wireless Connections]
        ColorCode[Colors: Red=Internet, Purple=Gateway, Blue=Switching, Green=Servers, Orange=IoT, Pink=Wireless]
    end

%% =============================================
%% Physical Topology Description:
%% 
%% This diagram shows the complete physical network layout:
%% 
%% INTERNET LAYER (Top):
%% - ISP provides internet via coaxial cable or fiber
%% - Modem in bridge mode passes public IP to UDMP
%% 
%% GATEWAY LAYER:
%% - UniFi Dream Machine Pro (UDMP) handles routing, firewall, VPN
%% - Single WAN port connected to modem
%% - LAN1 port connected to main switch
%% 
%% CORE SWITCHING LAYER:
%% - UniFi Switch 24 PoE provides 24 ports with 95W PoE budget
%% - Secondary 8-port switch in another room for additional devices
%% - All connections use Cat6a cables for 10Gbps capability
%% 
%% ACCESS LAYER - WIRED:
%% - Rack contains servers and critical infrastructure (VLAN 10)
%% - Living Room has Smart TV (VLAN 50) and primary access point
%% - Bedroom and Office have additional access points
%% 
%% ACCESS LAYER - WIRELESS:
%% - 3x UniFi AP AC Pro covering 2,500 sq ft
%% - Each AP broadcasts 4 SSIDs mapped to different VLANs
%% - Wireless clients connect to appropriate VLAN based on SSID
%% 
%% CABLE INFRASTRUCTURE:
%% - All wired connections use Cat6a cables
%% - Patch panel (not shown) organizes 24 cable runs
%% - PoE provided to access points (no separate power needed)
%% - Cable lengths: 1-3ft (rack), 25ft (living room), 50ft (bedroom), 75ft (office)
%% 
%% POWER MANAGEMENT:
%% - All rack equipment on UPS battery backup
%% - APs powered via PoE from switch (no local power needed)
%% - Estimated total power draw: 150W (rack) + 36W (APs) = 186W
%% =============================================
```

## Source File

Original: `physical-topology.mermaid`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*
