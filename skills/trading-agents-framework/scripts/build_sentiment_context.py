#!/usr/bin/env python3
"""
A-Share Market Sentiment via Eastmoney (东方财富股吧) — Free, real-time.

Provides:
- Attention index (关注指数)
- Composite score (综合得分)
- Institutional participation (机构参与度)
- Rank change momentum (上升/排名变化)
- Market-wide sentiment summary
- Hot stocks by attention

Usage:
  python3 build_sentiment_context.py --symbol 600519 --out ./social_context.json
  python3 build_sentiment_context.py --market-overview --out ./market_sentiment.json
"""
import argparse, json, re, collections, time, sqlite3
from pathlib import Path

CACHE_DB = Path.home()/'.openclaw'/'skills'/'trading-agents-framework'/'assets.sentiment_cache.sqlite3'
TTL_SECONDS = 3600

SENTIMENT_LEXICON = {
    'bullish': ['涨', '买', '多', '好', '强', '突破', '利好', '加仓', '看多', '牛市', '反弹', '新高', '龙头'],
    'bearish': ['跌', '卖', '空', '差', '弱', '破位', '利空', '减仓', '看空', '熊市', '回调', '新低', '套牢']
}


def init_db():
    CACHE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB)
    conn.execute('CREATE TABLE IF NOT EXISTS sentiment_cache (key TEXT PRIMARY KEY, fetched_at INTEGER, payload TEXT)')
    conn.commit()
    return conn


def get_cached(conn, key):
    row = conn.execute('SELECT fetched_at, payload FROM sentiment_cache WHERE key=?', (key,)).fetchone()
    if not row: return None
    if int(time.time()) - row[0] > TTL_SECONDS: return None
    return json.loads(row[1])


def set_cached(conn, key, payload):
    conn.execute('REPLACE INTO sentiment_cache(key, fetched_at, payload) VALUES (?, ?, ?)',
                 (key, int(time.time()), json.dumps(payload, ensure_ascii=False)))
    conn.commit()


def fetch_eastmoney_comments():
    """获取全市场股吧评论/关注数据"""
    import akshare as ak
    df = ak.stock_comment_em()
    return df


def fetch_hot_rank():
    """获取热门股票排行"""
    import akshare as ak
    df = ak.stock_hot_rank_em()
    return df


def score_sentiment_from_name(name):
    """从股票名称中检测情绪词（简化）"""
    tokens = re.findall(r'[\u4e00-\u9fa5]', name)
    pos = sum(1 for t in tokens if t in SENTIMENT_LEXICON['bullish'])
    neg = sum(1 for t in tokens if t in SENTIMENT_LEXICON['bearish'])
    return pos - neg


def analyze_single_symbol(symbol, df):
    """分析单个股票的情绪数据"""
    if df is None or df.empty:
        return None
    code_col = None
    for c in df.columns:
        if '代码' in c:
            code_col = c
            break
    if not code_col: return None

    symbol_clean = symbol.zfill(6)
    row = df[df[code_col].astype(str).str.zfill(6) == symbol_clean]
    if row.empty:
        return None
    r = row.iloc[0]

    attention = None
    composite = None
    inst = None
    rank_change = None
    rank = None
    for c in df.columns:
        if '关注' in c: attention = r.get(c)
        elif '综合得分' in c: composite = r.get(c)
        elif '机构参与' in c: inst = r.get(c)
        elif '上升' in c: rank_change = r.get(c)
        elif '目前排名' in c: rank = r.get(c)

    # Sentiment classification
    if composite is not None:
        if composite > 70: sentiment = 'strong_bullish'
        elif composite > 55: sentiment = 'slightly_bullish'
        elif composite > 45: sentiment = 'neutral'
        elif composite > 35: sentiment = 'slightly_bearish'
        else: sentiment = 'strong_bearish'
    else:
        sentiment = 'unknown'

    return {
        'symbol': symbol,
        'name': r.get('名称', ''),
        'attention_index': float(attention) if attention is not None else None,
        'composite_score': float(composite) if composite is not None else None,
        'institutional_participation': float(inst) if inst is not None else None,
        'rank': int(rank) if rank is not None else None,
        'rank_change': int(rank_change) if rank_change is not None else None,
        'sentiment_summary': sentiment,
        'price_change_pct': float(r.get('涨跌幅', 0)) if r.get('涨跌幅') is not None else 0,
        'turnover_rate': float(r.get('换手率', 0)) if r.get('换手率') is not None else 0
    }


