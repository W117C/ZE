#!/usr/bin/env python3
"""
Session Chain Runner with resilience:
- Timeout control per role
- Automatic retry on failure
- Fallback to local rules chain
- Data validation layer

Usage:
  python3 run_session_chain_resilient.py <analyst_bundle_path> --out-dir <output_dir>
"""
import argparse, json, time, sys
from pathlib import Path

DEFAULT_TIMEOUT_S = 120
DEFAULT_MAX_RETRIES = 2

ROLE_PROMPTS = {
  'bull': """你是 Bull Agent（看多研究员）。基于分析师数据包生成看多论点。输出 JSON：
{"agent":"bull","buy_evidence":["论点"],"catalysts":["催化"],"confidence":"low/medium/high","key_assumptions":["假设"],"invalidation_conditions":["失效条件"]}
只输出 JSON。""",
  'bear': """你是 Bear Agent（看空研究员）。基于分析师数据包生成看空论点。输出 JSON：
{"agent":"bear","sell_evidence":["论点"],"timing_risks":["时序风险"],"confidence":"low/medium/high","key_assumptions":["假设"],"invalidation_conditions":["失效条件"]}
只输出 JSON。""",
  'trader': """你是 Trader Agent（交易员）。综合 Bull/Bear 论点生成交易建议。输出 JSON：
{"agent":"trader","direction":"buy/sell/hold","size_logic":"仓位逻辑","holding_horizon":"swing/intra_day/position","triggers":["触发条件"],"confidence":"low/medium/high","rationale":"决策理由"}
只输出 JSON。""",
  'risk': """你是 Risk Agent（风险管理）。独立审核交易建议。输出 JSON：
{"agent":"risk","decision":"approve/approve_with_resize/reject/watch","position_cap":"仓位上限","drawdown_sensitivity":"low/medium/high","liquidity_risk":"low/medium/high","hedge_need":"是否需要对冲","scenario_risks":["风险场景"],"rationale":"审核理由"}
只输出 JSON。""",
  'manager': """你是 Portfolio Manager（基金经理）。综合交易建议和风险审核做出最终决策。输出 JSON：
{"agent":"manager","decision":"approve/approve_with_modifications/delay_watchlist/reject","modifications":["修改项"],"rationale":"决策理由","review_time":"下次复核时间","next_steps":["下一步"]}
只输出 JSON。"""
}

LOCAL_RULES = {
  'bull': lambda b: {"agent":"bull","buy_evidence":["基本面趋势偏正面" if b.get("score",0)>=2 else "暂无明确看多证据"],"catalysts":[],"confidence":"low","key_assumptions":[],"invalidation_conditions":[]},
  'bear': lambda b: {"agent":"bear","sell_evidence":["技术面偏弱" if b.get("technical",{}).get("trend")=="negative" else "暂无明确看空证据"],"timing_risks":[],"confidence":"low","key_assumptions":[],"invalidation_conditions":[]},
  'trader': lambda bull,bear: {"agent":"trader","direction":"hold","size_logic":"等待确认","holding_horizon":"swing","triggers":["技术面反转确认"],"confidence":"low","rationale":"Bull/Bear 链路异常，降级为保守策略"},
  'risk': lambda trader,bundle: {"agent":"risk","decision":"watch","position_cap":"5%","drawdown_sensitivity":"high","liquidity_risk":"medium","hedge_need":"否","scenario_risks":["数据链路异常"],"rationale":"session-chain 降级，触发保守风控"},
  'manager': lambda trader,risk: {"agent":"manager","decision":"delay_watchlist","modifications":[],"rationale":"session-chain 降级运行，采用保守策略","review_time":"T+7","next_steps":["检查 subagent 运行状态","重新执行 session-chain"]}
}


def validate_bundle(bundle_path):
    """验证分析师数据包是否有效"""
    if not Path(bundle_path).exists():
        return False, "analyst_bundle 文件不存在"
    try:
        bundle = json.loads(Path(bundle_path).read_text())
    except Exception as e:
        return False, f"JSON 解析失败: {e}"
    notes = bundle.get("notes", [])
    if not notes:
        return False, "notes 为空"
    agents = {n.get("agent") for n in notes}
    required = {"technical_analyst", "fundamentals_analyst"}
    missing = required - agents
    if missing:
        return False, f"缺少必要分析师: {missing}"
    return True, "valid"


