# AI Prompts for Dashboard & UI Mockups

Generate realistic dashboard and monitoring interface mockups for your portfolio.

---

## Prompt 1: CloudWatch Dashboard Mockup

### For Midjourney / DALL-E / Figma AI:

```
Create a professional AWS CloudWatch monitoring dashboard mockup:

LAYOUT:
Full-screen dark theme dashboard with multiple panels arranged in a grid

TOP BAR (Header):
- Left: AWS CloudWatch logo and "Production Monitoring" title
- Center: Environment selector dropdown "Production (us-east-1)"
- Right: Time range selector "Last 6 hours", user avatar, settings icon

MAIN CONTENT (Grid Layout - 3 columns):

ROW 1 (Key Metrics Cards):
1. EKS Cluster Health Card:
   - Large green "HEALTHY" status
   - Pods: 12/15 Running
   - Nodes: 3/3 Ready
   - Small line graph showing CPU trend

2. RDS Database Card:
   - Large green "AVAILABLE" status
   - CPU: 45%
   - Connections: 23/100
   - Small area chart showing query performance

3. API Response Time Card:
   - Large number "234ms" (p95)
   - Green indicator "Within SLA"
   - Small histogram showing distribution

ROW 2 (Detailed Charts):
1. Application Response Time (Left Panel):
   - Multi-line chart showing p50, p95, p99 percentiles
   - X-axis: Time (last 6 hours)
   - Y-axis: Response time in milliseconds
   - Lines: Green (p50), Yellow (p95), Red (p99)
   - Hovering tooltip showing exact values

2. Request Rate & Error Rate (Center Panel):
   - Dual-axis chart
   - Left axis: Request per second (blue area chart)
   - Right axis: Error rate percentage (red line)
   - Threshold line at 1% errors

3. Database Performance (Right Panel):
   - Stacked area chart showing:
     - Read queries (blue)
     - Write queries (green)
     - Active connections (orange)
   - Peak indicators marked

ROW 3 (System Resources):
1. CPU Utilization (Left):
   - Heat map showing CPU across all nodes
   - Color gradient: Green (low) to Red (high)
   - Node labels: eks-node-1, eks-node-2, eks-node-3

2. Memory Usage (Center):
   - Stacked bar chart showing:
     - Used memory (blue)
     - Cached memory (green)
     - Free memory (gray)
   - Percentage labels on bars

3. Network Traffic (Right):
   - Area chart showing inbound/outbound traffic
   - Blue: Inbound (MB/s)
   - Orange: Outbound (MB/s)
   - Peak traffic annotations

BOTTOM ROW (Alarms & Events):
- Alarm status panel:
  - 0 Critical (red circle with "0")
  - 1 Warning (yellow circle with "1")
  - 15 OK (green circle with "15")
- Recent events list:
  - Timestamps, event types, status icons
  - Last 5 events shown

SIDEBAR (Right):
- "Active Alarms" section
  - Single yellow warning: "High Memory on eks-node-2"
  - Triggered: "2 minutes ago"
  - "View Details" button

- "Quick Actions" section
  - "View Logs" button
  - "Create Alarm" button
  - "Export Metrics" button

VISUAL STYLE:
- Dark theme: Background #1a1a1a
- Chart background: #2a2a2a
- Text: #e0e0e0
- Accent color: AWS Orange (#FF9900)
- Green: #00D084
- Red: #FF5252
- Yellow: #FFB800
- Modern SaaS dashboard aesthetic
- Subtle shadows and depth
- Clean, professional typography (Inter or Roboto)

CHART SPECIFICATIONS:
- Smooth curved lines
- Grid lines subtle gray
- Tooltips on hover
- Time-series data looks realistic
- Axes clearly labeled
- Legend for multi-line charts

TECHNICAL SPECIFICATIONS:
- Resolution: 2560x1440 (1440p)
- Aspect ratio: 16:9
- Format: PNG with dark background
- Modern UI/UX standards
- Accessible color contrasts
```

### Expected Output:
- Realistic CloudWatch-style dashboard
- Dark theme, professional appearance
- Suitable for portfolio screenshots
- Shows monitoring expertise

---

## Prompt 2: Grafana Metrics Dashboard

### For Midjourney / DALL-E / Figma AI:

