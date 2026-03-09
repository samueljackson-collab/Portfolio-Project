#!/bin/bash
###############################################################################
# Portfolio Screenshot Automation Script
# Helps organize and guide screenshot capture for portfolio projects
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCREENSHOT_DIR="assets/screenshots"
DEMOS_DIR="demos/html-mockups"
PROJECTS_DIR="projects"

# Create directories
mkdir -p "$SCREENSHOT_DIR"/{homelab,aws,monitoring,kubernetes,database,demos}

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

###############################################################################
# Screenshot Guide Functions
###############################################################################

guide_homelab_screenshots() {
    print_header "Homelab Infrastructure Screenshots"

    cat << EOF
📸 Required Screenshots for Homelab Project:

1. Proxmox VE Dashboard
   - Navigate to: https://proxmox.local:8006
   - Show: VM list, resource usage, cluster status
   - Save as: $SCREENSHOT_DIR/homelab/proxmox-dashboard.png

2. Nginx Proxy Manager
   - Navigate to: https://nginx.local
   - Show: Proxy hosts list, SSL certificates
   - Save as: $SCREENSHOT_DIR/homelab/nginx-proxy-hosts.png

3. Grafana Monitoring Dashboard
   - Navigate to: https://grafana.local
   - Show: System overview dashboard
   - Save as: $SCREENSHOT_DIR/homelab/grafana-system-overview.png

4. Wiki.js Documentation
   - Navigate to: https://wiki.local
   - Show: Homepage with navigation
   - Save as: $SCREENSHOT_DIR/homelab/wikijs-homepage.png

5. Home Assistant Dashboard
   - Navigate to: https://homeassistant.local:8123
   - Show: Main dashboard with devices
   - Save as: $SCREENSHOT_DIR/homelab/homeassistant-dashboard.png

6. Immich Photo Gallery
   - Navigate to: https://immich.local
   - Show: Photo library view
   - Save as: $SCREENSHOT_DIR/homelab/immich-gallery.png

💡 Screenshot Tips:
- Use full-page screenshots (Ctrl+Shift+P in Chrome → "Capture full size screenshot")
- Resolution: 1920x1080 minimum
- Hide personal/sensitive information
- Use clean browser window (no bookmarks bar, extensions)

EOF
    read -p "Press Enter when you've captured the homelab screenshots..."
}

guide_aws_screenshots() {
    print_header "AWS Infrastructure Screenshots"

    cat << EOF
📸 Required Screenshots for AWS Projects:

1. VPC Dashboard
   - Navigate to: AWS Console → VPC
   - Show: VPC overview, subnets, route tables
   - Save as: $SCREENSHOT_DIR/aws/vpc-overview.png

2. EC2 Instances
   - Navigate to: AWS Console → EC2 → Instances
   - Show: Running instances with tags
   - Save as: $SCREENSHOT_DIR/aws/ec2-instances.png

3. RDS Databases
   - Navigate to: AWS Console → RDS
   - Show: Database instances, backup status
   - Save as: $SCREENSHOT_DIR/aws/rds-databases.png

4. CloudWatch Dashboard
   - Navigate to: AWS Console → CloudWatch
   - Show: Custom dashboard with metrics
   - Save as: $SCREENSHOT_DIR/aws/cloudwatch-dashboard.png

5. IAM Policies
   - Navigate to: AWS Console → IAM → Policies
   - Show: Custom policies (sanitized)
   - Save as: $SCREENSHOT_DIR/aws/iam-policies.png

6. Terraform State (Local Screenshot)
   - Run: terraform plan
   - Screenshot the plan output
   - Save as: $SCREENSHOT_DIR/aws/terraform-plan.png

⚠️  Security Reminder:
- Redact account IDs, access keys, secrets
- Blur IP addresses if needed
- Don't show sensitive resource names

EOF
    read -p "Press Enter when you've captured the AWS screenshots..."
}

guide_monitoring_screenshots() {
    print_header "Monitoring & Observability Screenshots"

    cat << EOF
📸 Required Screenshots for Monitoring Stack:

1. Prometheus Targets
   - Navigate to: http://prometheus.local:9090/targets
   - Show: All targets with UP status
   - Save as: $SCREENSHOT_DIR/monitoring/prometheus-targets.png

2. Prometheus Alerts
   - Navigate to: http://prometheus.local:9090/alerts
   - Show: Alert rules and current status
   - Save as: $SCREENSHOT_DIR/monitoring/prometheus-alerts.png

3. Grafana Dashboards
   - Infrastructure Overview:
     Save as: $SCREENSHOT_DIR/monitoring/grafana-infrastructure.png
   - Application Metrics:
     Save as: $SCREENSHOT_DIR/monitoring/grafana-application.png
   - Database Performance:
     Save as: $SCREENSHOT_DIR/monitoring/grafana-database.png

4. Loki Log Explorer
   - Navigate to: Grafana → Explore → Loki
   - Show: Log query and results
   - Save as: $SCREENSHOT_DIR/monitoring/loki-logs.png

5. AlertManager
   - Navigate to: http://alertmanager.local:9093
   - Show: Alert groups and routing
   - Save as: $SCREENSHOT_DIR/monitoring/alertmanager.png

EOF
    read -p "Press Enter when you've captured the monitoring screenshots..."
}

