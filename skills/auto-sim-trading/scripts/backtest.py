#!/usr/bin/env python3
import argparse, json, subprocess, statistics
from pathlib import Path
from run_real_sim import build_universe, filter_universe

BASE = Path.home()/'.openclaw'/'skills'/'finance-data'/'tools'

def run_json(cmd):
    return json.loads(subprocess.check_output(cmd, text=True))

def get_return(symbol, days=250):
    hist = run_json(['python3', str(BASE/'history_price.py'), symbol, str(days)])
    return hist.get('statistics', {}).get('price_change_pct', 0)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbols', nargs='*', default=None)
    p.add_argument('--days', type=int, default=250)
    p.add_argument('--limit', type=int, default=80)
    args = p.parse_args()
    if args.symbols:
        universe = [{'symbol': s, 'name': ''} for s in args.symbols]
    else:
        universe = filter_universe(build_universe())[:args.limit]
    per_symbol = []
    for item in universe:
        s = item['symbol']
        try:
            r = get_return(s, args.days)
            per_symbol.append({'symbol': s, 'name': item.get('name',''), 'return_pct': round(r,2)})
        except Exception:
            continue
    clean = [x['return_pct'] for x in per_symbol if 'return_pct' in x]
    avg = round(statistics.mean(clean), 2) if clean else 0
    win_rate = round(sum(1 for x in clean if x > 0) / len(clean) * 100, 2) if clean else 0
    max_ret = max(clean) if clean else 0
    min_ret = min(clean) if clean else 0
    print(json.dumps({'mode':'backtest','market':'A-share','days':args.days,'universe_size':len(universe),'summary':{'avg_return_pct':avg,'win_rate_pct':win_rate,'best_return_pct':max_ret,'worst_return_pct':min_ret},'results':per_symbol[:20]}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
