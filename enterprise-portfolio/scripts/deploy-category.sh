#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <category>" >&2
  exit 1
fi

category=$1
root_dir=$(cd "$(dirname "$0")/.." && pwd)
projects_dir="$root_dir/projects/$category"

if [ ! -d "$projects_dir" ]; then
  echo "Category not found: $projects_dir" >&2
  exit 1
fi

for project in $(ls "$projects_dir" | sort); do
  [ -d "$projects_dir/$project" ] || continue
  echo "=== Deploying $category/$project ==="
  "$root_dir/scripts/deploy-project.sh" "$category" "$project"
done
