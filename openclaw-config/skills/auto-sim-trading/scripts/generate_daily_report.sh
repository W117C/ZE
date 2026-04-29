#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 run_real_sim.py > /tmp/auto-sim-trading-daily-report.txt
cat /tmp/auto-sim-trading-daily-report.txt
