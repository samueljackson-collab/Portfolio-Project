#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

mapfile -t readmes < <(git ls-files '*README.md')

if [ ${#readmes[@]} -eq 0 ]; then
  echo "No tracked README.md files found."
  exit 0
fi

patterns=(
  '# see project-specific'
  '`# project-specific`'
  'Project owner'
  '\[project-specific unit command\]'
  '\[project-specific integration command\]'
  '\[project-specific e2e/manual steps\]'
)

status=0
for pattern in "${patterns[@]}"; do
  if rg -n --no-heading -e "$pattern" "${readmes[@]}"; then
    status=1
  fi
done

# Fail only on table placeholder n/a markers to avoid false positives in prose.
if rg -n --no-heading -e '^\| (Unit|Integration|E2E/Manual) \| .*\| n/a \|' "${readmes[@]}"; then
  status=1
fi

if [ "$status" -ne 0 ]; then
  echo "Placeholder content found in tracked README.md files."
  exit 1
fi

echo "README placeholder check passed."
