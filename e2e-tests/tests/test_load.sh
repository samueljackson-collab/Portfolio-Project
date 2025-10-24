#!/usr/bin/env bash
set -euo pipefail

k6 run "$(dirname "$0")/../k6/scenarios.js"
