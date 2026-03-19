#!/usr/bin/env bash
##############################################################################
# run_validation.sh
# Runs the Python validation tests for the Terraform RDS module.
# Usage: bash scripts/run_validation.sh [--save-output]
##############################################################################
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$PROJECT_ROOT/tests"
DEMO_OUTPUT_DIR="$PROJECT_ROOT/demo_output"

VALIDATE_SCRIPT="$TESTS_DIR/validate_module.py"
OUTPUT_FILE="$DEMO_OUTPUT_DIR/validation_results.txt"

# Colours (disabled when not a TTY)
if [ -t 1 ]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[1;33m'
  NC='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; NC=''
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Terraform RDS Module – Validation Run ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Verify Python 3 is available
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}ERROR: python3 not found on PATH.${NC}"
  exit 1
fi

echo "Project root : $PROJECT_ROOT"
echo "Test script  : $VALIDATE_SCRIPT"
echo ""

# Run validation
if python3 "$VALIDATE_SCRIPT"; then
  EXIT_CODE=0
  echo ""
  echo -e "${GREEN}All checks passed!${NC}"
else
  EXIT_CODE=$?
  echo ""
  echo -e "${RED}One or more checks failed (exit code: $EXIT_CODE).${NC}"
fi

# Optionally save output
if [[ "${1:-}" == "--save-output" ]]; then
  mkdir -p "$DEMO_OUTPUT_DIR"
  python3 "$VALIDATE_SCRIPT" > "$OUTPUT_FILE" 2>&1 || true
  echo ""
  echo "Output saved to: $OUTPUT_FILE"
fi

exit $EXIT_CODE
