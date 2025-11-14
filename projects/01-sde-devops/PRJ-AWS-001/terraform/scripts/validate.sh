#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "$0")/.." && pwd)"

pushd "$ROOT_DIR" >/dev/null
terraform fmt -check -recursive
for env in environments/*; do
  [[ -d "$env" ]] || continue
  pushd "$env" >/dev/null
  terraform init -backend=false
  terraform validate
  popd >/dev/null
done
popd >/dev/null
