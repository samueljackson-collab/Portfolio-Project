# AI Prompts for Homelab Screenshot Mockups

This document contains detailed prompts for generating realistic screenshot mockups of homelab infrastructure dashboards and UIs. These can be used with AI image generators (Midjourney, DALL-E 3, Stable Diffusion) or as reference for manual mockup creation.

## Interactive HTML Dashboards

Three **interactive HTML mockups** are available in this directory for live demonstrations:

### 1. Grafana Homelab Infrastructure Dashboard
- **File:** `grafana-homelab-dashboard.html`
- **Features:**
  - Fully functional Grafana-style UI with dark theme
  - Real-time clock and animated metrics
  - Interactive charts using Chart.js (CPU, Memory, Network, Disk I/O)
  - Service status table showing all homelab services
  - Responsive dashboard panels with sparklines and progress bars
- **Usage:** Open in any modern web browser for a live demo
- **Screenshot:** Can be used to capture high-quality dashboard screenshots

### 2. Nginx Proxy Manager Dashboard
- **File:** `nginx-proxy-manager-dashboard.html`
- **Features:**
  - Modern light-theme UI with gradient header
  - 8 configured proxy hosts with detailed statistics
  - SSL certificate management panel
  - Real-time metrics: requests, data transfer, latency
  - Activity log showing recent changes
  - Filter and search functionality
- **Usage:** Open in any modern web browser for a live demo
- **Screenshot:** Can be used to capture high-quality dashboard screenshots

### 3. Proxmox VE Dashboard
- **File:** `proxmox-ve-dashboard.html`
- **Features:**
  - Authentic Proxmox VE 8.x interface design
  - Interactive tree navigation with collapsible nodes
  - 6 running VMs with detailed resource metrics
  - Node summary with CPU, Memory, Swap, and Filesystem usage
  - SVG resource charts (CPU and Memory over time)
  - VM table with VMID, status, and per-VM statistics
  - Server information panel
  - Tabbed interface (Summary, VMs, Containers, Storage, Network, Shell)
- **Usage:** Open in any modern web browser for a live demo
- **Screenshot:** Can be used to capture high-quality dashboard screenshots

---

## =� 1. Grafana Dashboard - Homelab Overview

### AI Image Generation Prompt (Midjourney/DALL-E)

```
A professional Grafana monitoring dashboard on a dark background showing homelab infrastructure metrics. The dashboard has a clean, modern dark UI with the Grafana logo in the top left corner. The screen shows:

TOP ROW (4 stat panels):
- "Total VMs: 5" with green uptime indicator showing "99.8%"
- "CPU Usage: 42%" with orange gauge chart
- "Memory: 64GB/128GB" with blue progress bar at 50%
- "Storage: 8.2TB/16TB" with yellow progress bar at 51%

MIDDLE SECTION (2 large graphs):
- Left: Line graph titled "CPU Usage (24h)" showing fluctuating green/blue lines between 20-60% with timestamps
- Right: Area chart titled "Network Traffic" showing incoming (blue) and outgoing (orange) traffic over 24 hours

BOTTOM SECTION (3 panels):
- Left: Table titled "VM Status" with 5 rows:
  * Wiki.js - 192.168.40.20 -  Online - 2.1GB RAM
  * Home Assistant - 192.168.40.21 -  Online - 1.5GB RAM
  * Immich - 192.168.40.22 -  Online - 8.2GB RAM
  * PostgreSQL - 192.168.40.23 -  Online - 4.8GB RAM
  * Nginx Proxy - 192.168.40.25 -  Online - 0.5GB RAM

- Middle: Pie chart titled "Storage by Service" showing segments for:
  * Immich Photos (45% - largest, blue)
  * Database (25% - green)
  * Wiki Content (15% - orange)
  * Backups (10% - yellow)
  * System (5% - red)

- Right: Alert panel titled "Recent Alerts" showing:
  * 0 Critical (red badge)
  * 2 Warning (yellow badge)
  * 12 Info (blue badge)

The time range selector in top right shows "Last 24 hours". Overall dark theme with green, blue, orange accent colors. Professional IT monitoring aesthetic. 4K resolution, sharp text, realistic data visualization. --ar 16:9 --v 6
```

### Alternative: Specific Details for Manual Creation

