#!/usr/bin/env python3
"""
Quant Fund OS: Anti-cyclic Portfolio Builder.

Builds a diversified portfolio across strategy types with correlation control.

Usage:
  python3 portfolio_builder.py --cta 0.25 --market-neutral 0.25 --long-only 0.25 --arbitrage 0.15 --cash 0.10
  python3 portfolio_builder.py --preset core
"""
import argparse, json

# Default allocation ranges
STRATEGY_PROFILES = {
    'CTA': {'expected_return': 12, 'expected_dd': 15, 'vol': 10, 'correlation_base': 0.2},
    'market-neutral': {'expected_return': 8, 'expected_dd': 8, 'vol': 5, 'correlation_base': 0.1},
    'long-only': {'expected_return': 15, 'expected_dd': 25, 'vol': 18, 'correlation_base': 0.6},
    'index-enhance': {'expected_return': 13, 'expected_dd': 20, 'vol': 15, 'correlation_base': 0.5},
    'arbitrage': {'expected_return': 6, 'expected_dd': 5, 'vol': 3, 'correlation_base': 0.05},
    'options': {'expected_return': 10, 'expected_dd': 12, 'vol': 8, 'correlation_base': 0.15},
    'high-frequency': {'expected_return': 18, 'expected_dd': 10, 'vol': 7, 'correlation_base': 0.1},
    'multi-asset': {'expected_return': 10, 'expected_dd': 12, 'vol': 8, 'correlation_base': 0.3},
    'cash': {'expected_return': 2, 'expected_dd': 0, 'vol': 0, 'correlation_base': 0}
}

PRESETS = {
    'core': {'CTA': 0.25, 'market-neutral': 0.25, 'long-only': 0.20, 'arbitrage': 0.15, 'cash': 0.15},
    'aggressive': {'CTA': 0.30, 'long-only': 0.30, 'index-enhance': 0.20, 'options': 0.10, 'cash': 0.10},
    'conservative': {'market-neutral': 0.30, 'arbitrage': 0.25, 'cash': 0.25, 'CTA': 0.10, 'long-only': 0.10}
}

def build_portfolio(allocations, correlation_matrix=None):
    """构建组合并计算预期指标"""
    total_return = 0
    total_vol = 0
    total_dd = 0
    max_corr = 0

    for strat, weight in allocations.items():
        profile = STRATEGY_PROFILES.get(strat, STRATEGY_PROFILES['long-only'])
        total_return += profile['expected_return'] * weight
        total_vol += profile['vol'] * weight
        total_dd += profile['expected_dd'] * weight
        max_corr = max(max_corr, profile['correlation_base'])

    sharpe_approx = total_return / total_vol if total_vol > 0 else 0
    calmar_approx = total_return / total_dd if total_dd > 0 else 0

    # Correlation check
    correlation_ok = max_corr < 0.6
    correlation_warning = "" if correlation_ok else "⚠️ 部分策略相关性偏高"

    # Rating
    if sharpe_approx > 1.2 and total_dd < 12:
        quality = "优秀"
    elif sharpe_approx > 0.8 and total_dd < 20:
        quality = "良好"
    else:
        quality = "一般"

    return {
        'allocations': allocations,
        'expected_return': round(total_return, 1),
        'expected_vol': round(total_vol, 1),
        'expected_max_dd': round(total_dd, 1),
        'sharpe_approx': round(sharpe_approx, 2),
        'calmar_approx': round(calmar_approx, 2),
        'max_correlation': round(max_corr, 2),
        'correlation_ok': correlation_ok,
        'portfolio_quality': quality,
        'warnings': [] if correlation_ok else [correlation_warning]
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cta', type=float)
    p.add_argument('--market-neutral', type=float)
    p.add_argument('--long-only', type=float)
    p.add_argument('--index-enhance', type=float)
    p.add_argument('--arbitrage', type=float)
    p.add_argument('--options', type=float)
    p.add_argument('--high-frequency', type=float)
    p.add_argument('--multi-asset', type=float)
    p.add_argument('--cash', type=float)
    p.add_argument('--preset', choices=['core', 'aggressive', 'conservative'])
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    if args.preset:
        allocations = PRESETS[args.preset]
    else:
        allocations = {}
        if args.cta: allocations['CTA'] = args.cta
        if args.market_neutral: allocations['market-neutral'] = args.market_neutral
        if args.long_only: allocations['long-only'] = args.long_only
        if args.index_enhance: allocations['index-enhance'] = args.index_enhance
        if args.arbitrage: allocations['arbitrage'] = args.arbitrage
        if args.options: allocations['options'] = args.options
        if args.high_frequency: allocations['high-frequency'] = args.high_frequency
        if args.multi_asset: allocations['multi-asset'] = args.multi_asset
        if args.cash: allocations['cash'] = args.cash

    if not allocations:
        print("Error: specify allocations or --preset", file=sys.stderr)
        sys.exit(1)

    result = build_portfolio(allocations)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"📊 抗周期组合分析")
        print(f"\n配置:")
        for s, w in allocations.items():
            print(f"  {s}: {w:.0%}")
        print(f"\n预期收益: {result['expected_return']}%")
        print(f"预期波动: {result['expected_vol']}%")
        print(f"预期最大回撤: {result['expected_max_dd']}%")
        print(f"Sharpe 近似: {result['sharpe_approx']}")
        print(f"Calmar 近似: {result['calmar_approx']}")
        print(f"最大相关性: {result['max_correlation']}")
        print(f"组合质量: {result['portfolio_quality']}")
        if result['warnings']:
            for w in result['warnings']:
                print(f"  {w}")

import sys
if __name__ == '__main__':
    main()
