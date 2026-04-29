#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('market_context'); p.add_argument('--out', default='./technical_note.json'); args = p.parse_args()
    data = json.loads(Path(args.market_context).read_text())
    stats = data.get('history', {}).get('statistics', {})
    note = {
      'agent':'technical_analyst',
      'trend':'positive' if stats.get('price_change_pct',0) > 0 else 'negative',
      'momentum': stats.get('price_change_pct',0),
      'volatility': stats.get('volatility',0),
      'levels':'simplified',
      'confidence':'medium'
    }
    Path(args.out).write_text(json.dumps(note, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
