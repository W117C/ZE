#!/bin/bash
# 启动模拟炒股系统
echo "启动自动模拟炒股系统..."
cd "$(dirname "$0")"
python3 skills/auto-sim-trading/scripts/run_real_sim.py --top 10
