#!/usr/bin/env python3
"""
Analyze holding fund trends based on real-time hot news.
"""

import akshare as ak
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Holdings definition
HOLDINGS = {
    "Gold": {
        "name": "黄金 (华安ETF联接)",
        "keywords": ["黄金", "金价", "美联储", "美元", "降息", "通胀", "避险", "地缘", "央行"],
        "sentiment_rules": {
            "pos": ["降息", "避险", "通胀", "央行买入", "地缘冲突", "美元走弱"],
            "neg": ["加息", "美元走强", "实际利率上升", "抛售", "流动性危机"]
        }
    },
    "Oil": {
        "name": "石油 (鹏华油气)",
        "keywords": ["原油", "石油", "油价", "OPEC", "减产", "库存", "中东", "页岩油"],
        "sentiment_rules": {
            "pos": ["减产", "需求旺盛", "库存下降", "冲突", "供应中断"],
            "neg": ["增产", "需求疲软", "库存增加", "页岩油增产", "经济衰退"]
        }
    },
    "Internet": {
        "name": "中美互联网 (天弘QDII)",
        "keywords": ["互联网", "中概", "纳斯达克", "科技", "AI", "腾讯", "阿里", "监管", "财报"],
        "sentiment_rules": {
            "pos": ["财报超预期", "AI突破", "政策利好", "降息", "回购"],
            "neg": ["制裁", "监管", "不及预期", "加息", "反垄断"]
        }
    },
    "Resources": {
        "name": "资源精选 (路博迈)",
        "keywords": ["有色", "铜", "锂", "矿业", "大宗商品", "周期", "资源", "新能源"],
        "sentiment_rules": {
            "pos": ["价格上涨", "需求复苏", "限产", "新能源"],
            "neg": ["价格下跌", "需求疲软", "产能过剩", "替代"]
        }
    }
}

def get_market_news():
    """Fetch financial news via akshare (using broad market symbols)"""
    texts = []
    # Fetching news for key market leaders to get broad sentiment
    symbols = ["000001", "600519", "000858"] # Ping An, Moutai, Wuliangye -> broad market news
    for sym in symbols:
        try:
            df = ak.stock_news_em(symbol=sym)
            if df is not None and not df.empty:
                col = "新闻内容" if "新闻内容" in df.columns else (
                    "content" if "content" in df.columns else (df.columns[3] if len(df.columns) > 3 else None)
                )
                if col and col in df.columns:
                    texts.extend(df[col].astype(str).tolist())
        except Exception:
            continue
    return pd.DataFrame({"text": texts})

def analyze_news(df):
    """Analyze news against holdings"""
    results = {}
    
    if df.empty:
        return {k: {**v, "news_count": 0, "trend": "N/A", "summary": "新闻获取失败"} for k, v in HOLDINGS.items()}

    texts = df["text"].tolist()
        
    for key, info in HOLDINGS.items():
        related_news = []
        pos_count = 0
        neg_count = 0
        
        for text in texts:
            if any(kw in text for kw in info["keywords"]):
                clean_text = text.replace("\n", " ").strip()
                related_news.append(clean_text[:80] + "..." if len(clean_text) > 80 else clean_text)
                
                for p in info["sentiment_rules"]["pos"]:
                    if p in text: pos_count += 1
                for n in info["sentiment_rules"]["neg"]:
                    if n in text: neg_count += 1
                    
        total = pos_count + neg_count
        if total == 0:
            trend = "震荡 🟡 (无明显信号)"
        elif pos_count > neg_count:
            trend = "看涨 🟢" if pos_count > neg_count * 1.5 else "偏多 🟢"
        else:
            trend = "看跌 🔴" if neg_count > pos_count * 1.5 else "偏空 🔴"
            
        results[key] = {
            "name": info["name"],
            "trend": trend,
            "summary": f"相关新闻 {len(related_news)} 条 | 利好 {pos_count} | 利空 {neg_count}",
            "news_samples": list(set(related_news))[:3]
        }
        
    return results

def main():
    print("📡 正在获取财经热点...")
    df = get_market_news()
    
    if df.empty:
        print("⚠️ 无法获取新闻数据。")
        return

    results = analyze_news(df)
    
    print(f"\n📈 持仓基金热点新闻趋势分析 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print("=" * 60)
    
    for key, res in results.items():
        print(f"\n🔹 {res['name']}")
        print(f"   📊 趋势预测: {res['trend']}")
        print(f"   📝 信号统计: {res['summary']}")
        if res.get("news_samples"):
            print("   🔥 相关热点:")
            for n in res["news_samples"]:
                print(f"     - {n}")

    out_dir = Path.home() / "openclaw" / "workspace" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"news-trend-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    (out_dir / filename).write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n💾 报告已保存: {out_dir / filename}")

if __name__ == "__main__":
    main()
