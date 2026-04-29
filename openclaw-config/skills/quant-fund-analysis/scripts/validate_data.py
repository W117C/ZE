#!/usr/bin/env python3
"""
Quant Fund OS: Data Layer - Validation and completeness check.

Enforces data priority rules and checks minimum data requirements.
"""
import argparse, json, sys

# Data priority levels
PRIORITY = {
    'user_real': 1,       # 用户真实数据（最高）
    'official': 2,        # 官方披露
    'third_party': 3,     # 第三方平台
    'manager_word': 4,    # 管理人口径
    'speculation': 5      # 推测（最低）
}

# Minimum required fields
REQUIRED_FIELDS = {
    'essential': ['annual_return', 'max_dd'],
    'recommended': ['vol', 'sharpe', 'strategy'],
    'optional': ['calmar', 'win_rate', 'profit_loss_ratio', 'aum', 'fee',
                 'track_record_years', 'leverage', 'liquidity_days',
                 'monthly_returns', 'drawdown_duration']
}

# Data quality levels
def assess_data_quality(data):
    """评估数据完整性"""
    missing_essential = [f for f in REQUIRED_FIELDS['essential'] if f not in data or data[f] is None]
    missing_recommended = [f for f in REQUIRED_FIELDS['recommended'] if f not in data or data[f] is None]
    missing_optional = [f for f in REQUIRED_FIELDS['optional'] if f not in data or data[f] is None]

    if missing_essential:
        quality = 'insufficient'
        verdict = '条件式分析'
        can_score = False
    elif missing_recommended:
        quality = 'partial'
        verdict = '有限分析'
        can_score = True
    else:
        quality = 'sufficient'
        verdict = '完整分析'
        can_score = True

    return {
        'quality': quality,
        'verdict': verdict,
        'can_score': can_score,
        'missing_essential': missing_essential,
        'missing_recommended': missing_recommended,
        'missing_optional_count': len(missing_optional),
        'completeness_pct': round((1 - (len(missing_essential) + len(missing_recommended) + len(missing_optional)) / 14) * 100, 1)
    }

def check_data_source(source_type):
    """验证数据来源优先级"""
    if source_type not in PRIORITY:
        return {'valid': False, 'message': f'未知数据源类型: {source_type}'}
    priority = PRIORITY[source_type]
    if priority >= 4:
        return {'valid': True, 'priority': priority, 'warning': '数据来源优先级较低，结论需谨慎'}
    return {'valid': True, 'priority': priority, 'warning': None}

def stability_check(monthly_returns=None, track_record_years=None, max_dd=None, vol=None):
    """稳定性分析"""
    findings = []

    # Cross-cycle stability
    if track_record_years is not None:
        if track_record_years >= 5:
            findings.append({'metric': 'cross_cycle', 'status': 'good', 'note': '实盘≥5年，跨周期验证充分'})
        elif track_record_years >= 3:
            findings.append({'metric': 'cross_cycle', 'status': 'partial', 'note': '实盘3-5年，部分跨周期'})
        else:
            findings.append({'metric': 'cross_cycle', 'status': 'weak', 'note': '实盘<3年，未跨完整周期'})

    # Monthly return consistency
    if monthly_returns and len(monthly_returns) >= 12:
        positive_months = sum(1 for r in monthly_returns if r > 0)
        win_rate_monthly = positive_months / len(monthly_returns)
        if win_rate_monthly >= 0.6:
            findings.append({'metric': 'monthly_consistency', 'status': 'good', 'note': f'月度胜率 {win_rate_monthly:.0%}'})
        else:
            findings.append({'metric': 'monthly_consistency', 'status': 'partial', 'note': f'月度胜率 {win_rate_monthly:.0%}'})
    elif monthly_returns:
        findings.append({'metric': 'monthly_consistency', 'status': 'weak', 'note': f'数据不足 ({len(monthly_returns)} 个月)'})
    else:
        findings.append({'metric': 'monthly_consistency', 'status': 'unknown', 'note': '无月度收益数据'})

    # Drawdown duration check
    max_consecutive_loss = 0
    if monthly_returns:
        current_streak = 0
        for r in monthly_returns:
            if r < 0:
                current_streak += 1
                max_consecutive_loss = max(max_consecutive_loss, current_streak)
            else:
                current_streak = 0
        if max_consecutive_loss > 3:
            findings.append({'metric': 'drawdown_duration', 'status': 'warning', 'note': f'最长连续亏损 {max_consecutive_loss} 个月'})
        elif max_consecutive_loss > 0:
            findings.append({'metric': 'drawdown_duration', 'status': 'good', 'note': f'最长连续亏损 {max_consecutive_loss} 个月'})

    # Volatility consistency
    if vol is not None:
        if vol < 5:
            findings.append({'metric': 'volatility', 'status': 'good', 'note': f'波动率 {vol}%，低波动'})
        elif vol < 15:
            findings.append({'metric': 'volatility', 'status': 'moderate', 'note': f'波动率 {vol}%，中等'})
        else:
            findings.append({'metric': 'volatility', 'status': 'high', 'note': f'波动率 {vol}%，高波动'})

    # Style drift proxy
    if max_dd is not None and vol is not None:
        dd_vol_ratio = max_dd / vol if vol > 0 else 0
        if dd_vol_ratio > 5:
            findings.append({'metric': 'style_drift_risk', 'status': 'warning', 'note': f'回撤/波动比 {dd_vol_ratio:.1f}，可能存在风格暴露漂移'})
        else:
            findings.append({'metric': 'style_drift_risk', 'status': 'good', 'note': f'回撤/波动比 {dd_vol_ratio:.1f}，风格稳定'})

    return findings

