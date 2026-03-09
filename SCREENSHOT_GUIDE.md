# SCREENSHOT GUIDE FOR PORTFOLIO

# ================================

# How to capture, organize, and catalog screenshots for your portfolio

## OVERVIEW

This guide shows you exactly how to take professional screenshots of your infrastructure and use the `organize-screenshots.py` tool to automatically catalog them.

---

## PART 1: TAKING SCREENSHOTS

### What to Screenshot

#### For PRJ-HOME-001 (Network Infrastructure)

1. **UniFi Controller Dashboard**
   - Main dashboard showing all devices
   - Network topology view
   - VLAN configuration page
   - Wireless networks list
   - Firewall rules page
   - Client devices list

2. **pfSense Firewall**
   - Dashboard (System > Status > Dashboard)
   - Firewall rules (Firewall > Rules)
   - NAT configuration
   - Interface assignments
   - System logs

3. **Network Diagrams**
   - UniFi topology map (screenshot from controller)
   - Any physical setup photos

**Recommended Tools:**

- Browser built-in (Ctrl+Shift+S in Firefox, Cmd+Shift+4 on Mac)
- Windows Snipping Tool
- macOS Screenshot (Cmd+Shift+3 for full screen, Cmd+Shift+4 for selection)

---

#### For PRJ-HOME-002 (Virtualization)

1. **Proxmox Dashboard**
   - Datacenter view (node list)
   - Summary page for each node
   - VM list
   - Storage view
   - Cluster status

2. **Proxmox Backup Server**
   - Datastore overview
   - Backup jobs list
   - Recent backup logs
   - Backup verification results

3. **TrueNAS**
   - Dashboard
   - Storage > Pools
   - Sharing > NFS exports
   - Sharing > SMB shares
   - Snapshot list

4. **Service UIs**
   - Wiki.js homepage
   - Home Assistant dashboard
   - Immich photo library
   - Nginx Proxy Manager proxy hosts list

---

#### For PRJ-SDE-002 (Observability)

1. **Grafana Dashboards**
   - Infrastructure overview dashboard
   - Node exporter dashboard
   - Container metrics dashboard
   - Any custom dashboards
   - Alert history panel

2. **Prometheus**
   - Status > Targets page
   - Alerts page
   - Graph view with sample query
   - Configuration page

3. **Alertmanager**
   - Alert list
   - Silences page
   - Alert history

4. **Loki/Grafana Explore**
   - Log query example
   - Log stream visualization

---

### Screenshot Best Practices

#### Resolution & Quality

```
Minimum: 1920x1080 (Full HD)
Recommended: 2560x1440 (2K) or higher
Format: PNG (best quality) or JPG (if PNG too large)
```

#### What to Include

