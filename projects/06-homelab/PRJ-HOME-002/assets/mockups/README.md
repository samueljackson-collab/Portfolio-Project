# Homelab Dashboard Mockups

This directory contains mockups and prototypes for homelab infrastructure monitoring dashboards.

## Available Mockups

### 1. Interactive Grafana Dashboard
**File:** `grafana-homelab-dashboard.html`

A fully functional, interactive Grafana-style dashboard mockup showcasing homelab infrastructure monitoring.

**Features:**
- **Real-time Updates:** Live clock and animated metrics
- **Interactive Charts:**
  - CPU Usage by VM (multi-line chart)
  - Memory Usage by VM (stacked area chart)
  - Network Traffic (line chart with inbound/outbound)
  - Disk I/O (bar chart by service)
- **Key Metrics Panels:**
  - Total VMs Running: 6 VMs + 2 containers
  - CPU Usage: 34% of 32 cores
  - Memory Usage: 58% (73.6GB / 128GB)
  - Storage Used: 51% (8.2TB / 16TB)
- **Service Status Table:**
  - Wiki.js, Home Assistant, Immich, PostgreSQL, Nginx Proxy, Grafana
  - All services showing Online status with uptime
- **Authentic Grafana UI:**
  - Dark theme matching Grafana's design system
  - Time range selector and refresh interval picker
  - Panel menus and interactive elements

**Usage:**
```bash
# Open in browser
open grafana-homelab-dashboard.html
# or
firefox grafana-homelab-dashboard.html
```

**Screenshot Capture:**
To capture high-quality screenshots for documentation:
1. Open the HTML file in a browser
2. Press F11 for fullscreen (optional)
3. Use browser screenshot tools:
   - Chrome: F12 → Ctrl+Shift+P → "Capture full size screenshot"
   - Firefox: Shift+F2 → :screenshot --fullpage

**Technologies Used:**
- Chart.js for data visualization
- Pure HTML/CSS/JavaScript (no build process required)
- Responsive design with CSS Grid
- SVG sparklines for mini-charts

### 2. Interactive Nginx Proxy Manager Dashboard
**File:** `nginx-proxy-manager-dashboard.html`

A fully functional, interactive Nginx Proxy Manager interface mockup showcasing reverse proxy and SSL certificate management.

**Features:**
- **Modern UI:** Light theme with gradient header and card-based design
- **Proxy Host Management:**
  - 8 configured proxy hosts with detailed statistics
  - Domain mapping display (e.g., wiki.example.com → 192.168.40.20:3000)
  - SSL status indicators (Let's Encrypt, Self-Signed)
  - Online/Offline status badges
  - Per-host metrics: requests, data transferred, latency
- **Statistics Dashboard:**
  - Total Hosts: 8
  - Online Hosts: 8 (100% uptime)
  - Requests (24h): 12.4K
  - Data Transfer (24h): 3.2 GB
- **SSL Certificate Management:**
  - Wildcard certificate (*.example.com)
  - Self-signed certificates for internal services
  - Certificate expiry tracking
  - Renewal status indicators
- **Recent Activity Log:**
  - SSL renewals
  - Proxy host changes
  - Access list updates
- **Interactive Elements:**
  - Filter and search functionality
  - View toggle (List/Grid)
  - Action buttons (Edit, Delete, Disable)
  - Sortable columns

**Usage:**
```bash
# Open in browser
open nginx-proxy-manager-dashboard.html
# or
firefox nginx-proxy-manager-dashboard.html
```

**Screenshot Capture:**
Same process as Grafana dashboard - use browser developer tools to capture full-page screenshots.

**Technologies Used:**
- Pure HTML/CSS (no JavaScript framework required)
- CSS Grid and Flexbox for responsive layout
- Gradient backgrounds and modern card design
- Emoji icons for visual elements

### 3. AI Generation Prompts
**File:** `AI-PROMPTS.md`

Detailed prompts for generating additional mockup screenshots using AI tools (Midjourney, DALL-E 3, etc.) or manual creation tools (Figma, Excalidraw).

**Includes prompts for:**
- Grafana Dashboard
- Nginx Proxy Manager
- TrueNAS Storage Dashboard
- Home Assistant Dashboard
- Immich Photo Library
- Proxmox VE Cluster View
- Prometheus Alerts View

## Use Cases

1. **Portfolio Documentation:** Include screenshots in your portfolio to demonstrate infrastructure monitoring capabilities
2. **Presentation Materials:** Use for talks, blog posts, or documentation
3. **Design Reference:** Reference for implementing actual Grafana dashboards
4. **Training Materials:** Demo environment for teaching monitoring concepts

## Related Documentation

- [Monitoring Stack Configuration](../configs/monitoring/README.md)
- [PRJ-HOME-002 Main README](../../README.md)
- [AI Generation Prompts](./AI-PROMPTS.md)

---

**Last Updated:** November 10, 2025
**Project:** PRJ-HOME-002 - Virtualization & Core Services
