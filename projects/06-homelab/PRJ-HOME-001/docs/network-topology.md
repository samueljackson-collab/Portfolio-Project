# Network Topology Overview

## 1. Topology Summary
The home network is organized around a single UniFi Dream Machine Pro (UDM-Pro) that handles routing, firewall, and controller duties. All wired endpoints home-run to a UniFi Switch Pro 24 PoE installed in the structured media rack. Optional remote PoE switches provide short cable drops to high-density zones (living room entertainment cluster and upstairs office). Outdoor security pods (AP + camera + flood light) land directly on the main PoE switch to simplify PoE budgeting and monitoring.

## 2. Logical Diagram (ASCII)
```
                     ┌────────────────────────────────────────────┐
                     │                Internet                     │
                     └──────────────────┬──────────────────────────┘
                                        │
                               ┌────────▼────────┐
                               │    ISP ONT      │
                               └────────┬────────┘
                                        │
                               ┌────────▼────────┐
                               │   UDM-Pro (GW)  │
                               │  VLAN 10/20/30  │
                               │ 40/50 Routing   │
                               └───────┬─────────┘
             Management + Trunk (10/20/30/40/50) │
                               ┌────────▼────────┐
                               │ UniFi Switch    │
                               │ Pro 24 PoE      │
                               └───────┬─────────┘
          ┌────────────────────────────┼─────────────────────────────┐
          │                            │                             │
   ┌──────▼──────┐              ┌──────▼──────┐               ┌──────▼──────┐
   │ Downstairs  │              │ Upstairs    │               │ Outdoor Pod │
   │ Zone Switch │              │ Zone Switch │               │ Breakouts   │
   │ (8-port)    │              │ (8-port)    │               │ (5 bundles) │
   └──────┬──────┘              └──────┬──────┘               └──────┬──────┘
          │                            │                             │
  Indoor APs (4x)              Indoor APs (2x)               ┌───────┼─────────────────────────┐
  VLAN trunk ports             VLAN trunk ports              │ Outdoor AP + Camera + Flood    │
                                                             │ (5 sets, VLAN 10 + 30)          │
                                                             └────────┬────────────┬──────────┘
                                                                      │            │
                                                              Doorbell AP Mesh  Doorbell AP Mesh
```

## 3. Physical Placement Highlights
- **Living Room AP (AP-01):** Ceiling mount near center of downstairs floor plan for maximum propagation into kitchen and dining.
- **Office AP (AP-03):** Focused on work-from-home office and entryway; wired drop in wall chase.
- **Upstairs APs (AP-05/AP-06):** Deployed in master bedroom hallway ceiling and northeast bedroom closet for even coverage.
- **Outdoor AP Pods:** Mounted under eaves, with drip loops and weatherproof junction boxes housing RJ45 couplers.
- **Rack Location:** Garage closet at ground level with dedicated 20A circuit and ventilation.

## 4. Cable Pathways
- Indoor runs: Structured through attic and crawlspace using existing HVAC chases. All drops terminated on CAT6 patch panel with printed labels (e.g., `AP-01`, `CAM-O2`).
- Outdoor runs: UV-rated CAT6A in 1/2" PVC conduit exiting soffit, with drip loops before enclosure entry.
- Doorbell cameras: Powered via in-wall transformer; wireless association to outdoor APs (primary + fallback defined in controller).

## 5. Redundancy Considerations
- Dual fiber/SFP uplink capability reserved on switch for future WAN redundancy.
- Spare PoE ports dedicated for quick replacement of failed security pod components.
- UDM-Pro and switch connected to UPS with graceful shutdown triggered via USB signaling to NAS (Services VLAN) for configuration backup integrity.

