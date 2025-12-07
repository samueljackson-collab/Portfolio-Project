# Switch Port Configuration Map

## UniFi Switch 24 PoE - Primary Distribution Switch
**Management IP**: 192.168.1.10  
**Location**: Network Rack, 15U  
**Firmware**: 6.6.51 (current controller release)

### Port Configuration Table

| Port | Connected Device | Device Location | VLAN Mode | VLAN ID(s) | PoE Status | Speed/Duplex | Port Profile | Notes |
|------|------------------|-----------------|-----------|------------|------------|--------------|--------------|-------|
| 1 | Workstation-01 | Office Desk 1 | Access | 10 | Disabled | 1G/Full | Trusted-Access | Main development machine |
| 2 | Workstation-02 | Office Desk 2 | Access | 10 | Disabled | 1G/Full | Trusted-Access | Secondary workstation |
| 3 | Laptop Dock-01 | Office Desk 1 | Access | 10 | Disabled | 1G/Full | Trusted-Access | Thunderbolt dock |
| 4-8 | Available | - | Access | 10 | Disabled | - | Trusted-Access | Reserved for expansion |
| 9 | Proxmox-01 | Rack 10U | Access | 40 | Disabled | 1G/Full | Server-Access | Virtualization host |
| 10 | Proxmox-02 | Rack 11U | Access | 40 | Disabled | 1G/Full | Server-Access | Virtualization host |
| 11 | TrueNAS | Rack 12U | Access | 40 | Disabled | 1G/Full | Server-Access | Storage server |
| 12 | Available | - | Access | 40 | Disabled | - | Server-Access | Reserved for additional server |
| 13 | AP-Office | Office Ceiling | Trunk | 1,10,20,30 | Active (15.4W) | 1G/Full | AP-Trunk | Office access point |
| 14 | AP-LivingRoom | Living Room | Trunk | 1,10,20,30 | Active (13.2W) | 1G/Full | AP-Trunk | Living room AP |
| 15 | AP-Bedroom | Master Bedroom | Trunk | 1,10,20,30 | Active (14.1W) | 1G/Full | AP-Trunk | Bedroom AP |
| 16 | Available | - | Trunk | All | Available | - | AP-Trunk | Reserved for 4th AP |
| 17 | Camera-Front | Front Door | Access | 50 | Active (4.2W) | 100M/Full | Camera-Access | Front door camera |
| 18 | Camera-Back | Back Door | Access | 50 | Active (3.8W) | 100M/Full | Camera-Access | Back door camera |
| 19 | Camera-Garage | Garage | Access | 50 | Active (4.5W) | 100M/Full | Camera-Access | Garage camera |
| 20 | Camera-Driveway | Driveway | Access | 50 | Active (5.1W) | 100M/Full | Camera-Access | Driveway camera |
| 21 | Smart Hub-01 | Office | Access | 20 | Disabled | 100M/Full | IoT-Access | Zigbee/Z-Wave hub |
| 22 | Printer-Office | Office | Access | 10 | Disabled | 100M/Full | Trusted-Access | Network printer |
| 23 | UDMP Uplink | Rack 1U | Trunk | All | Disabled | 1G/Full | Uplink | Uplink to UDMP |
| 24 | Available | - | Trunk | All | Disabled | - | General | Available for trunking |

### Port Profiles

#### Trusted-Access Profile
- **Type**: Access
- **Native VLAN**: 10 (Trusted)
- **Tagged VLANs**: None
- **PoE**: Disabled
- **Storm Control**: Enabled (broadcast 10%)
- **Spanning Tree**: RSTP Edge Port

#### Server-Access Profile
- **Type**: Access
- **Native VLAN**: 40 (Servers)
- **Tagged VLANs**: None
- **PoE**: Disabled
- **Storm Control**: Enabled (broadcast 5%)
- **Spanning Tree**: RSTP Edge Port
- **Jumbo Frames**: Enabled (9000 MTU)

#### AP-Trunk Profile
- **Type**: Trunk
- **Native VLAN**: 1 (Management)
- **Tagged VLANs**: 1,10,20,30
- **PoE**: 802.3at (PoE+)
- **PoE Priority**: High
- **Storm Control**: Enabled (broadcast 20%)
- **Spanning Tree**: RSTP

#### Camera-Access Profile
- **Type**: Access
- **Native VLAN**: 50 (Cameras)
- **Tagged VLANs**: None
- **PoE**: 802.3af (PoE)
- **PoE Priority**: Medium
- **Storm Control**: Enabled (broadcast 10%)
- **Spanning Tree**: RSTP Edge Port

### PoE Budget Summary
- **Total Capacity**: 95W
- **Allocated**: 60.3W (63%)
  - AP-Office: 15.4W
  - AP-LivingRoom: 13.2W
  - AP-Bedroom: 14.1W
  - Camera-Front: 4.2W
  - Camera-Back: 3.8W
  - Camera-Garage: 4.5W
  - Camera-Driveway: 5.1W
- **Available**: 34.7W (37%)
- **Reserved**: Future AP or 2-3 cameras

### Cable Runs
| Port | Cable Type | Length | Run Path | Certification |
|------|------------|--------|----------|---------------|
| 1-8 | Cat6 | <15ft | Under desk | Patch cable |
| 9-11 | Cat6 | <3ft | Rack patch | Patch cable |
| 13 | Cat6 | 45ft | Ceiling run via conduit | Tested 1G |
| 14 | Cat6 | 75ft | Ceiling/wall via conduit | Tested 1G |
| 15 | Cat6 | 60ft | Ceiling/wall via conduit | Tested 1G |
| 17-20 | Cat5e | 30-100ft | Outdoor-rated, conduit | Tested 100M |

### Maintenance Log
| Date | Action | Port(s) | Performed By | Notes |
|------|--------|---------|--------------|-------|
| 2024-01-15 | Initial configuration | All | Admin | Base deployment |
| 2024-03-20 | Added Camera-Driveway | 20 | Admin | New camera installation |
| 2024-06-10 | Replaced cable | 14 | Admin | Cable damage, re-run |
| 2024-11-10 | Port profile update | 9-11 | Admin | Enabled jumbo frames |
