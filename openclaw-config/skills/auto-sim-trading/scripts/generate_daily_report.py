#!/usr/bin/env python3
"""
Daily Report Generator: Generates end-of-day summary report with trades, problems, and improvements.

Usage:
  python3 generate_daily_report.py --out /tmp/daily-report.json
  python3 generate_daily_report.py --out /tmp/daily-report.json --send
"""
import argparse, json, subprocess, time
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/'data'
TRADE_LOG = DATA_DIR/'trade_log.json'
PROBLEMS_LOG = DATA_DIR/'problems_log.json'
PORTFOLIO = DATA_DIR/'portfolio.json'

def load_json(path, default=None):
    if path.exists():
        return json.loads(path.read_text())
    return default if default else []

def get_todays_trades():
    log = load_json(TRADE_LOG)
    today = time.strftime('%Y-%m-%d')
    return [t for t in log if t.get('date') == today]

def get_todays_problems():
    log = load_json(PROBLEMS_LOG)
    today = time.strftime('%Y-%m-%d')
    return [p for p in log if p.get('date') == today]

def get_current_portfolio():
    return load_json(PORTFOLIO, {'positions': []})

def generate_market_context():
    """获取今日市场概况（优先使用缓存，超时则fallback）"""
    # Try to use today's report cache first
    cached = Path.home()/'.openclaw'/'skills'/'auto-sim-trading'/f'daily-report-{time.strftime("%Y-%m-%d")}.json'
    if cached.exists():
        try:
            data = json.loads(cached.read_text())
            if 'candidates' in data:
                return {'candidates': data['candidates'], 'news': data.get('news', [])}
        except:
            pass
    
    # Fallback to running the scan
    try:
        result = subprocess.check_output(
            ['python3', str(SCRIPT_DIR/'run_real_sim.py'), '--json', '--top', '5'],
            text=True, timeout=120
        )
        return json.loads(result)
    except Exception as e:
        return {'error': str(e)}

def generate_improvements(trades, problems, market):
    """基于今日数据生成改进建议"""
    suggestions = []

    # 基于交易记录
    if not trades:
        suggestions.append("今日无操作记录，建议检查评分系统是否正常运行")

    # 基于问题记录
    data_problems = [p for p in problems if p.get('category') == 'data']
    if data_problems:
        suggestions.append(f"今日发现 {len(data_problems)} 个数据问题，建议检查数据源稳定性")

    model_problems = [p for p in problems if p.get('category') == 'model']
    if model_problems:
        suggestions.append(f"今日发现 {len(model_problems)} 个模型问题，建议审视评分逻辑")

    # 基于市场
    if 'error' not in market:
        candidates = market.get('candidates', [])
        if candidates:
            top_score = candidates[0].get('total_score', 0) if candidates else 0
            if top_score < 60:
                suggestions.append("今日最高评分偏低，市场整体偏弱，建议降低仓位预期")
            elif top_score > 85:
                suggestions.append("今日最高评分偏高，注意不要过度集中单一标的")

    # 通用建议
    suggestions.append("建议每日检查情绪数据源是否正常获取")
    suggestions.append("建议定期审视因子权重是否需要调整")

    return suggestions

def get_current_account():
    """获取当前账户状态"""
    account_path = DATA_DIR/'account.json'
    if account_path.exists():
        return json.loads(account_path.read_text())
    return None

