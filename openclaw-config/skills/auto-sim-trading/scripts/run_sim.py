#!/usr/bin/env python3
import argparse
import json
from dataclasses import dataclass, asdict

@dataclass
class StockScore:
    symbol: str
    name: str
    trend_score: float
    risk_score: float
    liquidity_score: float
    total_score: float
    note: str


def mock_universe(limit: int):
    base = [
        ("600519", "贵州茅台", 82, 76, 90, "趋势稳定，波动可控"),
        ("300750", "宁德时代", 78, 68, 88, "弹性较强，波动偏高"),
        ("600036", "招商银行", 74, 80, 86, "稳健型权重标的"),
        ("601899", "紫金矿业", 76, 70, 92, "强趋势但受商品价格影响"),
        ("688981", "中芯国际", 73, 62, 84, "科技属性强，波动较高"),
    ]
    rows = []
    for symbol, name, t, r, l, note in base[:limit]:
        total = round(t * 0.45 + r * 0.25 + l * 0.30, 2)
        rows.append(StockScore(symbol, name, t, r, l, total, note))
    return rows


def build_report(scores, max_positions):
    top = scores[:max_positions]
    lines = []
    lines.append("A股日频模拟交易简报")
    lines.append("")
    lines.append("一、市场结论")
    lines.append("- 当前为模拟评分输出，仅用于研究与演练。")
    lines.append("- 优先保留趋势较稳、流动性较好的标的。")
    lines.append("")
    lines.append("二、候选标的")
    for i, s in enumerate(scores, 1):
        lines.append(f"- {i}. {s.name}({s.symbol}) | 总分 {s.total_score} | 趋势 {s.trend_score} | 风险 {s.risk_score} | 流动性 {s.liquidity_score} | {s.note}")
    lines.append("")
    lines.append("三、模拟持仓建议")
    for s in top:
        lines.append(f"- 保留观察/候选持仓：{s.name}({s.symbol})")
    lines.append("")
    lines.append("四、风险提示")
    lines.append("- 本结果不连接实盘，不自动下单。")
    lines.append("- 因子模型需要结合真实行情、回测和风控参数进一步校准。")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run A-share daily paper trading simulation")
    parser.add_argument("--limit", type=int, default=5, help="candidate universe size")
    parser.add_argument("--max-positions", type=int, default=3, help="max simulated positions")
    parser.add_argument("--json", action="store_true", help="output json instead of text")
    args = parser.parse_args()

    scores = mock_universe(args.limit)
    scores = sorted(scores, key=lambda x: x.total_score, reverse=True)

    if args.json:
        print(json.dumps({
            "mode": "paper-trading",
            "market": "A-share",
            "frequency": "daily",
            "max_positions": args.max_positions,
            "candidates": [asdict(x) for x in scores],
        }, ensure_ascii=False, indent=2))
    else:
        print(build_report(scores, args.max_positions))

if __name__ == "__main__":
    main()
