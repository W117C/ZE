# System Design

## Pipeline
Data -> Analysts -> Debate -> Trader -> Risk -> Manager -> Execution Ticket

## Principles
- 证据与决策分离
- Bull/Bear 必须先显式分歧
- 风险审核独立于交易建议
- 执行只做交接，不伪装成真实下单

## Input Contracts
- market_context.json
- fundamentals_context.json
- news_context.json
- social_context.json

## Output Contracts
- technical_note.json
- fundamentals_note.json
- news_note.json
- sentiment_note.json
- analyst_bundle.json
- bull_case.json
- bear_case.json
- debate_summary.json
- trade_proposal.json
- risk_review.json
- final_decision.json
- execution_ticket.json