def analyze_market_overview(df, top_n=10):
    """全市场情绪概览"""
    if df is None or df.empty:
        return None

    composite_col = None
    for c in df.columns:
        if '综合得分' in c:
            composite_col = c
            break

    if composite_col:
        scores = df[composite_col].astype(float).dropna()
        avg_score = round(scores.mean(), 1)
        high_count = int((scores > 70).sum())
        low_count = int((scores < 35).sum())
        total = len(scores)
        bullish_pct = round(high_count / total * 100, 1) if total > 0 else 0
    else:
        avg_score = None
        high_count = 0
        low_count = 0
        bullish_pct = None

    # Top N by attention
    attention_col = None
    for c in df.columns:
        if '关注' in c:
            attention_col = c
            break

    hot_stocks = []
    if attention_col:
        top = df.nlargest(top_n, attention_col)
        name_col = next((c for c in df.columns if '名称' in c), None)
        code_col = next((c for c in df.columns if '代码' in c), None)
        for _, r in top.iterrows():
            hot_stocks.append({
                'symbol': str(r.get(code_col, '')).zfill(6),
                'name': r.get(name_col, ''),
                'attention': float(r.get(attention_col, 0))
            })

    return {
        'avg_composite_score': avg_score,
        'bullish_pct': bullish_pct,
        'high_sentiment_count': high_count,
        'low_sentiment_count': low_count,
        'total_stocks': total if composite_col else 0,
        'market_sentiment': 'bullish' if bullish_pct and bullish_pct > 20 else 'neutral' if bullish_pct and bullish_pct > 10 else 'bearish',
        'hot_stocks': hot_stocks
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbol')
    p.add_argument('--market-overview', action='store_true')
    p.add_argument('--provider', default='eastmoney')
    p.add_argument('--out', default='./social_context.json')
    args = p.parse_args()

    conn = init_db()
    import akshare as ak

    try:
        if args.market_overview:
            cache_key = 'market_overview'
            cached = get_cached(conn, cache_key)
            if cached:
                out = {**cached, 'provider_status': {'ready': True, 'note': 'eastmoney 股吧数据 (cached)', 'cache': 'hit'}}
            else:
                df = fetch_eastmoney_comments()
                overview = analyze_market_overview(df)
                out = {'provider': 'eastmoney', 'provider_status': {'ready': True, 'note': 'eastmoney 股吧数据', 'cache': 'miss'}, **overview}
                set_cached(conn, cache_key, out)
        elif args.symbol:
            cache_key = f'symbol_{args.symbol}'
            cached = get_cached(conn, cache_key)
            if cached:
                out = {**cached, 'provider_status': {'ready': True, 'note': 'eastmoney 股吧数据 (cached)', 'cache': 'hit'}}
            else:
                df = fetch_eastmoney_comments()
                result = analyze_single_symbol(args.symbol, df)
                if result:
                    out = {'provider': 'eastmoney', 'provider_status': {'ready': True, 'note': 'eastmoney 股吧数据', 'cache': 'miss'}, **result}
                    set_cached(conn, cache_key, out)
                else:
                    out = {'symbol': args.symbol, 'provider': 'eastmoney', 'provider_status': {'ready': False, 'note': 'symbol not found in comment data'}, 'sentiment_summary': 'unknown'}
        else:
            out = {'error': 'specify --symbol or --market-overview'}

    except Exception as e:
        out = {'error': str(e), 'provider': 'eastmoney', 'provider_status': {'ready': False, 'note': f'fetch failed: {e}'}}

    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(args.out)


if __name__ == '__main__':
    main()