def conditional_judgment(data):
    """条件式判断规则"""
    conditions_met = []
    conditions_failed = []

    # Check 1: Drawdown data exists
    if data.get('max_dd') is not None:
        conditions_met.append('回撤数据完整')
    else:
        conditions_failed.append('回撤数据缺失')

    # Check 2: Return not from single market regime
    monthly = data.get('monthly_returns', [])
    if len(monthly) >= 24:
        bull_months = sum(1 for r in monthly if r > 0)
        bear_months = len(monthly) - bull_months
        if bull_months > 0 and bear_months > 0:
            conditions_met.append('收益跨牛熊验证')
        else:
            conditions_failed.append('收益可能依赖单一行情')
    elif data.get('annual_return') is not None and (data.get('track_record_years') or 0) >= 3:
        conditions_met.append('实盘≥3年，有一定验证')
    else:
        conditions_failed.append('验证周期不足')

    # Check 3: Return source explainable
    if data.get('strategy') and data.get('strategy') in ['CTA', 'market-neutral', 'arbitrage']:
        conditions_met.append('收益来源可解释')
    elif data.get('return_source_cleared'):
        conditions_met.append('收益来源已说明')
    else:
        conditions_failed.append('收益来源不清晰')

    if not conditions_failed:
        verdict = '可纳入候选池'
    elif len(conditions_failed) <= 1:
        verdict = '条件式纳入 / 需谨慎'
    else:
        verdict = '高风险 / 不建议'

    return {
        'conditions_met': conditions_met,
        'conditions_failed': conditions_failed,
        'verdict': verdict
    }

def red_flag_check(data):
    """红旗系统 → 降级逻辑"""
    flags = []
    downgrade = 0

    # Flag 1: Return too high but vol too low
    if data.get('annual_return', 0) > 25 and data.get('vol', 100) < 8:
        flags.append({'flag': 'curve_too_smooth', 'desc': '收益高但波动低，曲线过于平滑', 'downgrade': 1.0})
        downgrade += 1.0

    # Flag 2: No drawdown data
    if data.get('max_dd') is None:
        flags.append({'flag': 'no_drawdown', 'desc': '无回撤数据', 'downgrade': 1.0})
        downgrade += 1.0

    # Flag 3: Sharpe too high
    if data.get('sharpe', 0) > 3.0:
        flags.append({'flag': 'sharpe_too_high', 'desc': 'Sharpe过高，需验证真实性', 'downgrade': 0.5})
        downgrade += 0.5

    # Flag 4: Win rate too high
    if data.get('win_rate', 0) > 90:
        flags.append({'flag': 'win_rate_too_high', 'desc': '胜率过高，需验证', 'downgrade': 0.5})
        downgrade += 0.5

    # Flag 5: Small AUM with high return
    if data.get('aum', 10000) < 10 and data.get('annual_return', 0) > 20:
        flags.append({'flag': 'small_aum_high_return', 'desc': '小规模高收益，容量存疑', 'downgrade': 0.5})
        downgrade += 0.5

    # Flag 6: No track record
    if data.get('track_record_years') is not None and data.get('track_record_years') < 1:
        flags.append({'flag': 'no_track_record', 'desc': '实盘记录不足1年', 'downgrade': 1.0})
        downgrade += 1.0

    # Flag 7: Return source unclear
    if not data.get('return_source_cleared') and data.get('strategy') not in ['CTA', 'market-neutral', 'arbitrage']:
        flags.append({'flag': 'return_source_unclear', 'desc': '收益来源模糊', 'downgrade': 0.5})
        downgrade += 0.5

    return {
        'flags': flags,
        'downgrade_amount': downgrade,
        'has_red_flags': len(flags) > 0
    }