**Dashboard Layout:**
- **Theme:** Dark (background: #1e1e1e, panels: #2d2d2d)
- **Resolution:** 1920x1080
- **Time Range:** Last 24 hours
- **Refresh:** 30s

**Stat Panels (Row 1):**
1. Total VMs: `5` | Uptime: `99.8%` | Status: Green checkmark
2. CPU Usage: `42%` | Graph: Small line chart trending down
3. Memory: `64GB / 128GB (50%)` | Color: Blue | Progress bar
4. Storage: `8.2TB / 16TB (51%)` | Color: Yellow | Progress bar

**Graph Panels (Row 2):**
- **CPU Usage (24h):** Multi-line graph
  - Wiki.js: Green line (20-30%)
  - Home Assistant: Blue line (10-20%)
  - Immich: Orange line (40-60%)
  - PostgreSQL: Purple line (15-25%)
  - X-axis: Time (00:00 - 24:00)
  - Y-axis: Percentage (0-100%)

- **Network Traffic:** Stacked area chart
  - RX (incoming): Blue area (5-50 Mbps)
  - TX (outgoing): Orange area (2-20 Mbps)
  - Peaks during backup hours (02:00-04:00)

**Lower Panels (Row 3):**
- **VM Status Table:** 5 rows � 4 columns
  - Columns: Name, IP, Status, RAM Usage
  - Status icons: Green checkmarks
  - Font: Roboto Mono, 12px

- **Storage Pie Chart:**
  - Immich: 7.2TB (45% - #3274D9)
  - Database: 4.0TB (25% - #37872D)
  - Wiki: 2.4TB (15% - #FA6400)
  - Backups: 1.6TB (10% - #FDB80E)
  - System: 0.8TB (5% - #C4162A)

- **Alerts Panel:**
  - Critical: 0 (red badge)
  - Warning: 2 (yellow badge - "High disk usage on VM 102", "SSL cert expires in 30d")
  - Info: 12 (blue badge)

---

## < 2. Nginx Proxy Manager - Proxy Hosts View

### AI Image Generation Prompt

```
A clean, modern web interface for Nginx Proxy Manager showing a list of reverse proxy configurations. The UI has a light background with blue accents. Top navigation bar shows "Nginx Proxy Manager" logo on the left and user avatar on the right.

The main content area shows a table titled "Proxy Hosts" with 6 rows:

Headers: Domain Name | Forward To | SSL | Status | Actions

Row 1: wiki.homelab.local � http://192.168.40.20:3000 � Green SSL badge "Active" � Green "Online" badge � Edit/Delete buttons
Row 2: homeassistant.homelab.local � http://192.168.40.21:8123 � Green SSL badge "Active" � Green "Online" badge � Edit/Delete buttons
Row 3: photos.homelab.local � http://192.168.40.22:2283 � Green SSL badge "Active" � Green "Online" badge � Edit/Delete buttons
Row 4: grafana.homelab.local � http://192.168.40.30:3000 � Green SSL badge "Active" � Green "Online" badge � Edit/Delete buttons
Row 5: wiki.example.com � http://192.168.40.20:3000 � Green SSL badge "Let's Encrypt" � Green "Online" badge � Edit/Delete buttons
Row 6: photos.example.com � http://192.168.40.22:2283 � Green SSL badge "Let's Encrypt" � Green "Online" badge � Edit/Delete buttons

Left sidebar shows menu items: Dashboard (active), Proxy Hosts, SSL Certificates, Access Lists, Settings.

Top right corner shows "Add Proxy Host" button in blue. Bottom of table shows "Showing 6 of 6 entries".

Clean, professional SaaS application design, light mode, blue (#0D6EFD) primary color. --ar 16:10 --v 6
```

### Manual Creation Details

**Color Scheme:**
- Background: #FFFFFF
- Sidebar: #F8F9FA
- Primary Blue: #0D6EFD
- Success Green: #198754
- Table Border: #DEE2E6

**SSL Badges:**
- Let's Encrypt: Green badge with lock icon
- Self-Signed: Yellow badge
- Expired: Red badge

**Status Indicators:**
- Online: Green dot + "Online" text
- Offline: Red dot + "Offline" text
- Error: Orange dot + "Error" text

---

## =� 3. TrueNAS Storage Dashboard

### AI Image Generation Prompt

```
A TrueNAS storage management dashboard with dark blue professional theme. The interface shows storage pool health and usage statistics.

TOP SECTION: System overview cards
- Card 1: "System Health:  Healthy" (green checkmark)
- Card 2: "Uptime: 87 days 14 hours"
- Card 3: "Temperature: 42�C / 108�F" (blue thermometer icon)
- Card 4: "Services: 12 Running" (green indicator)

MIDDLE SECTION: Two large pool status cards side by side

LEFT CARD - "Pool: tank"
- Status: Healthy (green shield icon)
- Topology: RAIDZ2
- Disks: 6x 4TB WD Red
- Total Size: 24TB raw
- Usable: 16TB
- Used: 8.2TB (51%)
- Large horizontal progress bar showing 51% filled (blue)
- ZFS health status: ONLINE

RIGHT CARD - "Pool: backup"
- Status: Healthy (green shield icon)
- Topology: RAIDZ1
- Disks: 4x 2TB Seagate
- Total Size: 8TB raw
- Usable: 6TB
- Used: 3.1TB (52%)
- Large horizontal progress bar showing 52% filled (orange)
- ZFS health status: ONLINE

BOTTOM SECTION: Active shares table
Columns: Share Name | Type | Path | Status
Row 1: media � SMB � /mnt/tank/media � Active (green)
Row 2: backups � SMB � /mnt/tank/backups � Active (green)
Row 3: immich � NFS � /mnt/tank/immich � Active (green)
Row 4: pbs � NFS � /mnt/backup/pbs � Active (green)

Professional dark blue theme (#1e3a5f background), modern data center aesthetic. --ar 16:9 --v 6
```

---

## <� 4. Home Assistant Dashboard

### AI Image Generation Prompt

```
A modern Home Assistant smart home dashboard with dark theme showing room controls and device status.

TOP BAR: "Home" title, weather widget showing "72�F Sunny" with sun icon, time "2:45 PM"

MAIN GRID LAYOUT (3x3 cards):

Row 1:
- "Living Room" card: 3 lights on (yellow bulb icons), temperature 72�F, toggle switches
- "Bedroom" card: 1 light on, temperature 68�F, climate control widget
- "Office" card: 2 lights on, temperature 70�F, desk lamp control

Row 2:
- "Energy Monitor" card: Real-time power usage graph showing 2.4 kW, line chart with green area
- "Security" card: All sensors OK (green checkmarks), 2 doors closed, 3 windows closed
- "Media" card: Sonos playing "Jazz Playlist", volume slider at 40%

Row 3:
- "Automations" card: 12 active automations, last triggered "Sunset Lights" 1h ago
- "Climate" card: Thermostat set to 70�F, current 72�F, mode "Cool", fan auto
- "Cameras" card: 2 cameras online, thumbnail previews, "Front Door" and "Backyard"

BOTTOM: Quick actions bar with icons for:
- All Lights Off (moon icon)
- Goodnight Scene (bed icon)
- Away Mode (lock icon)
- Vacation Mode (suitcase icon)

Modern dark UI (#1e1e1e background), colorful accent cards (blue, green, orange, purple), iOS/Material Design inspired. --ar 9:16 --v 6
```

---

## =� 5. Immich Photo Library View

### AI Image Generation Prompt

```
A modern photo library web application interface similar to Google Photos, showing a grid of photo thumbnails. Dark theme with clean design.

TOP NAVIGATION: "Immich" logo (left), search bar (center), user avatar (right)

LEFT SIDEBAR:
- Photos (active, highlighted)
- Albums
- Favorites
- Archive
- Settings

MAIN CONTENT AREA: Photo grid layout

Date header: "November 6, 2025 - 24 photos"
Grid of 24 photo thumbnails (4 columns � 6 rows) showing:
- Landscape photos
- Family photos
- Pet photos
- Food photos
- Travel photos
Each thumbnail is 250x250px with slight rounded corners

Date header: "November 5, 2025 - 18 photos"
Grid continues with more photo thumbnails

TOP RIGHT INFO PANEL:
- Total Photos: 10,847
- Total Videos: 342
- Storage Used: 487GB
- ML Processing: 100% complete (green checkmark)
- Faces Detected: 8 people
- Places: 47 locations

BOTTOM RIGHT: Floating action button with + icon for upload

Clean, modern photo app design, dark theme (#1a1a1a background), white text, blue (#3b82f6) accents. Realistic photo thumbnails showing nature, people, and everyday life. --ar 16:10 --v 6
```

---

## =� 6. Proxmox VE Cluster View

### AI Image Generation Prompt

```
A Proxmox Virtual Environment web interface showing datacenter cluster view. Professional dark theme.

LEFT SIDEBAR - Resource Tree:
- Datacenter
    pve-01 (Dell R720)
       VM 100 (wiki-js) - running (green icon)
       VM 101 (homeassistant) - running (green icon)
       VM 102 (immich) - running (green icon)
       VM 103 (postgresql) - running (green icon)
       VM 105 (nginx-proxy) - running (green icon)
       CT 200 (monitoring) - running (green icon)
       CT 201 (logging) - running (green icon)
       CT 202 (backup-agent) - running (green icon)

MAIN CONTENT - Summary View:

Top status cards (4 across):
- "Cluster Health: Good" (green checkmark)
- "Total VMs: 5 running"
- "Total CTs: 3 running"
- "Node Status: Online" (green)

Resource usage graphs (2 large panels):
LEFT: "CPU Usage" - Line graph showing server load at 42% average
RIGHT: "Memory Usage" - Bar showing 64GB / 128GB (50% used)

Bottom section - Resource allocation table:
Columns: VM ID | Name | Status | CPU | Memory | Disk | Node

Row 1: 100 � wiki-js � Running (green) � 12% (4 cores) � 2.1GB / 8GB � 18GB / 50GB � pve-01
Row 2: 101 � homeassistant � Running (green) � 8% (2 cores) � 1.5GB / 4GB � 12GB / 32GB � pve-01
Row 3: 102 � immich � Running (green) � 45% (4 cores) � 8.2GB / 16GB � 42GB / 100GB � pve-01
Row 4: 103 � postgresql � Running (green) � 18% (4 cores) � 4.8GB / 16GB � 78GB / 200GB � pve-01
Row 5: 105 � nginx-proxy � Running (green) � 5% (2 cores) � 0.5GB / 2GB � 6GB / 20GB � pve-01

Professional datacenter management interface, dark theme, green/blue/orange accent colors. --ar 16:9 --v 6
```

---

## = 7. Prometheus Alerts View

### AI Image Generation Prompt

```
A Prometheus alerts dashboard showing monitoring alert rules and their status. Dark theme with technical/DevOps aesthetic.

TOP NAVIGATION: Prometheus logo (orange flame), menu items: "Graph | Alerts | Status | Help"

MAIN CONTENT - Alerts Page:

Active Alerts (2):
1. ALERT: HighDiskUsage
   - Severity: warning (yellow badge)
   - Description: "Disk usage on immich-vm is above 80% (currently 82%)"
   - Labels: instance="192.168.40.22", job="node-exporter", severity="warning"
   - Active since: 2h 14m ago
   - Value: 82.4%

2. ALERT: SSLCertExpiringSoon
   - Severity: warning (yellow badge)
   - Description: "SSL certificate for wiki.example.com expires in 28 days"
   - Labels: domain="wiki.example.com", cert_type="letsencrypt"
   - Active since: 45m ago
   - Expires: 2025-12-04

Inactive Alert Rules (showing healthy state):
 HighCPUUsage (OK - last checked 30s ago)
 ServiceDown (OK - all services up)
 HighMemoryUsage (OK - memory at 50%)
 BackupFailed (OK - last backup successful)
 DatabaseConnectionError (OK - all databases responsive)
 NetworkThroughputHigh (OK - traffic normal)

SIDEBAR - Alert Statistics:
- Total Rules: 24
- Firing: 2 (yellow)
- Pending: 0
- Inactive: 22 (green)
- Last Evaluation: 15s ago

Technical monitoring interface, dark theme (#1a1a1a background), Prometheus orange (#e6522c) branding, monospace font for values. --ar 16:10 --v 6
```

---

## =� Non-AI Mockup Tools

If AI generation isn't producing realistic enough results, use these browser-based tools:

### Option 1: Figma (Professional)
**URL:** https://figma.com

**Steps:**
1. Create free account
2. Use "Grafana Dashboard" template from Community
3. Customize with your data (VMs, IPs, metrics)
4. Export as PNG (2x resolution)

**Pre-made Templates:**
- Search Figma Community for "Grafana Dashboard"
- Search for "TrueNAS UI"
- Search for "Proxmox Interface"

### Option 2: Excalidraw (Quick & Simple)
**URL:** https://excalidraw.com

**Steps:**
1. No account needed (browser-based)
2. Draw boxes for panels
3. Add text for metrics
4. Use libraries for icons (search "dashboard icons")
5. Export as PNG

**Pros:** Fast, simple, no login
**Cons:** Hand-drawn aesthetic (not photorealistic)

### Option 3: MockFlow (UI Mockups)
**URL:** https://mockflow.com

**Features:**
- Dashboard wireframe templates
- Pre-built UI components
- Export to PNG/PDF
- Free tier available

### Option 4: Actual Screenshots (Best Quality)

If you have access to a demo/test environment:

**Grafana Demo:**
- https://play.grafana.org/
- Login: admin / admin
- Create custom dashboard
- Screenshot with browser DevTools (F12 � Ctrl+Shift+P � "Capture screenshot")

**TrueNAS Demo:**
- Download TrueNAS CORE as VM
- Install in VirtualBox
- Configure mock pools
- Screenshot web UI

**Proxmox Demo:**
- https://pve.proxmox.com/pve-docs/screenshots.html (official screenshots)
- Or install in VM for custom screenshots

---

## =� Screenshot Best Practices

### Resolution & Quality
```
- Minimum: 1920�1080 (Full HD)
- Recommended: 2560�1440 (2K)
- Portfolio: 3840�2160 (4K)
- Format: PNG (lossless) not JPEG
- DPI: 144 or 300 for print
```

### Browser Screenshot Tools
```bash
# Chrome DevTools (F12)
Ctrl+Shift+P � "Capture full size screenshot"

# Firefox
Shift+F2 � :screenshot --fullpage

# Mac Safari
Cmd+Shift+4 � Drag to select area
```

### Post-Processing (Optional)
- **Tool:** GIMP (free) or Photoshop
- **Adjustments:**
  - Crop to remove browser chrome
  - Add subtle drop shadow
  - Increase contrast slightly (+10%)
  - Sharpen (Unsharp Mask: Amount 50%, Radius 1px)

### Annotation (for documentation)
- **Tool:** Snagit, ShareX (Windows), Skitch (Mac)
- **Add:**
  - Red arrows pointing to important metrics
  - Text boxes explaining key features
  - Numbered callouts for step-by-step guides

---

## <� Portfolio Usage Guidelines

### DO:
 Use consistent theme (all dark or all light)
 Show realistic data (avoid "Lorem Ipsum" placeholder text)
 Include timestamps, IP addresses, versions
 Show green "healthy" status (demonstrates operational system)
 Display your actual project names (wiki.homelab.local, not example.com)

### DON'T:
L Use fake/unrealistic numbers (999TB storage, 99.9999% uptime)
L Show error states (unless explaining troubleshooting)
L Include sensitive data (passwords, API keys, real IP addresses)
L Mix different UI themes (dark Grafana + light Proxmox looks inconsistent)
L Use low-resolution or blurry screenshots

---

## = Security Note

**BEFORE** including screenshots in your portfolio:

1. **Redact sensitive information:**
   - Public IP addresses (replace with X.X.X.X)
   - Real domain names (use example.com or homelab.local)
   - API keys, tokens, passwords (even if partially visible)
   - Personal location data (GPS coordinates, city names)

2. **Use demo data where possible:**
   - Replace real names with "Admin User"
   - Use RFC 1918 private IPs (192.168.x.x, 10.x.x.x)
   - Replace photos with stock images or blurred thumbnails

3. **Tools for redaction:**
   - GIMP/Photoshop: Clone tool or black rectangles
   - ShareX: Built-in pixelate/blur tool
   - Online: redact.photo (browser-based)

---

**Last Updated:** November 6, 2025
**Project:** PRJ-HOME-002 (Homelab Infrastructure Documentation)