```
Create a professional Grafana-style monitoring dashboard mockup:

HEADER:
- Left: Grafana logo + "Portfolio Application - Production"
- Center: Time picker "Last 6 hours" with refresh rate "30s"
- Right: Share, Star, Settings icons

NAVIGATION BAR:
- Dashboard dropdown: "General / Portfolio Application"
- Add panel button
- Save dashboard button

MAIN CONTENT (Panel Grid):

PANEL 1 (Top-left, Large):
"Application Health Overview"
- Single stat visualization
- Large number "99.97%"
- Label: "Uptime (7 days)"
- Sparkline showing historical uptime
- Green color indicating healthy

PANEL 2 (Top-center):
"Request Rate"
- Graph panel with area fill
- Current: "1,234 req/s"
- Trend: upward arrow +12%
- Time series chart (last 6 hours)
- Blue gradient fill

PANEL 3 (Top-right):
"Error Budget"
- Gauge visualization
- Current value: 92.5%
- Thresholds:
  - 0-80%: Red
  - 80-95%: Yellow
  - 95-100%: Green
- Shows remaining error budget

PANEL 4 (Second row, full width):
"HTTP Request Duration"
- Graph panel with multiple series
- Lines showing:
  - p50: Green line (stable around 150ms)
  - p95: Yellow line (stable around 450ms)
  - p99: Red line (occasionally spiking to 800ms)
- SLA threshold line at 500ms (gray dashed)
- Legend at bottom with current values
- X-axis: Time, Y-axis: Milliseconds

PANEL 5 (Third row, left):
"Top Endpoints by Request Count"
- Table panel showing:
  - Endpoint | Requests | Avg Duration | Error %
  - /api/users | 45.2K | 134ms | 0.1%
  - /api/products | 32.1K | 267ms | 0.3%
  - /api/orders | 12.8K | 456ms | 0.2%
  - /api/auth/login | 8.9K | 89ms | 0.0%
- Colored bars for visual comparison

PANEL 6 (Third row, center):
"Pod CPU Usage"
- Heat map visualization
- Rows: Individual pods (portfolio-prod-1 through 5)
- Columns: Time intervals
- Color scale: Green (low) → Yellow → Red (high)
- Most cells green/yellow (healthy)

PANEL 7 (Third row, right):
"Database Queries"
- Bar gauge panel
- Showing:
  - SELECT queries: 89% (blue)
  - INSERT queries: 7% (green)
  - UPDATE queries: 3% (yellow)
  - DELETE queries: 1% (red)
- Horizontal bars

PANEL 8 (Bottom row, full width):
"Error Rate & Active Incidents"
- Graph panel with annotations
- Line chart showing error percentage over time
- Mostly flat at <0.1%
- Two annotation markers:
  - Red marker: "Incident started" (small spike)
  - Green marker: "Incident resolved" (return to normal)
- Second Y-axis showing active incidents count

FOOTER ROW (Status Indicators):
- Green dot "All Systems Operational"
- Yellow dot "1 Performance Degradation"
- Red dot "0 Outages"
- Last updated: "30 seconds ago"

SIDEBAR (Right, collapsible):
"Alert Rules"
- High CPU Alert: OK (green)
- Error Rate: OK (green)
- Response Time SLA: WARNING (yellow)
- Database Connections: OK (green)

VISUAL STYLE:
- Dark Grafana theme
- Background: #0b0c0e
- Panel background: #181b1f
- Text: #d8d9da
- Grafana orange accents: #ff6b00
- Modern, professional monitoring dashboard
- Realistic data visualizations
- Subtle panel borders
- Hover tooltips implied

TECHNICAL SPECIFICATIONS:
- Resolution: 2560x1440
- Aspect ratio: 16:9
- Dark theme consistent throughout
- Grafana UI style
- Clear, readable fonts (Roboto)
```

### Expected Output:
- Professional Grafana dashboard mockup
- Realistic metrics and visualizations
- Dark theme, modern design
- Portfolio-quality screenshot

---

## Prompt 3: ArgoCD Applications Dashboard

### For Midjourney / DALL-E / Figma AI:

