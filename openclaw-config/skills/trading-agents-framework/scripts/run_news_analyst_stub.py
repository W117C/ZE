#!/usr/bin/env python3
import argparse, json, collections
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('news_context'); p.add_argument('--out', default='./news_note.json'); args = p.parse_args()
    data = json.loads(Path(args.news_context).read_text())
    events = data.get('classified_events', [])
    counter = collections.Counter()
    for item in events:
        counter.update(item.get('event_tags', []))
    top_tags = [k for k,_ in counter.most_common(5)]
    narrative = [x.get('title','') for x in events[:4]]
    impact = 'company_specific' if events else 'macro_only' if data.get('market_news') else 'unknown'
    timing = 'medium_to_high' if any(t in top_tags for t in ['财报','并购','风险','订单']) else 'low_to_medium'
    note = {'agent':'news_analyst','event_impact':impact,'timing_risk':timing,'top_event_tags':top_tags,'narrative_summary':narrative,'company_event_count':len(events),'confidence':'medium' if events else 'low'}
    Path(args.out).write_text(json.dumps(note, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
