#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('debate_summary'); p.add_argument('--out', default='./trade_proposal.json'); args = p.parse_args()
    data = json.loads(Path(args.debate_summary).read_text())
    buy = len(data.get('buy_evidence', []))
    sell = len(data.get('sell_evidence', []))
    if buy > sell:
        direction = 'buy'; size = 'starter position'; horizon = 'swing'; confidence = 'medium'
    elif sell > buy:
        direction = 'hold'; size = 'no new position'; horizon = 'watch'; confidence = 'medium'
    else:
        direction = 'hold'; size = 'small initial size'; horizon = 'swing'; confidence = 'low_to_medium'
    proposal = {'direction': direction, 'size_logic': size, 'holding_horizon': horizon, 'triggers':['review on new data','reassess after risk review'], 'confidence': confidence}
    Path(args.out).write_text(json.dumps(proposal, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
