#!/usr/bin/env python3
import argparse, json, subprocess, datetime as dt
from pathlib import Path
import akshare as ak
import pandas as pd

BASE = Path.home()/'.openclaw'/'skills'/'finance-data'/'tools'
WATCHLIST_FILE = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'assets.user-watchlist.json'


def run_json(cmd):
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def get_history(symbol, days=250):
    return run_json(['python3', str(BASE/'history_price.py'), symbol, str(days)])


def get_news(limit=5):
    return run_json(['python3', str(BASE/'market_news.py'), '--limit', str(limit)])


def load_watchlist():
    if WATCHLIST_FILE.exists():
        try:
            return json.loads(WATCHLIST_FILE.read_text())['watchlist']
        except Exception:
            return []
    return []


def safe_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def fetch_index_universe(index_symbol):
    try:
        df = ak.index_stock_cons_csindex(symbol=index_symbol)
        code_col = safe_col(df, ['成分券代码','证券代码','股票代码'])
        name_col = safe_col(df, ['成分券名称','证券简称','股票简称'])
        if not code_col:
            return []
        rows = []
        for _, row in df.iterrows():
            rows.append({'symbol': str(row[code_col]).zfill(6), 'name': str(row[name_col]) if name_col else ''})
        return rows
    except Exception:
        return []


def fetch_all_spot_meta():
    try:
        df = ak.stock_zh_a_spot_em()
        return df
    except Exception:
        return pd.DataFrame()


def build_universe():
    hs300 = fetch_index_universe('000300')
    zz500 = fetch_index_universe('000905')
    watch = [{'symbol': s, 'name': ''} for s in load_watchlist()]
    merged = {}
    for item in hs300 + zz500 + watch:
        merged[item['symbol']] = item
    return list(merged.values())


def filter_universe(universe):
    meta = fetch_all_spot_meta()
    if meta.empty:
        return universe
    code_col = safe_col(meta, ['代码'])
    name_col = safe_col(meta, ['名称'])
    if not code_col:
        return universe
    meta[code_col] = meta[code_col].astype(str).str.zfill(6)
    meta_map = {row[code_col]: row for _, row in meta.iterrows()}
    filtered = []
    cutoff = dt.datetime.now() - dt.timedelta(days=60)
    list_date_col = safe_col(meta, ['上市时间','上市日期'])
    for item in universe:
        symbol = item['symbol']
        row = meta_map.get(symbol)
        if row is None:
            filtered.append(item)
            continue
        name = str(row.get(name_col, item.get('name',''))) if name_col else item.get('name','')
        if 'ST' in name.upper():
            continue
        if symbol.startswith(('8','4')):
            continue
        if list_date_col and pd.notna(row.get(list_date_col)):
            try:
                d = pd.to_datetime(str(int(row[list_date_col])) if str(row[list_date_col]).isdigit() else row[list_date_col])
                if d.to_pydatetime() > cutoff:
                    continue
            except Exception:
                pass
        item['name'] = name
        filtered.append(item)
    return filtered


def score_symbol(symbol, name=''):
    hist = get_history(symbol, 250)
    stats = hist.get('statistics', {})
    latest = hist.get('latest_data', {})
    price = latest.get('close', 0)
    change_pct = stats.get('price_change_pct', 0)
    vol = stats.get('volatility', 0)
    avg_vol = stats.get('avg_volume', 0)
    trend = max(0, min(100, 50 + change_pct))
    risk = max(0, min(100, 100 - vol * 10))
    liquidity = max(20, min(100, 40 + (10 if avg_vol > 0 else 0)))
    total = round(trend * 0.45 + risk * 0.25 + liquidity * 0.30, 2)
    return {
        'symbol': symbol,
        'name': name,
        'price': price,
        'trend_score': round(trend,2),
        'risk_score': round(risk,2),
        'liquidity_score': round(liquidity,2),
        'total_score': total,
        'price_change_pct': round(change_pct,2),
        'volatility': round(vol,2),
        'avg_volume': avg_vol,
    }


def build_report(rows, news, scanned, filtered):
    lines = ['A股真实行情模拟交易日报','', '一、结论',f'- 股票池来源：沪深300 + 中证500 + 自选池。',f'- 扫描 {scanned} 只，过滤后 {filtered} 只，以下展示前10名。','- 本结果仅用于模拟研究，不构成投资建议。','', '二、候选股票']
    for i, r in enumerate(rows[:10], 1):
        nm = r['name'] or r['symbol']
        lines.append(f"- {i}. {nm}({r['symbol']}) | 总分 {r['total_score']} | 近1年涨跌 {r['price_change_pct']}% | 波动 {r['volatility']} | 现价 {r['price']}")
    lines += ['', '三、市场新闻']
    for item in news.get('data', {}).get('news', [])[:5]:
        lines.append(f"- {item.get('tag','')} {item.get('title','')[:80]}")
    lines += ['', '四、风险提示', '- 已排除 ST / 北交所 / 上市未满60天标的。', '- 当前版本仍为简化评分模型，未计入完整交易成本与调仓冲击。']
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbols', nargs='*', default=None)
    p.add_argument('--top', type=int, default=10)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    if args.symbols:
        universe = [{'symbol': s, 'name': ''} for s in args.symbols]
    else:
        universe = build_universe()
        scanned = len(universe)
        universe = filter_universe(universe)
    scanned = len(args.symbols) if args.symbols else scanned
    rows = []
    for item in universe[:80]:
        try:
            rows.append(score_symbol(item['symbol'], item.get('name','')))
        except Exception:
            continue
    rows.sort(key=lambda x: x['total_score'], reverse=True)
    news = get_news(5)
    if args.json:
        print(json.dumps({'mode':'paper-trading','market':'A-share','frequency':'daily','scanned':scanned,'filtered':len(universe),'candidates':rows[:args.top],'news':news.get('data',{}).get('news',[])[:5]}, ensure_ascii=False, indent=2))
    else:
        print(build_report(rows[:args.top], news, scanned, len(universe)))

if __name__ == '__main__':
    main()
