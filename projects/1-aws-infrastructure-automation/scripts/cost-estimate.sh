#!/bin/bash
# Cost Estimation Script using Infracost
# Generates cost breakdown and comparison for infrastructure changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Infrastructure Cost Estimation ===${NC}"
echo ""

# Check if Infracost is installed
if ! command -v infracost &> /dev/null; then
    echo -e "${RED}Error: Infracost is not installed${NC}"
    echo ""
    echo "Install Infracost:"
    echo "  macOS:  brew install infracost"
    echo "  Linux:  curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh"
    echo ""
    echo "Then register for a free API key:"
    echo "  infracost auth login"
    exit 1
fi

# Check for Infracost API key
if [ -z "$INFRACOST_API_KEY" ]; then
    echo -e "${YELLOW}Warning: INFRACOST_API_KEY not set${NC}"
    echo "Run 'infracost auth login' to authenticate"
    echo ""
fi

# Parse arguments
ENVIRONMENT="${1:-dev}"
OUTPUT_FORMAT="${2:-table}"
COMPARE_TO=""

usage() {
    echo "Usage: $0 [environment] [format] [--compare baseline.json]"
    echo ""
    echo "Arguments:"
    echo "  environment   Environment to estimate (dev, staging, production). Default: dev"
    echo "  format        Output format (table, json, html). Default: table"
    echo ""
    echo "Options:"
    echo "  --compare FILE  Compare against a baseline JSON file"
    echo ""
    echo "Examples:"
    echo "  $0                           # Estimate dev environment in table format"
    echo "  $0 production json           # Estimate production in JSON format"
    echo "  $0 dev table --compare baseline.json"
}

# Parse --compare flag
while [[ $# -gt 0 ]]; do
    case $1 in
        --compare)
            COMPARE_TO="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            # Handle positional arguments
            if [ -z "$ENVIRONMENT_SET" ]; then
                ENVIRONMENT="$1"
                ENVIRONMENT_SET=true
            elif [ -z "$FORMAT_SET" ]; then
                OUTPUT_FORMAT="$1"
                FORMAT_SET=true
            fi
            shift
            ;;
    esac
done

TFVARS_FILE="$TERRAFORM_DIR/${ENVIRONMENT}.tfvars"

echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "Terraform Dir: $TERRAFORM_DIR"
echo ""

# Initialize Terraform if needed
if [ ! -d "$TERRAFORM_DIR/.terraform" ]; then
    echo "Initializing Terraform..."
    cd "$TERRAFORM_DIR"
    terraform init -backend=false > /dev/null 2>&1
fi

# Generate cost breakdown
echo -e "${GREEN}Generating cost breakdown...${NC}"
echo ""

INFRACOST_ARGS=(
    "breakdown"
    "--path" "$TERRAFORM_DIR"
    "--format" "$OUTPUT_FORMAT"
    "--show-skipped"
)

# Add tfvars file if it exists
if [ -f "$TFVARS_FILE" ]; then
    INFRACOST_ARGS+=("--terraform-var-file" "$TFVARS_FILE")
elif [ -f "${TFVARS_FILE}.example" ]; then
    echo -e "${YELLOW}Note: Using example tfvars file${NC}"
    INFRACOST_ARGS+=("--terraform-var-file" "${TFVARS_FILE}.example")
fi

# Run Infracost
if [ "$OUTPUT_FORMAT" == "json" ]; then
    infracost "${INFRACOST_ARGS[@]}" | tee "$PROJECT_ROOT/cost-estimate-${ENVIRONMENT}.json"
    echo ""
    echo -e "${GREEN}JSON output saved to: cost-estimate-${ENVIRONMENT}.json${NC}"
else
    infracost "${INFRACOST_ARGS[@]}"
fi

# Generate comparison if baseline provided
if [ -n "$COMPARE_TO" ] && [ -f "$COMPARE_TO" ]; then
    echo ""
    echo -e "${GREEN}Comparing against baseline...${NC}"
    echo ""

    infracost diff \
        --path "$TERRAFORM_DIR" \
        --compare-to "$COMPARE_TO" \
        --format table
fi

echo ""
echo -e "${GREEN}=== Cost Estimation Complete ===${NC}"

# Save baseline for future comparisons
if [ "$OUTPUT_FORMAT" != "json" ]; then
    echo ""
    echo "To save a baseline for future comparisons:"
    echo "  $0 $ENVIRONMENT json > baseline-${ENVIRONMENT}.json"
fi
