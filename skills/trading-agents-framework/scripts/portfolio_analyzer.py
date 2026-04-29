#!/usr/bin/env python3
"""
Portfolio Analyzer: Multi-stock portfolio analysis with correlation, concentration, and risk contribution.

Usage:
  python3 portfolio_analyzer.py --symbols 600519 300750 600036 --weights 0.4 0.35 0.25
  python3 portfolio_analyzer.py --symbols-file ./portfolio.json
"""
import argparse, json, subprocess, statistics, sys
from pathlib import Path

BASE = Path.home()/'.openclaw'/'skills'/'finance-data'/'tools'

def run_json(cmd):
    return json.loads(subprocess.check_output(cmd, text=True))

def get_stock_data(symbol, days=60):
    """获取股票历史数据"""
    try:
        hist = run_json(['python3', str(BASE/'history_price.py'), symbol, str(days)])
        stats = hist.get('statistics', {})
        return {
            'symbol': symbol,
            'price': stats.get('latest_price'),
            'return_pct': stats.get('price_change_pct'),
            'volatility': stats.get('volatility'),
            'avg_volume': stats.get('avg_volume')
        }
    except Exception as e:
        return {'symbol': symbol, 'error': str(e)}

def calc_correlation(returns_a, returns_b):
    """计算两只股票收益率相关性（简化版）"""
    if len(returns_a) < 2 or len(returns_b) < 2:
        return None
    n = min(len(returns_a), len(returns_b))
    a = returns_a[:n]
    b = returns_b[:n]
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    cov = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n)) / n
    std_a = (sum((x - mean_a)**2 for x in a) / n) ** 0.5
    std_b = (sum((x - mean_b)**2 for x in b) / n) ** 0.5
    if std_a == 0 or std_b == 0:
        return None
    return cov / (std_a * std_b)

def analyze_portfolio(symbols, weights=None):
    """分析投资组合"""
    if not weights:
        weights = [1.0 / len(symbols)] * len(symbols)

    # 获取数据
    stock_data = []
    for s in symbols:
        d = get_stock_data(s, 60)
        stock_data.append(d)

    # 计算组合收益和波动
    weighted_return = sum(
        (d.get('return_pct', 0) or 0) * w
        for d, w in zip(stock_data, weights)
    )
    weighted_vol = sum(
        (d.get('volatility', 0) or 0) * w
        for d, w in zip(stock_data, weights)
    )

    # 风险贡献
    risk_contrib = []
    total_vol = weighted_vol if weighted_vol > 0 else 1
    for d, w in zip(stock_data, weights):
        vol = d.get('volatility', 0) or 0
        contrib = (w * vol / total_vol) * 100 if total_vol > 0 else 0
        risk_contrib.append({
            'symbol': d['symbol'],
            'weight': w,
            'volatility': vol,
            'risk_contribution_pct': round(contrib, 2)
        })

    # 集中度指标
    hhi = sum(w**2 for w in weights)  # Herfindahl-Hirschman Index
    concentration = '高' if hhi > 0.5 else '中' if hhi > 0.3 else '低'

    return {
        'portfolio_return_pct': round(weighted_return, 2),
        'portfolio_volatility': round(weighted_vol, 2),
        'sharpe_approx': round(weighted_return / weighted_vol, 2) if weighted_vol > 0 else 0,
        'concentration_index': round(hhi, 4),
        'concentration_level': concentration,
        'stocks': stock_data,
        'risk_contribution': risk_contrib,
        'weights': weights
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbols', nargs='+')
    p.add_argument('--weights', type=float, nargs='+')
    p.add_argument('--symbols-file')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    if args.symbols_file:
        data = json.loads(Path(args.symbols_file).read_text())
        symbols = data.get('symbols', [])
        weights = data.get('weights')
    elif args.symbols:
        symbols = args.symbols
        weights = args.weights
    else:
        print("Error: provide --symbols or --symbols-file", file=sys.stderr)
        sys.exit(1)

    result = analyze_portfolio(symbols, weights)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=== Portfolio Analysis ===")
        print(f"组合收益: {result['portfolio_return_pct']}%")
        print(f"组合波动: {result['portfolio_volatility']}")
        print(f"Sharpe 近似: {result['sharpe_approx']}")
        print(f"集中度: {result['concentration_level']} (HHI={result['concentration_index']})")
        print("\n风险贡献:")
        for r in result['risk_contribution']:
            print(f"  {r['symbol']}: 权重 {r['weight']:.0%}, 风险贡献 {r['risk_contribution_pct']}%")
        print("=== End ===")

if __name__ == '__main__':
    main()
