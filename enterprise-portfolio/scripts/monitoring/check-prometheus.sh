#!/usr/bin/env bash
set -euo pipefail

config_dir=$(cd "$(dirname "$0")/../.." && pwd)/monitoring/prometheus
config_file="$config_dir/prometheus.yml"

if [ ! -f "$config_file" ]; then
  echo "Prometheus configuration not found: $config_file" >&2
  exit 1
fi

if command -v promtool >/dev/null 2>&1; then
  promtool check config "$config_file"
else
  echo "promtool not installed; skipping lint" >&2
fi
