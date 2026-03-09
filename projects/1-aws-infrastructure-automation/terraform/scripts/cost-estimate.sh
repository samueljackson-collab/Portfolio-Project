#!/bin/bash
###############################################################################
# Cost Estimation Script for AWS Infrastructure
#
# Uses Infracost to estimate AWS costs before deployment. Supports multiple
# environments and provides cost comparisons against baselines.
#
# Usage:
#   ./cost-estimate.sh [dev|staging|production]
#   ./cost-estimate.sh --help
#
# Requirements:
#   - Infracost CLI (https://www.infracost.io/docs/)
#   - Terraform >= 1.4
#   - jq (for JSON parsing)
#
# Environment Variables:
#   INFRACOST_API_KEY: Your Infracost API key (or use `infracost auth login`)
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENV="${1:-dev}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-table}"
SHOW_DETAILS="${SHOW_DETAILS:-true}"

#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [ENVIRONMENT]

Estimate AWS infrastructure costs using Infracost.

ENVIRONMENT:
    dev         Development environment (default)
    staging     Staging environment
    production  Production environment

OPTIONS:
    -h, --help      Show this help message
    -f, --format    Output format: table, json, html (default: table)
    -q, --quiet     Suppress detailed output
    --compare       Compare against baseline
    --save-baseline Save current estimate as baseline

EXAMPLES:
    $(basename "$0")                    # Estimate dev costs
    $(basename "$0") production         # Estimate production costs
    $(basename "$0") --compare staging  # Compare staging against baseline
    $(basename "$0") --save-baseline    # Save current estimate as baseline

EOF
}

check_dependencies() {
    local missing_deps=()

    if ! command -v infracost &> /dev/null; then
        missing_deps+=("infracost")
    fi

    if ! command -v terraform &> /dev/null; then
        missing_deps+=("terraform")
    fi

    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}Error: Missing required dependencies: ${missing_deps[*]}${NC}"
        echo ""
        echo "Install instructions:"
        for dep in "${missing_deps[@]}"; do
            case $dep in
                infracost)
                    echo "  curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh"
                    echo "  infracost auth login"
                    ;;
                terraform)
                    echo "  https://developer.hashicorp.com/terraform/downloads"
                    ;;
                jq)
                    echo "  apt-get install jq  # Debian/Ubuntu"
                    echo "  brew install jq     # macOS"
                    ;;
            esac
        done
        exit 1
    fi
}

check_infracost_auth() {
    if [ -z "${INFRACOST_API_KEY:-}" ]; then
        if ! infracost configure get api_key &> /dev/null; then
            echo -e "${YELLOW}Warning: Infracost API key not configured${NC}"
            echo "Run: infracost auth login"
            echo "Or set: export INFRACOST_API_KEY=your-api-key"
            return 1
        fi
    fi
    return 0
}

#------------------------------------------------------------------------------
# Parse Arguments
#------------------------------------------------------------------------------

COMPARE_MODE=false
SAVE_BASELINE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -q|--quiet)
            SHOW_DETAILS=false
            shift
            ;;
        --compare)
            COMPARE_MODE=true
            shift
            ;;
        --save-baseline)
            SAVE_BASELINE=true
            shift
            ;;
        dev|staging|production)
            ENV="$1"
            shift
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

#------------------------------------------------------------------------------
# Main Execution
#------------------------------------------------------------------------------

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         AWS Infrastructure Cost Estimation                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check dependencies
check_dependencies

# Check Infracost auth
if ! check_infracost_auth; then
    echo -e "${YELLOW}Continuing without Infracost API (limited functionality)${NC}"
fi

