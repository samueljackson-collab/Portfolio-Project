#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <category> <project>" >&2
  exit 1
fi

category=$1
project=$2
root_dir=$(cd "$(dirname "$0")/.." && pwd)
project_dir="$root_dir/projects/$category/$project"

if [ ! -d "$project_dir" ]; then
  echo "Project directory not found: $project_dir" >&2
  exit 1
fi

script="$project_dir/deploy.sh"
if [ ! -x "$script" ]; then
  echo "Deployment script is missing or not executable: $script" >&2
  exit 1
fi

pushd "$project_dir" >/dev/null
./deploy.sh
popd >/dev/null
