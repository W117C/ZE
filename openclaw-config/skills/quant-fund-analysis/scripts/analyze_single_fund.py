#!/usr/bin/env python3
"""
Quant Fund OS: Single Fund Analysis with 10-point scoring, A/B/C rating, and complete decision output.

Usage:
  python3 analyze_single_fund.py --name "某CTA基金" --strategy CTA --annual-return 18 --max-dd 9 --vol 11 --sharpe 1.2 --calmar 2.0 --win-rate 55 --profit-loss-ratio 1.5 --aum 500 --fee 1.5
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_data import run_full_validation

# ========== Scoring Functions ==========

def score_return_quality(annual_return):
    """收益质量 (20%)"""
    if annual_return is None: return 5, "数据缺失"
    if annual_return >= 15: return 9.5, "优秀"
    if annual_return >= 10: return 7.5, "良好"
    if annual_return >= 5: return 5.5, "一般"
    return 3.0, "偏弱"

def score_drawdown_control(max_dd):
    """回撤控制 (20%)"""
    if max_dd is None: return 5, "数据缺失"
    if max_dd < 10: return 9.5, "优秀"
    if max_dd < 20: return 7.5, "良好"
    if max_dd < 30: return 5.5, "一般"
    return 3.0, "偏弱"

def score_stability(sharpe, calmar, win_rate):
    """稳定性 (20%)"""
    if sharpe is None and calmar is None: return 5, "数据缺失"
    score = 5
    if sharpe is not None:
        if sharpe >= 1.5: score += 2
        elif sharpe >= 1.0: score += 1
        elif sharpe < 0.5: score -= 1
    if calmar is not None:
        if calmar >= 2.0: score += 1.5
        elif calmar >= 1.0: score += 0.5
        elif calmar < 0.5: score -= 1
    if win_rate is not None:
        if win_rate >= 60: score += 1
        elif win_rate < 40: score -= 1
    return max(1, min(10, score)), "优秀" if score >= 8 else "良好" if score >= 6 else "一般"

def score_explainability(strategy, return_source):
    """可解释性 (15%)"""
    if return_source: return 9.0, "清晰"
    if strategy in ['CTA', '市场中性', '套利']: return 8.5, "较清晰"
    if strategy in ['股票多空', '指数增强']: return 7.5, "部分清晰"
    if strategy in ['高频', '期权']: return 7.0, "部分黑箱"
    return 6.0, "需更多信息"

def score_capacity(aum):
    """容量 (10%)"""
    if aum is None: return 5, "数据缺失"
    if aum >= 1000: return 9.0, "大"
    if aum >= 500: return 8.0, "较大"
    if aum >= 100: return 7.0, "中等"
    if aum >= 50: return 6.0, "较小"
    return 4.0, "小"

def score_manager(track_record_years, team_size=None):
    """管理人 (10%)"""
    if track_record_years is None: return 5, "数据缺失"
    if track_record_years >= 5: return 9.0, "优秀"
    if track_record_years >= 3: return 7.5, "良好"
    if track_record_years >= 1: return 6.0, "一般"
    return 4.0, "偏短"

def score_fee(fee):
    """费用 (5%)"""
    if fee is None: return 5, "数据缺失"
    if fee <= 1.0: return 9.0, "低"
    if fee <= 1.5: return 7.5, "中等"
    if fee <= 2.0: return 6.0, "偏高"
    return 4.0, "高"

# ========== Main Analysis ==========

STRATEGY_TYPES = {
    'CTA': '趋势跟踪',
    'market-neutral': '市场中性',
    'long-short': '股票多空',
    'index-enhance': '指数增强',
    'high-frequency': '高频',
    'options': '期权/波动率',
    'multi-asset': '多资产',
    'arbitrage': '套利'
}

RETURN_SOURCES = {
    'CTA': ['趋势', '动量'],
    'market-neutral': ['Alpha', '套利'],
    'long-short': ['Beta', 'Alpha', '选股'],
    'index-enhance': ['Beta', 'Alpha', '增强'],
    'high-frequency': ['套利', '做市', '微观结构'],
    'options': ['波动率', '希腊字母', 'Carry'],
    'multi-asset': ['Beta', '配置', '轮动'],
    'arbitrage': ['套利', 'Carry']
}

RISK_TYPES = {
    'CTA': ['趋势反转', '震荡市失效', '参数过拟合'],
    'market-neutral': ['风格暴露漂移', '流动性冲击', '对冲成本'],
    'long-short': ['方向风险', '集中度', '流动性'],
    'index-enhance': ['跟踪误差', '风格偏离', '拥挤交易'],
    'high-frequency': ['技术风险', '延迟', '监管'],
    'options': ['尾部风险', '波动率跳跃', '流动性'],
    'multi-asset': ['相关性突变', '流动性错配', '再平衡风险'],
    'arbitrage': ['价差扩大', '流动性', '执行风险']
}

def analyze(name, strategy, annual_return=None, max_dd=None, vol=None, sharpe=None, calmar=None,
           win_rate=None, profit_loss_ratio=None, aum=None, fee=None,
           track_record_years=None, return_source=None):

    # 1. Score each dimension
    weights = {'return': 0.20, 'drawdown': 0.20, 'stability': 0.20, 'explain': 0.15, 'capacity': 0.10, 'manager': 0.10, 'fee': 0.05}

    rq_score, rq_note = score_return_quality(annual_return)
    dd_score, dd_note = score_drawdown_control(max_dd)
    st_score, st_note = score_stability(sharpe, calmar, win_rate)
    ex_score, ex_note = score_explainability(strategy, return_source)
    ca_score, ca_note = score_capacity(aum)
    mg_score, mg_note = score_manager(track_record_years)
    fe_score, fe_note = score_fee(fee)

    total = round(rq_score * weights['return'] + dd_score * weights['drawdown'] +
                  st_score * weights['stability'] + ex_score * weights['explain'] +
                  ca_score * weights['capacity'] + mg_score * weights['manager'] +
                  fe_score * weights['fee'], 2)

    # 2. Rating
    if total >= 8.5: rating = 'A'
    elif total >= 7.0: rating = 'B'
    else: rating = 'C'

    # 3. Strategy analysis
    strat_type = STRATEGY_TYPES.get(strategy, strategy)
    ret_sources = RETURN_SOURCES.get(strategy, ['未知'])
    risks = RISK_TYPES.get(strategy, ['未知'])

    # 4. Data validation layer
    data_for_validation = {
        'name': name, 'strategy': strategy,
        'annual_return': annual_return, 'max_dd': max_dd, 'vol': vol,
        'sharpe': sharpe, 'calmar': calmar, 'win_rate': win_rate,
        'profit_loss_ratio': profit_loss_ratio, 'aum': aum, 'fee': fee,
        'track_record_years': track_record_years, 'return_source_cleared': return_source
    }
    validation = run_full_validation(data_for_validation)

    # 5. Red flags with downgrade logic (from validate_data, replaces simple check)
    red_flags_detail = validation['red_flags']['flags']
    red_flags = [f['desc'] for f in red_flags_detail]
    downgrade = validation['red_flags']['downgrade_amount']

    # Apply downgrade
    total_after_downgrade = round(max(1, total - downgrade), 2)
    if total_after_downgrade >= 8.5: rating = 'A'
    elif total_after_downgrade >= 7.0: rating = 'B'
    else: rating = 'C'

    # 6. Stability analysis
    stability_findings = validation['stability']

    # 7. Conditional judgment
    condition_result = validation['conditional_judgment']

    # 8. Decision
    if rating == 'A':
        suitable = "稳健型 / 配置型"
        not_suitable = "短期资金"
    elif rating == 'B':
        suitable = "进攻型 / 配置型"
        not_suitable = "低风险 / 短期资金"
    else:
        suitable = "仅限高风险偏好"
        not_suitable = "低风险 / 大资金"

    result = {
        'name': name,
        'strategy': strat_type,
        'rating': rating,
        'total_score': total_after_downgrade,
        'raw_score': total,
        'downgrade': downgrade,
        'scores': {
            '收益质量': {'score': rq_score, 'note': rq_note, 'weight': 20},
            '回撤控制': {'score': dd_score, 'note': dd_note, 'weight': 20},
            '稳定性': {'score': st_score, 'note': st_note, 'weight': 20},
            '可解释性': {'score': ex_score, 'note': ex_note, 'weight': 15},
            '容量': {'score': ca_score, 'note': ca_note, 'weight': 10},
            '管理人': {'score': mg_score, 'note': mg_note, 'weight': 10},
            '费用': {'score': fe_score, 'note': fe_note, 'weight': 5}
        },
        'return_sources': ret_sources,
        'risks': risks,
        'red_flags': red_flags,
        'stability': stability_findings,
        'data_quality': validation['data_quality'],
        'conditional_judgment': condition_result,
        'decision': {
            'worth_research': 'Yes' if rating in ['A', 'B'] else ('条件式' if rating == 'C' else 'No'),
            'suitable_for': suitable,
            'not_suitable_for': not_suitable,
            'condition': condition_result['verdict'],
            'verdict': '纳入候选池' if rating in ['A', 'B'] else '谨慎观察'
        }
    }
    return result

def format_text(r):
    lines = []
    lines.append(f"📊 Quant Fund OS 分析报告 — {r['name']}")
    lines.append("")

    # 【结论】
    lines.append("═══ 【结论】 ═══")
    lines.append(f"  策略类型: {r['strategy']}")
    lines.append(f"  综合评分: {r['total_score']} / 10 → 评级: {r['rating']}")
    if r.get('downgrade', 0) > 0:
        lines.append(f"  ⚠️ 红旗降级: 原始 {r.get('raw_score', r['total_score'])} → 降级后 {r['total_score']} (-{r['downgrade']})")
    lines.append(f"  是否值得研究: {r['decision']['worth_research']}")
    lines.append(f"  适合资金: {r['decision']['suitable_for']}")
    lines.append(f"  不适合: {r['decision']['not_suitable_for']}")
    lines.append("")

    # 【评分】
    lines.append("═══ 【评分】 ═══")
    for dim, info in r['scores'].items():
        lines.append(f"  {dim}: {info['score']} ({info['note']}) | 权重 {info['weight']}%")
    lines.append("")

    # 【收益来源】
    lines.append("═══ 【收益来源】 ═══")
    lines.append(f"  {', '.join(r['return_sources'])}")
    dq = r.get('data_quality', {})
    lines.append(f"  数据完整性: {dq.get('completeness_pct', 'N/A')}%")
    lines.append(f"  数据质量: {dq.get('quality', 'N/A')}")
    lines.append("")

    # 【风险】
    lines.append("═══ 【风险】 ═══")
    lines.append(f"  策略风险: {', '.join(r['risks'])}")
    if r['red_flags']:
        lines.append("  🚩 红旗:")
        for flag in r['red_flags']:
            lines.append(f"    ❗ {flag}")
    lines.append("")

    # 【稳定性】
    lines.append("═══ 【稳定性】 ═══")
    stability = r.get('stability', [])
    if stability:
        for s in stability:
            icon = '✅' if s['status'] == 'good' else '⚠️' if s['status'] in ['partial', 'moderate'] else '❌'
            lines.append(f"  {icon} {s['metric']}: {s['note']}")
    else:
        lines.append("  数据不足，无法评估")
    lines.append("")

    # 【可投资性】
    lines.append("═══ 【可投资性】 ═══")
    lines.append(f"  条件判断: {r['conditional_judgment']['verdict']}")
    for c in r['conditional_judgment']['conditions_met']:
        lines.append(f"  ✅ {c}")
    for c in r['conditional_judgment']['conditions_failed']:
        lines.append(f"  ❌ {c}")
    lines.append("")

    # 【待验证】
    lines.append("═══ 【待验证】 ═══")
    missing = dq.get('missing_recommended', [])
    if missing:
        for m in missing:
            lines.append(f"  ⏳ {m}")
    if not r.get('return_source_cleared', True):
        lines.append("  ⏳ 收益来源需要管理人进一步说明")
    if not missing and r.get('return_source_cleared', True):
        lines.append("  ✅ 无明显待验证项")
    lines.append("")

    # 【下一步】
    lines.append("═══ 【下一步】 ═══")
    if r['rating'] == 'A':
        lines.append("  1. 纳入核心候选池")
        lines.append("  2. 安排管理人尽调")
        lines.append("  3. 小比例试配跟踪")
    elif r['rating'] == 'B':
        lines.append("  1. 纳入观察池")
        lines.append("  2. 补充缺失数据后复评")
        lines.append("  3. 关注红旗项变化")
    else:
        lines.append("  1. 谨慎观察，不建议配置")
        lines.append("  2. 补充核心数据后可复评")
        lines.append("  3. 重点关注风险项")
    lines.append("")
    lines.append("⚠️ 本系统仅用于研究分析，不构成投资建议。市场有风险，投资需谨慎。")
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--name', required=True)
    p.add_argument('--strategy', required=True)
    p.add_argument('--annual-return', type=float)
    p.add_argument('--max-dd', type=float)
    p.add_argument('--vol', type=float)
    p.add_argument('--sharpe', type=float)
    p.add_argument('--calmar', type=float)
    p.add_argument('--win-rate', type=float)
    p.add_argument('--profit-loss-ratio', type=float)
    p.add_argument('--aum', type=float, help='管理规模(亿)')
    p.add_argument('--fee', type=float, help='综合费率(%)')
    p.add_argument('--track-record', type=float, help='实盘年数')
    p.add_argument('--return-source', action='store_true', help='收益来源是否清晰')
    p.add_argument('--monthly-returns', type=float, nargs='*', help='月度收益序列(%)')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    result = analyze(
        name=args.name, strategy=args.strategy,
        annual_return=args.annual_return, max_dd=args.max_dd, vol=args.vol,
        sharpe=args.sharpe, calmar=args.calmar, win_rate=args.win_rate,
        profit_loss_ratio=args.profit_loss_ratio, aum=args.aum, fee=args.fee,
        track_record_years=args.track_record, return_source=args.return_source
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))

if __name__ == '__main__':
    main()