- ✅ Navigation bars (shows context)
- ✅ Timestamps (proves it's your system)
- ✅ Key metrics and data
- ✅ Multiple views of same system

#### What to Redact

- ❌ Real IP addresses (use browser dev tools to edit page before screenshot)
- ❌ Real hostnames (unless they're obviously homelab)
- ❌ Email addresses
- ❌ API keys or tokens
- ❌ Client names or proprietary data

#### Pro Tips

1. **Clean up before screenshots:**
   - Close unrelated tabs
   - Clear notifications
   - Maximize important panels

2. **Use browser zoom:**
   - Zoom to 90% or 80% to fit more content
   - Or zoom to 110-125% for readability in documentation

3. **Take multiple angles:**
   - Overview screenshots
   - Detail screenshots of specific features
   - Before/after comparisons

---

## PART 2: ORGANIZING SCREENSHOTS

### Step 1: Collect Screenshots in One Directory

Create a temporary directory for new screenshots:

```bash
mkdir ~/portfolio-screenshots
```

Move/copy all screenshots there:

```bash
mv ~/Downloads/Screenshot*.png ~/portfolio-screenshots/
mv ~/Pictures/Screenshots/*.png ~/portfolio-screenshots/
```

---

### Step 2: Name Files Descriptively (Optional but Recommended)

The organization tool auto-categorizes by filename, so descriptive names help:

**Good Names:**

```
grafana-dashboard-infrastructure.png
proxmox-cluster-summary.png
unifi-network-topology.png
homeassistant-dashboard.png
prometheus-targets-healthy.png
```

**Tool Will Auto-Detect:**

- "grafana" → dashboards category
- "proxmox" → infrastructure category
- "unifi" → networking category
- "prometheus" → monitoring category

**Bad Names:**

```
Screenshot 2024-11-06 at 3.41.23 PM.png  (No context)
IMG_1234.png  (Generic)
```

---

### Step 3: Run Organization Tool

Navigate to portfolio repository:

```bash
cd ~/Portfolio-Project
```

**Option A: Auto-Detect Project (if filename contains project ID)**

```bash
python3 scripts/organize-screenshots.py ~/portfolio-screenshots

# Tool will look for PRJ-HOME-001, PRJ-SDE-002, etc. in filenames
```

**Option B: Specify Project Explicitly**

```bash
# For homelab network screenshots
python3 scripts/organize-screenshots.py ~/portfolio-screenshots --project PRJ-HOME-001

# For virtualization screenshots
python3 scripts/organize-screenshots.py ~/portfolio-screenshots --project PRJ-HOME-002

# For monitoring screenshots
python3 scripts/organize-screenshots.py ~/portfolio-screenshots --project PRJ-SDE-002
```

**Option C: Dry Run (Preview First)**

```bash
# See what would happen without actually moving files
python3 scripts/organize-screenshots.py ~/portfolio-screenshots --project PRJ-HOME-001 --dry-run

# Review output, then run without --dry-run
```

---

### Step 4: Review Organization

The tool will:

1. ✅ Categorize screenshots automatically
2. ✅ Rename with consistent format: `PRJ-XXX_category_NN_YYYYMMDD.png`
3. ✅ Detect and skip duplicates
4. ✅ Extract metadata (dimensions, file size)
5. ✅ Generate README.md catalog
6. ✅ Create JSON index

**Check the results:**

```bash
# View the catalog
cat projects/06-homelab/PRJ-HOME-001/assets/screenshots/README.md

# See organized files
ls -lh projects/06-homelab/PRJ-HOME-001/assets/screenshots/*/

# Check JSON index
cat projects/06-homelab/PRJ-HOME-001/assets/screenshots/screenshots-index.json
```

---

### Step 5: Commit to Git

```bash
cd ~/Portfolio-Project

# Add screenshots
git add projects/*/assets/screenshots/

# Commit
git commit -m "Add infrastructure screenshots for PRJ-HOME-001"

# Push
git push origin your-branch-name
```

---

## PART 3: EXAMPLE WORKFLOW

### Complete Example: Adding Grafana Screenshots

```bash
# 1. Take screenshots of Grafana dashboards
# Open Grafana → Dashboard → Screenshot (name: grafana-infrastructure-overview.png)
# Open Grafana → Another Dashboard → Screenshot (name: grafana-node-metrics.png)

# 2. Collect screenshots
mkdir ~/portfolio-screenshots/grafana
mv ~/Downloads/grafana-*.png ~/portfolio-screenshots/grafana/

# 3. Organize with tool
cd ~/Portfolio-Project
python3 scripts/organize-screenshots.py ~/portfolio-screenshots/grafana --project PRJ-SDE-002

# Output:
# Found 2 screenshot(s) to organize
#
# Processing: grafana-infrastructure-overview.png
#   → PRJ-SDE-002/dashboards/PRJ-SDE-002_dashboards_01_20241107.png
#      Size: 1.2 MB
#      Dimensions: 2560x1440
#
# Processing: grafana-node-metrics.png
#   → PRJ-SDE-002/dashboards/PRJ-SDE-002_dashboards_02_20241107.png
#      Size: 1.4 MB
#      Dimensions: 2560x1440
#
# ============================================================
# ORGANIZATION SUMMARY
# ============================================================
# Total screenshots: 2
# Organized: 2
# Skipped: 0
# Duplicates: 0
# Errors: 0
# ============================================================

# 4. Review catalog
cat projects/01-sde-devops/PRJ-SDE-002/assets/screenshots/README.md

# 5. View on GitHub (after commit/push)
# GitHub will show images inline in the README

# 6. Commit
git add projects/01-sde-devops/PRJ-SDE-002/assets/screenshots/
git commit -m "Add Grafana dashboard screenshots"
git push origin claude/review-portfolio-completeness-011CUsNpct9dDKup4KLZHtE1
```

---

## PART 4: CATEGORIES EXPLAINED

The tool automatically categorizes based on filename keywords:

| Category | Keywords | Examples |
|----------|----------|----------|
| **dashboards** | grafana, dashboard, metrics, graph, chart | Grafana dashboards, Kibana views |
| **infrastructure** | proxmox, vcenter, esxi, cluster, node, vm | Hypervisor dashboards, VM lists |
| **networking** | unifi, switch, router, topology, network, vlan, firewall, pfsense | Network topology, VLAN configs, firewall rules |
| **monitoring** | prometheus, alert, loki, log, monitor | Prometheus targets, alert history, log queries |
| **services** | wikijs, homeassistant, immich, service, app, application | Application UIs, service dashboards |
| **storage** | truenas, nas, zfs, dataset, disk, storage | NAS dashboards, ZFS pools, storage stats |
| **security** | siem, opensearch, security, threat, detection | SIEM dashboards, security logs |
| **configuration** | config, setting, setup, preferences | Configuration screens, settings panels |
| **deployment** | deploy, install, provision, terraform, ansible | Deployment progress, terraform output |
| **misc** | (anything else) | Uncategorized screenshots |

**Pro Tip:** Include category keywords in your filename for accurate auto-categorization.

---

## PART 5: TROUBLESHOOTING

### Problem: "Could not determine project"

**Solution:** Use `--project` flag explicitly:

```bash
python3 scripts/organize-screenshots.py ~/screenshots --project PRJ-HOME-001
```

### Problem: "Duplicate detected"

**Solution:** This is expected if you've already organized this file. The tool detects duplicates by content (MD5 hash), not filename.

### Problem: "Wrong category assigned"

**Solution:** Rename file to include category keyword before organizing:

```bash
mv screenshot.png grafana-dashboard-overview.png
```

### Problem: "PIL not installed" warning

**Solution:** Install Pillow for full metadata extraction:

```bash
pip install Pillow
```

(Tool works without it, but metadata will be limited)

### Problem: "Permission denied"

**Solution:** Ensure script is executable:

```bash
chmod +x scripts/organize-screenshots.py
```

---

## PART 6: ADVANCED USAGE

### Batch Processing Multiple Projects

```bash
# Organize screenshots for multiple projects in one go
for project in PRJ-HOME-001 PRJ-HOME-002 PRJ-SDE-002; do
  if [ -d ~/screenshots/$project ]; then
    python3 scripts/organize-screenshots.py ~/screenshots/$project --project $project
  fi
done
```

### Custom Screenshot Directory Structure

```bash
# If you have screenshots already organized by project:
~/screenshots/
├── homelab-network/     # PRJ-HOME-001
├── virtualization/      # PRJ-HOME-002
└── monitoring/          # PRJ-SDE-002

# Organize each:
python3 scripts/organize-screenshots.py ~/screenshots/homelab-network --project PRJ-HOME-001
python3 scripts/organize-screenshots.py ~/screenshots/virtualization --project PRJ-HOME-002
python3 scripts/organize-screenshots.py ~/screenshots/monitoring --project PRJ-SDE-002
```

### Re-organizing Existing Screenshots

```bash
# If you need to recategorize, just re-run the tool
# It will detect existing files as duplicates and skip them
# To force re-organization, delete the organized files first
```

---

## QUICK REFERENCE CARD

```bash
# Basic usage
cd ~/Portfolio-Project
python3 scripts/organize-screenshots.py ~/screenshots --project PRJ-XXX-###

# With dry-run (test first)
python3 scripts/organize-screenshots.py ~/screenshots --project PRJ-XXX-### --dry-run

# View help
python3 scripts/organize-screenshots.py --help

# Check results
cat projects/PATH/TO/PROJECT/assets/screenshots/README.md
ls -lh projects/PATH/TO/PROJECT/assets/screenshots/

# Commit to git
git add projects/*/assets/screenshots/
git commit -m "Add screenshots for PROJECT"
git push
```

---

## EXPECTED OUTPUT STRUCTURE

After organizing, your project will have:

```
projects/PROJECT/assets/screenshots/
├── dashboards/
│   ├── PRJ-XXX_dashboards_01_20241107.png
│   ├── PRJ-XXX_dashboards_02_20241107.png
│   └── PRJ-XXX_dashboards_03_20241107.png
├── infrastructure/
│   ├── PRJ-XXX_infrastructure_01_20241107.png
│   └── PRJ-XXX_infrastructure_02_20241107.png
├── networking/
│   └── PRJ-XXX_networking_01_20241107.png
├── README.md                      # Generated catalog with previews
└── screenshots-index.json         # Machine-readable index
```

The README.md will show:

- Image previews (GitHub renders these automatically)
- Original filenames
- Metadata (size, dimensions, date)
- Category summaries
- Usage instructions

---

## TIPS FOR PORTFOLIO PRESENTATION

1. **Quality over Quantity:**
   - 10-15 high-quality screenshots per project is enough
   - Show different aspects (overview, detail, metrics, configuration)

2. **Tell a Story:**
   - Start with architecture/overview screenshots
   - Then show detailed configurations
   - End with monitoring/results

3. **Consistency:**
   - Use same browser/theme for all screenshots
   - Same resolution when possible
   - Organize as you go (don't wait until the end)

4. **Documentation:**
   - The auto-generated README is great for GitHub
   - Reference screenshots in your project READMEs:

     ```markdown
     ![Infrastructure Dashboard](./assets/screenshots/dashboards/PRJ-SDE-002_dashboards_01_20241107.png)
     ```

---

## NEXT STEPS

1. ✅ Read this guide
2. ✅ Take screenshots of your systems
3. ✅ Organize with the tool
4. ✅ Review generated catalogs
5. ✅ Commit to git
6. ✅ View on GitHub to see inline images

**Time Estimate:**

- Taking screenshots: 30-60 minutes per project
- Organizing with tool: 5-10 minutes per batch
- Review and commit: 10-15 minutes

**Total: 1-2 hours for comprehensive screenshot documentation**

---

**Questions?** See `scripts/README.md` for detailed tool documentation.

**Last Updated:** 2024-11-07
