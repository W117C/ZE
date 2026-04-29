#!/usr/bin/env python3
"""
Refresh sentiment cache for watchlist stocks.

Reads from auto-sim-trading watchlist, fetches eastmoney guba sentiment for each,
and writes a summary report.

Usage:
  python3 refresh_sentiment_cache.py
  python3 refresh_sentiment_cache.py --symbols 600519 300750 600036
"""
import argparse, subprocess, json, time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'build_sentiment_context.py'
WATCHLIST = Path.home() / '.openclaw' / 'skills' / 'auto-sim-trading' / 'assets.user-watchlist.json'

def load_watchlist():
    if WATCHLIST.exists():
        data = json.loads(WATCHLIST.read_text())
        return data.get('watchlist', [])
    return []

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbols', nargs='*', default=None, help='Override watchlist')
    p.add_argument('--out', default='./sentiment_refresh_report.json')
    args = p.parse_args()

    symbols = args.symbols if args.symbols else load_watchlist()
    if not symbols:
        print("⚠️ 无股票可刷新（watchlist 为空且未传 --symbols）")
        return

    results = []
    for symbol in symbols:
        tmp = Path('/tmp') / f'sentiment-{symbol}.json'
        subprocess.call(['python3', str(SCRIPT), '--symbol', symbol, '--out', str(tmp)])
        data = json.loads(tmp.read_text()) if tmp.exists() else {'symbol': symbol, 'provider_status': {'cache': 'missing'}}
        results.append({
            'symbol': symbol,
            'name': data.get('name', ''),
            'cache': data.get('provider_status', {}).get('cache'),
            'sentiment_summary': data.get('sentiment_summary'),
            'composite_score': data.get('composite_score'),
            'attention_index': data.get('attention_index')
        })

    report = {
        'refreshed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'count': len(results),
        'status': '全部成功' if all(r['cache'] is not None for r in results) else '部分失败',
        'results': results
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2))

    # Print summary
    print(f"\n刷新股票数：{len(results)} 只  状态：{report['status']}")
    for r in results:
        print(f"  {r['symbol']} {r['name']}: {r['sentiment_summary']} (综合分 {r['composite_score']})")

if __name__ == '__main__':
    main()
