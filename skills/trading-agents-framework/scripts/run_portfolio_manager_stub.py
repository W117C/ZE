#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('trade_proposal'); p.add_argument('risk_review'); p.add_argument('--out', default='./final_decision.json'); args = p.parse_args()
    proposal = json.loads(Path(args.trade_proposal).read_text())
    risk = json.loads(Path(args.risk_review).read_text())
    rounds = [
      {'round': 1, 'focus': '是否接受 trader 方向', 'observation': proposal.get('direction')},
      {'round': 2, 'focus': '是否满足风险约束', 'observation': risk.get('decision')},
      {'round': 3, 'focus': '是否需要修改后批准', 'observation': 'apply cap' if 'approve' in risk.get('decision','') else 'watch'}
    ]
    if proposal.get('direction') == 'buy' and risk.get('decision') in ['approve','approve_with_resize']:
        decision = 'approve_with_modifications' if risk.get('decision') == 'approve_with_resize' else 'approve'
    elif proposal.get('direction') == 'hold':
        decision = 'delay_watchlist'
    else:
        decision = 'reject'
    final = {'decision': decision, 'modifications':['respect risk cap'] if 'approve' in decision else [], 'rationale':'manager decision based on multi-round review', 'rounds': rounds}
    Path(args.out).write_text(json.dumps(final, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