def run_full_validation(data):
    """运行完整数据层验证"""
    quality = assess_data_quality(data)
    source_check = check_data_source(data.get('data_source', 'user_real'))
    stability = stability_check(
        monthly_returns=data.get('monthly_returns'),
        track_record_years=data.get('track_record_years'),
        max_dd=data.get('max_dd'),
        vol=data.get('vol')
    )
    condition = conditional_judgment(data)
    red_flags = red_flag_check(data)

    return {
        'data_quality': quality,
        'data_source': source_check,
        'stability': stability,
        'conditional_judgment': condition,
        'red_flags': red_flags
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--json-input', help='JSON file with fund data')
    p.add_argument('--name', default='测试基金')
    p.add_argument('--strategy', default='CTA')
    p.add_argument('--annual-return', type=float)
    p.add_argument('--max-dd', type=float)
    p.add_argument('--vol', type=float)
    p.add_argument('--sharpe', type=float)
    p.add_argument('--calmar', type=float)
    p.add_argument('--win-rate', type=float)
    p.add_argument('--profit-loss-ratio', type=float)
    p.add_argument('--aum', type=float)
    p.add_argument('--fee', type=float)
    p.add_argument('--track-record', type=float)
    p.add_argument('--return-source', action='store_true')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    if args.json_input:
        data = json.loads(__import__('pathlib').Path(args.json_input).read_text())
    else:
        data = {
            'name': args.name,
            'strategy': args.strategy,
            'annual_return': args.annual_return,
            'max_dd': args.max_dd,
            'vol': args.vol,
            'sharpe': args.sharpe,
            'calmar': args.calmar,
            'win_rate': args.win_rate,
            'profit_loss_ratio': args.profit_loss_ratio,
            'aum': args.aum,
            'fee': args.fee,
            'track_record_years': args.track_record,
            'return_source_cleared': args.return_source
        }

    result = run_full_validation(data)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        q = result['data_quality']
        print(f"📊 数据层验证 — {data.get('name', '未知')}")
        print(f"\n数据完整性: {q['completeness_pct']}%")
        print(f"数据质量: {q['quality']} → {q['verdict']}")
        if q['missing_essential']:
            print(f"  ❌ 缺失必要字段: {', '.join(q['missing_essential'])}")
        if q['missing_recommended']:
            print(f"  ⚠️ 缺失推荐字段: {', '.join(q['missing_recommended'])}")
        print(f"  ✅ 缺失可选字段: {q['missing_optional_count']} 个")

        print(f"\n条件判断: {result['conditional_judgment']['verdict']}")
        for c in result['conditional_judgment']['conditions_met']:
            print(f"  ✅ {c}")
        for c in result['conditional_judgment']['conditions_failed']:
            print(f"  ❌ {c}")

        if result['red_flags']['flags']:
            print(f"\n🚩 红旗 ({len(result['red_flags']['flags'])}个):")
            for f in result['red_flags']['flags']:
                print(f"  ❗ {f['desc']} (降级 {f['downgrade']})")
            print(f"  总降级: {result['red_flags']['downgrade_amount']}")
        else:
            print(f"\n🚩 红旗: 无")

        print(f"\n稳定性:")
        for s in result['stability']:
            icon = '✅' if s['status'] == 'good' else '⚠️' if s['status'] in ['partial', 'moderate'] else '❌'
            print(f"  {icon} {s['metric']}: {s['note']}")

if __name__ == '__main__':
    main()