def run_trade_decisions(market):
    """在生成报告前，先执行交易决策"""
    candidates = market.get('candidates', [])
    if not candidates:
        return []
    
    # 保存候选股到临时文件供 trade_decision 使用
    tmp_file = Path('/tmp/sim_candidates.json')
    tmp_file.write_text(json.dumps({'candidates': candidates}, ensure_ascii=False, indent=2))
    
    try:
        result = subprocess.check_output(
            ['python3', str(SCRIPT_DIR/'trade_decision.py'), '--candidates-file', str(tmp_file)],
            text=True, timeout=60
        )
        print(f"[交易决策] {result.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"[交易决策] 执行异常: {e}")
    except subprocess.TimeoutExpired:
        print("[交易决策] 超时")
    
    # 重新加载今日交易（trade_decision 可能已写入新交易）
    return get_todays_trades()

def generate_report():
    """生成完整日报"""
    market = generate_market_context()
    
    # 先执行交易决策（这会自动记录交易到 trade_log）
    trades = run_trade_decisions(market)
    
    problems = get_todays_problems()
    portfolio = get_current_portfolio()
    account = get_current_account()
    improvements = generate_improvements(trades, problems, market)

    report = {
        'date': time.strftime('%Y-%m-%d'),
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'account': account,
        'today_trades': trades,
        'today_problems': problems,
        'portfolio': portfolio,
        'market_summary': market if 'error' not in market else None,
        'improvements': improvements,
        'summary': {
            'trade_count': len(trades),
            'problem_count': len(problems),
            'position_count': len(portfolio.get('positions', [])),
            'total_value': account.get('total_value', 0) if account else 0,
            'return_pct': account.get('total_return_pct', 0) if account else 0
        },
        'candidates': market.get('candidates', []) if 'error' not in market else []
    }

    return report

def format_text_report(report):
    """格式化为文本报告"""
    lines = []
    lines.append(f"📊 自动模拟炒股日报 — {report['date']}")
    lines.append("")

    # 账户概览
    account = report.get('account')
    if account:
        lines.append("═══ 账户概览 ═══")
        lines.append(f"  初始资金: ¥{account.get('initial_capital', 0):,.2f}")
        lines.append(f"  总资产: ¥{account.get('total_value', 0):,.2f}")
        lines.append(f"  持仓市值: ¥{account.get('market_value', 0):,.2f}")
        lines.append(f"  可用现金: ¥{account.get('cash', 0):,.2f}")
        total = account.get('total_value', 1)
        mkt = account.get('market_value', 0)
        lines.append(f"  仓位比例: {mkt/total*100:.1f}%" if total > 0 else "  仓位比例: 0%")
        lines.append(f"  总收益率: {account.get('total_return_pct', 0)}%")
        lines.append(f"  最大回撤: {account.get('max_drawdown_pct', 0)}%")
        lines.append("")

    # 今日操作
    lines.append("═══ 今日操作 ═══")
    trades = report.get('today_trades', [])
    if not trades:
        lines.append("  今日无操作")
    else:
        for t in trades:
            lines.append(f"  [{t['action'].upper()}] {t['symbol']} {'@'+str(t['price']) if t.get('price') else ''} | {t.get('reason', '')}")
    lines.append("")

    # 今日问题
    lines.append("═══ 今日问题 ═══")
    problems = report.get('today_problems', [])
    if not problems:
        lines.append("  今日无问题")
    else:
        for p in problems:
            lines.append(f"  [{p['category']}] {p['description']}")
            if p.get('suggestion'):
                lines.append(f"    建议: {p['suggestion']}")
    lines.append("")

    # 当前持仓
    lines.append("═══ 当前持仓 ═══")
    positions = report.get('portfolio', {}).get('positions', [])
    if not positions:
        lines.append("  无持仓")
    else:
        for p in positions:
            lines.append(f"  {p['symbol']}: 数量 {p.get('quantity', 0)}, 均价 {p.get('avg_price', 0)}")
    lines.append("")

    # 改进建议
    lines.append("═══ 需要改进的地方 ═══")
    for i, imp in enumerate(report.get('improvements', []), 1):
        lines.append(f"  {i}. {imp}")
    lines.append("")

    # 候选股 Top 5
    candidates = report.get('candidates', [])
    if candidates:
        lines.append("═══ 候选股 Top 5 ═══")
        for i, c in enumerate(candidates[:5], 1):
            lines.append(f"  {i}. {c.get('name','')}({c['symbol']}) | 总分 {c['total_score']} | 趋势 {c['trend_score']} | 风险 {c['risk_score']} | 现价 ¥{c['price']}")
        lines.append("")

    # 统计
    s = report.get('summary', {})
    lines.append(f"📈 今日统计: {s.get('trade_count', 0)} 笔操作 | {s.get('problem_count', 0)} 个问题 | {s.get('position_count', 0)} 只持仓")
    lines.append("")
    lines.append("⚠️ 免责声明：本系统仅用于模拟研究，不构成投资建议。市场有风险，投资需谨慎。")

    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--send', action='store_true', help='输出到 stdout 以便发送')
    p.add_argument('--reflect', action='store_true', help='运行反思分析')
    args = p.parse_args()

    report = generate_report()

    # 保存 JSON
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"[OK] 日报已保存到 {args.out}")

    # 输出文本
    if args.send:
        text = format_text_report(report)
        print("\n" + text)

    # 运行反思
    if args.reflect:
        print("\n=== 开始反思分析 ===")
        try:
            import subprocess
            script_dir = Path(__file__).resolve().parent
            subprocess.run(['python3', str(script_dir/'self_reflection.py'), '--auto-upgrade'], check=True)
        except Exception as e:
            print(f"[反思] 执行失败: {e}")

if __name__ == '__main__':
    main()
