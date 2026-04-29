#!/usr/bin/env python3
"""
Portfolio Optimizer: Suggest optimal weights for a candidate portfolio.
Supports: equal weight, risk parity, return-weighted, and custom constraints.

Usage:
  python3 portfolio_optimizer.py --symbols 600519 300750 600036 --method risk_parity
"""
import argparse, json, subprocess, sys, statistics
from pathlib import Path

BASE = Path.home()/'.openclaw'/'skills'/'finance-data'/'tools'

def run_json(cmd):
    return json.loads(subprocess.check_output(cmd, text=True))

def get_stock_data(symbol):
    try:
        hist = run_json(['python3', str(BASE/'history_price.py'), symbol, '60'])
        stats = hist.get('statistics', {})
        return {
            'symbol': symbol,
            'return_pct': stats.get('price_change_pct', 0) or 0,
            'volatility': stats.get('volatility', 0) or 0,
            'price': stats.get('latest_price')
        }
    except Exception:
        return {'symbol': symbol, 'return_pct': 0, 'volatility': 2, 'price': 0}

def optimize(symbols, method='risk_parity', max_weight=0.4, min_weight=0.05):
    """优化投资组合权重"""
    stocks = [get_stock_data(s) for s in symbols]
    n = len(stocks)

    if method == 'equal':
        weights = [1.0 / n] * n

    elif method == 'risk_parity':
        # 风险平价：波动率倒数加权
        inv_vols = [1.0 / (s['volatility'] if s['volatility'] > 0 else 2) for s in stocks]
        total = sum(inv_vols)
        weights = [w / total for w in inv_vols]

    elif method == 'return_weighted':
        # 收益加权：正向收益正权重，负收益最小权重
        returns = [max(s['return_pct'], -20) for s in stocks]
        positive = [max(r, 0) + min_weight * 100 for r in returns]
        total = sum(positive)
        weights = [w / total for w in positive]

    elif method == 'sharpe_max':
        # 近似 Sharpe 最大化：收益/波动 正比
        ratios = [(s['return_pct'] / s['volatility']) if s['volatility'] > 0 else 0 for s in stocks]
        positive = [max(r, 0) + 0.1 for r in ratios]
        total = sum(positive)
        weights = [w / total for w in positive]

    else:
        weights = [1.0 / n] * n

    # 应用约束
    weights = [max(w, min_weight) for w in weights]
    weights = [min(w, max_weight) for w in weights]
    total = sum(weights)
    weights = [w / total for w in weights]

    # 计算优化后指标
    port_return = sum(s['return_pct'] * w for s, w in zip(stocks, weights))
    port_vol = sum(s['volatility'] * w for s, w in zip(stocks, weights))

    return {
        'method': method,
        'symbols': symbols,
        'weights': {s: round(w, 4) for s, w in zip(symbols, weights)},
        'constraints': {'max_weight': max_weight, 'min_weight': min_weight},
        'portfolio_return_pct': round(port_return, 2),
        'portfolio_volatility': round(port_vol, 2),
        'sharpe_approx': round(port_return / port_vol, 2) if port_vol > 0 else 0,
        'stocks': stocks
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbols', nargs='+', required=True)
    p.add_argument('--method', default='risk_parity', choices=['equal', 'risk_parity', 'return_weighted', 'sharpe_max'])
    p.add_argument('--max-weight', type=float, default=0.4)
    p.add_argument('--min-weight', type=float, default=0.05)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    result = optimize(args.symbols, args.method, args.max_weight, args.min_weight)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"=== Portfolio Optimization ({args.method}) ===")
        print("\n建议权重:")
        for s, w in result['weights'].items():
            print(f"  {s}: {w:.1%}")
        print(f"\n组合收益: {result['portfolio_return_pct']}%")
        print(f"组合波动: {result['portfolio_volatility']}")
        print(f"Sharpe 近似: {result['sharpe_approx']}")
        print("=== End ===")

if __name__ == '__main__':
    main()
