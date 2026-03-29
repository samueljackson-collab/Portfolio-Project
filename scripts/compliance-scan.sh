#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/compliance-scan.sh [OPTIONS] [TARGET ...]

Options:
  --policy-dir DIR   Path to the directory containing Rego policies (default: security/policies)
  --target PATH      Explicit manifest or directory to evaluate (repeatable)
  -h, --help         Show this help message

Any additional positional arguments are treated as extra targets.
USAGE
}

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POLICY_DIR="security/policies"
TARGETS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --policy-dir)
      if [[ $# -lt 2 ]]; then
        echo "error: --policy-dir requires a value" >&2
        usage
        exit 2
      fi
      POLICY_DIR="$2"
      shift 2
      ;;
    --target)
      if [[ $# -lt 2 ]]; then
        echo "error: --target requires a path" >&2
        usage
        exit 2
      fi
      TARGETS+=("$2")
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      TARGETS+=("$@")
      break
      ;;
    -* )
      echo "error: unknown option $1" >&2
      usage
      exit 2
      ;;
    * )
      TARGETS+=("$1")
      shift
      ;;
  esac

done

cd "$REPO_ROOT"

if [[ ! -d "$POLICY_DIR" ]]; then
  echo "error: policy directory '$POLICY_DIR' does not exist" >&2
  exit 3
fi

if ! command -v conftest >/dev/null 2>&1; then
  echo "error: conftest binary not found in PATH" >&2
  exit 4
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  if [[ -d "kubernetes" ]]; then
    mapfile -t TARGETS < <(find kubernetes -type f \( -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) -print)
  fi
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  TARGETS=(".")
fi

conftest test --policy "$POLICY_DIR" "${TARGETS[@]}"
