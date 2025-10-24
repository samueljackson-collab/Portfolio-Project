#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "$0")/.." && pwd)
projects_dir="$root_dir/projects"

printf "%-24s | %-30s\n" "Category" "Project"
printf '%s\n' "------------------------------------------+--------------------------------"

for category in $(ls "$projects_dir" | sort); do
  for project in $(ls "$projects_dir/$category" | sort); do
    printf "%-24s | %-30s\n" "$category" "$project"
  done
done
