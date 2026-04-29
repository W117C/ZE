#!/usr/bin/env python3
"""
Run Session Chain: Execute the trading agent session chain using OpenClaw subagents.

Usage:
  python3 run_session_chain.py <analyst_bundle_path> --mode run --out-dir <output_dir>
  python3 run_session_chain.py <analyst_bundle_path> --mode session --label trading-session
"""
import argparse, json, sys
from pathlib import Path

ROLE_PROMPTS = {
  'bull': """你是 Bull Agent（看多研究员）。
基于提供的分析师数据包，生成看多论点。
输出必须包含 JSON：
{
  "agent": "bull",
  "buy_evidence": ["论点1", "论点2"],
  "catalysts": ["潜在催化"],
  "confidence": "low/medium/high",
  "key_assumptions": ["假设1", "假设2"],
  "invalidation_conditions": ["什么情况下论点失效"]
}
只输出 JSON，不要其他内容。""",
  'bear': """你是 Bear Agent（看空研究员）。
基于提供的分析师数据包，生成看空论点。
输出必须包含 JSON：
{
  "agent": "bear",
  "sell_evidence": ["论点1", "论点2"],
  "timing_risks": ["时序风险"],
  "confidence": "low/medium/high",
  "key_assumptions": ["假设1", "假设2"],
  "invalidation_conditions": ["什么情况下论点失效"]
}
只输出 JSON，不要其他内容。""",
  'trader': """你是 Trader Agent（交易员）。
综合 Bull 和 Bear 的论点，生成交易建议。
输出必须包含 JSON：
{
  "agent": "trader",
  "direction": "buy/sell/hold",
  "size_logic": "仓位逻辑",
  "holding_horizon": "swing/intra_day/position",
  "triggers": ["触发条件"],
  "confidence": "low/medium/high",
  "rationale": "决策理由"
}
只输出 JSON，不要其他内容。""",
  'risk': """你是 Risk Agent（风险管理）。
独立审核交易员建议，评估风险。
输出必须包含 JSON：
{
  "agent": "risk",
  "decision": "approve/approve_with_resize/reject/watch",
  "position_cap": "仓位上限",
  "drawdown_sensitivity": "low/medium/high",
  "liquidity_risk": "low/medium/high",
  "hedge_need": "是否需要对冲",
  "scenario_risks": ["风险场景"],
  "rationale": "审核理由"
}
只输出 JSON，不要其他内容。""",
  'manager': """你是 Portfolio Manager（基金经理）。
综合交易建议和风险审核，做出最终决策。
输出必须包含 JSON：
{
  "agent": "manager",
  "decision": "approve/approve_with_modifications/delay_watchlist/reject",
  "modifications": ["修改项"],
  "rationale": "决策理由",
  "review_time": "下次复核时间",
  "next_steps": ["下一步"]
}
只输出 JSON，不要其他内容。"""
}

def parse_json_from_output(text):
    """Extract JSON from agent output (handles markdown code blocks)."""
    if text.strip().startswith('{'):
        try: return json.loads(text.strip())
        except: pass
    if '```' in text:
        for block in text.split('```'):
            if block.strip().startswith('{'):
                try: return json.loads(block.strip())
                except: pass
    return None

def print_chain_result(results):
    print("\n=== Session Chain Result ===")
    for step in ['bull', 'bear', 'trader', 'risk', 'manager']:
        r = results.get(step)
        if r and 'decision' in r:
            print(f"  [{step}] decision={r['decision']}")
        elif r and 'direction' in r:
            print(f"  [{step}] direction={r['direction']}")
        elif r and 'agent' in r:
            print(f"  [{step}] confidence={r.get('confidence', 'N/A')}")
    print("=== End ===\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('analyst_bundle', help='Path to analyst_bundle.json')
    p.add_argument('--mode', default='run', choices=['run', 'session'])
    p.add_argument('--label', default='trading-session', help='Session label for persistent mode')
    p.add_argument('--out-dir', default='./session-chain-output')
    p.add_argument('--runtime', default='subagent', choices=['subagent', 'acp'])
    args = p.parse_args()

    # Load analyst bundle
    bundle_path = Path(args.analyst_bundle)
    if not bundle_path.exists():
        print(f"Error: analyst_bundle not found at {bundle_path}", file=sys.stderr)
        sys.exit(1)
    bundle = json.loads(bundle_path.read_text())

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # This script is a scaffold for subagent-based execution.
    # It outputs the contract and prompts so that an agent can execute the chain.
    chain_spec = {
      'chain_type': 'trading_agentic_session_chain',
      'mode': args.mode,
      'runtime': args.runtime,
      'label': args.label,
      'roles': list(ROLE_PROMPTS.keys()),
      'input_bundle': bundle_path.name,
      'execution_plan': [
        {'step': 1, 'role': 'bull', 'input': 'analyst_bundle', 'prompt': ROLE_PROMPTS['bull']},
        {'step': 2, 'role': 'bear', 'input': 'analyst_bundle', 'prompt': ROLE_PROMPTS['bear']},
        {'step': 3, 'role': 'trader', 'input': ['bull_output', 'bear_output'], 'prompt': ROLE_PROMPTS['trader']},
        {'step': 4, 'role': 'risk', 'input': ['trader_output', 'analyst_bundle'], 'prompt': ROLE_PROMPTS['risk']},
        {'step': 5, 'role': 'manager', 'input': ['trader_output', 'risk_output'], 'prompt': ROLE_PROMPTS['manager']}
      ],
      'fallback': 'rules_chain'
    }
    spec_path = out_dir / 'session_chain_spec.json'
    spec_path.write_text(json.dumps(chain_spec, ensure_ascii=False, indent=2))
    print(f"Session chain spec written to {spec_path}")
    print("\nTo execute this chain, provide the spec to an OpenClaw agent that can spawn subagents.")

if __name__ == '__main__':
    main()