```
Create a professional ArgoCD GitOps dashboard mockup:

HEADER:
- Left: ArgoCD logo + "Portfolio Applications"
- Center: Search bar "Search applications..."
- Right: "+ NEW APP" button, Settings icon, User avatar

TOOLBAR:
- Filter buttons: "All", "Synced" (green badge 12), "OutOfSync" (yellow badge 2), "Degraded" (red badge 0)
- Sort dropdown: "Last updated"
- View toggle: Grid view (selected), List view

MAIN CONTENT (Application Cards Grid - 3 columns):

CARD 1: "portfolio-production"
- Top bar: Green "Synced" badge + "Healthy" badge
- Icon: Kubernetes logo
- Details:
  - Namespace: production
  - Cluster: eks-production
  - Repo: github.com/org/portfolio-gitops
  - Path: k8s/overlays/production
  - Last sync: 2m ago
- Resources visual:
  - 5 Deployments (green checkmark)
  - 5 Services (green checkmark)
  - 2 Ingresses (green checkmark)
  - 5 Pods running
- Bottom: "SYNC" button, "DETAILS" button, "..." menu

CARD 2: "portfolio-staging"
- Top bar: Yellow "OutOfSync" badge + "Healthy" badge
- Icon: Kubernetes logo
- Details:
  - Namespace: staging
  - Cluster: eks-staging
  - Repo: github.com/org/portfolio-gitops
  - Path: k8s/overlays/staging
  - Last sync: 5m ago
- Resources visual:
  - 3 Deployments (yellow warning - needs sync)
  - 3 Services (green checkmark)
  - 1 Ingress (green checkmark)
  - 3 Pods running
- Bottom: "SYNC" button (highlighted), "DETAILS" button

CARD 3: "portfolio-monitoring"
- Top bar: Green "Synced" badge + "Healthy" badge
- Icon: Prometheus logo
- Details:
  - Namespace: monitoring
  - Cluster: eks-production
  - Repo: github.com/org/monitoring-gitops
  - Path: k8s/prometheus
  - Last sync: 10m ago
- Resources visual:
  - 1 StatefulSet (green)
  - 2 Services (green)
  - 3 ConfigMaps (green)
- Bottom: "SYNC" button, "DETAILS" button

CARD 4: "portfolio-ingress-nginx"
- Top bar: Green "Synced" badge + "Progressing" badge (yellow)
- Icon: NGINX logo
- Details:
  - Namespace: ingress-nginx
  - Cluster: eks-production
  - Repo: charts.helm.sh/ingress-nginx
  - Chart version: 4.8.3
  - Last sync: 1m ago
- Resources visual:
  - 1 Deployment (yellow - rolling update)
  - 1 Service (green)
  - 1 LoadBalancer (green)
- Progress bar: 66% complete
- Bottom: "SYNC" button (disabled), "DETAILS" button

SIDEBAR (Right):
"Recent Activity"
- Timeline showing recent sync events:
  - portfolio-production synced (2m ago) ✓
  - portfolio-staging sync required (5m ago) ⚠
  - portfolio-monitoring synced (10m ago) ✓
  - portfolio-database configured (15m ago) ✓

"Sync Statistics"
- Pie chart showing:
  - Synced: 12 apps (green, 85%)
  - OutOfSync: 2 apps (yellow, 14%)
  - Unknown: 0 apps (gray, 0%)

BOTTOM PANEL (Collapsible):
"Application Details - portfolio-production"
- Resource Tree visualization:
  - Deployment (portfolio) → ReplicaSet → 5 Pods (all green)
  - Service (portfolio) → Endpoints (green)
  - Ingress → LoadBalancer (green)
- Each resource with health status indicator
- Expandable tree structure

VISUAL STYLE:
- Modern SaaS dashboard
- Light theme (optional: dark mode toggle)
- Background: #f5f7fa (light) or #1e1e1e (dark)
- ArgoCD brand blue: #1b5e99
- Status colors:
  - Synced/Healthy: #18be94 (green)
  - OutOfSync/Warning: #f4c030 (yellow)
  - Degraded/Error: #e96d76 (red)
  - Progressing: #0dadea (blue)
- Card shadows and depth
- Clean, modern typography (Inter)

TECHNICAL SPECIFICATIONS:
- Resolution: 2560x1440
- Aspect ratio: 16:9
- Option for light or dark theme
- ArgoCD UI style
- Clear status indicators
- Professional GitOps dashboard
```

### Expected Output:
- Professional ArgoCD dashboard mockup
- Clear application sync status
- Modern GitOps interface design
- Suitable for DevOps portfolio

---

## Prompt 4: K6 Performance Test Results

### For Midjourney / DALL-E / Figma AI:

