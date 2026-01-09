#!/bin/bash
###############################################################################
# CloudWatch Dashboard Import Script
#
# This script imports CloudWatch dashboard definitions from JSON files.
# It replaces placeholder variables with actual resource IDs.
#
# Usage:
#   ./import-dashboards.sh <environment> [options]
#
# Example:
#   ./import-dashboards.sh dev
#   ./import-dashboards.sh production --dry-run
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
ENV="${1:-dev}"
DRY_RUN=false
AWS_REGION="${AWS_REGION:-us-west-2}"

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           CloudWatch Dashboard Import                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Environment: ${ENV}"
echo "Region:      ${AWS_REGION}"
echo "Dry Run:     ${DRY_RUN}"
echo ""

# Get resource IDs from Terraform outputs
TERRAFORM_DIR="${SCRIPT_DIR}/../terraform"

if [ -f "${TERRAFORM_DIR}/.terraform/terraform.tfstate" ] || [ -d "${TERRAFORM_DIR}/.terraform" ]; then
    echo -e "${YELLOW}Fetching resource IDs from Terraform...${NC}"

    cd "${TERRAFORM_DIR}"

    # Initialize if needed
    if [ ! -d ".terraform" ]; then
        terraform init -backend=false > /dev/null 2>&1 || true
    fi

    # Try to get outputs
    OUTPUTS=$(terraform output -json 2>/dev/null || echo '{}')

    # Extract resource IDs
    NAT_GATEWAY_ID=$(echo "$OUTPUTS" | jq -r '.nat_gateway_ids.value[0] // "nat-placeholder"' 2>/dev/null || echo "nat-placeholder")
    DB_INSTANCE_ID=$(echo "$OUTPUTS" | jq -r '.rds_endpoint.value // "portfolio-'${ENV}'"' 2>/dev/null | cut -d'.' -f1 || echo "portfolio-${ENV}")
    ASG_NAME=$(echo "$OUTPUTS" | jq -r '.app_autoscaling_group_name.value // "portfolio-app-'${ENV}'"' 2>/dev/null || echo "portfolio-app-${ENV}")
    cd "${SCRIPT_DIR}"
else
    echo -e "${YELLOW}Terraform not initialized, using placeholder values${NC}"
    NAT_GATEWAY_ID="nat-placeholder"
    DB_INSTANCE_ID="portfolio-${ENV}"
    ASG_NAME="portfolio-app-${ENV}"
fi

# Set derived values
DB_REPLICA_ID="${DB_INSTANCE_ID}-replica"
FLOW_LOG_GROUP="/aws/vpc/portfolio-${ENV}-flow-logs"
LOG_GROUP_NAMESPACE="portfolio-${ENV}/vpc"

echo ""
echo "Resource IDs:"
echo "  NAT Gateway:    ${NAT_GATEWAY_ID}"
echo "  DB Instance:    ${DB_INSTANCE_ID}"
echo "  ASG Name:       ${ASG_NAME}"
echo "  Flow Log Group: ${FLOW_LOG_GROUP}"
echo ""

# Function to process and import dashboard
import_dashboard() {
    local json_file="$1"
    local dashboard_name="$2"

    if [ ! -f "$json_file" ]; then
        echo -e "${YELLOW}Dashboard file not found: ${json_file}${NC}"
        return
    fi

    echo -e "${GREEN}Processing: ${dashboard_name}${NC}"

    # Replace placeholders
    local processed_json
    processed_json=$(cat "$json_file" | \
        sed "s|\${AWS_REGION}|${AWS_REGION}|g" | \
        sed "s|\${NAT_GATEWAY_ID}|${NAT_GATEWAY_ID}|g" | \
        sed "s|\${DB_INSTANCE_ID}|${DB_INSTANCE_ID}|g" | \
        sed "s|\${DB_REPLICA_ID}|${DB_REPLICA_ID}|g" | \
        sed "s|\${ASG_NAME}|${ASG_NAME}|g" | \
        sed "s|\${FLOW_LOG_GROUP}|${FLOW_LOG_GROUP}|g" | \
        sed "s|\${LOG_GROUP_NAMESPACE}|${LOG_GROUP_NAMESPACE}|g"
    )

    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would create dashboard: ${dashboard_name}"
        echo "  Processed JSON preview:"
        echo "$processed_json" | jq '.widgets | length' | xargs -I {} echo "    Widgets: {}"
    else
        # Create/update CloudWatch dashboard
        aws cloudwatch put-dashboard \
            --dashboard-name "${dashboard_name}" \
            --dashboard-body "$processed_json" \
            --region "${AWS_REGION}"

        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓${NC} Dashboard created/updated: ${dashboard_name}"
        else
            echo -e "  ${RED}✗${NC} Failed to create dashboard: ${dashboard_name}"
        fi
    fi
}

# Import dashboards
echo -e "${YELLOW}Importing dashboards...${NC}"
echo ""

import_dashboard "${SCRIPT_DIR}/vpc-dashboard.json" "portfolio-${ENV}-vpc"
import_dashboard "${SCRIPT_DIR}/rds-dashboard.json" "portfolio-${ENV}-rds"

echo ""
echo -e "${GREEN}Dashboard import complete!${NC}"
echo ""

if [ "$DRY_RUN" = false ]; then
    echo "View dashboards in CloudWatch console:"
    echo "  https://${AWS_REGION}.console.aws.amazon.com/cloudwatch/home?region=${AWS_REGION}#dashboards:"
fi
