#!/bin/bash
# 快速测试所有模块
set -e

echo "=== 测试环境 ==="
python3 --version
echo ""

echo "=== 测试 akshare ==="
python3 -c "import akshare; print('akshare OK:', akshare.__version__)" 2>/dev/null || echo "akshare 未安装"

echo "=== 测试股票查询 ==="
python3 skills/finance-data/tools/stock_query.py 600519 2>/dev/null | head -5 || echo "股票查询测试失败"

echo "=== 测试基金分析 ==="
python3 skills/quant-fund-analysis/scripts/analyze_single_fund.py 000216 2>/dev/null | head -5 || echo "基金分析测试失败"

echo ""
echo "=== 测试完成 ==="
