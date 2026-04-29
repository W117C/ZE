#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
BASE = Path.home()/'.openclaw'/'skills'/'finance-data'/'tools'

def run_json(cmd):
    return json.loads(subprocess.check_output(cmd, text=True))

def main():
    p = argparse.ArgumentParser()
    p.add_argument('symbol')
    p.add_argument('--market', default='CN')
    p.add_argument('--horizon', default='swing')
    p.add_argument('--range', dest='days', type=int, default=250)
    p.add_argument('--out', default='./market_context.json')
    args = p.parse_args()
    hist = run_json(['python3', str(BASE/'history_price.py'), args.symbol, str(args.days)])
    out = {'symbol': args.symbol, 'market': args.market, 'horizon': args.horizon, 'history': hist}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
