---
name: auto-sim-trading
description: Create and run an A-share daily paper-trading workflow with real market data, virtual account management (initial capital, NAV, return, max drawdown), HS300/CSI500 universe expansion, user watchlist support, one-year backtesting, daily report generation with trade logging, problem tracking, self-reflection and auto-evolution engine. Use when the user wants a simulated stock trading system that learns from daily reports, identifies recurring issues, generates upgrade tasks, tracks account performance, and continuously improves itself.
---

# Auto Sim Trading

## Overview

A-share paper-trading system with virtual account management, self-reflection, and continuous evolution.

## Features
- **虚拟账户管理**：初始资金、总资产、持仓市值、收益率、最大回撤
- Real market data from finance-data + akshare
- HS300 + CSI500 + watchlist universe
- Multi-factor scoring (trend/risk/liquidity)
- Trade logging and portfolio state persistence
- Daily summary report with account overview, trades, problems, and improvements
- **Self-reflection engine**: analyzes patterns across daily reports
- **Auto-evolution**: identifies recurring issues and generates upgrade tasks
- Scheduled daily report at 15:30 with automatic reflection

## Quick Start

Initialize account:
```bash
python3 scripts/account_manager.py init --capital 200000
python3 scripts/account_manager.py show
python3 scripts/account_manager.py update
```

Record a trade (auto-updates account cash):
```bash
python3 scripts/trade_logger.py record --action buy --symbol 600519 --price 1527.2 --quantity 100 --reason "基本面偏正面"
```

Generate daily report with account overview:
```bash
python3 scripts/generate_daily_report.py --out ./daily-report.json --send --reflect
```

Run a one-year backtest:
```bash
python3 scripts/backtest.py --days 250
```

## Resources

### scripts/
- `account_manager.py`: Virtual account management (capital, NAV, return, drawdown)
- `trade_logger.py`: Trade logging with auto account cash update
- `generate_daily_report.py`: Daily report with account overview
- `self_reflection.py`: Self-reflection and auto-evolution engine
- `run_real_sim.py`: Real-data A-share daily paper-trading report
- `backtest.py`: One-year backtest summary

### references/
- `strategy.md`: Factor model, filtering logic, risk-control guidance
- `universe.md`: HS300 + CSI500 + watchlist universe rules
