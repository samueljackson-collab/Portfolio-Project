#!/bin/bash
# Lambda Deployment Package Script
# Creates a ZIP file with the log transformer function for AWS Lambda

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Lambda Deployment Package Builder${NC}"
echo -e "${BLUE}================================================${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
LAMBDA_FUNCTION="log_transformer.py"
OUTPUT_ZIP="log_transformer.zip"
TEMP_DIR="package_temp"

# Check if Lambda function exists
if [ ! -f "$LAMBDA_FUNCTION" ]; then
    echo -e "${RED}Error: $LAMBDA_FUNCTION not found!${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Cleaning up old package...${NC}"
rm -f "$OUTPUT_ZIP"
rm -rf "$TEMP_DIR"

echo -e "${BLUE}Step 2: Creating temporary directory...${NC}"
mkdir -p "$TEMP_DIR"

echo -e "${BLUE}Step 3: Copying Lambda function...${NC}"
cp "$LAMBDA_FUNCTION" "$TEMP_DIR/"

# Check if requirements.txt exists and has dependencies beyond testing
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}Step 4: Checking for runtime dependencies...${NC}"

    # Create filtered requirements file excluding test and AWS SDK dependencies
    FILTERED_REQS_FILE="$(mktemp)"
    grep -v "^pytest" requirements.txt | grep -v "^#" | grep -v "^$" | grep -v "^boto" > "$FILTERED_REQS_FILE" || true

    if [ -s "$FILTERED_REQS_FILE" ]; then
        echo -e "${BLUE}Installing runtime dependencies...${NC}"
        pip install -r "$FILTERED_REQS_FILE" -t "$TEMP_DIR" --quiet
        echo -e "${GREEN}Dependencies installed${NC}"
    else
        echo -e "${GREEN}No additional runtime dependencies needed (boto3 included in Lambda runtime)${NC}"
    fi

    rm -f "$FILTERED_REQS_FILE"
else
    echo -e "${GREEN}Step 4: No requirements.txt found (using Lambda runtime packages)${NC}"
fi

echo -e "${BLUE}Step 5: Creating ZIP package...${NC}"
cd "$TEMP_DIR"
zip -r "../$OUTPUT_ZIP" . -q
cd ..

echo -e "${BLUE}Step 6: Cleaning up temporary files...${NC}"
rm -rf "$TEMP_DIR"

# Get ZIP file size
ZIP_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Package created successfully!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "Package: ${BLUE}$OUTPUT_ZIP${NC}"
echo -e "Size: ${BLUE}$ZIP_SIZE${NC}"
echo -e ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Verify package contents: ${GREEN}unzip -l $OUTPUT_ZIP${NC}"
echo -e "2. Deploy with Terraform: ${GREEN}cd ../infrastructure && terraform apply${NC}"
echo -e "3. Or upload manually to Lambda console"
echo -e ""
echo -e "${BLUE}Testing:${NC}"
echo -e "Run tests before deployment: ${GREEN}pytest test_log_transformer.py -v${NC}"
echo -e ""

# Optional: Show package contents
echo -e "${BLUE}Package contents:${NC}"
unzip -l "$OUTPUT_ZIP" | head -20

echo -e ""
echo -e "${GREEN}Done!${NC}"
