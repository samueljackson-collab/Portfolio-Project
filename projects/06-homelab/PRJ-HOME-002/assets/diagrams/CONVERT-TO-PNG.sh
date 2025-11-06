#!/bin/bash
# Mermaid Diagram to PNG Conversion Script
# ==========================================
# This script converts all .mmd files in the current directory to PNG images
# 
# Prerequisites:
# 1. Node.js installed (v18 or higher)
# 2. Mermaid CLI installed: npm install -g @mermaid-js/mermaid-cli
#
# Usage:
#   chmod +x CONVERT-TO-PNG.sh
#   ./CONVERT-TO-PNG.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "  Mermaid Diagram PNG Conversion Script"
echo "=================================================="
echo ""

# Check if mmdc is installed
if ! command -v mmdc &> /dev/null; then
    echo -e "${RED}ERROR: Mermaid CLI (mmdc) is not installed${NC}"
    echo ""
    echo "Installation instructions:"
    echo "1. Install Node.js (if not installed):"
    echo "   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    echo ""
    echo "2. Install Mermaid CLI globally:"
    echo "   sudo npm install -g @mermaid-js/mermaid-cli"
    echo ""
    echo "3. Verify installation:"
    echo "   mmdc --version"
    echo ""
    exit 1
fi

# Check mmdc version
MMDC_VERSION=$(mmdc --version 2>&1 || echo "unknown")
echo -e "${GREEN}✓${NC} Mermaid CLI version: $MMDC_VERSION"
echo ""

# Find all .mmd files
MMD_FILES=$(find . -maxdepth 1 -name "*.mmd" -type f)

if [ -z "$MMD_FILES" ]; then
    echo -e "${YELLOW}WARNING: No .mmd files found in current directory${NC}"
    exit 0
fi

# Count files
FILE_COUNT=$(echo "$MMD_FILES" | wc -l)
echo "Found $FILE_COUNT Mermaid diagram(s) to convert"
echo ""

# Conversion settings
BACKGROUND="transparent"
WIDTH=3000
SCALE=2
THEME="default"

# Convert each file
SUCCESS_COUNT=0
FAIL_COUNT=0

for FILE in $MMD_FILES; do
    BASENAME=$(basename "$FILE" .mmd)
    OUTPUT="${BASENAME}.png"
    
    echo -n "Converting ${BASENAME}.mmd → ${OUTPUT}... "
    
    if mmdc -i "$FILE" \
            -o "$OUTPUT" \
            -b "$BACKGROUND" \
            -w "$WIDTH" \
            -s "$SCALE" \
            -t "$THEME" \
            2>&1 | grep -q "Success"; then
        echo -e "${GREEN}✓ Success${NC}"
        ((SUCCESS_COUNT++))
        
        # Show file size
        SIZE=$(du -h "$OUTPUT" | cut -f1)
        echo "   Output: $OUTPUT ($SIZE)"
    else
        echo -e "${RED}✗ Failed${NC}"
        ((FAIL_COUNT++))
    fi
    echo ""
done

# Summary
echo "=================================================="
echo "Conversion Summary:"
echo -e "  ${GREEN}Success: $SUCCESS_COUNT${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "  ${RED}Failed: $FAIL_COUNT${NC}"
fi
echo "=================================================="

# List generated PNGs
if [ $SUCCESS_COUNT -gt 0 ]; then
    echo ""
    echo "Generated PNG files:"
    ls -lh *.png 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
fi

echo ""
echo "Done!"
