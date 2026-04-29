#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
BASE = Path.home()/'.openclaw'/'skills'/'finance-data'/'tools'
TAGS = Path.home()/'.openclaw'/'skills'/'trading-agents-framework'/'references'/'news-event-tags.json'
SEVERITY_MAP = {
  '风险': 5, '并购': 4, '财报': 4, '订单': 3, '高管变动': 3,
  '融资资本': 3, '分红': 2, '停复牌': 4, '澄清': 2, '产品经营': 3, '其他': 1
}

def run_json(cmd):
    return json.loads(subprocess.check_output(cmd, text=True))

def classify(title, tag_map):
    matches = []
    for label, keywords in tag_map.items():
        if any(k in title for k in keywords):
            matches.append(label)
    return matches or ['其他']

def score_severity(tags):
    score = max(SEVERITY_MAP.get(t, 1) for t in tags) if tags else 1
    level = '高' if score >= 4 else '中' if score >= 2 else '低'
    return score, level

def main():
    p = argparse.ArgumentParser(); p.add_argument('symbol'); p.add_argument('--provider', default='auto'); p.add_argument('--out', default='./news_context.json'); args = p.parse_args()
    tag_map = json.loads(TAGS.read_text())
    market_news = []; company_news = []; announcements = []; notes = []
    try:
        data = run_json(['python3', str(BASE/'market_news.py'), '--limit', '5'])
        market_news = data.get('data', {}).get('news', [])[:5]
    except Exception as e:
        notes.append(f'market news failed: {e}')
    try:
        data = run_json(['python3', str(BASE/'stock_news.py'), args.symbol, '8'])
        company_news = data.get('data', {}).get('news', [])[:8]
    except Exception as e:
        notes.append(f'company news failed: {e}')
    try:
        data = run_json(['python3', str(BASE/'stock_announcements.py'), args.symbol, '7', 'true'])
        announcements = data.get('announcements', [])[:8]
    except Exception as e:
        notes.append(f'announcements failed: {e}')
    normalized = []
    for item in company_news:
        title = item.get('title',''); tags = classify(title, tag_map); sev_score, sev_level = score_severity(tags)
        normalized.append({**item, 'event_tags': tags, 'severity_score': sev_score, 'severity_level': sev_level, 'source_type': 'company_news'})
    for item in announcements:
        title = item.get('title',''); tags = classify(title, tag_map); sev_score, sev_level = score_severity(tags)
        normalized.append({**item, 'event_tags': tags, 'severity_score': sev_score, 'severity_level': sev_level, 'source_type': 'announcement'})
    out = {'symbol': args.symbol, 'provider': args.provider, 'market_news': market_news, 'company_news': company_news, 'announcements': announcements, 'classified_events': normalized, 'news': normalized[:10], 'notes': notes}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
