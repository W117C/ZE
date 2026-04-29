#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('social_context'); p.add_argument('--out', default='./sentiment_note.json'); args = p.parse_args()
    data = json.loads(Path(args.social_context).read_text())
    note = {
      'agent':'sentiment_analyst',
      'sentiment_state': data.get('sentiment_summary', 'unknown'),
      'crowding_risk': data.get('crowding_risk', 'unknown'),
      'attention_level': data.get('attention_level', 'unknown'),
      'confidence':'low'
    }
    Path(args.out).write_text(json.dumps(note, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
