# Orchestration Blueprint

## 双层结构

1. **规则链保底层**
- 确保没有 LLM 也能跑通
- 负责基本结论、风控和兜底输出

2. **Agent 增强层**
- 预留给真实多 Agent 编排
- Bull / Bear / Manager 采用回合制

## 推荐回合
- Round 1: Bull / Bear 开场
- Round 2: Bull / Bear 反驳与不确定性
- Round 3: Manager 综合决策