# Validate environment
TFVARS_FILE="${PROJECT_ROOT}/${ENV}.tfvars"
if [ ! -f "$TFVARS_FILE" ]; then
    echo -e "${RED}Error: tfvars file not found: ${TFVARS_FILE}${NC}"
    echo "Available environments:"
    ls -1 "${PROJECT_ROOT}"/*.tfvars 2>/dev/null | xargs -n1 basename | sed 's/.tfvars$//' || echo "  None found"
    exit 1
fi

echo -e "Environment: ${BLUE}${ENV}${NC}"
echo -e "Terraform:   ${BLUE}${PROJECT_ROOT}${NC}"
echo -e "Variables:   ${BLUE}${TFVARS_FILE}${NC}"
echo ""

# Change to terraform directory
cd "$PROJECT_ROOT"

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    echo -e "${YELLOW}Initializing Terraform...${NC}"
    terraform init -backend=false -input=false > /dev/null 2>&1 || true
fi

# Generate Infracost breakdown
echo -e "${GREEN}Generating cost breakdown...${NC}"
echo ""

COST_JSON=$(infracost breakdown \
    --path . \
    --terraform-var-file "${TFVARS_FILE}" \
    --format json \
    2>/dev/null || echo '{"totalMonthlyCost": "0", "projects": []}')

# Display results based on format
case $OUTPUT_FORMAT in
    json)
        echo "$COST_JSON" | jq .
        ;;
    html)
        REPORT_FILE="${PROJECT_ROOT}/cost-report-${ENV}.html"
        infracost breakdown \
            --path . \
            --terraform-var-file "${TFVARS_FILE}" \
            --format html \
            --out-file "$REPORT_FILE" \
            2>/dev/null || true
        echo -e "HTML report saved to: ${GREEN}${REPORT_FILE}${NC}"
        ;;
    *)
        # Table format (default)
        infracost breakdown \
            --path . \
            --terraform-var-file "${TFVARS_FILE}" \
            --format table \
            --show-skipped \
            2>/dev/null || echo "Cost estimation unavailable"
        ;;
esac

echo ""

#------------------------------------------------------------------------------
# Cost Summary
#------------------------------------------------------------------------------

TOTAL_COST=$(echo "$COST_JSON" | jq -r '.totalMonthlyCost // "0"')
TOTAL_HOURLY=$(echo "$COST_JSON" | jq -r '.totalHourlyCost // "0"')

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Cost Summary                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"

if [ "$TOTAL_COST" != "0" ] && [ "$TOTAL_COST" != "null" ]; then
    echo -e "  Monthly estimate: ${YELLOW}\$${TOTAL_COST}${NC}"
    if [ "$TOTAL_HOURLY" != "0" ] && [ "$TOTAL_HOURLY" != "null" ]; then
        echo -e "  Hourly estimate:  ${YELLOW}\$${TOTAL_HOURLY}${NC}"
    fi

    # Calculate annual estimate
    ANNUAL=$(echo "$TOTAL_COST * 12" | bc 2>/dev/null || echo "N/A")
    if [ "$ANNUAL" != "N/A" ]; then
        echo -e "  Annual estimate:  ${YELLOW}\$${ANNUAL}${NC}"
    fi
else
    echo -e "${YELLOW}  Cost estimation unavailable (may need AWS credentials)${NC}"
fi

echo ""

#------------------------------------------------------------------------------
# Save JSON Report
#------------------------------------------------------------------------------

REPORT_FILE="${PROJECT_ROOT}/cost-estimate-${ENV}.json"
echo "$COST_JSON" > "$REPORT_FILE"
echo -e "Detailed report saved to: ${GREEN}${REPORT_FILE}${NC}"

#------------------------------------------------------------------------------
# Baseline Comparison
#------------------------------------------------------------------------------

BASELINE_FILE="${PROJECT_ROOT}/cost-baseline-${ENV}.json"

if [ "$SAVE_BASELINE" = true ]; then
    cp "$REPORT_FILE" "$BASELINE_FILE"
    echo -e "Baseline saved to: ${GREEN}${BASELINE_FILE}${NC}"
fi

if [ "$COMPARE_MODE" = true ] && [ -f "$BASELINE_FILE" ]; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Cost Comparison vs Baseline                     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"

    infracost diff \
        --path . \
        --terraform-var-file "${TFVARS_FILE}" \
        --compare-to "$BASELINE_FILE" \
        --format table \
        2>/dev/null || echo "Comparison unavailable"

    # Calculate percentage change
    BASELINE_COST=$(jq -r '.totalMonthlyCost // "0"' "$BASELINE_FILE")
    if [ "$BASELINE_COST" != "0" ] && [ "$BASELINE_COST" != "null" ] && [ "$TOTAL_COST" != "0" ]; then
        CHANGE=$(echo "scale=2; (($TOTAL_COST - $BASELINE_COST) / $BASELINE_COST) * 100" | bc 2>/dev/null || echo "N/A")
        if [ "$CHANGE" != "N/A" ]; then
            if (( $(echo "$CHANGE > 0" | bc -l) )); then
                echo -e "  Cost change: ${RED}+${CHANGE}%${NC}"
            elif (( $(echo "$CHANGE < 0" | bc -l) )); then
                echo -e "  Cost change: ${GREEN}${CHANGE}%${NC}"
            else
                echo -e "  Cost change: ${GREEN}0%${NC}"
            fi
        fi
    fi
fi

echo ""

#------------------------------------------------------------------------------
# Resource Breakdown
#------------------------------------------------------------------------------

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Resource Breakdown                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"

echo "$COST_JSON" | jq -r '
    .projects[0].breakdown.resources[] |
    select(.monthlyCost != null and .monthlyCost != "0") |
    "  \(.name): $\(.monthlyCost)/month"
' 2>/dev/null | head -20 || echo "  No detailed breakdown available"

echo ""

#------------------------------------------------------------------------------
# Cost Optimization Recommendations
#------------------------------------------------------------------------------

if [ "$SHOW_DETAILS" = true ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           Cost Optimization Recommendations                  ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"

    recommendations=()

    # Check for T2 instances (recommend T3)
    if echo "$COST_JSON" | grep -qi "t2\."; then
        recommendations+=("💡 Consider T3 instances instead of T2 for better performance/cost")
    fi

    # Check for GP2 volumes (recommend GP3)
    if echo "$COST_JSON" | grep -qi "gp2"; then
        recommendations+=("💡 Consider GP3 volumes instead of GP2 for cost savings")
    fi

    # Check for NAT Gateways in non-prod
    if [ "$ENV" != "production" ] && echo "$COST_JSON" | grep -qi "nat"; then
        recommendations+=("💡 Use single NAT Gateway for non-production environments")
    fi

    # Check for Multi-AZ RDS in dev
    if [ "$ENV" = "dev" ] && echo "$COST_JSON" | grep -qi "multi-az"; then
        recommendations+=("💡 Consider single-AZ RDS for development environment")
    fi

    # Reserved instances suggestion for production
    if [ "$ENV" = "production" ]; then
        recommendations+=("💡 Consider Reserved Instances or Savings Plans for production")
    fi

    # Spot instances suggestion
    if echo "$COST_JSON" | grep -qi "ec2"; then
        recommendations+=("💡 Consider Spot Instances for non-critical workloads")
    fi

    if [ ${#recommendations[@]} -eq 0 ]; then
        echo "  No specific recommendations at this time."
    else
        for rec in "${recommendations[@]}"; do
            echo "  $rec"
        done
    fi
fi

echo ""
echo -e "${GREEN}Cost estimation complete!${NC}"
echo ""
echo "Next steps:"
echo "  - Review the cost breakdown above"
echo "  - Compare: $0 --compare ${ENV}"
echo "  - Save baseline: $0 --save-baseline ${ENV}"
echo "  - Try another env: $0 [dev|staging|production]"
echo ""
