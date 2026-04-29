#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text())

def main():
    p = argparse.ArgumentParser()
    p.add_argument('screening')
    p.add_argument('market_context')
    p.add_argument('fundamentals_context')
    p.add_argument('news_context')
    p.add_argument('social_context')
    p.add_argument('--out', default='./integrated_candidate_packet.json')
    args = p.parse_args()
    out = {
      'screening': load(args.screening),
      'market_context': load(args.market_context),
      'fundamentals_context': load(args.fundamentals_context),
      'news_context': load(args.news_context),
      'social_context': load(args.social_context),
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