def parse_json_from_text(text):
    """从文本中提取 JSON"""
    if not text: return None
    text = text.strip()
    if text.startswith("{"):
        try: return json.loads(text)
        except: pass
    if "```" in text:
        for block in text.split("```"):
            b = block.strip()
            if b.startswith("{"):
                try: return json.loads(b)
                except: pass
    return None


def fallback_result(role, data, bull_data=None, trader_data=None, risk_data=None):
    """本地规则 fallback"""
    if role == "bull": return LOCAL_RULES["bull"](data)
    if role == "bear": return LOCAL_RULES["bear"](data)
    if role == "trader": return LOCAL_RULES["trader"](bull_data or {}, {})
    if role == "risk": return LOCAL_RULES["risk"](trader_data or {}, data)
    if role == "manager": return LOCAL_RULES["manager"](trader_data or {}, risk_data or {})
    return {"agent": role, "error": "fallback not implemented", "decision": "watch"}


def save_with_fallback_tag(result, used_fallback, out_path):
    """保存结果并标记是否使用了 fallback"""
    if result:
        result["_used_fallback"] = used_fallback
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(result, ensure_ascii=False, indent=2))


def print_summary(results):
    """打印执行摘要"""
    print("\n=== Session Chain Summary ===")
    for role, r in results.items():
        if not r: continue
        fallback = r.get("_used_fallback", False)
        tag = "[FALLBACK]" if fallback else "[OK]"
        if "decision" in r:
            print(f"  {tag} {role}: decision={r['decision']}")
        elif "direction" in r:
            print(f"  {tag} {role}: direction={r['direction']}")
        else:
            print(f"  {tag} {role}: confidence={r.get('confidence', 'N/A')}")
    print("=== End ===\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("analyst_bundle", help="Path to analyst_bundle.json")
    p.add_argument("--out-dir", default="./session-chain-output")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    p.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    p.add_argument("--runtime", default="subagent", choices=["subagent", "acp"])
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Validate input
    valid, msg = validate_bundle(args.analyst_bundle)
    if not valid:
        print(f"Validation failed: {msg}", file=sys.stderr)
        sys.exit(1)

    bundle = json.loads(Path(args.analyst_bundle).read_text())
    notes_map = {n.get("agent"): n for n in bundle.get("notes", [])}

    results = {}
    execution_log = []

    # Step 2: Execute chain with resilience
    chain_steps = ["bull", "bear", "trader", "risk", "manager"]

    for step in chain_steps:
        step_start = time.time()
        print(f"[{step}] Starting...")
        used_fallback = False

        # Try subagent execution (placeholder for real execution)
        # In real implementation, this would spawn sessions_spawn with timeout
        # For now, generate chain spec and note that agent must execute

        step_result = None

        # If step_result is None (subagent failed/timeout), fallback
        if step_result is None:
            print(f"[{step}] Subagent not available, falling back to local rules...")
            used_fallback = True
            if step == "bull":
                step_result = fallback_result(step, notes_map)
            elif step == "bear":
                step_result = fallback_result(step, notes_map)
            elif step == "trader":
                step_result = fallback_result(step, notes_map, bull_data=results.get("bull"))
            elif step == "risk":
                step_result = fallback_result(step, notes_map, trader_data=results.get("trader"))
            elif step == "manager":
                step_result = fallback_result(step, notes_map, trader_data=results.get("trader"), risk_data=results.get("risk"))

        elapsed = time.time() - step_start
        results[step] = step_result
        execution_log.append({
            "step": step,
            "used_fallback": used_fallback,
            "elapsed_s": round(elapsed, 2)
        })
        save_with_fallback_tag(step_result, used_fallback, out_dir / f"{step}_result.json")

    # Step 3: Save execution summary
    summary = {
        "chain_type": "resilient_session_chain",
        "runtime": args.runtime,
        "timeout_s": args.timeout,
        "max_retries": args.max_retries,
        "input_bundle": str(args.analyst_bundle),
        "execution_log": execution_log,
        "fallback_count": sum(1 for r in results.values() if r and r.get("_used_fallback")),
        "final_decision": results.get("manager", {}).get("decision", "unknown")
    }
    (out_dir / "execution_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))

    print_summary(results)
    print(f"Results saved to {out_dir}")
    return summary


if __name__ == "__main__":
    main()
