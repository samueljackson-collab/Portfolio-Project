#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "$0")/.." && pwd)
projects_dir="$root_dir/projects"

for category in $(ls "$projects_dir" | sort); do
  for project in $(ls "$projects_dir/$category" | sort); do
    project_dir="$projects_dir/$category/$project"
    [ -d "$project_dir" ] || continue
    script="$project_dir/validate.sh"
    if [ -x "$script" ]; then
      echo "=== Validating $category/$project ==="
      pushd "$project_dir" >/dev/null
      ./validate.sh
      popd >/dev/null
    else
      echo "Validation script missing: $category/$project" >&2
      exit 1
    fi
  done
done
