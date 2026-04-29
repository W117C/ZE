#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
BASE = Path.home()/'.openclaw'/'skills'/'finance-data'/'tools'

def run_json(cmd):
    return json.loads(subprocess.check_output(cmd, text=True))

def main():
    p = argparse.ArgumentParser(); p.add_argument('symbol'); p.add_argument('--provider', default='auto'); p.add_argument('--out', default='./fundamentals_context.json'); args = p.parse_args()
    valuation = {'pe_ratio': None, 'pb_ratio': None, 'ps_ratio': None, 'market_cap': None}
    profitability = {'roe': None, 'roa': None, 'net_margin': None, 'gross_margin': None}
    growth = {'revenue_yoy': None, 'net_profit_yoy': None}
    leverage = {'debt_ratio': None, 'current_ratio': None}
    quality = {'ocf_to_sales': None, 'eps': None, 'bvps': None}
    notes = []
    try:
        data = run_json(['python3', str(BASE/'financial_report.py'), args.symbol])
        d = data.get('data', {})
        valuation.update({k: d.get(k) for k in ['pe_ratio','pb_ratio','ps_ratio','market_cap']})
        profitability.update({k: d.get(k) for k in ['roe','roa','net_margin','gross_margin']})
        growth.update({k: d.get(k) for k in ['revenue_yoy','net_profit_yoy']})
        leverage.update({k: d.get(k) for k in ['debt_ratio','current_ratio']})
        quality.update({k: d.get(k) for k in ['ocf_to_sales','eps','bvps']})
        notes.append('来自 financial_report 的财务与估值摘要')
    except Exception as e:
        notes.append(f'financial_report 获取失败: {e}')
    out = {'symbol': args.symbol, 'provider': args.provider, 'valuation': valuation, 'profitability': profitability, 'growth': growth, 'leverage': leverage, 'quality': quality, 'notes': notes}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
