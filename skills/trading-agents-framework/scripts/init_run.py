#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('symbol')
    p.add_argument('--market', default='CN')
    p.add_argument('--risk-profile', default='neutral')
    p.add_argument('--horizon', default='swing')
    p.add_argument('--out', default='./runs')
    args = p.parse_args()
    run_dir = Path(args.out) / f"{args.symbol}-{args.market}-{args.horizon}"
    run_dir.mkdir(parents=True, exist_ok=True)
    meta = {'symbol': args.symbol, 'market': args.market, 'risk_profile': args.risk_profile, 'horizon': args.horizon}
    (run_dir/'run_meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(run_dir)

if __name__ == '__main__':
    main()
