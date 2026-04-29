#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def get_note(notes, agent):
    for n in notes:
        if n.get('agent') == agent:
            return n
    return {}

def main():
    p = argparse.ArgumentParser(); p.add_argument('analyst_bundle'); p.add_argument('--out-dir', default='./debate'); args = p.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    bundle = json.loads(Path(args.analyst_bundle).read_text())
    notes = bundle.get('notes', [])
    tech = get_note(notes, 'technical_analyst')
    funda = get_note(notes, 'fundamentals_analyst')
    news = get_note(notes, 'news_analyst')
    sentiment = get_note(notes, 'sentiment_analyst')

    round1 = {
      'bull_opening': ['技术面支持' if tech.get('trend') == 'positive' else '技术面一般', f"基本面观点: {funda.get('thesis','unknown')}", '新闻面存在潜在催化' if news.get('confidence') in ['medium','high'] else '新闻催化不足'],
      'bear_opening': ['估值或回撤风险仍在', '情绪过热可能带来拥挤风险' if sentiment.get('attention_level') == 'high' else '情绪信号有限']
    }
    round2 = {
      'bull_rebuttal': ['若盈利和收入趋势继续改善，可支持继续观察或试探仓位'] if funda.get('score',0) >= 1 else ['基本面改善证据仍不足'],
      'bear_rebuttal': ['若市场新闻偏噪声，短期方向不稳', '若无新增催化则不宜激进']
    }
    final = {
      'buy_evidence': round1['bull_opening'] + round2['bull_rebuttal'],
      'sell_evidence': round1['bear_opening'] + round2['bear_rebuttal'],
      'unresolved': ['需要更多公司级新闻/社交源验证','需要后续财报更新确认趋势'],
      'rounds': [round1, round2]
    }
    (out/'bull_case.json').write_text(json.dumps({'agent':'bull_researcher','rounds':[round1, round2],'confidence':'medium'}, ensure_ascii=False, indent=2))
    (out/'bear_case.json').write_text(json.dumps({'agent':'bear_researcher','rounds':[round1, round2],'confidence':'medium'}, ensure_ascii=False, indent=2))
    (out/'debate_summary.json').write_text(json.dumps(final, ensure_ascii=False, indent=2))
    print(out)

if __name__ == '__main__':
    main()
