#!/bin/bash

# ============================================================================
# BULK DEPENDABOT PR MERGE SCRIPT
# ============================================================================
# This script enables auto-merge for existing Dependabot PRs in bulk.
# 
# Features:
# - Validates GitHub CLI installation and authentication
# - Separates Python version updates from other Docker updates
# - Shows preview and asks for confirmation before proceeding
# - Enables auto-merge with squash and branch deletion
# - Rate limiting to avoid API throttling
# - Error handling for merge conflicts
# - Summary report of actions taken
#
# Usage:
#   ./scripts/bulk-merge-dependabot.sh
#
# Prerequisites:
#   - GitHub CLI (gh) must be installed
#   - Must be authenticated with gh auth login
#   - Must have write permissions on the repository
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_PRS=0
PYTHON_PRS=0
OTHER_DOCKER_PRS=0
PIP_PRS=0
MERGED_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}  Dependabot Bulk Merge Script${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# ============================================================================
# 1. Validate GitHub CLI
# ============================================================================
echo -e "${YELLOW}[1/7] Checking GitHub CLI installation...${NC}"
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ Error: GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI found: $(gh --version | head -1)${NC}"
echo ""

# ============================================================================
# 2. Validate Authentication
# ============================================================================
echo -e "${YELLOW}[2/7] Checking GitHub authentication...${NC}"
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Error: Not authenticated with GitHub CLI.${NC}"
    echo "Please run: gh auth login"
    exit 1
fi
echo -e "${GREEN}✓ Authenticated${NC}"
echo ""

# ============================================================================
# 3. Fetch All Dependabot PRs
# ============================================================================
echo -e "${YELLOW}[3/7] Fetching all Dependabot PRs...${NC}"

# Get all open PRs by Dependabot (limit to 1000 to be safe)
ALL_PRS=$(gh pr list --author "app/dependabot" --state open --limit 1000 --json number,title,url)
TOTAL_PRS=$(echo "$ALL_PRS" | jq '. | length')

echo -e "${GREEN}✓ Found $TOTAL_PRS open Dependabot PRs${NC}"
echo ""

if [ "$TOTAL_PRS" -eq 0 ]; then
    echo -e "${GREEN}No Dependabot PRs to process. Exiting.${NC}"
    exit 0
fi

# ============================================================================
# 4. Categorize PRs
# ============================================================================
echo -e "${YELLOW}[4/7] Categorizing PRs...${NC}"

# Filter Python Docker updates (3.11 -> 3.14, etc.)
PYTHON_DOCKER_PRS=$(echo "$ALL_PRS" | jq '[.[] | select(.title | test("python"; "i"))]')
PYTHON_PRS=$(echo "$PYTHON_DOCKER_PRS" | jq '. | length')

# Filter other Docker updates (Node, Alpine, Golang, Java, etc.)
OTHER_DOCKER_PRS_DATA=$(echo "$ALL_PRS" | jq '[.[] | select(.title | test("docker"; "i") and (.title | test("python"; "i") | not))]')
OTHER_DOCKER_PRS=$(echo "$OTHER_DOCKER_PRS_DATA" | jq '. | length')

# Filter pip dependency updates
PIP_PRS_DATA=$(echo "$ALL_PRS" | jq '[.[] | select(.title | test("pip|requirements"; "i"))]')
PIP_PRS=$(echo "$PIP_PRS_DATA" | jq '. | length')

echo -e "  ${BLUE}Python Docker updates:${NC} $PYTHON_PRS"
echo -e "  ${BLUE}Other Docker updates:${NC} $OTHER_DOCKER_PRS"
echo -e "  ${BLUE}Pip dependency updates:${NC} $PIP_PRS"
echo ""

# ============================================================================
# 5. Show Preview and Confirm
# ============================================================================
echo -e "${YELLOW}[5/7] Preview of PRs to auto-merge:${NC}"
echo ""

if [ "$PYTHON_PRS" -gt 0 ]; then
    echo -e "${BLUE}Python Docker Updates ($PYTHON_PRS PRs):${NC}"
    echo "$PYTHON_DOCKER_PRS" | jq -r '.[] | "  #\(.number) - \(.title)"' | head -10
    if [ "$PYTHON_PRS" -gt 10 ]; then
        echo "  ... and $((PYTHON_PRS - 10)) more"
    fi
    echo ""
fi

if [ "$OTHER_DOCKER_PRS" -gt 0 ]; then
    echo -e "${BLUE}Other Docker Updates ($OTHER_DOCKER_PRS PRs):${NC}"
    echo "$OTHER_DOCKER_PRS_DATA" | jq -r '.[] | "  #\(.number) - \(.title)"' | head -10
    if [ "$OTHER_DOCKER_PRS" -gt 10 ]; then
        echo "  ... and $((OTHER_DOCKER_PRS - 10)) more"
    fi
    echo ""
fi

if [ "$PIP_PRS" -gt 0 ]; then
    echo -e "${BLUE}Pip Dependency Updates ($PIP_PRS PRs):${NC}"
    echo "$PIP_PRS_DATA" | jq -r '.[] | "  #\(.number) - \(.title)"' | head -10
    if [ "$PIP_PRS" -gt 10 ]; then
        echo "  ... and $((PIP_PRS - 10)) more"
    fi
    echo ""
fi

echo -e "${YELLOW}This will enable auto-merge for all $TOTAL_PRS PRs.${NC}"
echo -e "${YELLOW}They will merge automatically once CI passes.${NC}"
echo ""
read -p "Do you want to proceed? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}Aborted by user.${NC}"
    exit 0
fi
echo ""

# ============================================================================
# 6. Enable Auto-Merge for All PRs
# ============================================================================
echo -e "${YELLOW}[6/7] Enabling auto-merge for PRs...${NC}"
echo ""

# Function to enable auto-merge for a PR
enable_auto_merge() {
    local PR_NUMBER=$1
    local PR_TITLE=$2
    local COUNTER=$3
    
    echo -e "${BLUE}[$COUNTER/$TOTAL_PRS]${NC} Processing PR #$PR_NUMBER: $PR_TITLE"
    
    # Try to enable auto-merge
    if gh pr merge "$PR_NUMBER" --auto --squash --delete-branch 2>/dev/null; then
        echo -e "  ${GREEN}✓ Auto-merge enabled${NC}"
        ((MERGED_COUNT++))
    else
        # Check if PR has conflicts or other issues
        PR_STATUS=$(gh pr view "$PR_NUMBER" --json mergeable,mergeStateStatus --jq '.mergeable + " " + .mergeStateStatus')
        
        if [[ "$PR_STATUS" == *"CONFLICTING"* ]]; then
            echo -e "  ${YELLOW}⚠ Skipped: Has merge conflicts${NC}"
            ((SKIPPED_COUNT++))
        else
            echo -e "  ${RED}✗ Failed: $PR_STATUS${NC}"
            ((FAILED_COUNT++))
        fi
    fi
    
    # Rate limiting: sleep 2 seconds every 10 PRs
    if [ $((COUNTER % 10)) -eq 0 ]; then
        echo -e "  ${YELLOW}⏸ Rate limiting: sleeping 2 seconds...${NC}"
        sleep 2
    fi
}

# Process all PRs - using process substitution to preserve counter variables
COUNTER=0
while IFS='|' read -r PR_NUM PR_TITLE; do
    ((COUNTER++))
    enable_auto_merge "$PR_NUM" "$PR_TITLE" "$COUNTER"
done < <(echo "$ALL_PRS" | jq -r '.[] | "\(.number)|\(.title)"')

# Wait a moment for final counts to update
sleep 1

echo ""

# ============================================================================
# 7. Summary Report
# ============================================================================
echo -e "${YELLOW}[7/7] Summary Report${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo -e "${GREEN}✓ Successfully enabled auto-merge:${NC} $MERGED_COUNT PRs"
echo -e "${YELLOW}⚠ Skipped (conflicts or issues):${NC} $SKIPPED_COUNT PRs"
echo -e "${RED}✗ Failed:${NC} $FAILED_COUNT PRs"
echo -e "${BLUE}Total processed:${NC} $TOTAL_PRS PRs"
echo -e "${BLUE}============================================================================${NC}"
echo ""

echo -e "${GREEN}Done! PRs will merge automatically when CI passes.${NC}"
echo ""
echo "To check PR status, run:"
echo "  gh pr list --author 'app/dependabot'"
echo ""
echo "To disable auto-merge on a specific PR, run:"
echo "  gh pr merge --disable-auto <PR_NUMBER>"
echo ""
