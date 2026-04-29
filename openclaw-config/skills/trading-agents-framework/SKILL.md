---
name: trading-agents-framework
description: Use when the user wants to design, analyze, document, or operationalize a multi-agent trading research framework with real subagent session chains and built-in fault tolerance. Includes fundamentals, sentiment via eastmoney guba (A-share), technical analysts, bull/bear debate, trader, risk manager, portfolio manager decision, portfolio analysis/optimization, and execution handoff. Supports subagent-based execution with timeout/retry/fallback, local rules fallback, eastmoney sentiment cache, company-news event classification, and screening-to-decision integration. Not for guaranteed returns, direct financial advice, or unverified live broker execution claims.
---

# Trading Agents Framework

## Current Highlights
- **Real subagent session chain** (Bull / Bear / Trader / Risk / Manager) — verified and working
- **Resilient execution** with timeout, retry, and local rules fallback
- **Eastmoney Guba sentiment** — free, real-time A-share sentiment from 东方财富股吧
- Reddit sentiment fallback (optional)
- **Portfolio layer**: multi-stock analysis + optimization (equal/risk_parity/return_weighted/sharpe_max)
- **Advanced sentiment analysis**: NLP-level scoring, topic clustering, intensity calculation
- Company-news event tags + severity score/level
- Data validation layer before chain execution
- Local rules fallback + OpenClaw subagent dual-mode architecture

## Quick Start
Run integrated pipeline (rules fallback):
```bash
python3 scripts/run_integrated_pipeline.py --top 1 --out-dir ./integrated-runs --risk-profile neutral
```

Run resilient subagent session chain:
```bash
python3 scripts/run_session_chain_resilient.py <analyst_bundle_path> --out-dir ./session-chain-output
```

Eastmoney sentiment (A-share):
```bash
python3 scripts/build_sentiment_context.py --symbol 600519 --out ./social_context.json
python3 scripts/build_sentiment_context.py --market-overview --out ./market_sentiment.json
```

## Boundary
This framework is for research and decision support only. It is not financial, investment, or trading advice.
