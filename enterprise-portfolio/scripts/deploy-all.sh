#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "$0")/.." && pwd)
projects_dir="$root_dir/projects"

for category in $(ls "$projects_dir" | sort); do
  echo "===== Deploying category: $category ====="
  "$root_dir/scripts/deploy-category.sh" "$category"
done
