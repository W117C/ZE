#!/usr/bin/env python3
"""
Quant Fund OS: Multi-fund comparison with scoring, ranking, and recommendation.

Usage:
  python3 compare_funds.py --json-file ./funds.json
  python3 compare_funds.py --demo
"""
import argparse, json, sys

# Import scoring from analyze_single_fund
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from analyze_single_fund import analyze

def compare(funds_data):
    """比较多个基金"""
    results = []
    for f in funds_data:
        r = analyze(
            name=f.get('name', 'Unknown'),
            strategy=f.get('strategy', 'long-only'),
            annual_return=f.get('annual_return'),
            max_dd=f.get('max_dd'),
            vol=f.get('vol'),
            sharpe=f.get('sharpe'),
            calmar=f.get('calmar'),
            win_rate=f.get('win_rate'),
            profit_loss_ratio=f.get('profit_loss_ratio'),
            aum=f.get('aum'),
            fee=f.get('fee'),
            track_record_years=f.get('track_record_years'),
            return_source=f.get('return_source_cleared', True)
        )
        results.append(r)

    # Sort by score
    results.sort(key=lambda x: x['total_score'], reverse=True)

    return {
        'funds': results,
        'best': results[0] if results else None,
        'count': len(results),
        'rating_distribution': {
            'A': sum(1 for r in results if r['rating'] == 'A'),
            'B': sum(1 for r in results if r['rating'] == 'B'),
            'C': sum(1 for r in results if r['rating'] == 'C')
        }
    }

def format_comparison(result):
    lines = []
    lines.append(f"📊 基金对比报告 ({result['count']} 只)")
    lines.append("")
    lines.append("═══ 排名 ═══")
    for i, r in enumerate(result['funds'], 1):
        lines.append(f"  {i}. [{r['rating']}] {r['name']} | 评分 {r['total_score']} | 策略 {r['strategy']}")
    lines.append("")
    lines.append("═══ 评级分布 ═══")
    d = result['rating_distribution']
    lines.append(f"  A级: {d['A']} | B级: {d['B']} | C级: {d['C']}")
    if result['best']:
        lines.append(f"\n🏆 推荐: {result['best']['name']} ({result['best']['total_score']}分, {result['best']['rating']}级)")
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--json-file')
    p.add_argument('--demo', action='store_true')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    if args.demo:
        funds = [
            {'name': 'CTA趋势一号', 'strategy': 'CTA', 'annual_return': 18, 'max_dd': 9, 'vol': 11, 'sharpe': 1.2, 'calmar': 2.0, 'win_rate': 55, 'aum': 500, 'fee': 1.5, 'track_record_years': 3},
            {'name': '中性阿尔法', 'strategy': 'market-neutral', 'annual_return': 10, 'max_dd': 5, 'vol': 4, 'sharpe': 1.8, 'calmar': 2.0, 'win_rate': 65, 'aum': 1000, 'fee': 1.2, 'track_record_years': 5},
            {'name': '指增300', 'strategy': 'index-enhance', 'annual_return': 14, 'max_dd': 22, 'vol': 16, 'sharpe': 0.7, 'calmar': 0.6, 'win_rate': 50, 'aum': 3000, 'fee': 1.0, 'track_record_years': 4}
        ]
    elif args.json_file:
        funds = json.loads(__import__('pathlib').Path(args.json_file).read_text())
    else:
        print("Error: provide --json-file or --demo", file=sys.stderr)
        sys.exit(1)

    result = compare(funds)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_comparison(result))

if __name__ == '__main__':
    main()
