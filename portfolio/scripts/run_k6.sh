#!/usr/bin/env bash
set -euo pipefail

k6 run tools/perf/k6-smoke.js