guide_demo_screenshots() {
    print_header "HTML Demo Screenshots"

    if [ ! -d "$DEMOS_DIR" ]; then
        print_warning "Demos directory not found: $DEMOS_DIR"
        return
    fi

    echo "📸 Capturing HTML demo screenshots..."
    echo ""

    # List all HTML files in demos
    local html_files=()
    while IFS= read -r -d '' file; do
        html_files+=("$file")
    done < <(find "$DEMOS_DIR" -name "*.html" -type f -print0 2>/dev/null || true)

    if [ ${#html_files[@]} -eq 0 ]; then
        print_warning "No HTML demo files found in $DEMOS_DIR"
        return
    fi

    for html_file in "${html_files[@]}"; do
        filename=$(basename "$html_file" .html)
        echo "  → $filename"
        echo "    Open: file://$(realpath "$html_file")"
        echo "    Save: $SCREENSHOT_DIR/demos/${filename}.png"
        echo ""
    done

    print_info "Use Chrome DevTools to capture:"
    echo "  1. F12 to open DevTools"
    echo "  2. Ctrl+Shift+P for command palette"
    echo "  3. Type 'screenshot' and select 'Capture full size screenshot'"
    echo ""

    read -p "Press Enter when you've captured all demo screenshots..."
}

###############################################################################
# Verification Functions
###############################################################################

verify_screenshots() {
    print_header "Screenshot Verification"

    local total=0
    local found=0

    echo "Checking screenshot directories..."
    echo ""

    for dir in "$SCREENSHOT_DIR"/{homelab,aws,monitoring,kubernetes,database,demos}; do
        if [ -d "$dir" ]; then
            local count=$(find "$dir" -type f \( -name "*.png" -o -name "*.jpg" \) | wc -l)
            total=$((total + 1))
            if [ "$count" -gt 0 ]; then
                found=$((found + 1))
                print_success "$(basename "$dir"): $count screenshots"
            else
                print_warning "$(basename "$dir"): No screenshots found"
            fi
        fi
    done

    echo ""
    echo "Summary: $found/$total directories with screenshots"
}

###############################################################################
# Image Optimization
###############################################################################

optimize_screenshots() {
    print_header "Screenshot Optimization"

    if ! command -v optipng &> /dev/null && ! command -v pngquant &> /dev/null; then
        print_warning "Image optimization tools not found"
        print_info "Install with: sudo apt install optipng pngquant"
        return
    fi

    echo "Optimizing PNG files for web..."
    local count=0

    while IFS= read -r -d '' file; do
        if command -v optipng &> /dev/null; then
            optipng -quiet -o2 "$file" 2>/dev/null || true
            count=$((count + 1))
        fi
    done < <(find "$SCREENSHOT_DIR" -name "*.png" -type f -print0 2>/dev/null || true)

    if [ "$count" -gt 0 ]; then
        print_success "Optimized $count PNG files"
    else
        print_info "No PNG files to optimize"
    fi
}

###############################################################################
# Main Menu
###############################################################################

show_menu() {
    clear
    cat << EOF
${GREEN}
╔═══════════════════════════════════════════════════════════╗
║         Portfolio Screenshot Automation Tool             ║
╚═══════════════════════════════════════════════════════════╝
${NC}

Select a category to capture screenshots:

  ${BLUE}1)${NC} Homelab Infrastructure
  ${BLUE}2)${NC} AWS Cloud Architecture
  ${BLUE}3)${NC} Monitoring & Observability
  ${BLUE}4)${NC} HTML Demo Screenshots
  ${BLUE}5)${NC} All Categories (Full Tour)

  ${BLUE}6)${NC} Verify Screenshots
  ${BLUE}7)${NC} Optimize Images

  ${BLUE}0)${NC} Exit

EOF
    read -p "Enter choice [0-7]: " choice
    echo ""

    case $choice in
        1) guide_homelab_screenshots ;;
        2) guide_aws_screenshots ;;
        3) guide_monitoring_screenshots ;;
        4) guide_demo_screenshots ;;
        5)
            guide_homelab_screenshots
            guide_aws_screenshots
            guide_monitoring_screenshots
            guide_demo_screenshots
            ;;
        6) verify_screenshots ;;
        7) optimize_screenshots ;;
        0)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            sleep 2
            ;;
    esac

    read -p "Press Enter to continue..."
}

###############################################################################
# Main Loop
###############################################################################

main() {
    print_header "Portfolio Screenshot Tool - Starting"

    while true; do
        show_menu
    done
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" -eq "${0}" ]; then
    main
fi
