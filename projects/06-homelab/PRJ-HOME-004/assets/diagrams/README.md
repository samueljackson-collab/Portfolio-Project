# Homelab Infrastructure Diagrams

This directory contains Mermaid diagram source files for the Homelab Enterprise Infrastructure Program (v6.0).

## Diagram Files

### 1. Architecture Overview
**File:** `architecture-overview.mermaid`

Comprehensive system architecture showing:
- Internet perimeter (Cloudflare DNS, Nginx Proxy Manager)
- Security layer (WireGuard VPN, UniFi Firewall)
- Network segmentation (5 VLANs with color-coded trust levels)
- Compute layer (Proxmox VE with service containers)
- Storage layer (TrueNAS ZFS with datasets)
- Multi-site resilience (Syncthing replication across 3 locations)
- Camera system (UniFi Protect with 4K cameras)

### 2. Firewall Policy
**File:** `firewall-policy.mermaid`

Network segmentation and firewall rules:
- Default deny stance
- Explicit allow rules between VLANs
- East/West traffic isolation
- Trust boundary enforcement

### 3. Backup Strategy
**File:** `backup-strategy.mermaid`

3-2-1 backup implementation:
- 3 copies of data (primary + local + offsite)
- 2 different media types (disk + object storage)
- 1 offsite location (cloud + physical)
- Verification procedures (weekly automated + monthly manual)

### 4. Risk Assessment Matrix
**File:** `risk-assessment-matrix.mermaid`

Quadrant chart showing risk probability vs. impact:
- Scope creep (medium probability, medium impact)
- Time overrun (medium probability, medium impact)
- VPN misconfiguration (high probability, high impact)
- SSD failure (medium probability, high impact)
- Data loss (low probability, high impact)
- Privacy breach (low probability, high impact)

### 5. Implementation Timeline
**File:** `implementation-timeline.mermaid`

Gantt chart with project phases:
- **Foundation** (Oct 20 - Nov 9, 2025): Planning, hardware, networking
- **Core Platform** (Nov 10 - Dec 1, 2025): Proxmox, TrueNAS, services
- **Resilience & Services** (Dec 1 - 22, 2025): Monitoring, cameras, replication
- **Validation** (Dec 22 - Jan 5, 2026): DR testing, service validation, handover

## Rendering

These Mermaid diagrams can be rendered using:
- **GitHub:** Displays natively in markdown files
- **VS Code:** With Mermaid preview extension
- **Mermaid Live Editor:** https://mermaid.live/
- **Documentation platforms:** GitBook, Docusaurus, MkDocs

## Export for AI Enhancement

These diagrams are exported in the `/exports` directory as a tar archive for enhancement by AI visualization tools (e.g., Gamma, Figma, Lucidchart).

### Suggested Enhancements

1. **Architecture Overview:**
   - Add icons for each service type
   - Show data flow directions with different arrow styles
   - Include bandwidth/latency annotations
   - Add legend for trust levels

2. **Firewall Policy:**
   - Visualize packet flow with numbered steps
   - Add protocol/port labels on connections
   - Include drop/accept counters
   - Show logging points

3. **Backup Strategy:**
   - Add time-based flow (schedule annotations)
   - Show data sizes and transfer rates
   - Include retention policy timelines
   - Visualize verification checkpoints

4. **Risk Assessment Matrix:**
   - Use different shapes for risk categories
   - Add mitigation strategy annotations
   - Show risk movement over time
   - Include heat map shading

5. **Implementation Timeline:**
   - Add milestone markers with deliverables
   - Show resource allocation (team members)
   - Include dependency arrows between tasks
   - Visualize critical path

## Integration

These diagrams are embedded in the main project README at:
`/home/user/Portfolio-Project/projects/06-homelab/PRJ-HOME-004/README.md`

---

**For questions or diagram enhancement suggestions, contact:**
- Samuel Jackson
- GitHub: [github.com/sams-jackson](https://github.com/sams-jackson)
- LinkedIn: [linkedin.com/in/sams-jackson](https://www.linkedin.com/in/sams-jackson)