```
Create a professional K6 load testing results dashboard:

HEADER:
- K6 logo + "Load Test Results - Portfolio Application"
- Test name: "Production Load Test - Nov 2024"
- Status: Large green "PASSED" badge

SUMMARY CARDS (Top Row - 4 cards):

CARD 1: "Virtual Users"
- Large number: "200"
- Label: "Peak Concurrent Users"
- Small line chart showing ramp-up: 0 → 50 → 100 → 200
- Green indicator

CARD 2: "Requests"
- Large number: "127,459"
- Label: "Total HTTP Requests"
- Subtext: "945 req/s average"
- Green indicator

CARD 3: "Response Time"
- Large number: "324ms"
- Label: "P95 Response Time"
- SLA: 500ms (green checkmark "Within SLA")
- Target: < 500ms

CARD 4: "Error Rate"
- Large number: "0.12%"
- Label: "Failed Requests"
- SLA: 1% (green checkmark "Within SLA")
- Target: < 1%

MAIN CHART (Large, center):
"Response Time Distribution Over Time"
- Area chart with multiple percentile bands:
  - P50 band (green, 150-200ms)
  - P95 band (yellow, 300-400ms)
  - P99 band (orange, 500-700ms)
  - Max (red line, occasionally spikes to 1200ms)
- X-axis: Test duration (0-27 minutes)
- Y-axis: Response time (ms)
- Annotations showing test phases:
  - "Ramp-up to 50 users" (0-2min)
  - "Steady state 50 users" (2-7min)
  - "Ramp-up to 100 users" (7-9min)
  - "Steady state 100 users" (9-14min)
  - "Ramp-up to 200 users" (14-16min)
  - "Steady state 200 users" (16-21min)
  - "Ramp-down" (21-27min)
- Threshold line at 500ms (gray dashed)

SECONDARY CHARTS (Second Row - 3 panels):

CHART 1: "Requests Per Second"
- Line chart showing throughput
- Starts at ~100 req/s
- Ramps up to peak ~945 req/s at 200 users
- Smooth curve matching user ramp-up
- Green line

CHART 2: "Error Rate Over Time"
- Line chart showing error percentage
- Mostly flat at ~0.1%
- Small spike to 0.5% during 200-user phase
- Returns to baseline
- Red line

CHART 3: "Active Connections"
- Stacked area chart showing:
  - Established connections (blue)
  - Time to establish (yellow)
- Grows with virtual users
- Max: 200 concurrent connections

DETAILED METRICS TABLE (Bottom):
"Endpoint Performance Breakdown"

| Endpoint | Requests | Avg | P95 | P99 | Max | Errors |
|----------|----------|-----|-----|-----|-----|--------|
| POST /api/auth/login | 8,954 | 89ms | 156ms | 234ms | 456ms | 0.0% |
| GET /api/products | 45,231 | 145ms | 267ms | 389ms | 1,023ms | 0.1% |
| GET /api/users/:id | 32,109 | 98ms | 189ms | 267ms | 567ms | 0.0% |
| POST /api/orders | 12,890 | 234ms | 456ms | 678ms | 1,234ms | 0.3% |
| GET /api/search | 28,275 | 178ms | 334ms | 489ms | 890ms | 0.2% |

- Color-coded performance bars
- Green: Within SLA
- Yellow: Approaching limit
- Red: Exceeds threshold

SIDEBAR (Right):
"Test Configuration"
- Duration: 27 minutes
- Max VUs: 200
- Ramp-up stages: 5
- Scenarios: 4
- Target RPS: 1,000
- Geo-location: us-east-1

"Pass/Fail Checks"
✓ P95 response time < 500ms
✓ P99 response time < 1000ms
✓ Error rate < 1%
✓ Successful requests > 99%
✗ Max response time < 1000ms (1,234ms)

VISUAL STYLE:
- Clean, technical report aesthetic
- White background with subtle gray panels
- K6 purple accents: #7d64ff
- Status colors:
  - Pass/Good: #00d084
  - Warning: #ffb800
  - Fail/Error: #ff5252
- Professional data visualization
- Clear grid lines
- Readable sans-serif font (Roboto)

TECHNICAL SPECIFICATIONS:
- Resolution: 2560x1440
- Aspect ratio: 16:9
- Light theme with color accents
- Professional testing report style
- Export-ready for presentations
```

### Expected Output:
- Professional K6 test results dashboard
- Comprehensive performance metrics
- Clear pass/fail indicators
- Suitable for QA/performance portfolio

---

## Tools for Creating Dashboard Mockups

### Recommended Approaches:

1. **Figma (Best for editable mockups)**
   - Use AWS/Grafana UI kits
   - Fully customizable
   - Export to PNG/SVG
   - Share live links

2. **AI + Figma Hybrid**
   - Generate base with AI
   - Import to Figma
   - Add annotations and details
   - Polish and export

3. **Screenshot Real Dashboards**
   - CloudWatch: Use AWS console
   - Grafana: Use Grafana Cloud free tier
   - ArgoCD: Deploy locally with Minikube
   - K6: Run actual tests

4. **Dashboard Builder Tools**
   - Retool: Build custom dashboards
   - Grafana: Create with dummy data
   - Kibana: Elasticsearch visualizations

### Post-Processing Tips:

1. **Blur Sensitive Data**
   - Account IDs
   - IP addresses
   - API keys
   - Real domain names

2. **Add Annotations**
   - Callouts for key features
   - Arrows pointing to important metrics
   - Text explanations

3. **Export Multiple Formats**
   - PNG for presentations
   - SVG for web
   - PDF for print

4. **Create Variants**
   - Light/dark theme versions
   - Different states (healthy/degraded)
   - Multiple time ranges
