# Session Chain Contract

## 输入契约
- analyst_bundle.json: 所有分析师输出合并后的数据包

## 角色定义

### bull_agent
- 任务：从分析包中提取看多证据，生成 Bull case
- 输入：analyst_bundle.json
- 输出：bull_case.json

### bear_agent
- 任务：从分析包中提取看空证据，生成 Bear case
- 输入：analyst_bundle.json
- 输出：bear_case.json

### trader_agent
- 任务：综合 Bull/Bear 输出，生成交易建议
- 输入：bull_case.json + bear_case.json
- 输出：trade_proposal.json

### risk_agent
- 任务：独立审核交易建议
- 输入：trade_proposal.json + analyst_bundle.json
- 输出：risk_review.json

### manager_agent
- 任务：最终决策
- 输入：trade_proposal.json + risk_review.json
- 输出：final_decision.json

## 执行模式
- run: 一次性执行，完成后关闭
- session: 持久会话，支持多轮对话

## 容错机制
- 超时控制：默认 120s
- 自动重试：默认 2 次
- Fallback: 本地规则链（subagent 失败时自动切换）
- 数据验证：执行前检查 analyst_bundle 完整性

## 输出标记
- 每个结果包含 `_used_fallback` 字段标记是否使用 fallback
- `execution_summary.json` 记录整条链路执行状态
