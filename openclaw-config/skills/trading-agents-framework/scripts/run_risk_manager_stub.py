#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('trade_proposal'); p.add_argument('--risk-profile', default='neutral'); p.add_argument('--out', default='./risk_review.json'); args = p.parse_args()
    proposal = json.loads(Path(args.trade_proposal).read_text())
    direction = proposal.get('direction')
    if args.risk_profile == 'neutral':
        cap = '5%'; drawdown = 'medium'; decision = 'approve_with_resize' if direction == 'buy' else 'approve_watch'
    elif args.risk_profile == 'aggressive':
        cap = '10%'; drawdown = 'high'; decision = 'approve'
    else:
        cap = '2%'; drawdown = 'low'; decision = 'approve_with_resize' if direction == 'buy' else 'watch'
    review = {'profile': args.risk_profile, 'decision': decision, 'position_cap': cap, 'drawdown_sensitivity': drawdown, 'liquidity_risk': 'low', 'hedge_need': 'none'}
    Path(args.out).write_text(json.dumps(review, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
