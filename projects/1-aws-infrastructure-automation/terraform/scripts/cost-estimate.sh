#!/bin/bash
# Cost Estimation Script for AWS Infrastructure
# Uses Infracost to estimate AWS costs before deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AWS Infrastructure Cost Estimation ===${NC}"
echo ""

# Check if Infracost is installed
if ! command -v infracost &> /dev/null; then
    echo -e "${RED}Error: Infracost is not installed${NC}"
    echo "Install with: curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh"
    echo "Then run: infracost auth login"
    exit 1
fi

# Check if Infracost API key is configured
if ! infracost configure get api_key &> /dev/null; then
    echo -e "${YELLOW}Warning: Infracost API key not configured${NC}"
    echo "Run: infracost auth login"
    exit 1
fi

# Environment to estimate (default: dev)
ENV="${1:-dev}"
ENV_DIR="$PROJECT_ROOT/environments/$ENV"

if [ ! -d "$ENV_DIR" ]; then
    echo -e "${RED}Error: Environment directory not found: $ENV_DIR${NC}"
    exit 1
fi

echo -e "Estimating costs for environment: ${GREEN}$ENV${NC}"
echo ""

# Change to environment directory
cd "$ENV_DIR"

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    echo -e "${YELLOW}Initializing Terraform...${NC}"
    terraform init -backend=false > /dev/null
fi

# Generate cost breakdown
echo -e "${GREEN}Generating cost breakdown...${NC}"
echo ""

infracost breakdown \
    --path . \
    --format table \
    --show-skipped \
    --sync-usage-file \
    2>/dev/null || true

echo ""
echo -e "${GREEN}=== Cost Summary ===${NC}"

# Generate JSON output for detailed analysis
COST_JSON=$(infracost breakdown \
    --path . \
    --format json \
    2>/dev/null || echo '{}')

# Parse total monthly cost
TOTAL_COST=$(echo "$COST_JSON" | jq -r '.totalMonthlyCost // "0"')

if [ "$TOTAL_COST" != "0" ] && [ "$TOTAL_COST" != "null" ]; then
    echo -e "Estimated monthly cost: ${YELLOW}\$$TOTAL_COST${NC}"
else
    echo -e "${YELLOW}Cost estimation unavailable (may need AWS credentials or usage data)${NC}"
fi

# Save detailed breakdown to file
REPORT_FILE="$PROJECT_ROOT/cost-estimate-$ENV.json"
echo "$COST_JSON" > "$REPORT_FILE"
echo ""
echo -e "Detailed report saved to: ${GREEN}$REPORT_FILE${NC}"

# Compare with baseline if it exists
BASELINE_FILE="$PROJECT_ROOT/cost-baseline-$ENV.json"
if [ -f "$BASELINE_FILE" ]; then
    echo ""
    echo -e "${GREEN}=== Cost Comparison vs Baseline ===${NC}"
    echo ""

    infracost diff \
        --path . \
        --compare-to "$BASELINE_FILE" \
        --format table \
        2>/dev/null || true

    # Calculate percentage change
    BASELINE_COST=$(jq -r '.totalMonthlyCost // "0"' "$BASELINE_FILE")
    if [ "$BASELINE_COST" != "0" ] && [ "$BASELINE_COST" != "null" ] && [ "$TOTAL_COST" != "0" ]; then
        CHANGE=$(echo "scale=2; (($TOTAL_COST - $BASELINE_COST) / $BASELINE_COST) * 100" | bc)
        if (( $(echo "$CHANGE > 0" | bc -l) )); then
            echo -e "Cost change: ${RED}+$CHANGE%${NC}"
        elif (( $(echo "$CHANGE < 0" | bc -l) )); then
            echo -e "Cost change: ${GREEN}$CHANGE%${NC}"
        else
            echo -e "Cost change: ${GREEN}0%${NC}"
        fi
    fi
else
    echo ""
    echo -e "${YELLOW}No baseline found. Creating baseline...${NC}"
    cp "$REPORT_FILE" "$BASELINE_FILE"
    echo -e "Baseline saved to: ${GREEN}$BASELINE_FILE${NC}"
fi

echo ""
echo -e "${GREEN}=== Resource Breakdown ===${NC}"

# Show breakdown by service
echo "$COST_JSON" | jq -r '
    .projects[0].breakdown.resources[] |
    select(.monthlyCost != null and .monthlyCost != "0") |
    "\(.name): $\(.monthlyCost)/month"
' 2>/dev/null | sort -t'$' -k2 -rn || echo "No detailed breakdown available"

echo ""
echo -e "${GREEN}=== Cost Optimization Recommendations ===${NC}"

# Analyze for cost optimization opportunities
HAS_T2=$(echo "$COST_JSON" | grep -i "t2\." || true)
if [ -n "$HAS_T2" ]; then
    echo -e "⚠️  Consider using T3 instances instead of T2 for better performance/cost ratio"
fi

HAS_GP2=$(echo "$COST_JSON" | grep -i "gp2" || true)
if [ -n "$HAS_GP2" ]; then
    echo -e "⚠️  Consider using GP3 volumes instead of GP2 for cost savings"
fi

NO_RESERVED=$(echo "$COST_JSON" | grep -i "reserved" || true)
if [ -z "$NO_RESERVED" ]; then
    echo -e "💡 Consider reserved instances or savings plans for production workloads"
fi

echo ""
echo -e "${GREEN}=== Estimation Complete ===${NC}"
echo ""
echo "To update the baseline with current costs:"
echo "  cp $REPORT_FILE $BASELINE_FILE"
echo ""
echo "To estimate a different environment:"
echo "  $0 [dev|staging|prod]"
