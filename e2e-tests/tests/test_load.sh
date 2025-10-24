#!/usr/bin/env bash
set -euo pipefail

k6 run ../k6/load-test.js
