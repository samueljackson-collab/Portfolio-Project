# Switch Port Configuration Map

## UniFi Switch 24 PoE - Primary Distribution Switch
**Management IP**: 192.168.1.10  
**Location**: Rack 15U  
**Firmware**: 6.5.55

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
| 12 | Available | - | Access | 40 | Disabled | - | Server-Access | Reserved |
| 13 | AP-Office | Office Ceiling | Trunk | 1,10,20,30 | Active (15.4W) | 1G/Full | AP-Trunk | Office AP |
| 14 | AP-LivingRoom | Living Room | Trunk | 1,10,20,30 | Active (13.2W) | 1G/Full | AP-Trunk | Living room AP |
| 15 | AP-Bedroom | Master Bedroom | Trunk | 1,10,20,30 | Active (14.1W) | 1G/Full | AP-Trunk | Bedroom AP |
| 16 | Available | - | Trunk | All | Available | - | AP-Trunk | Spare for expansion |
| 17 | Camera-Front | Front Door | Access | 50 | Active (4.2W) | 100M/Full | Camera-Access | Front door camera |
| 18 | Camera-Back | Back Door | Access | 50 | Active (3.8W) | 100M/Full | Camera-Access | Back door camera |
| 19 | Camera-Garage | Garage | Access | 50 | Active (4.5W) | 100M/Full | Camera-Access | Garage camera |
| 20 | Camera-Driveway | Driveway | Access | 50 | Active (5.1W) | 100M/Full | Camera-Access | Driveway camera |
| 21 | Smart Hub-01 | Office | Access | 20 | Disabled | 100M/Full | IoT-Access | Zigbee/Z-Wave hub |
| 22 | Printer-Office | Office | Access | 10 | Disabled | 100M/Full | Trusted-Access | Printer |
| 23 | UDMP Uplink | Rack 1U | Trunk | All | Disabled | 1G/Full | Uplink | Uplink to UDMP |
| 24 | Available | - | Trunk | All | Disabled | - | General | Spare |

### Port Profiles

#### Trusted-Access Profile
- Access port, native VLAN 10, storm control enabled, RSTP edge, no PoE.

#### Server-Access Profile
- Access VLAN 40, jumbo frames enabled, storm control 5%, RSTP edge.

#### AP-Trunk Profile
- Native VLAN 1, tagged 1/10/20/30, PoE+ high priority, storm control 20%, RSTP.

#### Camera-Access Profile
- Access VLAN 50, PoE 802.3af medium priority, storm control 10%, RSTP edge.

### PoE Budget Summary
- Total: 95W; used ~60W across APs and cameras; 35W available for growth.

### Cable Runs
| Port | Cable Type | Length | Run Path | Certification |
|------|------------|--------|----------|---------------|
| 1-8 | Cat6 | <15ft | Under desk | Patch |
| 9-11 | Cat6 | <3ft | Rack patch | Patch |
| 13 | Cat6 | 45ft | Ceiling conduit | Tested 1G |
| 14 | Cat6 | 75ft | Ceiling/wall conduit | Tested 1G |
| 15 | Cat6 | 60ft | Ceiling/wall conduit | Tested 1G |
| 17-20 | Cat5e | 30-100ft | Outdoor conduit | Tested 100M |

### Maintenance Log
| Date | Action | Port(s) | Performed By | Notes |
|------|--------|---------|--------------|-------|
| 2024-01-15 | Initial configuration | All | Admin | Base deployment |
| 2024-03-20 | Added Camera-Driveway | 20 | Admin | New camera |
| 2024-06-10 | Replaced cable | 14 | Admin | Damaged run replaced |
| 2024-11-10 | Enabled jumbo frames | 9-11 | Admin | Storage optimization |
