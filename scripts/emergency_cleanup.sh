#!/bin/bash
# 🎯 PR Cleanup Utility
# Usage: ./scripts/emergency_cleanup.sh

set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "❌ GitHub CLI (gh) is required but not installed. Install it before running this script."
  exit 1
fi

echo "🛑 CAUTION: This will close ALL open Pull Requests."
read -p "Are you sure? (y/n) " -n 1 -r
echo
if [[ ! ${REPLY:-} =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

echo "🔍 Fetching open PRs..."
# Get list of all open PR numbers
prs=$(gh pr list --state open --limit 500 --json number -q '.[].number')

if [[ -z "${prs}" ]]; then
  echo "✅ No open PRs found!"
  exit 0
fi

count=$(echo "${prs}" | wc -w | tr -d '[:space:]')
echo "🧹 Closing ${count} PRs..."

# Loop through and close them
for pr in ${prs}; do
  echo "   Closing PR #${pr}..."
  gh pr close "${pr}" --comment "Auto-closing as part of Q4 2025 Portfolio Consolidation."
done

echo "🎉 Cleanup complete! Repository is clean."
