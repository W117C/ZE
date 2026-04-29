#!/usr/bin/env python3
"""
Quant Fund OS: Due Diligence Question Generator.

Usage:
  python3 generate_dd_questions.py --strategy market-neutral
  python3 generate_dd_questions.py --strategy CTA --json
"""
import argparse, json

STRATEGY_QUESTIONS = {
    'CTA': [
        '策略在震荡市如何控制回撤？',
        '参数优化周期是多长？是否过拟合？',
        '品种选择逻辑是什么？',
        '趋势反转时如何识别并降低仓位？',
        '管理规模上限如何判断？',
        '实盘与回测的最大偏差是多少？'
    ],
    'market-neutral': [
        '收益中有多少来自 Beta，多少来自 Alpha？',
        '对冲方式是什么？股指期货还是融券？',
        '风格暴露如何控制？是否发生过漂移？',
        '对冲成本上升时策略是否依然有效？',
        '极端行情下（如2015年）表现如何？',
        '策略容量上限在哪里？'
    ],
    'long-short': [
        '选股模型是量化还是主观？',
        '多空比例如何确定？',
        '行业/风格暴露如何控制？',
        '流动性风险管理机制是什么？',
        '止损规则是什么？',
        '收益来源是选股还是择时？'
    ],
    'index-enhance': [
        '跟踪误差控制在什么范围？',
        '超额收益来源是什么？',
        '指数成分股调整时如何操作？',
        '风格偏离度如何监控？',
        '与基准指数的相关性是多少？',
        '超额收益的稳定性如何？'
    ],
    'high-frequency': [
        '交易延迟如何控制？',
        '策略衰减速度如何？',
        '技术基础设施是否依赖关键人？',
        '容量上限如何估算？',
        '监管变化对策略的影响？',
        '实盘换手率是多少？'
    ],
    'options': [
        '主要交易哪些期权品种？',
        '希腊字母敞口如何管理？',
        '尾部风险如何对冲？',
        '波动率跳跃时的应对机制？',
        '流动性不足时如何退出？',
        '收益主要来自方向还是波动率？'
    ],
    'multi-asset': [
        '资产配置逻辑是什么？',
        '再平衡频率和触发条件？',
        '相关性突变时如何应对？',
        '各类资产的容量限制？',
        '流动性错配如何管理？',
        '极端行情下各资产表现如何？'
    ],
    'arbitrage': [
        '套利机会来源是什么？',
        '价差扩大的应对机制？',
        '执行成本和滑点如何控制？',
        '策略衰减速度？',
        '容量上限在哪里？',
        '是否存在方向性敞口？'
    ]
}

GENERAL_QUESTIONS = [
    '策略什么时候会失效？',
    '过去最大回撤发生在什么环境？',
    '是否依赖关键个人或单点基础设施？',
    '风控是盘中、日内还是日终执行？',
    '实盘与回测的差异有多大？',
    '收益来源是否可解释？',
    '策略容量如何估算？',
    '费率结构是什么？',
    '申赎条款和流动性安排？'
]

RED_FLAG_CHECKLIST = [
    '只讲收益，不讲回撤',
    '业绩曲线过于平滑但解释含糊',
    '收益来源讲不清',
    '回测远多于实盘',
    '策略容量说不清',
    '风控描述空泛',
    '对极端行情没有解释',
    '过度依赖某一市场阶段'
]

def generate(strategy=None, include_general=True, include_red_flags=True):
    questions = []
    if strategy and strategy in STRATEGY_QUESTIONS:
        questions.extend(STRATEGY_QUESTIONS[strategy])
    if include_general:
        questions.extend(GENERAL_QUESTIONS)
    if include_red_flags:
        questions.extend([f"🚩 检查: {f}" for f in RED_FLAG_CHECKLIST])
    return questions

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--strategy')
    p.add_argument('--no-general', action='store_true')
    p.add_argument('--no-red-flags', action='store_true')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    questions = generate(
        strategy=args.strategy,
        include_general=not args.no_general,
        include_red_flags=not args.no_red_flags
    )

    if args.json:
        print(json.dumps({'strategy': args.strategy, 'questions': questions}, ensure_ascii=False, indent=2))
    else:
        print(f"=== 尽调问题清单 {'(' + args.strategy + ')' if args.strategy else '(通用)'} ===\n")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        print(f"\n共 {len(questions)} 个问题")

if __name__ == '__main__':
    main()
