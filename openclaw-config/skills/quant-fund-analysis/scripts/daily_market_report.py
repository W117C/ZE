#!/usr/bin/env python3
"""
Daily Fund Market Analysis Report.
Fetches NAV data for user's holdings and generates a Quant Fund OS report.
"""

import akshare as ak
import json
import time
from pathlib import Path
from datetime import datetime

USER_FUNDS = [
    {"code": "000216", "name": "华安黄金ETF联接A", "weight": 26.80, "type": "黄金/避险"},
    {"code": "000217", "name": "华安黄金ETF联接C", "weight": 0.05, "type": "黄金/避险"},
    {"code": "006143", "name": "鹏华石油天然气ETF联接C", "weight": 12.29, "type": "能源/商品"},
    {"code": "017312", "name": "天弘中美互联网指数(QDII)A", "weight": 9.99, "type": "科技/QDII"},
    {"code": "019559", "name": "路博迈资源精选股票C", "weight": 7.26, "type": "资源/周期"},
    {"code": "000198", "name": "余额宝", "weight": 43.61, "type": "现金/货基"},
]

def fetch_fund_nav(code):
    """获取基金最新净值"""
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            nav = float(latest["单位净值"])
            prev_nav = float(prev["单位净值"])
            chg = round((nav - prev_nav) / prev_nav * 100, 4) if prev_nav > 0 else 0
            return {
                "nav": nav,
                "prev_nav": prev_nav,
                "change_pct": chg,
                "date": str(latest["净值日期"])
            }
    except Exception as e:
        return {"error": str(e)}
    return None

def fetch_market_indices():
    """获取主要市场指数"""
    indices = {
        "sh000300": "沪深300",
        "sz399006": "创业板指",
        "sh000905": "中证500"
    }
    results = {}
    for sym, name in indices.items():
        try:
            df = ak.stock_zh_index_daily_em(symbol=sym)
            if df is not None and len(df) > 0:
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                c = float(latest["close"])
                p = float(prev["close"])
                results[name] = {
                    "value": c,
                    "change_pct": round((c - p) / p * 100, 2)
                }
        except:
            results[name] = {"value": "N/A", "change_pct": "N/A"}
    return results

def generate_report():
    report = {
        "title": "基金持仓市场分析报告",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "funds": [],
        "market": {},
        "portfolio_summary": {},
        "quant_analysis": {}
    }

    # 1. 获取持仓基金数据
    print("📊 获取持仓基金数据...")
    for fund in USER_FUNDS:
        data = fetch_fund_nav(fund["code"])
        fund_data = {**fund, "latest": data}
        report["funds"].append(fund_data)
        status = "✅" if data and "nav" in data else "❌"
        print(f"  {status} {fund['name']}: {data.get('nav', 'N/A')} ({data.get('change_pct', 'N/A')}%)")

    # 2. 获取市场指数
    print("📈 获取市场指数...")
    report["market"] = fetch_market_indices()
    for name, data in report["market"].items():
        print(f"  {name}: {data.get('value')} ({data.get('change_pct')}%)")

    # 3. 组合分析 (Quant Fund OS 逻辑)
    # 计算加权收益
    total_change = 0
    total_weight = 0
    for f in report["funds"]:
        w = f.get("weight", 0)
        chg = f.get("latest", {}).get("change_pct", 0)
        if w > 0 and chg:
            total_change += w * chg
            total_weight += w
    
    if total_weight > 0:
        weighted_return = round(total_change / total_weight, 4)
    else:
        weighted_return = 0

    report["portfolio_summary"] = {
        "weighted_return": weighted_return,
        "cash_ratio": 43.61,
        "commodity_ratio": 39.14,
        "equity_ratio": 16.75,
        "diversification_score": "C (过度集中商品与现金)"
    }

    # 4. 评分与评级
    # 简单逻辑：根据近期表现和当前配置给评级
    score = 6.5 # Base score
    notes = []
    
    if weighted_return < -0.1:
        score -= 0.5
        notes.append("今日组合加权收益为负")
    if report["portfolio_summary"]["cash_ratio"] > 30:
        score -= 0.5
        notes.append("现金比例过高，拖累长期收益")
    if report["portfolio_summary"]["commodity_ratio"] > 30:
        score -= 0.5
        notes.append("大宗商品集中度过高，波动风险大")
    
    report["quant_analysis"] = {
        "score": round(score, 1),
        "rating": "C" if score < 7 else "B",
        "notes": notes,
        "recommendation": "建议降低黄金与现金比例，增加宽基指数（沪深300）和红利资产。"
    }

    return report

def print_report(report):
    """打印格式化报告"""
    print(f"\n{'='*50}")
    print(f"  {report['title']}")
    print(f"  {report['date']}")
    print(f"{'='*50}")
    
    print(f"\n📊 组合概览:")
    print(f"  加权收益: {report['portfolio_summary']['weighted_return']:.4f}%")
    print(f"  现金占比: {report['portfolio_summary']['cash_ratio']}%")
    print(f"  商品占比: {report['portfolio_summary']['commodity_ratio']}%")
    
    print(f"\n🏆 评分与评级:")
    print(f"  综合得分: {report['quant_analysis']['score']}/10")
    print(f"  评级: {report['quant_analysis']['rating']}")
    for note in report['quant_analysis']['notes']:
        print(f"  ⚠️  {note}")
    print(f"  💡 建议: {report['quant_analysis']['recommendation']}")

def main():
    report = generate_report()
    print_report(report)
    
    # Save to file
    out_dir = Path.home() / "openclaw" / "workspace" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"daily-fund-report-{report['date']}.json"
    (out_dir / filename).write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n💾 报告已保存: {out_dir / filename}")

if __name__ == "__main__":
    main()
