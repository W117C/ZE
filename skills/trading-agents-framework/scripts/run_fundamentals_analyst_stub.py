#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def trend_label(v):
    if v is None: return 'unknown'
    if v > 15: return 'strong_up'
    if v > 0: return 'up'
    if v > -10: return 'flat_to_down'
    return 'down'

def score_metric(val, good_if='high'):
    if val is None: return 0
    if good_if == 'low': return 1 if val < 60 else -1
    return 1 if val > 0 else -1

def main():
    p = argparse.ArgumentParser(); p.add_argument('fundamentals_context'); p.add_argument('--out', default='./fundamentals_note.json'); args = p.parse_args()
    data = json.loads(Path(args.fundamentals_context).read_text())
    prof = data.get('profitability', {}); growth = data.get('growth', {}); lev = data.get('leverage', {}); quality = data.get('quality', {})
    score = 0
    score += score_metric(prof.get('roe'))
    score += score_metric(growth.get('revenue_yoy'))
    score += score_metric(growth.get('net_profit_yoy'))
    score += score_metric(lev.get('debt_ratio'), good_if='low')
    score += score_metric(quality.get('ocf_to_sales'))
    trends = {
      'revenue_trend': trend_label(growth.get('revenue_yoy')),
      'profit_trend': trend_label(growth.get('net_profit_yoy')),
      'roe_trend_proxy': trend_label(prof.get('roe')),
      'debt_trend_proxy': trend_label(-lev.get('debt_ratio') if lev.get('debt_ratio') is not None else None)
    }
    thesis = '基本面趋势偏正面' if score >= 2 else '基本面趋势中性' if score >= 0 else '基本面趋势偏弱'
    note = {'agent':'fundamentals_analyst','thesis': thesis,'valuation': data.get('valuation', {}),'profitability': prof,'growth': growth,'leverage': lev,'quality': quality,'trend_analysis': trends,'red_flags': data.get('notes', []),'confidence':'medium' if score != 0 else 'low_to_medium','score': score}
    Path(args.out).write_text(json.dumps(note, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
